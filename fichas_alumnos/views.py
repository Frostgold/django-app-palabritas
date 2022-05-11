from django.shortcuts import redirect, render
from django.db.models import Q
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno, DetalleApoderado
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.forms import inlineformset_factory

from .forms import AgregarFichaAlumno


@login_required
@permission_required('fichas_alumnos.view_fichaalumno', raise_exception=True)
def listado_fichas_alumnos_view(request):

    context = {}

    # Revisa si el usuario es apoderado y si es que tiene pupilos asginados
    if not request.user.has_perm('fichas_alumnos.can_view_listado_fichas'):
        lista_alumnos = []

        alumno = DetalleApoderado.objects.filter(apoderado=request.user)
        if alumno:
            for a in alumno:
                lista_alumnos.append(a.alumno.rut)
            
            listado = FichaAlumno.objects.filter(rut__in=lista_alumnos)

            try:
                if listado:
                    context['listado'] = listado
            except:
                pass

    else:
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
@permission_required('fichas_alumnos.view_fichaalumno', raise_exception=True)
def ficha_alumno_view(request, rut):

    context = {}

    # Revisa si el usuario es apoderado. Si el alumno le corresponde puede entrar.
    if not request.user.has_perm('fichas_alumnos.can_view_listado_fichas'):

        alumnos = DetalleApoderado.objects.filter(apoderado=request.user)
        for alumno in alumnos:
            if rut == alumno.alumno.rut:

                context['apoderado'] = DetalleApoderado.objects.filter(alumno=rut)
                context['ficha'] = FichaAlumno.objects.filter(rut=rut)
                context['avances'] = AvanceAlumno.objects.filter(alumno=rut)
                context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut)
                context['documentos'] = BancoDocumento.objects.filter(alumno=rut)

                return render(request, 'ficha_alumno.html', context)

        return redirect('listado_fichas_alumnos')

    context['apoderado'] = DetalleApoderado.objects.filter(alumno=rut)
    context['ficha'] = FichaAlumno.objects.filter(rut=rut)
    context['avances'] = AvanceAlumno.objects.filter(alumno=rut)
    context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut)
    context['documentos'] = BancoDocumento.objects.filter(alumno=rut)

    return render(request, 'ficha_alumno.html', context)

@login_required
@permission_required('fichas_alumnos.add_fichaalumno', raise_exception=True)
def form_agregar_ficha_alumno(request):

    context = {}
    context['form'] = AgregarFichaAlumno

    ApoderadoFormSet = inlineformset_factory(FichaAlumno, DetalleApoderado, fields=('apoderado',), can_delete=False, max_num=1)

    alumno = FichaAlumno()
    context['apoderado'] = ApoderadoFormSet(instance=alumno)


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AgregarFichaAlumno(request.POST)

        # check whether it's valid:
        if form.is_valid():         
            rut = form.cleaned_data['rut']
            ficha_creada = form.save(commit=False)
            print(ficha_creada)
            formset = ApoderadoFormSet(request.POST, instance=ficha_creada)
            if formset.is_valid():
                ficha_creada.save()
                formset.save()

                return redirect('ficha_alumno', rut)

        else:
            context['form'] = form


    return render(request, 'formularios/ficha_alumno_agregar_formulario.html', context)
