from django.db import models
from django.contrib.auth.models import User

class Casillero(models.Model):
    TAMANO_CHOICES = [
        ('P', 'Pequeño'),
        ('M', 'Mediano'),
        ('G', 'Grande'),
    ]
    tamano = models.CharField(max_length=1, choices=TAMANO_CHOICES)
    disponible = models.BooleanField(default=True)

class Reserva(models.Model):
    casillero = models.ForeignKey(Casillero, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    confirmada = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)

class ApiKey(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, unique=True)

