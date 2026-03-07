from .models import CustomUser
from .cookies import REFRESH_COOKIE_NAME, set_refresh_cookie, clear_refresh_cookie

from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from . serializers import RegisterSerializer

from rest_framework import status
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes



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


@api_view(["POST"])
@permission_classes([AllowAny])
def RefreshAccess(request):
    refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)

    if not refresh:
        return Response({"detail": "No refresh token"}, status=401)

    serializer = TokenRefreshSerializer(data={"refresh": refresh})

    try:
        serializer.is_valid(raise_exception=True)

    except Exception:
        return Response({"detail": "Refresh expired/invalid"}, status=401)

    data = serializer.validated_data
    access = data["access"]

    res = Response({"access": access}, status=200)

    # If rotation is on, SimpleJWT will include a new refresh in response data
    new_refresh = data.get("refresh")

    if new_refresh:
        set_refresh_cookie(res, new_refresh)

    return res

