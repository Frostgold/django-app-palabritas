from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path(
        'cuentas/registro', 
        views.registration_view, name='registro'),
    path(
        'cuentas/login/',
        auth_views.LoginView.as_view(template_name='registration/login_form.html'), name='login',
    ),
    path(
        'cuentas/cambiar_pass/',
        auth_views.PasswordChangeView.as_view(template_name='registration/cambiar_pass_form.html'), name='cambiar_password',
    ),
    path(
        'cuentas/cambiar_pass_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='registration/cambiar_pass_done.html'), name='password_change_done',
    ),
    path(
        'cuentas/reset_pass/',
        auth_views.PasswordResetView.as_view(template_name='password_reset/password_reset_form.html'), name='reset_password',
    ),
    path(
        'cuentas/reset_pass/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset/password_reset_done.html'), name='password_reset_done',
    ),
    path(
        'cuentas/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/password_reset_confirm.html'), name="password_reset_confirm",
    ),
    path(
        'cuentas/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'), name='password_reset_complete',
    ),
    path('cuentas/logout/', views.logout_view, name='logout'),
]