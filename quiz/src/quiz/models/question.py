from django.db import models
from .quiz import Quiz


class Question(models.Model):
    text = models.TextField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["quiz", "order"]),
        ]
        unique_together = ["quiz", "order"]


class QuestionVariant(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["question", "order"]
