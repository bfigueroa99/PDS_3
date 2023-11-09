from .models import ApiKey
from random import randint
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def obtener_api_key(usuario):
    try:
        api_key = ApiKey.objects.get(usuario=usuario)
        return api_key.key
    except ApiKey.DoesNotExist:
        return None

def generar_clave():
    clave = randint(1000,9999)
    while clave == 1234:
        generar_clave()
    return clave