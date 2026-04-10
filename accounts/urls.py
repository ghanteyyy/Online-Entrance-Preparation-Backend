from django.urls import path
from .services import login, logout, refresh, register

urlpatterns = [
    path("api/auth/login/", login.Login),
    path("api/auth/register/", register.Register),
    path("api/auth/refresh/", refresh.RefreshAccess),
    path("api/auth/logout/", logout.Logout),
]
