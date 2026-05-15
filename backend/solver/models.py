from django.db import models
from django.contrib.auth.models import User


class SolveHistory(models.Model):
    INPUT_TYPES = [('text', 'Text'), ('image', 'Image'), ('pdf', 'PDF')]
    DOMAINS     = [('calculus', 'Calculus'), ('probability', 'Probability'),
                   ('discrete', 'Discrete'), ('unknown', 'Unknown')]
    OCR_ENGINES = [('tesseract', 'Tesseract'), ('paddle', 'PaddleOCR'), ('none', 'None')]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solves')
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
