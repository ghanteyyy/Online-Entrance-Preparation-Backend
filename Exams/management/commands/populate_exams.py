import random
from accounts.models import CustomUser
from django.core.management.base import BaseCommand
from Programmes import models as programme_models
from Programmes import serializers as programme_serializers
from Exams import models as exam_models
from pprint import pprint
from django.db.models import F, Window
from django.db.models.functions import RowNumber, Random


class Command(BaseCommand):
    help = 'Populate exams with sample data'

    def handle(self, *args, **kwargs):
        programme = input("Enter the programme (e.g., BCA, BBA, BSc): ").strip().upper()
        email = input("Enter user email: ").strip()

        questions = programme_models.Question.objects.filter(subject__programme__abbr=programme).annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F('subject')],
                order_by=Random()
            )
        ).filter(row_number__lte=F('subject__question_to_select')).select_related('subject', 'subject__programme').prefetch_related('options')

        questions = sorted(questions, key=lambda x: x.subject.name)

        user_answers = []
        user = CustomUser.objects.get(email__iexact=email)
        exam = exam_models.Exam.objects.create(user=user)

        for question in questions:
            options = list(question.options.all())
            user_selected_option = random.choice(options)

            user_answer = exam_models.UserAnswer(
                exam=exam,
                question=question,
                selected_option=user_selected_option
            )

            if user_selected_option.is_correct:
                exam.total_correct += 1

            user_answers.append(user_answer)

        exam.save()
        exam_models.UserAnswer.objects.bulk_create(user_answers)

        self.stdout.write(self.style.SUCCESS(f'Exam created successfully for user {email} with {len(questions)} questions.'))
