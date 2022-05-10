from django.shortcuts import render
from django.db.models import Q
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno
from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required('view_fichaalumno', raise_exception=True)
def listado_fichas_alumnos_view(request):

    context = {}
    context['listado'] = FichaAlumno.objects.all()

    if request.method == 'GET':

        if request.GET.get('curso') == "0" and request.GET.get('nomrut') != "":
            query = request.GET.get('nomrut')
            object_list = FichaAlumno.objects.filter(
                Q(nombre__icontains=query) | Q(rut__icontains=query)
            )
            context['listado'] = object_list


    return render(request, 'listado_fichas_alumnos.html', context)


@login_required
@permission_required('view_fichaalumno', raise_exception=True)
def ficha_alumno_view(request, rut):

    context = {}
    context['ficha'] = FichaAlumno.objects.filter(rut=rut)
    context['avances'] = AvanceAlumno.objects.filter(alumno=rut)
    context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut)
    context['documentos'] = BancoDocumento.objects.filter(alumno=rut)

    return render(request, 'ficha_alumno.html', context)