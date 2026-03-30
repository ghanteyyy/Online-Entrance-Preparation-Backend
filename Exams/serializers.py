from . import models
from rest_framework import serializers
from Programmes.serializers import QuestionSerializer, OptionSerializer


class UserAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="question.title", read_only=True)
    options = OptionSerializer(source="question.options", many=True, read_only=True)
    user_selected_option = serializers.CharField(source="selected_option.option", read_only=True)

    class Meta:
        exclude = ['exam', 'selected_option']
        model = models.UserAnswer


class ExamSerializer(serializers.ModelSerializer):
    exam_id = serializers.CharField(source="id", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)
    user_answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        fields = ['exam_id', 'user', 'total_correct', 'user_answers']
        model = models.Exam

