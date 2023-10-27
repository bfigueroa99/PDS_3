from .models import ApiKey

def obtener_api_key(usuario):
    try:
        api_key = ApiKey.objects.get(usuario=usuario)
        return api_key.key
    except ApiKey.DoesNotExist:
        return None

