from rest_framework import serializers
from .models import SolveHistory


class SolveHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = SolveHistory
        fields = ['id', 'input_type', 'problem_text', 'solution',
                  'domain', 'ocr_engine', 'created_at']
        read_only_fields = fields
