from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import DatasetImport, ModelVersion, TrainingExample


@admin.register(TrainingExample)
class TrainingExampleAdmin(admin.ModelAdmin):
    list_display = ['external_id', 'label', 'subtopic', 'language', 'review_status']
    list_filter = ['review_status', 'label', 'language', 'dataset']
    search_fields = ['external_id', 'question']
    readonly_fields = ['content_hash', 'dataset', 'external_id', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at']

    def has_add_permission(self, request):
        return False  # Use the validated CSV importer to preserve provenance.

    def get_form(self, request, obj=None, **kwargs):
        base = super().get_form(request, obj, **kwargs)

        class ReviewForm(base):
            def clean(self):
                values = super().clean()
                if values.get('review_status') != 'pending':
                    self.instance.reviewed_by = request.user
                    self.instance.reviewed_at = timezone.now()
                else:
                    self.instance.reviewed_by = None
                    self.instance.reviewed_at = None
                return values

        return ReviewForm

    def save_model(self, request, obj, form, change):
        if obj.review_status != 'pending':
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        else:
            obj.reviewed_by = None
            obj.reviewed_at = None
        super().save_model(request, obj, form, change)


@admin.register(DatasetImport, ModelVersion)
class ProvenanceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
