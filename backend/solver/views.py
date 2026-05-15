import base64
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import SolveHistory
from .serializers import SolveHistorySerializer
from core.pipeline import solve_text, solve_image_bytes, solve_pdf_bytes

PROBLEM_TEXT_MAX = 500

OCR_ENGINE_NAMES = {'1': 'tesseract', '2': 'easyocr'}


def _decode_b64(content, label):
    """Decode base64 string; returns (bytes, None) or (None, error Response)."""
    try:
        return base64.b64decode(content), None
    except Exception:
        return None, Response(
            {'error': f'Invalid base64 {label}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SolveView(APIView):
    def post(self, request):
        input_type = request.data.get('input_type', 'text')
        content    = request.data.get('content', '')
        ocr_engine = request.data.get('ocr_engine', '1')

        if not content:
            return Response({'error': 'No content provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if input_type == 'text':
            result       = solve_text(content)
            problem_text = content[:PROBLEM_TEXT_MAX]
            engine_used  = 'none'

        elif input_type == 'image':
            image_bytes, err = _decode_b64(content, 'image')
            if err:
                return err
            result       = solve_image_bytes(image_bytes, ocr_engine)
            problem_text = result.get('problem_text', '')[:PROBLEM_TEXT_MAX]
            engine_used  = OCR_ENGINE_NAMES.get(ocr_engine, 'easyocr')

        elif input_type == 'pdf':
            pdf_bytes, err = _decode_b64(content, 'PDF')
            if err:
                return err
            result       = solve_pdf_bytes(pdf_bytes)
            problem_text = result.get('problem_text', '')[:PROBLEM_TEXT_MAX]
            engine_used  = 'none'

        else:
            return Response({'error': 'Invalid input_type.'}, status=status.HTTP_400_BAD_REQUEST)

        solution = result.get('solution', '')
        domain   = result.get('domain', 'unknown')

        if not solution:
            return Response(
                {'error': 'Could not extract or solve the problem.'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if solution.strip() == '[NOT_MATH]':
            return Response(
                {'error': 'This does not look like a math problem. Please enter a math question.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SolveHistory.objects.create(
            user=request.user,
            input_type=input_type,
            problem_text=problem_text,
            solution=solution,
            domain=domain,
            ocr_engine=engine_used,
        )

        return Response({'solution': solution, 'domain': domain, 'problem_text': problem_text})


class HistoryListView(ListAPIView):
    serializer_class = SolveHistorySerializer

    def get_queryset(self):
        return SolveHistory.objects.filter(user=self.request.user)


class StatsView(APIView):
    def get(self, request):
        stats = SolveHistory.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            text_solves=Count('id',  filter=Q(input_type='text')),
            image_solves=Count('id', filter=Q(input_type='image')),
            pdf_solves=Count('id',   filter=Q(input_type='pdf')),
            calculus=Count('id',     filter=Q(domain='calculus')),
            probability=Count('id',  filter=Q(domain='probability')),
            discrete=Count('id',     filter=Q(domain='discrete')),
        )
        return Response(stats)
