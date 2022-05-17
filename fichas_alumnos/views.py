from django.shortcuts import redirect, render
from django.db.models import Q
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno, DetalleApoderado
from cursos.models import Curso
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import inlineformset_factory

from .forms import FormFichaAlumno, FormChangeFichaAlumno, FormAvanceAlumno, FormTrabajoAlumno, FormDocumentoAlumno


@login_required
@permission_required('fichas_alumnos.view_fichaalumno', raise_exception=True)
def listado_fichas_alumnos_view(request):

    context = {}

    # Consigue la lista de cursos
    context['curso'] = Curso.objects.order_by().values('nombre').distinct()

    # Revisa si el usuario es apoderado y si es que tiene pupilos asginados
    if not request.user.has_perm('fichas_alumnos.can_view_listado_fichas'):

        alumnos = DetalleApoderado.objects.filter(apoderado=request.user).order_by().values('alumno_id').distinct()
        context['listado'] = FichaAlumno.objects.filter(rut__in=alumnos)

    else:
        context['listado'] = FichaAlumno.objects.all()

        if request.method == 'GET':

            if request.GET.get('nomrut') and request.GET.get('nomrut') != "":
                query = request.GET.get('nomrut')
                object_list = context['listado'].filter(
                    Q(nombre__icontains=query) | Q(rut__icontains=query)
                )
                context['listado'] = object_list
            if request.GET.get('curso') and request.GET.get('curso') != "":
                query = request.GET.get('curso')
                query_curso = Curso.objects.filter(nombre=query).order_by().values('id')
                object_list = context['listado'].filter(
                    Q(curso__in=query_curso)
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

    context['avance_form'] = FormAvanceAlumno
    context['trabajo_form'] = FormTrabajoAlumno
    context['documento_form'] = FormDocumentoAlumno
    context['apoderado'] = DetalleApoderado.objects.filter(alumno=rut)
    context['ficha'] = FichaAlumno.objects.filter(rut=rut)
    context['avances'] = AvanceAlumno.objects.filter(alumno=rut).order_by('-id')
    context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut).order_by('-id')
    context['documentos'] = BancoDocumento.objects.filter(alumno=rut).order_by('-id')

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

    ApoderadoFormSet = inlineformset_factory(FichaAlumno, DetalleApoderado, fields=('apoderado',), can_delete=False, max_num=1)

    alumno = FichaAlumno()
    context['apoderado'] = ApoderadoFormSet(instance=alumno)


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FormFichaAlumno(request.POST)

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


@login_required
@permission_required('fichas_alumnos.change_fichaalumno', raise_exception=True)
def change_ficha_alumno(request, rut):
    context = {}
    instance = FichaAlumno.objects.get(rut=rut)
    context['alumno'] = instance
    context['form'] = FormChangeFichaAlumno(instance=instance)

    ApoderadoFormSet = inlineformset_factory(FichaAlumno, DetalleApoderado, fields=('apoderado',), can_delete=False, max_num=1)
    context['apoderado'] = ApoderadoFormSet(instance=instance)
    
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = FormChangeFichaAlumno(request.POST, instance=instance)

        # check whether it's valid:
        if form.is_valid():
            rut = instance.rut
            ficha_modificada = form.save(commit=False)
            print(ficha_modificada)
            formset = ApoderadoFormSet(request.POST, instance=ficha_modificada)
            if formset.is_valid():
                ficha_modificada.save()
                formset.save()

                return redirect('ficha_alumno', rut)

        else:
            context['form'] = form


    return render(request, 'formularios/ficha_alumno_modificar_formulario.html', context)


@login_required
@permission_required('fichas_alumnos.change_avancealumno', raise_exception=True)
def change_avance_alumno(request, id):
    context = {}
    instance = AvanceAlumno.objects.get(id=id)
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
    instance = AvanceAlumno.objects.get(id=id)
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)


@login_required
@permission_required('fichas_alumnos.delete_bancotrabajo', raise_exception=True)
def delete_banco_trabajo(request, id):
    instance = BancoTrabajo.objects.get(id=id)
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)


@login_required
@permission_required('fichas_alumnos.delete_bancotrabajo', raise_exception=True)
def delete_banco_documento(request, id):
    instance = BancoDocumento.objects.get(id=id)
    rut = instance.alumno.rut
    instance.delete()

    return redirect('ficha_alumno', rut)
