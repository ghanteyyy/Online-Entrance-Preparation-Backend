from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .services import programmes, subjects, questions

router = DefaultRouter()

router.register(r'programmes', programmes.Programmes, basename='programme')
router.register(r'subjects', subjects.Subjects, basename='subject')
router.register(r'questions', questions.Questions, basename='question')

urlpatterns = [
    path('api/', include(router.urls)),
]
