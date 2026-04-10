from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes

from drf_spectacular.utils import extend_schema
from accounts.cookies import REFRESH_COOKIE_NAME, clear_refresh_cookie


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
@permission_classes([AllowAny])
def Logout(request):
    refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

    res = Response(
        {
            "status": True,
            "message": "Logged out"
        }, status=status.HTTP_200_OK
    )

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            pass

    clear_refresh_cookie(res)

    return res
