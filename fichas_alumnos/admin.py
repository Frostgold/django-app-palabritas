from django.contrib import admin
from .models import FichaAlumno, BancoDocumento

class FichaAlumnoConfig(admin.ModelAdmin):
    search_fields = ('rut', 'nombre',)
    ordering = ('rut',)
    list_display = ('rut', 'nombre', 'estado',)
    list_filter = ('estado',)

    fieldsets = (
        (None, {
            "fields": (
                'rut',
                'nombre',
                'fecha_nacimiento',
            ),
        }),
        ('Situación académica', {
            "fields": (
                'estado',
            ),
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": (
                'wide',
            ),
            "fields": (
                'rut',
                'nombre',
                'fecha_nacimiento',
                'estado',
            ),
        }),
    )


class BancoDocumentoConfig(admin.ModelAdmin):
    search_fields = ('alumno_id__rut',)
    ordering = ('alumno_id',)
    list_display = ('id', 'alumno_id', 'filename',)
    list_filter = ('alumno_id',)

    def filename(self, obj):
        return obj.filename()

    filename.short_description = 'Documento'
    filename.admin_order_field = 'nombre_documento'

    
admin.site.register(FichaAlumno, FichaAlumnoConfig)
admin.site.register(BancoDocumento, BancoDocumentoConfig)
