from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes

from drf_spectacular.utils import extend_schema

from accounts.cookies import REFRESH_COOKIE_NAME, set_refresh_cookie, clear_refresh_cookie


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
@api_view(["POST"])
@permission_classes([AllowAny])
def RefreshAccess(request):
    refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

    if not refresh_token:
        return Response(
            {
                "status": False,
                "message": "No refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)

    User = get_user_model()

    try:
        old_refresh = RefreshToken(refresh_token)

        user_id = old_refresh["user_id"]
        user = User.objects.get(id=user_id)

        new_fresh = RefreshToken.for_user(user)
        access = str(new_fresh.access_token)

        res = Response(
            {
                "status": True,
                "access": access
            }, status=status.HTTP_200_OK)

        set_refresh_cookie(res, str(new_fresh))

        try:
            old_refresh.blacklist()

        except Exception:
            pass

        return res

    except (TokenError, user.DoesNotExist):
        res = Response(
            {
                "status": False,
                "message": "Invalid or expired refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED
        )

        clear_refresh_cookie(res)

        return res
