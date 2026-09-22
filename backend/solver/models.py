from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Trim
from django.db.models.lookups import Exact


class Conversation(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=200)
    busy_until = models.DateTimeField(null=True, blank=True)
    lease = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-id']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sequence = models.PositiveIntegerField()
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    analysis = models.JSONField(default=dict, blank=True)
    memory = models.TextField(blank=True)  # Derived snapshot; never overwrites original messages.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence']
        constraints = [
            models.UniqueConstraint(fields=['conversation', 'sequence'], name='message_unique_sequence'),
            models.CheckConstraint(condition=Q(role__in=['user', 'assistant']), name='message_valid_role'),
            models.CheckConstraint(condition=~Exact(Trim('content'), models.Value('')), name='message_nonempty_content'),
        ]


class Problem(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='problem')
    text = models.TextField()  # Complete extracted task; never a lossy summary.
    input_type = models.CharField(max_length=10)
    reference_answer = models.TextField(blank=True)
    reference_label = models.CharField(max_length=20, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(input_type__in=['text', 'image', 'pdf']), name='problem_valid_input_type'),
            models.CheckConstraint(condition=~Exact(Trim('text'), models.Value('')), name='problem_nonempty_text'),
        ]


class Classification(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='classification')
    model = models.ForeignKey('datasets.ModelVersion', null=True, blank=True, on_delete=models.PROTECT)
    model_version = models.CharField(max_length=100)
    predicted_label = models.CharField(max_length=20)
    scores = models.JSONField(default=dict)
    uncertain = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(predicted_label__in=['CALCULUS', 'PROBABILITY', 'DISCRETE', 'UNKNOWN']), name='classification_valid_label')]


class SolveEvent(models.Model):
    """Operational metadata only. Do not copy prompts, keys, or provider errors here."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('succeeded', 'Succeeded'), ('failed', 'Failed')])
    error_code = models.CharField(max_length=50, blank=True)
    provider = models.CharField(max_length=30, blank=True)
    model = models.CharField(max_length=100, blank=True)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    reasoning_tokens = models.PositiveIntegerField(null=True, blank=True)
    cached_input_tokens = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(status__in=['succeeded', 'failed']), name='solve_event_valid_status')]


class SolveHistory(models.Model):
    INPUT_TYPES = [('text', 'Text'), ('image', 'Image'), ('pdf', 'PDF')]
    DOMAINS     = [('calculus', 'Calculus'), ('probability', 'Probability'),
                   ('discrete', 'Discrete'), ('unknown', 'Unknown')]
    OCR_ENGINES = [('tesseract', 'Tesseract'), ('paddle', 'PaddleOCR'), ('easyocr', 'EasyOCR'), ('none', 'None')]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solves')
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE, related_name='solves')
    input_type   = models.CharField(max_length=10, choices=INPUT_TYPES)
    problem_text = models.TextField(blank=True)   # the text that was sent to AI
    solution     = models.TextField()             # AI response
    domain       = models.CharField(max_length=20, choices=DOMAINS, default='unknown')
    ocr_engine   = models.CharField(max_length=20, choices=OCR_ENGINES, default='none')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | {self.input_type} | {self.domain} | {self.created_at.date()}"
