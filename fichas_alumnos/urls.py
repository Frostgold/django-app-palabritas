from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_fichas_alumnos_view, name='listado_fichas_alumnos'),
    path('agregar_ficha', views.form_agregar_ficha_alumno, name='agregar_ficha_alumno'),
    path('ficha_alumno/<str:rut>', views.ficha_alumno_view, name='ficha_alumno'),
    path('modificar_ficha/<str:rut>', views.change_ficha_alumno, name='change_ficha_alumno'),
    path('modificar_avance/<int:id>', views.change_avance_alumno, name='modificar_avance_alumno'),
    path('eliminar_avance/<int:id>', views.delete_avance_alumno, name='eliminar_avance_alumno'),
    path('eliminar_trabajo/<int:id>', views.delete_banco_trabajo, name='eliminar_trabajo_alumno'),
    path('eliminar_documento/<int:id>', views.delete_banco_documento, name='eliminar_documento_alumno'),
]
