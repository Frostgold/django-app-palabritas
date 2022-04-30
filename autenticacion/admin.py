from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UserAdminConfig(UserAdmin):
    search_fields = ('usuario', 'email', 'nombre',)
    ordering = ('usuario',)
    list_display = ('usuario', 'email', 'nombre', 'is_active',)
    list_filter = ('is_active',)

    fieldsets = (
        (None, {
            "fields": (
                'usuario',
                'email',
                'nombre',
            ),
        }),
        ('Permisos', {
            "fields": (
                'groups',
                'is_staff',
                'is_active',
            ),
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": (
                'wide',
            ),
            "fields": (
                'usuario',
                'email',
                'nombre',
                'password1',
                'password2',
            ),
        }),
    )
    

admin.site.register(Usuario, UserAdminConfig)
