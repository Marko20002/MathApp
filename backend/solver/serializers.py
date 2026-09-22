from rest_framework import serializers
from .models import SolveHistory, Conversation, Message


class SolveInputSerializer(serializers.Serializer):
    input_type = serializers.ChoiceField(choices=['text', 'image', 'pdf'], default='text')
    content = serializers.CharField(trim_whitespace=False, max_length=14000000, required=False, allow_blank=True, default='')
    file = serializers.FileField(required=False)
    ocr_engine = serializers.ChoiceField(choices=['1', '2'], default='2')
    conversation_id = serializers.IntegerField(min_value=1, required=False)

    def validate(self, attrs):
        if 'file' in attrs:
            if attrs['input_type'] == 'text':
                raise serializers.ValidationError('Choose image or PDF for an attachment.')
            if attrs['file'].size > 10000000:
                raise serializers.ValidationError('File exceeds 10 MB.')
            if len(attrs['content']) > 20000:
                raise serializers.ValidationError('Caption exceeds 20000 characters.')
            return attrs
        if not attrs['content'].strip():
            raise serializers.ValidationError('Content cannot be blank.')
        if attrs['input_type'] == 'text' and len(attrs['content']) > 20000:
            raise serializers.ValidationError('Text exceeds 20000 characters.')
        return attrs


class ClassifyInputSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=20000, allow_blank=False)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    analysis = serializers.SerializerMethodField()

    def get_analysis(self, obj):
        analysis = dict(obj.analysis)
        problem = self.context.get('problems', {}).get(analysis.get('problem_id'))
        if problem:
            analysis['reference'] = {'answer': problem.reference_answer, 'label': problem.reference_label,
                                     'reviewed_at': problem.reviewed_at, 'reviewed_by': problem.reviewed_by_id}
        return analysis

    class Meta:
        model = Message
        fields = ['id', 'sequence', 'role', 'content', 'created_at', 'analysis']


class SolveHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = SolveHistory
        fields = ['id', 'input_type', 'problem_text', 'solution',
                  'domain', 'ocr_engine', 'created_at']
        read_only_fields = fields
