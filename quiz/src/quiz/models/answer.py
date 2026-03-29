from django.db import models
from .question import Question
from .session import Session
from .question import QuestionVariant


class Answer(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_variant = models.ForeignKey(
        QuestionVariant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )


    class Meta:
        unique_together = ["session", "question"]
