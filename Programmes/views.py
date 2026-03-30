from django.db import transaction
from django.db.models import Q

import rest_framework.status as status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Random
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from . import models, serializers


@extend_schema_view(
    list=extend_schema(
        summary="Get Programmes",
        description="Retrieve all programmes",
        responses=serializers.ProgrammeSerializer(many=True)
    ),
    retrieve=extend_schema(
        summary="Get Programme Detail",
        responses=serializers.ProgrammeSerializer
    ),
    create=extend_schema(
        summary="Create Programme",
        request=serializers.ProgrammeSerializer,
        responses=serializers.ProgrammeSerializer
    ),
    update=extend_schema(
        summary="Update Programme",
        request=serializers.ProgrammeSerializer,
        responses=serializers.ProgrammeSerializer
    ),
    partial_update=extend_schema(
        summary="Partial Update Programme",
        request=serializers.ProgrammeSerializer,
        responses=serializers.ProgrammeSerializer
    ),
    destroy=extend_schema(
        summary="Delete Programme"
    )
)
class Programmes(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "status": True,
                "programmes": serializer.data
            }, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response(
            {
                "status": True,
                "programme": serializer.data
            }, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return Response(
            {
                "status": True,
                "programme": serializer.data
            }, status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.delete()

        return Response(
            {
                "status": True,
                "message": "Programme deleted successfully"
            }, status=status.HTTP_200_OK
        )


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
