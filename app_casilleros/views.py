from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from .models import Casillero, Reserva, ApiKey, User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import obtener_api_key, generar_clave
from django.core.cache import cache
from .serializers import CasilleroSerializer
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse

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
    casilleros = Casillero.objects.all()
    serializer = CasilleroSerializer(casilleros, many=True)
    context = {'casilleros': serializer.data}
    return render(request, 'casilleros_lista.html', context)

@api_view(['GET'])
def casilleros_disponibles(request):
    casilleros = Casillero.objects.all()
    serializer = CasilleroSerializer(casilleros, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def casillero_detalle(request, pk):
    casillero = get_object_or_404(Casillero, pk=pk)
    serializer = CasilleroSerializer(casillero)
    return Response(serializer.data)

@login_required
def reservar_casillero(request, casillero_id):
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    api_key = obtener_api_key(user)

    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)

    if casillero_id is not None:
        try:
            casillero = Casillero.objects.get(id=int(casillero_id), disponible="D")

        except Casillero.DoesNotExist:
            return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)

        reserva = Reserva(casillero=casillero, usuario=user)
        reserva.save()
        casillero.disponible = "R"
        casillero.clave = generar_clave()
        print(str(casillero.clave))
        enlace = request.build_absolute_uri(reverse('verificar_reserva', kwargs={'casillero_id': casillero_id, 'clave': casillero.clave}))

        subject = "Reserva de casillero"
        message = f"Estimado {casillero.o_name},\n\nLe informamos que un pedido ha sido reservado para en el casillero N°{casillero_id}. Para abrir y depositar el pedido, haga clic en el siguiente enlace: {enlace}.\n\n o ingrese el siguiente codigo en el casillero: '{casillero.clave}'.\n\n Muchas gracias por trabajar con nosotros."
        send_mail(subject,message,'saccnotification@gmail.com',[casillero.o_email])
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
            casillero = Casillero.objects.get(id=int(casillero_id), disponible="A")
            if casillero.disponible == "A":
                pass
            else:
                return Response({'error': 'Casillero is already available'}, status=status.HTTP_400_BAD_REQUEST)
        except Casillero.DoesNotExist:
            return Response({'error': 'Casillero not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # casillero.clave = generar_clave()
        # casillero.save()

        context = {'casillero_id': casillero_id, "clave": casillero.clave}     
        return render(request, 'liberar_casillero.html', context)
    else:
        return Response({'error': 'No se proporcionó el ID del casillero'}, status=status.HTTP_400_BAD_REQUEST)


@login_required
def check_clave_r(request):
    if request.method == 'POST':
        inputted_clave = request.POST.get('inputted_clave')
        casillero_id = request.POST.get('casillero_id')

        try:
            casillero = Casillero.objects.get(id=casillero_id)
        except Casillero.DoesNotExist:
            return JsonResponse({'correct': False})

        if str(inputted_clave) == str(casillero.clave):
            casillero.disponible = "C"
            casillero.abierto = True
            casillero.save()
            return JsonResponse({'correct': True})
        else:
            return JsonResponse({'correct': False})
    else:
        return JsonResponse({'correct': False})
    
@login_required
def check_clave_l(request):
    if request.method == 'POST':
        inputted_clave = request.POST.get('inputted_clave')
        casillero_id = request.POST.get('casillero_id')

        try:
            casillero = Casillero.objects.get(id=casillero_id)
        except Casillero.DoesNotExist:
            return JsonResponse({'correct': False})

        if str(inputted_clave) == str(casillero.clave):
            # casillero.disponible = "D"
            casillero.abierto = True
            casillero.r_email = None
            casillero.r_username = None
            casillero.o_email = None
            casillero.o_name = None
            casillero.save()
            return JsonResponse({'correct': True})
        else:
            return JsonResponse({'correct': False})
    else:
        return JsonResponse({'correct': False})

@login_required
def force_close(request):
    if request.method == 'POST':
        casillero_id = request.POST.get('casillero_id')

        try:
            casillero = Casillero.objects.get(id=casillero_id)
        except Casillero.DoesNotExist:
            return JsonResponse({'correct': False})
        
        casillero.abierto = False
        casillero.save()

@login_required
def correct_clave(request):
    return render(request, 'correct_clave.html') 
    
@login_required
def detalles_casillero(request, casillero_id):
    casillero = get_object_or_404(Casillero, id=casillero_id)
    context = {'casillero': casillero}
    return render(request, 'detalles_casillero.html', context)





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
    
@api_view(['POST'])
def actualizar_disponibilidad_casillero(request, casillero_id):
    try:
        casillero = Casillero.objects.get(id=casillero_id)
    except Casillero.DoesNotExist:
        return Response({'error': 'Casillero no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = request.data.get('disponible')
    nuevo_abierto =  request.data.get('abierto')
    casillero.disponible = nuevo_estado
    casillero.abierto = nuevo_abierto
    casillero.clave = generar_clave()
    print(str(casillero.clave))
    enlace = request.build_absolute_uri(reverse('verificar_reserva', kwargs={'casillero_id': casillero_id, 'clave': casillero.clave}))
    subject = "Carga de casillero"
    message = f"Estimado {casillero.r_username},\n\nLe informamos que su pedido ha sido exitosamente cargado en el casillero N°{casillero_id}.Para abrir y depositar el pedido, haga clic en el siguiente enlace: {enlace}.\n\n  o ingrese el siguiente codigo en el casillero: '{casillero.clave}'.\n\nMuchas gracias por su preferencia."
    send_mail(subject,message,'saccnotification@gmail.com',[casillero.r_email])
    casillero.save()

    if casillero.disponible == "A":
        # casillero.abierto = False
        # casillero.save()
        pass
    elif casillero.disponible == "D":
        # casillero.abierto = False
        # casillero.save()
        pass

    return Response({'success': 'Disponibilidad del casillero actualizada con éxito'})

@api_view(['POST'])
def cerrar_casillero(request, casillero_id):
    try:
        casillero = Casillero.objects.get(id=casillero_id)
    except Casillero.DoesNotExist:
        return Response({'error': 'Casillero no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    cerrado = request.data.get("abierto")
    casillero.abierto = cerrado
    casillero.save()

    return Response({'success': 'Casillero cerrado exitosamente'})

@login_required
def send_mail_view(request):
    mail = request.user.email
    send_mail('Subject','Message','saccnotification@gmail.com',[mail])
    return render(request, 'send_mail_view.html')

@login_required
def form_reserva(request, casillero_id):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    api_key = obtener_api_key(user)

    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API key inválida'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        input_client_email = request.POST.get('client_email')
        input_client_username = request.POST.get('client_username')
        input_operator_email = request.POST.get('operator_email')
        input_operator_name = request.POST.get('operator_name')

        try:
            casillero = Casillero.objects.get(id=casillero_id, disponible="D")
        except Casillero.DoesNotExist:
            return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)
        
        casillero.r_email = input_client_email
        casillero.r_username = input_client_username
        casillero.o_email = input_operator_email
        casillero.o_name = input_operator_name
        casillero.save()

        return redirect('reservar_casillero', casillero_id=casillero_id)

    return render(request, 'form_reserva.html', {'casillero_id': casillero_id})

@login_required
def verificar_reserva(request, casillero_id, clave):
    casillero = get_object_or_404(Casillero, id=casillero_id)

    if str(clave) == str(casillero.clave):
        # Clave correcta, realizar acciones adicionales si es necesario
        return render(request, 'correct_clave.html', {'casillero_id': casillero_id})
    else:
        # Clave incorrecta, redirigir o mostrar un mensaje de error
        return HttpResponse('Clave incorrecta')