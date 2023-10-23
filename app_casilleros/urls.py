from django.urls import path
from . import views

urlpatterns = [
    path('casilleros_disponibles/', views.casilleros_disponibles, name='casilleros_disponibles'),
    path('casillero_detalle/<int:pk>/', views.casillero_detalle, name='casillero_detalle'),
    path('reservar_casillero/', views.reservar_casillero, name='reservar_casillero'),
    path('confirmar_reserva/', views.confirmar_reserva, name='confirmar_reserva'),
    path('cancelar_reserva/', views.cancelar_reserva, name='cancelar_reserva'),
    path('estado_reserva/', views.estado_reserva, name='estado_reserva'),
]
