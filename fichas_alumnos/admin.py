from django.contrib import admin
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno, DetalleApoderado

class ApoderadoInline(admin.TabularInline):
    model = DetalleApoderado
    max_num = 1

class FichaAlumnoConfig(admin.ModelAdmin):
    inlines = [ApoderadoInline]

    search_fields = ('rut', 'nombre',)
    ordering = ('rut',)
    list_display = ('rut', 'nombre', 'estado', 'curso')
    list_filter = ('estado', 'curso')

    fieldsets = (
        (None, {
            "fields": (
                'rut',
                'nombre',
                'fecha_nacimiento',
                'direccion',
                'nombre_padre',
                'nombre_madre',
                'telefono',
                'ficha_social',
                'formulario_salud',
                'anamnesis',
                'certif_nacimiento',
                'consent_fonoaudiologia',
                'consent_vidasana',
            ),
        }),
        ('Situación académica', {
            "fields": (
                'estado',
                'curso',
            ),
        }),
    )

    def change_view(self, request, object_id, extra_content=None):
        self.fieldsets = (
            (None, {
            "fields": (
                'nombre',
                'fecha_nacimiento',
                'direccion',
                'nombre_padre',
                'nombre_madre',
                'telefono',
                'ficha_social',
                'formulario_salud',
                'anamnesis',
                'certif_nacimiento',
                'consent_fonoaudiologia',
                'consent_vidasana',
            ),
            }),
            ('Situación académica', {
                "fields": (
                    'estado',
                    'curso',
                ),
            }),
        )
        return super(FichaAlumnoConfig, self).change_view(request, object_id)


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


class DetalleApoderadoConfig(admin.ModelAdmin):
    search_fields = ('alumno_id__rut', 'apoderado',)
    ordering = ('alumno_id',)
    list_display = ('id', 'alumno_id', 'getapoderado',)
    list_filter = ('alumno_id', 'apoderado',)

    def getapoderado(self, obj):
        return obj.getapoderado()

    getapoderado.short_description = 'Apoderado'
    getapoderado.admin_order_field = 'apoderado'

    
admin.site.register(FichaAlumno, FichaAlumnoConfig)
admin.site.register(BancoDocumento, BancoDocumentoConfig)
admin.site.register(BancoTrabajo, BancoTrabajoConfig)
admin.site.register(AvanceAlumno, AvanceConfig)
admin.site.register(DetalleApoderado, DetalleApoderadoConfig)
