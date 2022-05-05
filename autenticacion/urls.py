from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('cuentas/registro', views.registration_view, name='registro'),
    path(
        'cuentas/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'), name='login',
    ),
    path(
        'cuentas/cambiar_pass/',
        auth_views.PasswordChangeView.as_view(template_name='registration/cambio_pass.html'), name='cambiar_password',
    ),
    path(
        'cuentas/cambiar_pass_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='done_views/cambiar_pass_done.html'), name='password_change_done',
    ),
    path(
        'cuentas/reset_pass/',
        auth_views.PasswordResetView.as_view(template_name='registration/reset_password.html'), name='reset_password',
    ),
    path(
        'cuentas/reset_pass_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='done_views/reset_pass_done.html'), name='password_reset_done',
    ),
    path('cuentas/logout/', views.logout_view, name='logout'),
]