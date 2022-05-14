from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_cursos_view, name='listado_cursos'),
]
