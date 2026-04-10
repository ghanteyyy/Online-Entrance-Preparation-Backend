from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .services import exams

router = DefaultRouter()
router.register(r'exams', exams.Exams, basename='exam')

urlpatterns = [
    path('api/', include(router.urls)),
]
