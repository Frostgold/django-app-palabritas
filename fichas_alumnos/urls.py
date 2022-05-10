from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_fichas_alumnos_view, name='listado_fichas_alumnos'),
    path('ficha_alumno/<str:rut>', views.ficha_alumno_view, name='ficha_alumno'),
]
