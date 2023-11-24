import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PDS_3.settings')  # Asegúrate de reemplazar 'myproject' con el nombre de tu proyecto

import django
django.setup()

from app_casilleros.models import Casillero, Reserva, ApiKey
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

username = "juan"
email = "sacc.user3@gmail.com"
password = "hola123"
user = User.objects.create_user(username=username, email=email, password=password)

# Ejemplo para crear usuarios
for _ in range(10):
    username = fake.user_name()
    email = fake.email()
    password = "hola123"
    user = User.objects.create_user(username=username, email=email, password=password)

# Ejemplo para crear casilleros
for _ in range(20):
    tamano = fake.random_element(elements=('M'))
    disponible = fake.random_element(elements=("D"))
    r_username = None
    r_email = None
    o_email = None
    o_name = None

    Casillero.objects.create(tamano=tamano, disponible=disponible, r_username=r_username, r_email=r_email, o_email=o_email, o_name=o_name)

# Ejemplo para crear reservas y api keys
users = User.objects.all()
casilleros = Casillero.objects.filter(disponible="D")

for user in users:
    ApiKey.objects.create(usuario=user, key=fake.uuid4())