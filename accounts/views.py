from .models import CustomUser
from .cookies import REFRESH_COOKIE_NAME, set_refresh_cookie, clear_refresh_cookie

from drf_spectacular.utils import extend_schema, OpenApiExample

from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from . serializers import RegisterSerializer

from rest_framework import status
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


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
        return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

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


register_response_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "boolean"},
        "message": {"type": "string"},
    },
}

@extend_schema(
    summary="Register user",
    description="Creates a new user account and returns an access token while setting refresh token in an HTTP-only cookie.",
    request=RegisterSerializer,
    responses={
        200: register_response_schema,
        400: register_response_schema
    },
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "StrongPass123",
                "gender": "male",
                "date_of_birth": "1990-01-01"
            },
            request_only=True,
        )
    ],
)
@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def Register(request):
    name = (request.data.get('name') or '').strip().lower()
    email = (request.data.get('email') or '').strip().lower()
    gender = (request.data.get('gender') or '').strip().lower()
    password = (request.data.get('password') or '').strip()
    date_of_birth = (request.data.get('date_of_birth') or '').strip()
    profile_image = (request.FILES.get('profile_image') or '')

    if not all([name, email, password, gender, date_of_birth]):
        return Response(
            {
                'status': False,
                'message': 'All fields (name, email, password, date_of_birth, profile_image) are required'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if CustomUser.objects.filter(email__iexact=email).exists():
        return Response(
            {
                'status': False,
                'message': 'Email aready exists'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) not in range(8, 16):
        return Response(
            {
                'status': False,
                'message': 'Password length must be between 8 and 16'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if gender not in ['male', 'female', 'others']:
        return Response(
            {
                'status': False,
                'message': 'Gender must be male, female or others'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    data['profile_image'] = profile_image

    user = RegisterSerializer(data=data)
    user.is_valid(raise_exception=True)
    user.save()

    return Response(
        {
            "status": True,
            "message": "User registerd successful"
        }, status=status.HTTP_201_CREATED
    )


@extend_schema(
    summary='Logout user',
    description='Logs out the user by blacklisting the refresh token and clearing the refresh token cookie.',
    request=None,
    responses={200: {"type": "object", "properties": {
        "status": {"type": "boolean"},
        "message": {"type": "string"},
    }}},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Logout(request):
    refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)

    res = Response(
        {
            "status": True,
            "message": "Logged out"
        }, status=status.HTTP_200_OK
    )

    if refresh:
        try:
            token = RefreshToken(refresh)
            token.blacklist()

        except Exception:
            pass

    clear_refresh_cookie(res)
    get_token(request)  # Ensure CSRF cookie is set for future requests

    return res


@extend_schema(
    summary='Refresh access token',
    description='Refreshes the access token using the refresh token stored in an HTTP-only cookie. If token rotation is enabled, also sets a new refresh token in the cookie.',
    request=None,
    responses={
        200: {"type": "object", "properties": {
            "status": {"type": "boolean"},
            "access": {"type": "string"},
        }},
        401: {"type": "object", "properties": {
            "status": {"type": "boolean"},
            "message": {"type": "string"},
        }},
    },
)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def RefreshAccess(request):
    refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)

    if not refresh:
        return Response(
            {
                "status": False,
                "message": "No refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)

    serializer = TokenRefreshSerializer(data={"refresh": refresh})

    try:
        serializer.is_valid(raise_exception=True)

    except Exception:
        return Response(
            {
                "status": False,
                "message": "Refresh expired/invalid"
            }, status=status.HTTP_401_UNAUTHORIZED)

    data = serializer.validated_data
    access = data["access"]

    res = Response(
        {
            "status": True,
            "access": access
        }, status=status.HTTP_200_OK)

    # If rotation is on, SimpleJWT will include a new refresh in response data
    new_refresh = data.get("refresh")

    if new_refresh:
        set_refresh_cookie(res, new_refresh)

    return res
