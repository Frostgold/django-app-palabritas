from django.contrib import admin
from .models import ListaEspera

class ListaEsperaConfig(admin.ModelAdmin):
    search_fields = ('id', 'alumno',)
    ordering = ('id',)
    list_display = ('id', 'alumno', 'nivel',)
    list_filter = ('nivel',)

admin.site.register(ListaEspera, ListaEsperaConfig)
