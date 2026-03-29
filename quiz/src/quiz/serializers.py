from rest_framework import serializers

from .models import Quiz, Question, QuestionVariant


class QuestionVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionVariant
        fields = ["id", "text", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    variants = QuestionVariantSerializer(
        source="questionvariant_set", many=True, read_only=True
    )

    class Meta:
        model = Question
        fields = ["id", "text", "order", "variants"]


class QuizListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "author_name", "creation_date"]


class QuizDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    questions = QuestionSerializer(
        source="question_set", many=True, read_only=True
    )

    class Meta:
        model = Quiz
        fields = ["id", "title", "author_name", "creation_date", "questions"]


class VariantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionVariant
        fields = ["text", "order"]


class QuestionWriteSerializer(serializers.ModelSerializer):
    variants = VariantWriteSerializer(many=True)

    class Meta:
        model = Question
        fields = ["text", "order", "variants"]


class QuizWriteSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions"]
        read_only_fields = ["id"]

    def _create_questions(self, quiz, questions_data):
        for q_data in questions_data:
            variants_data = q_data.pop("variants", [])
            question = Question.objects.create(quiz=quiz, **q_data)
            if variants_data:
                QuestionVariant.objects.bulk_create(
                    [QuestionVariant(question=question, **variant) for variant in variants_data]
                )

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)
        self._create_questions(quiz, questions_data)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if questions_data is not None:
            instance.question_set.all().delete()
            self._create_questions(instance, questions_data)

        return instance


class AnswerCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    answer_variant_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_question_id(self, value):
        quiz_id = self.context["quiz_id"]
        if not Question.objects.filter(id=value, quiz_id=quiz_id).exists():
            raise serializers.ValidationError(
                "This question does not belong to the given quiz."
            )
        return value

    def validate(self, data):
        variant_id = data.get("answer_variant_id")
        if variant_id is not None:
            exists = QuestionVariant.objects.filter(
                id=variant_id, question_id=data["question_id"]
            ).exists()
            if not exists:
                raise serializers.ValidationError(
                    {"answer_variant_id": "This answer option does not belong to the given question."}
                )
        return data
