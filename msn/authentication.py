from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class TokenQueryParamAuthentication(TokenAuthentication):
    """DRF token authentication with an optional auth_token query parameter.

    This is a fallback for hosting environments that strip the HTTP
    Authorization header before it reaches Django, such as some WSGI setups.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            return result

        token = request.query_params.get('auth_token')
        if not token:
            return None

        model = self.get_model()
        try:
            token_obj = model.objects.select_related('user').get(key=token)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        return (token_obj.user, token_obj)
