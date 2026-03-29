from django.db import models
from .quiz import Quiz
from django.contrib.auth.models import User


class Session(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["quiz", "user"]
