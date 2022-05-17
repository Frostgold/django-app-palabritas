from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_cursos_view, name='listado_cursos'),
    path('agregar_curso/', views.agregar_curso_view, name='agregar_curso'),
    path('modificar_curso/<str:id>', views.modificar_curso_view, name='modificar_curso'),
]
