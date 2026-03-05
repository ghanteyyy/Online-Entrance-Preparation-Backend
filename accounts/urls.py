from django.urls import path
from .views import Login, RefreshAccess, Logout, Register

urlpatterns = [
    path("api/auth/login/", Login),
    path("api/auth/register/", Register),
    path("api/auth/refresh/", RefreshAccess),
    path("api/auth/logout/", Logout),
]
