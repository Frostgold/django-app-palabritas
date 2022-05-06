from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

class Usuario(AbstractBaseUser, PermissionsMixin):
    usuario = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, blank=False, null=False)
    nombre = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['email', 'nombre', 'password']
    
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['usuario']

    def __str__(self):
        return self.usuario