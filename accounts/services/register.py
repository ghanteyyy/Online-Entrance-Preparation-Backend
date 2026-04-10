from django_ratelimit.decorators import ratelimit

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from drf_spectacular.utils import extend_schema, OpenApiExample

from accounts.models import CustomUser
from accounts. serializers import RegisterSerializer


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
