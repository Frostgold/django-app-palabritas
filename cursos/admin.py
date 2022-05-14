from django.contrib import admin
from .models import Nivel, Curso, DetalleDocente, CronogramaActividad

class NivelConfig(admin.ModelAdmin):
    search_fields = ('id', 'descripcion',)
    ordering = ('id',)
    list_display = ('id', 'descripcion',)


class DocenteInline(admin.TabularInline):
    model = DetalleDocente
    extra = 1

class CursoConfig(admin.ModelAdmin):
    inlines = [DocenteInline]

    search_fields = ('nivel_id__descripcion', 'nombre',)
    ordering = ('periodo', 'nivel', 'letra',)
    list_display = ('id', 'nombre', 'cupos', 'periodo',)
    list_filter = ('nivel', 'periodo',)

    fieldsets = (
        (None, {
            "classes": (
                'wide',
            ),
            "fields": (
                'id',
                'nivel',
                'letra',
                'nombre',
                'periodo',
                'cupos',
            ),
        }),
    )

    def change_view(self, request, object_id, extra_content=None):
        self.fieldsets = (
            (None, {
            "classes": (
                'wide',
            ),
            "fields": (
                'cupos',
            ),
        }),
        )
        return super(CursoConfig, self).change_view(request, object_id)


class DetalleDocenteConfig(admin.ModelAdmin):
    search_fields = ('curso_id__nombre', 'docente_id__nombre', 'asignatura',)
    ordering = ('id',)
    list_display = ('id', 'getcurso', 'getdocente',)
    list_filter = ('curso_id', 'docente_id',)

    def getcurso(self, obj):
        return obj.getcurso()

    def getdocente(self, obj):
        return obj.getdocente()

    getcurso.short_description = 'Curso'
    getcurso.admin_order_field = 'curso'
    

    getdocente.short_description = 'Docente'
    getdocente.admin_order_field = 'docente'


class CronogramaActividadConfig(admin.ModelAdmin):
    search_fields = ('curso_id__nombre', 'editor_id__nombre')
    ordering = ('id',)
    list_display = ('id', 'getcurso', 'geteditor', 'fecha_edicion', 'modificado',)
    list_filter = ('curso_id__nombre', 'modificado',)

    def geteditor(self, obj):
        return obj.geteditor()

    def getcurso(self, obj):
        return obj.getcurso()

    geteditor.short_description = 'Editor'
    geteditor.admin_order_field = 'editor'

    getcurso.short_description = 'Curso'
    getcurso.admin_order_field = 'curso'


admin.site.site_header  =  "Administración Palabritas"  
admin.site.site_title  =  "Sitio administrativo Palabritas"
admin.site.index_title  =  "Administración Palabritas - Modelos"

admin.site.register(Nivel, NivelConfig)
admin.site.register(Curso, CursoConfig)
admin.site.register(DetalleDocente, DetalleDocenteConfig)
admin.site.register(CronogramaActividad, CronogramaActividadConfig)
