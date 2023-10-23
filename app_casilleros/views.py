from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Casillero, Reserva, ApiKey

class CasilleroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casillero
        fields = ['id', 'tamano', 'disponible']

@api_view(['GET'])
def casilleros_disponibles(request):
    casilleros = Casillero.objects.filter(disponible=True)
    serializer = CasilleroSerializer(casilleros, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def casillero_detalle(request, pk):
    casillero = get_object_or_404(Casillero, pk=pk)
    serializer = CasilleroSerializer(casillero)
    return Response(serializer.data)

@api_view(['POST'])
def reservar_casillero(request):
    api_key = request.data.get('api_key')
    casillero_id = request.data.get('casillero_id')
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        casillero = Casillero.objects.get(id=casillero_id, disponible=True)
    except Casillero.DoesNotExist:
        return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)
    reserva = Reserva(casillero=casillero, usuario=api_key_obj.usuario)
    reserva.save()
    casillero.disponible = False
    casillero.save()
    return Response({'success': 'Reserva realizada con éxito'})

@api_view(['POST'])
def confirmar_reserva(request):
    api_key = request.data.get('api_key')
    reserva_id = request.data.get('reserva_id')
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=api_key_obj.usuario, confirmada=False, cancelada=False)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada o ya confirmada/cancelada'}, status=status.HTTP_400_BAD_REQUEST)
    reserva.confirmada = True
    reserva.fecha_confirmacion = timezone.now()
    reserva.save()
    return Response({'success': 'Reserva confirmada con éxito'})

@api_view(['POST'])
def cancelar_reserva(request):
    api_key = request.data.get('api_key')
    reserva_id = request.data.get('reserva_id')
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=api_key_obj.usuario, confirmada=False, cancelada=False)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada o ya confirmada/cancelada'}, status=status.HTTP_400_BAD_REQUEST)
    reserva.cancelada = True
    reserva.fecha_cancelacion = timezone.now()
    reserva.save()
    casillero = reserva.casillero
    casillero.disponible = True
    casillero.save()
    return Response({'success': 'Reserva cancelada con éxito'})

@api_view(['POST'])
def estado_reserva(request):
    api_key = request.data.get('api_key')
    reserva_id = request.data.get('reserva_id')
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=api_key_obj.usuario)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_400_BAD_REQUEST)
    data = {
        'casillero_id': reserva.casillero.id,
        'tamano': reserva.casillero.tamano,
        'confirmada': reserva.confirmada,
        'cancelada': reserva.cancelada,
        'fecha_reserva': reserva.fecha_reserva,
        'fecha_confirmacion': reserva.fecha_confirmacion,
        'fecha_cancelacion': reserva.fecha_cancelacion,
    }
    return Response(data)

