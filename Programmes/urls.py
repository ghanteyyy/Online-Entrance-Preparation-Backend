from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'programmes', views.Programmes, basename='programme')
router.register(r'subjects', views.Subjects, basename='subject')
router.register(r'questions', views.Questions, basename='question')

urlpatterns = [
    path('api/', include(router.urls)),
]
