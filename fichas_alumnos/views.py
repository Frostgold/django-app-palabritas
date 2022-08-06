from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.views.generic import View
import datetime

from cursos.models import Curso, BancoTrabajo as BancoTrabajoCurso
from lista_espera.models import ListaEspera
from .models import FichaAlumno, BancoDocumento, BancoTrabajo, AvanceAlumno, DetalleApoderado
from .forms import FormFichaAlumno, FormChangeFichaAlumno, FormAvanceAlumno, FormTrabajoAlumno, FormDocumentoAlumno, ApoderadoBaseFormSet, ListaEsperaBaseFormSet, DocumentoPautaCotejo, FormDatosPersonalesAlumno, FormDocumentoAnamnesis
from .utils import render_to_pdf

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

    alumno = FichaAlumno.objects.filter(rut=rut).first()

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
                context['trabajoscurso'] = BancoTrabajoCurso.objects.filter(curso=alumno.curso)

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
    context['trabajoscurso'] = BancoTrabajoCurso.objects.filter(curso=alumno.curso)

    if not context['ficha']:
        return redirect('listado_fichas_alumnos')

    context['rut_alumno'] = rut

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


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_cotejo_hab_prag(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_hab_prag=False)
    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            if alumno.curso:
                curso = alumno.curso
            else:
                curso = ""
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
                'curso': curso,
            }, datos_hab_prag=True)
        except:
            pass
        
    context['form'] = DocumentoPautaCotejo

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_hab_prag=True)

        if form_base.is_valid():
            form = DocumentoPautaCotejo(request.POST)
            print(form_base)
            if form.is_valid():
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))
                print(edad_mes)
                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'alumn_curso': form_base.cleaned_data['curso'] if form_base.cleaned_data['curso'] != None else "No asignado",
                    'fecha_exam': fecha_hoy,
                    'cinetica_S': "X" if form.cleaned_data['cinetica'] == "si" else "",
                    'cinetica_N': "X" if form.cleaned_data['cinetica'] == "no" else "",
                    'cinetica_AV': "X" if form.cleaned_data['cinetica'] == "av" else "",
                    'proxe_S': "X" if form.cleaned_data['proxemica'] == "si" else "",
                    'proxe_N': "X" if form.cleaned_data['proxemica'] == "no" else "",
                    'proxe_AV': "X" if form.cleaned_data['proxemica'] == "av" else "",
                    'inten_S': "X" if form.cleaned_data['intencion'] == "si" else "",
                    'inten_N': "X" if form.cleaned_data['intencion'] == "no" else "",
                    'inten_AV': "X" if form.cleaned_data['intencion'] == "av" else "",
                    'contac_S': "X" if form.cleaned_data['cont_visual'] == "si" else "",
                    'contac_N': "X" if form.cleaned_data['cont_visual'] == "no" else "",
                    'contac_AV': "X" if form.cleaned_data['cont_visual'] == "av" else "",
                    'expres_S': "X" if form.cleaned_data['exp_facial'] == "si" else "",
                    'expres_N': "X" if form.cleaned_data['exp_facial'] == "no" else "",
                    'expres_AV': "X" if form.cleaned_data['exp_facial'] == "av" else "",
                    'facult_S': "X" if form.cleaned_data['fac_conversacional'] == "si" else "",
                    'facult_N': "X" if form.cleaned_data['fac_conversacional'] == "no" else "",
                    'facult_AV': "X" if form.cleaned_data['fac_conversacional'] == "av" else "",
                    'varia_S': "X" if form.cleaned_data['var_estilisticas'] == "si" else "",
                    'varia_N': "X" if form.cleaned_data['var_estilisticas'] == "no" else "",
                    'varia_AV': "X" if form.cleaned_data['var_estilisticas'] == "av" else "",
                    'alter_S': "X" if form.cleaned_data['alt_reciproca'] == "si" else "",
                    'alter_N': "X" if form.cleaned_data['alt_reciproca'] == "no" else "",
                    'alter_AV': "X" if form.cleaned_data['alt_reciproca'] == "av" else "",
                    'temat_S': "X" if form.cleaned_data['tematizacion'] == "si" else "",
                    'temat_N': "X" if form.cleaned_data['tematizacion'] == "no" else "",
                    'temat_AV': "X" if form.cleaned_data['tematizacion'] == "av" else "",
                    'petic_S': "X" if form.cleaned_data['peticiones'] == "si" else "",
                    'petic_N': "X" if form.cleaned_data['peticiones'] == "no" else "",
                    'petic_AV': "X" if form.cleaned_data['peticiones'] == "av" else "",
                    'aclar_S': "X" if form.cleaned_data['aclar_rep'] == "si" else "",
                    'aclar_N': "X" if form.cleaned_data['aclar_rep'] == "no" else "",
                    'aclar_AV': "X" if form.cleaned_data['aclar_rep'] == "av" else "",
                }
                template = 'documentos/PautadeCotejohabilidadespragmticas.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "Cotejo Habilidades Pragmáticas - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    response['Content-Disposition'] = content 
                    return response
        
        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_hab_prag=False)
        context['form'] = DocumentoPautaCotejo(request.POST)

    return render(request, 'formularios/docs/form_cotejo_hab_prag.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_anamnesis(request, *rut):
    context = {}
    context['form'] = FormDocumentoAnamnesis

    return render(request, 'formularios/docs/form_anamnesis.html', context)
