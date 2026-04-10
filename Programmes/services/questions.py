from django.db import transaction
from django.db.models import Q

import rest_framework.status as status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Random
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from Programmes import models, serializers


@extend_schema_view(
    list=extend_schema(
        summary="Get Questions",
        description="Get questions by programme",
        responses=serializers.QuestionSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="programme",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Programme name (e.g. BCA, BIT, etc.)"
            )
        ]
    ),
    create=extend_schema(
        summary="Create Question",
        request=serializers.QuestionSerializer,
        responses=serializers.QuestionSerializer
    ),
    update=extend_schema(
        summary="Update Question",
        request=serializers.QuestionSerializer,
        responses=serializers.QuestionSerializer
    ),
    partial_update=extend_schema(
        summary="Partial Update Question",
        request=serializers.QuestionSerializer,
        responses=serializers.QuestionSerializer
    ),
    destroy=extend_schema(
        summary="Delete Question"
    )
)
class Questions(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.QuestionSerializer
    lookup_field = "id"

    def get_queryset(self):
        return models.Question.objects.select_related(
            "programme",
            "subject"
        ).prefetch_related(
            "options"
        )

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            programme_name = request.data.get("programme", "").strip()
            subject_name = request.data.get("subject", "").strip()
            title = request.data.get("title", "").strip()

            if not programme_name or not subject_name or not title:
                return Response(
                    {
                        "status": False,
                        "message": "Programme, subject and title are required"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

            programme = models.Programme.objects.filter(name__iexact=programme_name).first()

            if not programme:
                return Response(
                    {
                        "status": False,
                        "message": "Programme not found"
                    }, status=status.HTTP_404_NOT_FOUND
                )

            subject = models.Subject.objects.filter(name__iexact=subject_name, programme=programme).first()

            if not subject:
                return Response(
                    {
                        "status": False,
                        "message": "Subject does not exist in this programme"
                    }, status=status.HTTP_404_NOT_FOUND
                )

            question = models.Question.objects.create(programme=programme, subject=subject, title=title)

        return Response(
            {
                "status": True,
                "question": self.get_serializer(question).data
            }, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Get Random Questions",
        description="Generate random questions based on programme",
        parameters=[
            OpenApiParameter(
                name="programme",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Programme name (e.g. BCA, BIT, etc.)"
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Number of random questions to retrieve (default is 100)"
            )
        ],
        responses=serializers.QuestionSerializer(many=True)
    )
    @action(detail=False, methods=['get'], url_path='random')
    def random_questions(self, request):
        programme_name = request.query_params.get("programme", "").strip()
        limit = request.query_params.get("limit", 100)

        try:
            limit = int(limit)

        except ValueError:
            return Response(
                {
                    "status": False,
                    "message": "Limit must be an integer"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        if not programme_name:
            return Response(
                {
                    "status": False,
                    "message": "Programme is required"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        questions = self.get_queryset().filter(Q(programme__name__iexact=programme_name) | Q(programme__abbr__iexact=programme_name)).order_by(Random())[:limit]
        serializer = self.get_serializer(questions, many=True)

        return Response(
            {
                "status": True,
                "questions": serializer.data
            }, status=status.HTTP_200_OK
        )
