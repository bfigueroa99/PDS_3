from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from .models import Casillero, Reserva, ApiKey, User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import obtener_api_key, generar_clave


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
def casilleros_lista(request):
    casilleros = Casillero.objects.all()  # Obtener todos los casilleros sin filtrar
    serializer = CasilleroSerializer(casilleros, many=True)
    context = {'casilleros': serializer.data}
    return render(request, 'casilleros_lista.html', context)

@api_view(['GET'])
def casilleros_disponibles(request):
    casilleros = Casillero.objects.all()  # Obtener todos los casilleros sin filtrar
    serializer = CasilleroSerializer(casilleros, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def casillero_detalle(request, pk):
    casillero = get_object_or_404(Casillero, pk=pk)
    serializer = CasilleroSerializer(casillero)
    return Response(serializer.data)

@login_required
def reservar_casillero(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = obtener_api_key(user)
    casillero_id = None
    
    if request.method == 'POST':
        casillero_id = request.POST.get('casillero_id')
    
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if casillero_id is not None:
        try:
            casillero = Casillero.objects.get(id=int(casillero_id), disponible=True)
        except Casillero.DoesNotExist:
            return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)
        
        reserva = Reserva(casillero=casillero, usuario=user)
        reserva.save()
        casillero.disponible = False
        casillero.save()

    casillero.clave = generar_clave()
    casillero.save()
    context = {'casillero_id': casillero_id, "clave": casillero.clave}    
    return render(request, 'reservar_casillero.html', context)


@login_required
def liberar_casillero(request):
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = obtener_api_key(user)
    casillero_id = None
    
    if request.method == 'POST':
        casillero_id = request.POST.get('casillero_id')
    
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if casillero_id is not None:
        try:
            casillero = Casillero.objects.get(id=casillero_id)
            if not casillero.disponible:
                casillero.disponible = True
                casillero.save()
            else:
                return Response({'error': 'Casillero is already available'}, status=status.HTTP_400_BAD_REQUEST)
        except Casillero.DoesNotExist:
            return Response({'error': 'Casillero not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        context = {'casillero_id': casillero_id}    
        return render(request, 'liberar_casillero.html', context)
    else:
        return Response({'error': 'No se proporcionó el ID del casillero'}, status=status.HTTP_400_BAD_REQUEST)


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

@login_required
def obtener_api_key_usuario(request):
    usuario = request.user
    api_key = obtener_api_key(usuario)
    if api_key:
        print(api_key)
        return JsonResponse({'api_key': api_key})
    else:
        return JsonResponse({'message': 'API key no encontrada'})

