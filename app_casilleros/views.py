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
from django.urls import reverse
import requests
import ujson
from datetime import datetime



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
    # try:
    #     locker4 = requests.get(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/4/").json()
    #     locker5 = requests.get(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/5/").json()
    #     locker6 = requests.get(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/6/").json()
    #     locker4 = translate_json456(locker4)
    #     locker4.fecha_creacion = get_object_or_404(Casillero, id=4).fecha_creacion
    #     locker4.save()
    #     locker4.id = 4
    #     locker4.save()
    #     locker5 = translate_json456(locker5)
    #     locker5.fecha_creacion = get_object_or_404(Casillero, id=5).fecha_creacion
    #     locker5.save()
    #     locker5.id = 5
    #     locker5.save()
    #     locker6 = translate_json456(locker6)
    #     locker6.fecha_creacion = get_object_or_404(Casillero, id=6).fecha_creacion
    #     locker6.save()
    #     locker6.id = 6
    #     locker6.save()
    # except:
    #     print("Sister server offline")


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
        if casillero_id in [1,2,3]:
            try:
                casillero = Casillero.objects.get(id=int(casillero_id), disponible="D")

            except Casillero.DoesNotExist:
                return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)
            
            casillero.disponible = "R"
            casillero.clave = generar_clave()
            print(str(casillero.clave))
            enlace = request.build_absolute_uri(reverse('ingresar_clave', args=[casillero_id, casillero.clave,0]))
            subject = "Reserva de casillero"
            message = f"Estimado {casillero.o_name},\n\nLe informamos que un pedido ha sido reservado para en el casillero N°{casillero_id}.Para abrir y depositar el pedido, ingrese el siguiente codigo en el casillero: '{casillero.clave}'.\n\n {enlace} \n\nMuchas gracias por trabajar con nosotros."
            send_mail(subject,message,'saccnotification@gmail.com',[casillero.o_email])
            casillero.save()

        if casillero_id in [4,5,6]:
            try:
                casillero = requests.get(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/{casillero_id}/").json()
            except Casillero.DoesNotExist:
                return Response({'error': 'Casillero no disponible'}, status=status.HTTP_400_BAD_REQUEST)
            
            casillero = translate_json456(casillero)

            casillero.fecha_creacion = get_object_or_404(Casillero, id=casillero_id).fecha_creacion

            casillero.save()
            casillero.id = casillero_id
            casillero.save()
            delete_last_casillero(request)
            requests.put(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/{casillero_id}/update_reserved_true/")
            casillero.disponible = "R"
            casillero.clave = generar_clave()
            print(str(casillero.clave))

            enlace = request.build_absolute_uri(reverse('ingresar_clave', args=[casillero_id, casillero.clave,0]))
            subject = "Reserva de casillero"
            message = f"Estimado {casillero.o_name},\n\nLe informamos que un pedido ha sido reservado para en el casillero N°{casillero_id}.Para abrir y depositar el pedido, ingrese el siguiente codigo en el casillero: '{casillero.clave}'.\n\n {enlace} \n\nMuchas gracias por trabajar con nosotros."
            send_mail(subject,message,'saccnotification@gmail.com',[casillero.o_email])
            casillero.save()
        
        reserva = Reserva(casillero=casillero, usuario=user, fecha_reserva=datetime.now())
        reserva.save()
        reserva.agregar_a_bitacora_reserva("Reserva realizada")


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
        
        # Obtener la reserva asociada al casillero
        reserva = Reserva.objects.filter(casillero=casillero, usuario=user).first()

        if not reserva:
            return Response({'error': 'Reserva not found for the current user'}, status=status.HTTP_400_BAD_REQUEST)

        # Agregar a la bitácora
        reserva.bitacora += f"Liberación realizada por cliente {casillero.r_username} el {datetime.now()}.\n"
        reserva.save()

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
            if int(casillero_id) in [4,5,6]:
                requests.put(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/{casillero_id}/update_confirmed_true/")
                requests.put(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/{casillero_id}/update_locked_false/")
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
            if int(casillero_id) in [4,5,6]:
                requests.put(f"https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/{casillero_id}/update_locked_false/")
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
    reservas = Reserva.objects.filter(casillero=casillero).all()

    context = {'casillero': casillero, 'reservas': reservas}
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
    enlace = request.build_absolute_uri(reverse('ingresar_clave', args=[casillero_id, casillero.clave,1]))
    subject = "Carga de casillero"
    message = f"Estimado {casillero.r_username},\n\nLe informamos que su pedido ha sido exitosamente cargado en el casillero N°{casillero_id}. Para retirarlo, ingrese el siguiente codigo en el casillero: '{casillero.clave}'.\n\nMuchas gracias por su preferencia."
    send_mail(subject,message,'saccnotification@gmail.com',[casillero.r_email])
    casillero.save()

    # Obtener la reserva asociada al casillero
    reserva = Reserva.objects.filter(casillero=casillero).first()

    if not reserva:
        return Response({'error': 'Reserva not found for the current user'}, status=status.HTTP_400_BAD_REQUEST)

    # Agregar a la bitácora
    reserva.agregar_a_bitacora_cargado("Carga Realizada")
    reserva.save()

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
def ingresar_clave_view(request, casillero_id, clave, opcion):
    # Lógica para verificar la clave y realizar las acciones correspondientes
    # Puedes redirigir a otra página o mostrar un mensaje de éxito aquí
    if opcion == 0:
        return render(request, 'check_clave_r.html', {'casillero_id': casillero_id, 'clave': clave})
    if opcion == 1:
        return render(request, 'check_clave_l.html', {'casillero_id': casillero_id, 'clave': clave})

def translate_json456(data):

    new_casillero = Casillero(
    tamano='M',
    disponible='D',
    clave=1111,
    abierto=False,
    r_username= None,
    r_email= None,  
    o_email= None,  
    o_name = None,
    fecha_creacion = datetime.today(),  
    estacion = 2
)

    casillero_id = data.get('id')
    availability = data.get('availability')
    reserved = data.get('reserved')
    confirmed = data.get('confirmed')
    loaded = data.get('loaded' )
    locked = data.get('locked')

    if casillero_id in [4,5,6]:
        if availability:
            data['disponible'] = "D"
        if reserved:
            data['disponible'] = "R"
        if confirmed:
            data['disponible'] = "C"
        if loaded:
            data['disponible'] = "A"

        if locked == True:
            data['abierto'] = False
        if locked == False:
            data['abierto'] = True
        
        new_casillero.disponible = data["disponible"]
        new_casillero.abierto = data["abierto"]

    return new_casillero

def translate_json654(data):
    casillero_id = data.get('id')
    disponible = data.get('disponible')
    abierto = data.get('abierto')

    if casillero_id in [4,5,6]:
        if disponible == "D":
            data['availability'] = True
            data['reserved'] = False
            data['confirmed'] = False
            data['loaded'] = False
        elif disponible == "R":
            data['availability'] = False
            data['reserved'] = True
            data['confirmed'] = False
            data['loaded'] = False
        elif disponible == "C":
            data['availability'] = False
            data['reserved'] = False
            data['confirmed'] = True
            data['loaded'] = False
        elif disponible == "A":
            data['availability'] = False
            data['reserved'] = False
            data['confirmed'] = False
            data['loaded'] = True

        if abierto == True:
            data['locked'] = False
        elif abierto == False:
            data['locked'] = True

        data['height'] = 26.0
        data['width'] = 43.0

        data.pop('disponible', None)
        data.pop('abierto', None)
        data.pop('o_email', None)
        data.pop('r_email', None)
        data.pop('r_username', None)
        data.pop('o_name', None)
        data.pop('tamano', None)

    return data

# def reservar_amiwos():
#     response = requests.get('https://tsqrmn8j-8000.brs.devtunnels.ms/stations/2/get_lockers_by_station/')
#     print(response.json())
    
# reservar_amiwos()

def delete_last_casillero(request):

    last_casillero = Casillero.objects.order_by('id').last()

    if last_casillero:
        last_casillero.delete()
        return Response("Last Casillero deleted successfully")
    else:
        return Response("No Casillero to delete")
    

@login_required
def detalles_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    context = {'reserva': reserva}
    return render(request, 'detalles_reserva.html', context)