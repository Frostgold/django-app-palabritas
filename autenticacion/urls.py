from django.urls import path

from . import views

urlpatterns = [
    path('cuentas/registro', views.registration, name='registro'),
]