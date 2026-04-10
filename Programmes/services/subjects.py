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
        summary="Get Subjects",
        description="Get subjects by programme",
        responses=serializers.SubjectSerializer(many=True),
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
        summary="Create Subject",
        request=serializers.SubjectSerializer,
        responses=serializers.SubjectSerializer
    ),
    update=extend_schema(
        summary="Update Subject",
        request=serializers.SubjectSerializer,
        responses=serializers.SubjectSerializer
    ),
    partial_update=extend_schema(
        summary="Partial Update Subject",
        request=serializers.SubjectSerializer,
        responses=serializers.SubjectSerializer
    ),
    destroy=extend_schema(
        summary="Delete Subject"
    )
)
class Subjects(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        programme = request.query_params.get('programme', '').strip()

        if not programme:
            return Response(
                {
                    "status": False,
                    "message": "Programme is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        subjects = self.get_queryset().filter(Q(programme__name__iexact=programme) | Q(programme__abbr__iexact=programme))

        serializer = self.get_serializer(subjects, many=True)

        return Response(
            {
                "status": True,
                "subjects": serializer.data
            }
        )

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            programme = request.data.get('programme', '').strip()
            name = request.data.get('name', '').strip()
            question_to_select = request.data.get('question_to_select', 0)

            print("Received data:", request.data)

            if not programme or not name:
                return Response(
                    {
                        "status": False,
                        "message": "Programme and Subject name are required"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                programme = models.Programme.objects.get(Q(name__iexact=programme) | Q(abbr__iexact=programme))

            except models.Programme.DoesNotExist:
                return Response(
                    {
                        "status": False,
                        "message": "Programme not found"
                    }, status=status.HTTP_404_NOT_FOUND
                )

            subject = models.Subject.objects.create(
                programme=programme,
                name=name,
                question_to_select=question_to_select
            )

        return Response(
            {
                "status": True,
                "subject": self.get_serializer(subject).data
            }, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()

            name = request.data.get('name', '').strip()
            question_to_select = request.data.get('question_to_select', 0)

            if not name:
                return Response(
                    {
                        "status": False,
                        "message": "Name is required"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

            instance.name = name
            instance.question_to_select = question_to_select
            instance.save()

        return Response(
            {
                "status": True,
                "subject": self.get_serializer(instance).data
            }, status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()

            name = request.data.get('name')
            question_to_select = request.data.get('question_to_select')

            if name is not None:
                instance.name = name.strip()

            if question_to_select is not None:
                instance.question_to_select = question_to_select

            instance.save()

        return Response(
            {
                "status": True,
                "subject": self.get_serializer(instance).data
            }, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.delete()

        return Response(
            {
                "status": True,
                "message": "Subject deleted successfully"
            }, status=status.HTTP_200_OK
        )
