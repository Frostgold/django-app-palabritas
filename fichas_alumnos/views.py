from django.shortcuts import redirect, render
from django.db.models import Q
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno, DetalleApoderado
from cursos.models import Curso
from lista_espera.models import ListaEspera
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import inlineformset_factory

from .forms import FormFichaAlumno, FormChangeFichaAlumno, FormAvanceAlumno, FormTrabajoAlumno, FormDocumentoAlumno, ApoderadoBaseFormSet, ListaEsperaBaseFormSet


@login_required
@permission_required('fichas_alumnos.view_fichaalumno', raise_exception=True)
def listado_fichas_alumnos_view(request):

    context = {}

    # Consigue la lista de cursos
    context['curso'] = Curso.objects.order_by().values('nombre').distinct()

    # Revisa si el usuario es apoderado y si es que tiene pupilos asginados
    if not request.user.has_perm('fichas_alumnos.can_view_listado_fichas'):

        alumnos = DetalleApoderado.objects.filter(apoderado=request.user).order_by().values('alumno_id').distinct()
        context['listado'] = FichaAlumno.objects.filter(rut__in=alumnos).order_by('-curso', 'nombre')

    else:
        context['listado'] = FichaAlumno.objects.all().order_by('-curso', 'nombre')

        if request.method == 'GET':

            if request.GET.get('nomrut') and request.GET.get('nomrut') != "":
                query = request.GET.get('nomrut')
                object_list = context['listado'].filter(
                    Q(nombre__icontains=query) | Q(rut__icontains=query)
                ).order_by('nombre')
                context['listado'] = object_list
            if request.GET.get('curso') and request.GET.get('curso') != "":
                query = request.GET.get('curso')
                query_curso = Curso.objects.filter(nombre=query).order_by().values('id')
                object_list = context['listado'].filter(
                    Q(curso__in=query_curso)
                ).order_by('nombre')
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

    context['avance_form'] = FormAvanceAlumno
    context['trabajo_form'] = FormTrabajoAlumno
    context['documento_form'] = FormDocumentoAlumno
    context['apoderado'] = DetalleApoderado.objects.filter(alumno=rut)
    context['ficha'] = FichaAlumno.objects.filter(rut=rut)
    context['avances'] = AvanceAlumno.objects.filter(alumno=rut).order_by('-id')
    context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut).order_by('-id')
    context['documentos'] = BancoDocumento.objects.filter(alumno=rut).order_by('-id')

    if not context['ficha']:
        return redirect('listado_fichas_alumnos')

    if request.method == 'POST':

        if request.POST.get('comentario'):
            # create a form instance and populate it with data from the request:
            form = FormAvanceAlumno(request.POST)

            # check whether it's valid:
            if form.is_valid():
                nuevo_avance = form.save(commit=False)
                nuevo_avance.editor = request.user
                nuevo_avance.alumno = FichaAlumno(rut)
                nuevo_avance.save()
            else:
                context['avance_form'] = form

        if request.FILES.get('trabajo'):
            # create a form instance and populate it with data from the request:
            form = FormTrabajoAlumno(request.POST, request.FILES)

            # check whether it's valid:
            if form.is_valid():
                nuevo_trabajo = form.save(commit=False)
                nuevo_trabajo.alumno = FichaAlumno(rut)
                nuevo_trabajo.save()

        if request.FILES.get('documento'):
            # create a form instance and populate it with data from the request:
            form = FormDocumentoAlumno(request.POST, request.FILES)

            # check whether it's valid:
            if form.is_valid():
                nuevo_documento = form.save(commit=False)
                nuevo_documento.alumno = FichaAlumno(rut)
                nuevo_documento.save()

    

    return render(request, 'ficha_alumno.html', context)


@login_required
@permission_required('fichas_alumnos.add_fichaalumno', raise_exception=True)
def form_agregar_ficha_alumno(request):

    context = {}
    context['form'] = FormFichaAlumno

    ApoderadoFormSet = inlineformset_factory(FichaAlumno, DetalleApoderado, formset=ApoderadoBaseFormSet, fields=('apoderado',), can_delete=False, max_num=1)
    ListaEsperaFormSet = inlineformset_factory(FichaAlumno, ListaEspera, formset=ListaEsperaBaseFormSet, fields=('nivel',), can_delete=False, max_num=1)

    alumno = FichaAlumno()
    context['apoderado'] = ApoderadoFormSet(instance=alumno)
    context['lista_espera'] = ListaEsperaFormSet(instance=alumno)


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FormFichaAlumno(request.POST)

        # check whether it's valid:
        if form.is_valid():         
            rut = form.cleaned_data['rut']
            ficha_creada = form.save(commit=False)

            formset_apoderado = ApoderadoFormSet(request.POST, instance=ficha_creada)
            formset_lista_espera = ListaEsperaFormSet(request.POST, instance=ficha_creada)
            if formset_lista_espera.is_valid():
                ficha_creada.nombre = ficha_creada.nombre.title()
                ficha_creada.save()
                formset_apoderado.save()
                formset_lista_espera.save()

                return redirect('ficha_alumno', rut)
            else:
                form.add_error(None, 'Debe seleccionar el nivel.')

        context['form'] = form


    return render(request, 'formularios/ficha_alumno_agregar_formulario.html', context)


@login_required
@permission_required('fichas_alumnos.change_fichaalumno', raise_exception=True)
def change_ficha_alumno(request, rut):
    context = {}
    try:
        instance = FichaAlumno.objects.get(rut=rut)
    except:
        return redirect('listado_fichas_alumnos')
    context['alumno'] = instance
    if instance.curso:
        context['form'] = FormChangeFichaAlumno(instance=instance, has_curso=True, is_retirado=False)
    elif instance.estado == 'retirado':
        context['form'] = FormChangeFichaAlumno(instance=instance, has_curso=False, is_retirado=True)
    else:
        context['form'] = FormChangeFichaAlumno(instance=instance, has_curso=False, is_retirado=False)

    ApoderadoFormSet = inlineformset_factory(FichaAlumno, DetalleApoderado, fields=('apoderado',), can_delete=False, max_num=1)
    context['apoderado'] = ApoderadoFormSet(instance=instance)

    if instance.estado == 'retirado':
        ListaEsperaFormSet = inlineformset_factory(FichaAlumno, ListaEspera, formset=ListaEsperaBaseFormSet, fields=('nivel',), can_delete=False, max_num=1)
        context['lista_espera'] = ListaEsperaFormSet(instance=instance)
    
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        if instance.curso:
            form = FormChangeFichaAlumno(request.POST, instance=instance, has_curso=True, is_retirado=False)
        elif instance.estado == 'retirado':
            form = FormChangeFichaAlumno(request.POST, instance=instance, has_curso=False, is_retirado=True)
        else:
            form = FormChangeFichaAlumno(request.POST, instance=instance, has_curso=False, is_retirado=False)

        # check whether it's valid:
        if form.is_valid():
            rut = instance.rut
            ficha_modificada = form.save(commit=False)
            ficha_modificada.nombre = ficha_modificada.nombre.title()
            
            # Elimina la asignación de apoderado
            formset = ApoderadoFormSet(request.POST, instance=ficha_modificada)
            if not formset.is_valid():
                apoderado = DetalleApoderado.objects.filter(alumno=rut)
                if apoderado:
                    apoderado.delete()
            else:
                formset.save()

            # Reintrega al alumno retirado a una lista de espera según nivel seleccionado
            if instance.estado == 'retirado':
                formset_lista_espera = ListaEsperaFormSet(request.POST, instance=ficha_modificada)
                if formset_lista_espera.is_valid():
                    ficha_modificada.estado = 'lista_espera'
                    formset_lista_espera.save()

            ficha_modificada.save()

            return redirect('ficha_alumno', rut)

        else:
            context['form'] = form


    return render(request, 'formularios/ficha_alumno_modificar_formulario.html', context)


@login_required
@permission_required('fichas_alumnos.change_avancealumno', raise_exception=True)
def change_avance_alumno(request, id):
    context = {}
    try:
        instance = AvanceAlumno.objects.get(id=id)
    except:
        return redirect('listado_fichas_alumnos')
    context['avance'] = instance
    context['form'] = FormAvanceAlumno(instance=instance)
    
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = FormAvanceAlumno(request.POST, instance=instance)

        # check whether it's valid:
        if form.is_valid():
            avance_modificado = form.save(commit=False)
            avance_modificado.editor = request.user
            avance_modificado.modificado = True
            avance_modificado.save()
            return redirect('ficha_alumno', instance.alumno.rut)

        else:
            context['form'] = form


    return render(request, 'formularios/avance_modificar_formulario.html', context)


@login_required
@permission_required('fichas_alumnos.delete_avancealumno', raise_exception=True)
def delete_avance_alumno(request, id):
    try:
        instance = AvanceAlumno.objects.get(id=id)
    except:
        return redirect('listado_fichas_alumnos')
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)


@login_required
@permission_required('fichas_alumnos.delete_bancotrabajo', raise_exception=True)
def delete_banco_trabajo(request, id):
    try:
        instance = BancoTrabajo.objects.get(id=id)
    except:
        return redirect('listado_fichas_alumnos')
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)


@login_required
@permission_required('fichas_alumnos.delete_bancotrabajo', raise_exception=True)
def delete_banco_documento(request, id):
    try:
        instance = BancoDocumento.objects.get(id=id)
    except:
        return redirect('listado_fichas_alumnos')
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)


@login_required
@permission_required('fichas_alumnos.can_retirar_ficha_alumno', raise_exception=True)
def retirar_ficha_alumno(request, rut):
    try:
        instance = FichaAlumno.objects.get(rut=rut)
    except:
        return redirect('listado_fichas_alumnos')
    lista_espera_instance = ListaEspera.objects.filter(alumno=rut)
    instance.estado = 'retirado'
    instance.curso = None
    instance.save()
    if lista_espera_instance:
        lista_espera_instance.delete()

    return redirect('ficha_alumno', rut)
