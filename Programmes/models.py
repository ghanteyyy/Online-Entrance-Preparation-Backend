from django.db import models
from django.db.models import Q
from utils import utils


class Programme(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)

    name = models.CharField(blank=False, null=False, max_length=255)
    abbr = models.CharField(blank=False, null=False, max_length=10)
    total_questions = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        return f'{self.name} ({self.abbr})'


class Subject(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name="subjects")

    name = models.CharField(blank=False, null=False, max_length=100)
    question_to_select = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        return f'{self.name} ({self.programme.abbr})'


class Question(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")

    title = models.TextField(blank=False, null=False)


class Option(models.Model):
    class Meta:
        unique_together = ("question", "option")
        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=Q(is_correct=True),
                name='only_one_correct_option'
            )
        ]

    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)

    option = models.TextField(blank=False, null=False)
    is_correct = models.BooleanField()
