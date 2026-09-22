"""Curated training data is distinct from automatic predictions and chat history."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Trim
from django.db.models.lookups import Exact
from mathapp_ml.data import LABELS, STATUSES, question_hash


class DatasetImport(models.Model):
    filename = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64, unique=True)
    row_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class TrainingExample(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    dataset = models.ForeignKey(DatasetImport, on_delete=models.PROTECT, related_name='examples')
    question = models.TextField()
    content_hash = models.CharField(max_length=64, unique=True, editable=False)
    label = models.CharField(max_length=20, choices=[(v, v) for v in LABELS])
    subtopic = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=[('en', 'English'), ('mk', 'Macedonian')])
    source = models.CharField(max_length=500)
    group_id = models.CharField(max_length=200, db_index=True)
    review_status = models.CharField(max_length=10, choices=[(v, v) for v in STATUSES], default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['review_status', 'label'])]
        constraints = [
            models.CheckConstraint(condition=Q(label__in=LABELS), name='training_valid_label'),
            models.CheckConstraint(condition=Q(review_status__in=STATUSES), name='training_valid_status'),
            models.CheckConstraint(condition=Q(language__in=['en', 'mk']), name='training_valid_language'),
            models.CheckConstraint(condition=~Exact(Trim('question'), models.Value('')), name='training_nonempty_question'),
            models.CheckConstraint(condition=Q(review_status='pending') | Q(reviewed_by__isnull=False, reviewed_at__isnull=False), name='training_review_attribution'),
        ]

    def clean(self):
        super().clean()
        if not self.question.strip():
            raise ValidationError({'question': 'Question cannot be empty'})
        self.content_hash = question_hash(self.question)
        if type(self).objects.filter(content_hash=self.content_hash).exclude(pk=self.pk).exists():
            raise ValidationError({'question': 'This question already exists'})
        if self.review_status != 'pending' and (not self.reviewed_by_id or not self.reviewed_at):
            raise ValidationError('Reviewed examples require a reviewer and timestamp')

    def save(self, *args, **kwargs):
        self.content_hash = question_hash(self.question)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'content_hash'}
        super().save(*args, **kwargs)


class ModelVersion(models.Model):
    version = models.CharField(max_length=100, unique=True)
    artifact_path = models.CharField(max_length=1000)
    artifact_sha256 = models.CharField(max_length=64)
    dataset_sha256 = models.CharField(max_length=64)
    metrics = models.JSONField(default=dict)
    experimental = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
