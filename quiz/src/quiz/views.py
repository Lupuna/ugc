from django.db.models import Count, Prefetch
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, Question, QuestionVariant, Quiz, Session
from .paginations import QuizPagination
from .permissions import IsQuizAuthor
from .serializers import (
    AnswerCreateSerializer,
    QuestionSerializer,
    QuizDetailSerializer,
    QuizListSerializer,
    QuizWriteSerializer,
)


class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.select_related("author").all()
    serializer_class = QuizListSerializer
    pagination_class = QuizPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["title"]
    ordering = ["title"]


class QuizDetailView(APIView):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz.objects.select_related("author"), pk=pk)
        total_questions = Question.objects.filter(quiz=quiz).count()

        question_id = request.query_params.get("question_id")
        base_qs = Question.objects.prefetch_related("questionvariant_set")

        if question_id:
            question = get_object_or_404(base_qs, id=question_id, quiz=quiz)
        else:
            question = base_qs.filter(quiz=quiz).order_by("order").first()
            if question is None:
                return Response(
                    {"error": "This quiz has no questions."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {
                "quiz_id": quiz.id,
                "title": quiz.title,
                "author_name": quiz.author.username,
                "total_questions": total_questions,
                "question": QuestionSerializer(question).data,
            }
        )


class AnswerView(APIView):
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        serializer = AnswerCreateSerializer(
            data=request.data, context={"quiz_id": quiz_id}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session, _ = Session.objects.get_or_create(
            quiz=quiz, user_id=data["user_id"]
        )

        _, created = Answer.objects.update_or_create(
            session=session,
            question_id=data["question_id"],
            defaults={"answer_variant_id": data.get("answer_variant_id")},
        )

        return Response(
            {"status": "created" if created else "updated"},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AuthorQuizListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsQuizAuthor]
    pagination_class = QuizPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return QuizWriteSerializer
        return QuizListSerializer

    def get_queryset(self):
        return Quiz.objects.select_related("author").filter(author_id=self.kwargs["user_id"])

    def perform_create(self, serializer):
        serializer.save(author_id=self.kwargs["user_id"])


class AuthorQuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsQuizAuthor]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return QuizWriteSerializer
        return QuizDetailSerializer

    def get_queryset(self):
        return (
            Quiz.objects.filter(author_id=self.kwargs["user_id"])
            .select_related("author")
            .prefetch_related("question_set__questionvariant_set")
        )


class StatisticView(APIView):
    permission_classes = [IsQuizAuthor]

    def get(self, request, user_id, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, author_id=user_id)
        total_sessions = Session.objects.filter(quiz=quiz).count()
        questions = (
            Question.objects.filter(quiz=quiz)
            .prefetch_related(
                Prefetch(
                    "questionvariant_set",
                    queryset=QuestionVariant.objects.annotate(
                        answer_count=Count("answer"),
                    ).order_by("order"),
                )
            )
            .order_by("order")
        )

        return Response(
            {
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "total_sessions": total_sessions,
                "questions": [
                    {
                        "question_id": q.id,
                        "text": q.text,
                        "variants": [
                            {
                                "variant_id": v.id,
                                "text": v.text,
                                "answer_count": v.answer_count,
                            }
                            for v in q.questionvariant_set.all()
                        ],
                    }
                    for q in questions
                ],
            }
        )
