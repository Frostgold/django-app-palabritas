from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_lista_espera_view, name='listado_lista_espera'),
    path('avanzar_lista_espera/<str:kwargs>', views.avanzar_lista_espera_view, name='avanzar_lista_espera'),
]
