from django.db.models import Q
from django.db.models import Prefetch

import rest_framework.status as status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from Exams import models, serializers


class Exams(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExamSerializer

    def get_queryset(self):
        return models.Exam.objects.select_related(
            "user"
        ).prefetch_related(
            Prefetch(
                "user_answers",
                queryset=models.UserAnswer.objects.select_related(
                    "question",
                    "selected_option"
                ).prefetch_related(
                    "question__options"
                )
            )
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search exams by name or description',
                required=False,
                type=OpenApiTypes.STR
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "count": queryset.count(),
                "results": serializer.data
            }
        )

    @extend_schema(
        request=serializers.ExamSerializer,
        responses=serializers.ExamSerializer,
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    "name": "Exam 1",
                    "description": "This is the first exam.",
                    "duration": 60,
                    "total_marks": 100
                },
                request_only=True,
                response_only=False
            ),
            OpenApiExample(
                'Example Response',
                value={
                    "id": 1,
                    "name": "Exam 1",
                    "description": "This is the first exam.",
                    "duration": 60,
                    "total_marks": 100
                },
                request_only=False,
                response_only=True
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=serializers.ExamSerializer,
        responses=serializers.ExamSerializer,
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    "name": "Updated Exam 1",
                    "description": "This is the updated first exam.",
                    "duration": 90,
                    "total_marks": 150
                },
                request_only=True,
                response_only=False
            ),
            OpenApiExample(
                'Example Response',
                value={
                    "id": 1,
                    "name": "Updated Exam 1",
                    "description": "This is the updated first exam.",
                    "duration": 90,
                    "total_marks": 150
                },
                request_only=False,
                response_only=True
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
