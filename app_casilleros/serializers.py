from rest_framework import serializers
from .models import Casillero

class CasilleroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casillero
        fields = ['id', 'tamano', 'disponible','abierto','r_username','r_email','o_email','o_name']