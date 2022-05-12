from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_fichas_alumnos_view, name='listado_fichas_alumnos'),
    path('ficha_alumno/<str:rut>', views.ficha_alumno_view, name='ficha_alumno'),
    path('agregar_ficha', views.form_agregar_ficha_alumno, name='agregar_ficha_alumno'),
    path('eliminar_trabajo/<int:id>', views.delete_banco_trabajo, name='eliminar_trabajo_alumno'),
    path('eliminar_documento/<int:id>', views.delete_banco_documento, name='eliminar_documento_alumno'),
]
