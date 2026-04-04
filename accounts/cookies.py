from django.conf import settings

REFRESH_COOKIE_NAME = "refresh_token"


def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",   # cross-site
        path="/api/auth/", # restrict where cookie is sent
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/api/auth/",
        samesite="Lax",
    )
