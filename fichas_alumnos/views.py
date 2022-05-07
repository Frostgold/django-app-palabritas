from django.shortcuts import render
from django.views.generic import ListView
from .models import FichaAlumno

def listado_fichas_alumnos_view(request):

    context = {}
    context['listado'] = FichaAlumno.objects.all()


    return render(request, 'listado_fichas_alumnos.html', context)
