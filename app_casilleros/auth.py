# myapp/auth.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiKey

class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.data.get('api_key')
        if api_key:
            try:
                api_key_obj = ApiKey.objects.get(key=api_key)
                return (api_key_obj.usuario, None)
            except ApiKey.DoesNotExist:
                raise AuthenticationFailed('API key inválida')
        return None
