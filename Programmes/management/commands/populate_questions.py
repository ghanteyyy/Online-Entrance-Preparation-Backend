# script to populate questions for testing purposes
import json
from pathlib import Path
from Programmes import models
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''
    Sample JSON structure:
        {
            "subject": "English",
            "question": "An apple of discord",
            "programme": "BCA",
            "answer": "cause of quarrel",
            "choices": [
                "cause of wealth",
                "cause of illness",
                "cause of happiness",
                "cause of quarrel"
            ],
            "TotalQuestionsToSelect": 40
        }
    '''

    help = 'Populate questions from a JSON file'

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        file_path = base_dir / 'static' / 'Questions.json'

        programme_maps = {
            'BCA': 'Bachelor of Computer Applications',
            'BBA': 'Bachelor of Business Administration',
            'BSc': 'Bachelor of Science',
            'BIT': 'Bachelor of Information Technology',
            'BIM': 'Bachelor of Information Management',
            'BSCCSIT': 'Bachelor of Science in Computer Science and Information Technology',
        }

        with open(file_path, 'r') as f:
            data = json.load(f)

        for item in data:
            try:
                subject_name = item.get("subject", "").strip()
                title = item.get("question", "").strip()
                abbr = item.get("programme", "").strip().upper()

                if not subject_name or not title or not abbr:
                    break

                programme = models.Programme.objects.filter(abbr__iexact=abbr).first()

                if not programme:
                    programme, created = models.Programme.objects.get_or_create(name=programme_maps.get(abbr, abbr), abbr=abbr)

                subject = models.Subject.objects.filter(name__iexact=subject_name, programme=programme).first()

                if not subject:
                    subject, created = models.Subject.objects.get_or_create(name=subject_name, programme=programme, question_to_select=item.get("TotalQuestionsToSelect", 0))

                question, created = models.Question.objects.get_or_create(programme=programme, subject=subject, title=title)

                if not created:
                    continue

                for choice in item.get("choices", []):
                    choice_text = choice.strip()

                    if not choice_text:
                        continue

                    is_correct = choice_text == item.get("answer", "").strip()

                    models.Option.objects.get_or_create(question=question, option=choice_text, is_correct=is_correct)

            except Exception as e:
                print(f"Error processing item: {item}")
                break
