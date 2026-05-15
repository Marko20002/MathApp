from django.contrib import admin
from .models import SolveHistory


@admin.register(SolveHistory)
class SolveHistoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'input_type', 'domain', 'ocr_engine', 'short_problem', 'created_at']
    list_filter   = ['input_type', 'domain', 'ocr_engine']
    search_fields = ['user__username', 'problem_text']
    ordering      = ['-created_at']
    readonly_fields = ['user', 'input_type', 'problem_text', 'solution', 'domain', 'ocr_engine', 'created_at']

    @admin.display(description='Problem (preview)')
    def short_problem(self, obj):
        return obj.problem_text[:60] + '…' if len(obj.problem_text) > 60 else obj.problem_text
