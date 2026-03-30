from django.db import models
from utils import utils


class Exam(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)

    total_correct = models.IntegerField(blank=False, null=False, default=0)


class UserAnswer(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="user_answers")
    question = models.ForeignKey("Programmes.Question", on_delete=models.CASCADE)
    selected_option = models.ForeignKey("Programmes.Option", on_delete=models.CASCADE)
