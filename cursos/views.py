import datetime
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from lista_espera.models import ListaEspera
from .models import CronogramaActividad, Curso, DetalleDocente
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
    docentes = Curso.objects.order_by().values('docente_jefe').distinct()
    context['docente'] = Usuario.objects.filter(id__in=docentes)

    # Revisa si el usuario es docente y si es que tiene cursos asginados
    if not request.user.has_perm('cursos.can_view_listado_cursos'):

        cursos = DetalleDocente.objects.filter(docente=request.user).order_by().values('curso_id').distinct()
        listado = Curso.objects.filter(Q(id__in=cursos) | Q(docente_jefe=request.user)).order_by('-periodo')
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
        if request.user.has_perm('cursoscan_view_listado_cursos'):
            if request.GET.get('periodo') and request.GET.get('periodo') != "":
                query = request.GET.get('periodo')
                object_list =  context['listado'].filter(
                    Q(periodo=query)
                )
                context['listado'] = object_list
        if request.GET.get('docente') and request.GET.get('docente') != "":
            query = request.GET.get('docente')
            if query == 'No asignado':
                object_list =  context['listado'].filter(
                    Q(docente_jefe=None)
                )
            else:
                object_list =  context['listado'].filter(
                    Q(docente_jefe=query)
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

    try:
        instance = Curso.objects.get(id=id)
    except:
        return redirect('listado_cursos')
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
    try:
        context['curso'] = Curso.objects.get(id=id)
    except:
        return redirect('listado_cursos')
    context['docente'] = DetalleDocente.objects.filter(curso_id=id)
    context['cron_actividad'] = CronogramaActividad.objects.filter(curso_id=id).order_by('-id')
    context['alumnos'] = FichaAlumno.objects.filter(curso_id=id).order_by('nombre')
    context['docente_form'] = FormDetalleDocente
    context['actividad_form'] = FormCronActividades

    if 'error' in request.session:
        context['error'] = request.session['error']
        del request.session['error']
    if 'success' in request.session:
        context['success'] = request.session['success']
        del request.session['success']

    context['inscritos'] = FichaAlumno.objects.filter(curso_id=id).count()
    if context['curso'].cupos > context['inscritos']:
        context['cupos'] = context['curso'].cupos - context['inscritos']

        context['avanzan'] = ListaEspera.objects.filter(nivel=context['curso'].nivel).count()
        if context['avanzan'] > context['cupos']:
            context['avanzan'] = context['cupos']

    if request.method == 'POST':

        print(request.POST)

        if request.POST.get('docente') and request.POST.get('asignatura'):
            # create a form instance and populate it with data from the request:
            form = FormDetalleDocente(request.POST)

            # check whether it's valid:
            if form.is_valid():
                nuevo_docente = form.save(commit=False)
                nuevo_docente.curso = Curso.objects.get(id=id)
                nuevo_docente.asignatura = nuevo_docente.asignatura.title()
                nuevo_docente.save()
            else:
                context['docente_form'] = form

        if request.POST.get('comentario'):
            # create a form instance and populate it with data from the request:
            form = FormCronActividades(request.POST, request.FILES)

            # check whether it's valid:
            if form.is_valid():
                nueva_actividad = form.save(commit=False)
                nueva_actividad.curso = Curso.objects.get(id=id)
                nueva_actividad.editor = request.user
                nueva_actividad.save()
            else:
                context['actividad_form'] = form

    return render(request, 'detalle_curso.html', context)


@login_required
@permission_required('cursos.change_detalledocente', raise_exception=True)
def modificar_detalle_docente_view(request, id):
    context = {}

    try:
        instance = DetalleDocente.objects.get(id=id)
    except:
        return redirect('listado_cursos')
    context['form'] = FormModificarDetalleDocente(instance=instance)
    context['instance'] = instance
    
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
    try:
        instance = DetalleDocente.objects.get(id=id)
    except:
        return redirect('listado_cursos')
    curso = instance.curso.id
    instance.delete()

    return redirect('detalle_curso', curso)


@login_required
@permission_required('cursos.change_cronogramaactividad', raise_exception=True)
def modificar_cronograma_actividad_view(request, id):
    context = {}

    try:
        instance = CronogramaActividad.objects.get(id=id)
    except:
        return redirect('listado_cursos')
    context['form'] = FormCronActividades(instance=instance)
    context['instance'] = instance
    

    if request.POST:
        print(request.POST)
        print(request.FILES)

        form = FormCronActividades(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            actividad_modificada = form.save(commit=False)
            actividad_modificada.modificado = True
            if request.POST.get('chkEliminarImg') == "on":
                actividad_modificada.imagen = None
            actividad_modificada.save()
            
            return redirect('detalle_curso', instance.curso.id)

        else:
            context['form'] = form

    return render(request, 'formularios/cronograma_actividad_modificar_formulario.html', context)


@login_required
@permission_required('cursos.delete_cronogramaactividad', raise_exception=True)
def delete_cronograma_actividad_view(request, id):
    try:
        instance = CronogramaActividad.objects.get(id=id)
    except:
        return redirect('listado_cursos')
    curso = instance.curso.id
    instance.delete()

    return redirect('detalle_curso', curso)
