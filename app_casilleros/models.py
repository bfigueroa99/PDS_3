from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Casillero(models.Model):
    TAMANO_CHOICES = [
        ('P', 'Pequeño'),
        ('M', 'Mediano'),
        ('G', 'Grande'),
    ]
    DISPONIBLE_CHOICES = [
        ("D", "Disponible"),
        ("R", "Reservado"),
        ("C", "Confirmado"),
        ("A", "Cargado"),
    ]
    tamano = models.CharField(max_length=1, choices=TAMANO_CHOICES)
    disponible = models.CharField(max_length=1, choices=DISPONIBLE_CHOICES, default="D")
    clave = models.IntegerField(default=1234)
    abierto = models.BooleanField(default=False)
    r_username = models.CharField(max_length=50, null=True)
    r_email = models.CharField(max_length=50, null=True)
    o_email = models.CharField(max_length=50, null=True)
    o_name = models.CharField(max_length=50, null=True)
    fecha_creacion = models.DateTimeField(default=datetime.today)

class ApiKey(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, unique=True)

class Reserva(models.Model):
    casillero = models.ForeignKey(Casillero, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(null=True, blank=True)
    fecha_carga = models.DateTimeField(null=True, blank=True)
    fecha_retiro = models.DateTimeField(null=True, blank=True)

class Historial(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    porcentaje_uso = models.FloatField(default=0)


