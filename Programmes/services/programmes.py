from django.db import transaction
from django.db.models import Q

import rest_framework.status as status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Random
from drf_spectacular.utils import extend_schema, extend_schema_view

from Programmes import models, serializers


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
