from django.conf import settings


class AuthKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authkey_cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if authkey_cookie:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {authkey_cookie}'

        response = self.get_response(request)
        return response
