from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_cursos_view, name='listado_cursos'),
    path('agregar_curso/', views.agregar_curso_view, name='agregar_curso'),
    path('modificar_curso/<str:id>', views.modificar_curso_view, name='modificar_curso'),
    path('detalle_curso/<str:id>', views.detalle_curso_view, name='detalle_curso'),
    path('modificar_detalle_docente/<int:id>', views.modificar_detalle_docente_view, name='modificar_detalle_docente'),
    path('eliminar_detalle_docente/<int:id>', views.delete_detalle_docente_view, name='eliminar_detalle_docente'),
]
