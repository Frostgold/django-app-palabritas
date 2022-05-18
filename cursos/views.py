import datetime
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from .models import Curso, DetalleDocente
from .forms import FormAgregarCurso, FormDetalleDocente, FormModificarCurso, FormCronActividades, FormModificarDetalleDocente
from autenticacion.models import Usuario
from fichas_alumnos.models import FichaAlumno

@login_required
@permission_required('cursos.view_curso', raise_exception=True)
def listado_cursos_view(request):

    context = {}

    # Consigue una lista con los periodos de cada curso
    context['periodo'] = Curso.objects.order_by().values('periodo').distinct()

    # Consigue la lista de docentes
    docentes = DetalleDocente.objects.order_by().values('docente_id').distinct()
    context['docente'] = Usuario.objects.filter(id__in=docentes)

    # Revisa si el usuario es docente y si es que tiene cursos asginados
    if not request.user.has_perm('cursos.can_view_listado_cursos'):

        cursos = DetalleDocente.objects.filter(docente=request.user).order_by().values('curso_id').distinct()
        listado = Curso.objects.filter(id__in=cursos).order_by('-periodo')
        context['listado'] = listado

    else:
        context['listado'] = Curso.objects.all().order_by('-periodo')

    # Métodos para filtrar búsqueda
    if request.method == 'GET':

        if request.GET.get('nombre') and request.GET.get('nombre') != "":
            query = request.GET.get('nombre')
            object_list =  context['listado'].filter(
                Q(nombre__icontains=query)
            )
            context['listado'] = object_list
        if request.GET.get('periodo') and request.GET.get('periodo') != "":
            query = request.GET.get('periodo')
            object_list =  context['listado'].filter(
                Q(periodo=query)
            )
            context['listado'] = object_list
        if request.GET.get('docente') and request.GET.get('docente') != "":
            query = request.GET.get('docente')
            query_cursos = DetalleDocente.objects.filter(docente_id=query).order_by().values('curso_id').distinct()
            object_list =  context['listado'].filter(
                Q(id__in=query_cursos)
            )
            context['listado'] = object_list

    return render(request, 'listado_cursos.html', context)


@login_required
@permission_required('cursos.add_curso', raise_exception=True)
def agregar_curso_view(request):
    context = {}
    context['form'] = FormAgregarCurso

    if request.POST:
        form = FormAgregarCurso(request.POST)

        if form.is_valid():
            nivel = form.cleaned_data['nivel'].descripcion.capitalize()
            letra = form.cleaned_data['letra'].upper()
            periodo = datetime.datetime.now().year

            nuevo_curso = form.save(commit=False)
            nuevo_curso.id = "{0}{1}{2}".format(nivel[:(len(nivel)-7)], letra, periodo)
            nuevo_curso.nombre = "{0} {1}".format(nivel, letra)
            nuevo_curso.periodo = periodo
            if not Curso.objects.filter(id=nuevo_curso.id):
                nuevo_curso.save()
                return redirect('listado_cursos')
            
            form.add_error(None, "El curso que está intentando agregar ya existe.")

        context['form'] = form

    return render(request, 'formularios/curso_agregar_formulario.html', context)


@login_required
@permission_required('cursos.change_curso', raise_exception=True)
def modificar_curso_view(request, id):
    context = {}

    instance = Curso.objects.get(id=id)
    context['form'] = FormModificarCurso(instance=instance)
    context['id'] = id
    
    if request.POST:
        form = FormModificarCurso(request.POST, instance=instance)
        if form.is_valid():

            alumnos = FichaAlumno.objects.filter(curso=id).count()
            cupos = form.cleaned_data['cupos']
            curso_modificado = form.save(commit=False)
            if cupos >= alumnos:
                curso_modificado.save()
                return redirect('detalle_curso', id)
            else:
                form.add_error('cupos', "No pueden haber menos cupos que alumnos inscritos.")
                context['form'] = form

        else:
            context['form'] = form

    return render(request, 'formularios/curso_modificar_formulario.html', context)


@login_required
@permission_required('cursos.view_curso', raise_exception=True)
def detalle_curso_view(request, id):
    context = {}
    context['curso'] = Curso.objects.get(id=id)
    context['docente'] = DetalleDocente.objects.filter(curso_id=id)
    context['docente_form'] = FormDetalleDocente
    context['avance_form'] = FormCronActividades

    if request.method == 'POST':

        if request.POST.get('docente') and request.POST.get('asignatura'):
            # create a form instance and populate it with data from the request:
            form = FormDetalleDocente(request.POST)

            # check whether it's valid:
            if form.is_valid():
                nuevo_docente = form.save(commit=False)
                nuevo_docente.curso = Curso.objects.get(id=id)
                nuevo_docente.save()
            else:
                context['docente_form'] = form

    return render(request, 'detalle_curso.html', context)


@login_required
@permission_required('cursos.change_detalledocente', raise_exception=True)
def modificar_detalle_docente_view(request, id):
    context = {}

    instance = DetalleDocente.objects.get(id=id)
    context['form'] = FormModificarDetalleDocente(instance=instance)
    context['id'] = id
    
    if request.POST:
        form = FormModificarDetalleDocente(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('detalle_curso', instance.curso.id)

        else:
            context['form'] = form

    return render(request, 'formularios/detalle_docente_modificar_formulario.html', context)


@login_required
@permission_required('cursos.delete_detalledocente', raise_exception=True)
def delete_detalle_docente_view(request, id):
    instance = DetalleDocente.objects.get(id=id)
    curso = instance.curso.id
    instance.delete()

    return redirect('detalle_curso', curso)
