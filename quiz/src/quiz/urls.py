from django.urls import path

from .views import (
    AnswerView,
    AuthorQuizDetailView,
    AuthorQuizListCreateView,
    QuizDetailView,
    QuizListView,
    StatisticView,
)

urlpatterns = [
    path("quizzes/", QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quizzes/<int:quiz_id>/answer/", AnswerView.as_view(), name="quiz-answer"),
    path(
        "users/<int:user_id>/quizzes/",
        AuthorQuizListCreateView.as_view(),
        name="author-quiz-list",
    ),
    path(
        "users/<int:user_id>/quizzes/<int:pk>/",
        AuthorQuizDetailView.as_view(),
        name="author-quiz-detail",
    ),
    path(
        "users/<int:user_id>/quizzes/<int:quiz_id>/statistic/",
        StatisticView.as_view(),
        name="statistic",
    ),
]
