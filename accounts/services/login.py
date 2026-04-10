from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django_ratelimit.decorators import ratelimit

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes

from drf_spectacular.utils import extend_schema, OpenApiExample

from accounts.cookies import set_refresh_cookie


@extend_schema(
    summary="Login user",
    description="Authenticates a user and returns an access token while setting refresh token in an HTTP-only cookie.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "example": "abc@example.com"},
                "password": {"type": "string", "example": "StrongPass123"},
            },
            "required": ["email", "password"],
        }
    },
    responses={200: {"type": "object", "properties": {
        "status": {"type": "boolean"},
        "access": {"type": "string"},
    }}},
    examples=[
        OpenApiExample(
            "Login Example",
            value={"email": "abc@example.com", "password": "StrongPass123"},
            request_only=True,
        )
    ],
)
@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    email = (request.data.get("email") or '').strip().lower()
    password = (request.data.get("password") or '').strip()

    if not email or not password:
        return Response({"status": False, "message": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if not user:
        return Response(
            {
                "status": False,
                "message": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED
        )

    tokens = RefreshToken.for_user(user)

    get_token(request)  # Ensure CSRF cookie is set

    res = Response(
        {
            "status": True,
            "access": str(tokens.access_token)
        },

        status=status.HTTP_200_OK
    )

    set_refresh_cookie(res, str(tokens))

    return res
