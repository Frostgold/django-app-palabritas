from django.contrib import admin
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno

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
    filename.admin_order_field = 'documento'


class BancoTrabajoConfig(admin.ModelAdmin):
    search_fields = ('alumno_id__rut',)
    ordering = ('alumno_id',)
    list_display = ('id', 'alumno_id', 'filename',)
    list_filter = ('alumno_id',)

    def filename(self, obj):
        return obj.filename()

    filename.short_description = 'Trabajo'
    filename.admin_order_field = 'trabajo'


class AvanceConfig(admin.ModelAdmin):
    search_fields = ('alumno_id__rut', 'editor',)
    ordering = ('alumno_id',)
    list_display = ('id', 'alumno_id', 'geteditor', 'fecha_edicion',)
    list_filter = ('alumno_id', 'editor',)

    def geteditor(self, obj):
        return obj.geteditor()

    geteditor.short_description = 'Editor'
    geteditor.admin_order_field = 'editor'

    
admin.site.register(FichaAlumno, FichaAlumnoConfig)
admin.site.register(BancoDocumento, BancoDocumentoConfig)
admin.site.register(BancoTrabajo, BancoTrabajoConfig)
admin.site.register(AvanceAlumno, AvanceConfig)
