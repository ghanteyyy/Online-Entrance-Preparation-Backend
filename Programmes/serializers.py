from rest_framework import serializers
from . import models


class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Programme
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    programme = serializers.CharField(source="programme.name", read_only=True)

    class Meta:
        model = models.Subject
        fields = '__all__'


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Option
        fields = ['id', 'option', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    abbr = serializers.CharField(source="programme.abbr", read_only=True)
    programme = serializers.CharField(source="programme.name", read_only=True)
    subject = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = models.Question
        fields = '__all__'
