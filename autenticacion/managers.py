from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, usuario, email, nombre, password, **other_fields):

        if not usuario:
            raise ValueError('Debes ingresar un nombre de usuario')
        if not email:
            raise ValueError('Debes ingresar una dirección email')

        email = self.normalize_email(email)
        user = self.model(usuario=usuario, email=email, nombre=nombre, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, usuario, email, nombre, password, **other_fields):
        
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        if other_fields.get('is_active') is not True:
            raise ValueError(
                'El superusuario debe ser asignado a is_active=True.')
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'El superusuario debe ser asignado a is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'El superusuario debe ser asignado a is_superuser=True.')

        return self.create_user(usuario, email, nombre, password, **other_fields)
