from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from .models import Casillero, Reserva, ApiKey, User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .serializers import CasilleroSerializer
#a

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

class MyApiView(APIView):
    authentication_classes = [ApiKeyAuthentication] 
    permission_classes = [IsAuthenticated] 

@api_view(['GET'])
def casilleros_disponibles(request):
    casilleros = Casillero.objects.filter(disponible=True)
    serializer = CasilleroSerializer(casilleros, many=True)
    context = {'casilleros': serializer.data}
    return render(request, 'casilleros_disponibles.html', context)

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

@login_required
def home_view(request):
    user = request.user
    context = {'user_name': user.username}
    return render(request, 'home.html', context)

def obtener_reservas_usuario(request, usuario_id):
    usuario = User.objects.get(id=usuario_id)
    reservas = Reserva.objects.filter(usuario=usuario)

    reservas_json = []
    for reserva in reservas:
        reservas_json.append({
            'id': reserva.id,
            'casillero_id': reserva.casillero.id,
            'fecha_reserva': reserva.fecha_reserva,
            'confirmada': reserva.confirmada,
            'cancelada': reserva.cancelada,
            'fecha_confirmacion': reserva.fecha_confirmacion,
            'fecha_cancelacion': reserva.fecha_cancelacion,
        })

    return JsonResponse({'reservas': reservas_json})

