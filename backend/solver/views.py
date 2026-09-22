import base64
import binascii
import logging
import uuid
import json
import zlib
from datetime import timedelta
from django.utils import timezone
from django.http import StreamingHttpResponse
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import UserRateThrottle
from core.context import build_context
from django.db import transaction
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import SolveHistory, Conversation, Message, Problem, Classification, SolveEvent
from .serializers import (SolveHistorySerializer, SolveInputSerializer, ClassifyInputSerializer,
                          ConversationSerializer, MessageSerializer)
from core.pipeline import solve_text, solve_image_bytes, solve_pdf_bytes
from core.classification import classify_question
from core.errors import PipelineError
from datasets.models import ModelVersion

logger = logging.getLogger(__name__)


class ClassifyView(APIView):
    """Authenticated, local-only inference. No paid provider calls."""
    def post(self, request):
        serializer = ClassifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = classify_question(serializer.validated_data['question'])
        except (OSError, ValueError, KeyError):
            return Response({'error': 'Classifier unavailable.'}, status=503)
        if result['model_version'] == 'unconfigured':
            return Response({'error': 'Classifier is not configured.'}, status=503)
        return Response(result)


class SolveThrottle(UserRateThrottle):
    rate = '6/min'
    scope = 'solve'


class SolveView(APIView):
    throttle_classes = [SolveThrottle]

    def post(self, request):
        serializer = SolveInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        conversation = None
        lease = uuid.uuid4()
        if 'conversation_id' in data:
            conversation = get_object_or_404(Conversation, pk=data['conversation_id'], owner=request.user)
            claimed = Conversation.objects.filter(pk=conversation.pk).filter(
                Q(busy_until__isnull=True) | Q(busy_until__lt=timezone.now())
            ).update(busy_until=timezone.now() + timedelta(minutes=10), lease=lease)
            if not claimed:
                return Response({'error': 'An answer is already being generated in this chat.'}, status=409)
        try:
            return self.complete(request, data, conversation, lease)
        finally:
            if conversation:
                Conversation.objects.filter(pk=conversation.pk, lease=lease).update(busy_until=None, lease=None)

    def complete(self, request, data, conversation, lease):
        input_type, content = data['input_type'], data['content']
        try:
            history, context_info = build_context(conversation)
            if input_type == 'text':
                result = solve_text(content, history=history)
            else:
                if 'file' in data:
                    payload = data['file'].read()
                    caption = content
                else:
                    try:
                        payload = base64.b64decode(content, validate=True)
                    except (ValueError, binascii.Error) as exc:
                        raise PipelineError('invalid_base64', 'Invalid file encoding.', 400) from exc
                    caption = ''
                if len(payload) > 10000000:
                    raise PipelineError('file_too_large', 'File exceeds 10 MB.', 400)
                handler = solve_image_bytes if input_type == 'image' else solve_pdf_bytes
                result = handler(payload, history=history, caption=caption)
        except PipelineError as exc:
            SolveEvent.objects.create(owner=request.user, status='failed', error_code=exc.code,
                provider='openai' if exc.usage else '', **exc.usage)
            return Response({'error': exc.message, 'code': exc.code}, status=exc.status)
        except (OSError, ValueError, ImportError):
            SolveEvent.objects.create(owner=request.user, status='failed', error_code='service_unavailable')
            return Response({'error': 'A required solver service is unavailable.'}, status=503)

        with transaction.atomic():
            if conversation is None:
                conversation = Conversation.objects.create(owner=request.user, title=result['problem_text'][:200])
            else:
                conversation = Conversation.objects.select_for_update().get(pk=conversation.pk, owner=request.user)
                if conversation.lease != lease:
                    return Response({'error': 'This request expired. Reload the chat before continuing.'}, status=409)
            last = conversation.messages.aggregate(last=Max('sequence'))['last']
            sequence = 0 if last is None else last + 1
            user_message = Message.objects.create(conversation=conversation, sequence=sequence,
                role='user', content=content if input_type == 'text' else result['problem_text'])
            problem = Problem.objects.create(message=user_message, text=result['problem_text'], input_type=input_type)
            classification = result['classification']
            Classification.objects.create(problem=problem,
                model=ModelVersion.objects.filter(version=classification['model_version']).first(),
                model_version=classification['model_version'], predicted_label=classification['label'],
                scores=classification['scores'], uncertain=classification['uncertain'])
            analysis = {
                'problem_id': problem.pk, 'classification': classification,
                'openai_subject': result.get('openai_subject', 'UNKNOWN'),
                'final_answer': result.get('final_answer', ''),
                'provider_model': result['provider_model'], 'usage': result['usage'],
                'context': context_info, 'input_type': input_type,
                'reference': {'answer': '', 'label': '', 'reviewed_at': None, 'reviewed_by': None},
            }
            assistant = Message.objects.create(conversation=conversation, sequence=sequence + 1,
                role='assistant', content=result['solution'], analysis=analysis, memory=result.get('memory', ''))
            SolveHistory.objects.create(user=request.user, conversation=conversation, input_type=input_type,
                problem_text=result['problem_text'], solution=result['solution'], domain=result['domain'],
                ocr_engine='easyocr' if input_type == 'image' else 'none')
            SolveEvent.objects.create(owner=request.user, status='succeeded',
                provider=result['provider'], model=result['provider_model'], **result['usage'])
            conversation.save(update_fields=['updated_at'])
        # Memory snapshots remain private to the backend; never ask the browser to
        # resend the transcript. New requests carry just this id and the new task.
        public_result = {k: v for k, v in result.items() if k != 'memory'}
        return Response({**public_result, 'conversation_id': conversation.pk,
            'messages': MessageSerializer([user_message, assistant], many=True).data})


class ReferenceInputSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=20000, allow_blank=False)
    label = serializers.ChoiceField(choices=['CALCULUS', 'PROBABILITY', 'DISCRETE', 'OTHER', 'UNKNOWN'])


class ReferenceView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk, message__conversation__owner=request.user)
        serializer = ReferenceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        problem.reference_answer = serializer.validated_data['answer']
        problem.reference_label = serializer.validated_data['label']
        problem.reviewed_by = request.user
        problem.reviewed_at = timezone.now()
        problem.save(update_fields=['reference_answer', 'reference_label', 'reviewed_by', 'reviewed_at'])
        return Response({'answer': problem.reference_answer, 'label': problem.reference_label,
                         'reviewed_at': problem.reviewed_at, 'reviewed_by': request.user.pk})


class ConversationExportView(APIView):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk, owner=request.user)
        # Streaming gzip export: bounded memory even for very long transcripts.
        def chunks():
            compressor = zlib.compressobj(wbits=31)
            yield compressor.compress(b'{"version":1,"messages":[')
            for index, message in enumerate(conversation.messages.iterator()):
                record = {'role': message.role, 'content': message.content,
                          'sequence': message.sequence, 'created_at': message.created_at.isoformat()}
                yield compressor.compress(((',' if index else '') + json.dumps(record, ensure_ascii=False)).encode())
            yield compressor.compress(b']}')
            yield compressor.flush()
        response = StreamingHttpResponse(chunks(), content_type='application/gzip')
        response['Content-Disposition'] = f'attachment; filename="mathapp-chat-{pk}.json.gz"'
        return response


class HistoryListView(ListAPIView):
    serializer_class = SolveHistorySerializer

    def get_queryset(self):
        return SolveHistory.objects.filter(user=self.request.user)


class ConversationPagination(PageNumberPagination):
    page_size = 50


class ConversationListView(ListAPIView):
    serializer_class = ConversationSerializer
    pagination_class = ConversationPagination

    def get_queryset(self):
        return Conversation.objects.filter(owner=self.request.user)


class MessageListView(ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = ConversationPagination

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['pk'], owner=self.request.user)
        return conversation.messages.order_by('-sequence')

    def get_serializer(self, *args, **kwargs):
        context = self.get_serializer_context()
        ids = [m.analysis.get('problem_id') for m in args[0]] if args and kwargs.get('many') else []
        context['problems'] = {p.pk: p for p in Problem.objects.filter(
            pk__in=ids, message__conversation__owner=self.request.user)}
        kwargs['context'] = context
        return super().get_serializer(*args, **kwargs)


class StatsView(APIView):
    def get(self, request):
        stats = SolveHistory.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            text_solves=Count('id', filter=Q(input_type='text')),
            image_solves=Count('id', filter=Q(input_type='image')),
            pdf_solves=Count('id', filter=Q(input_type='pdf')),
            calculus=Count('id', filter=Q(domain='calculus')),
            probability=Count('id', filter=Q(domain='probability')),
            discrete=Count('id', filter=Q(domain='discrete')),
        )
        return Response(stats)
