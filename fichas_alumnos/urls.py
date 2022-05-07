from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_fichas_alumnos_view, name='listado_fichas_alumnos')
]
