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
from .forms import FormFichaAlumno, FormChangeFichaAlumno, FormAvanceAlumno, FormTrabajoAlumno, FormDocumentoAlumno, ApoderadoBaseFormSet, ListaEsperaBaseFormSet, FormDocumentoPautaCotejo, FormDatosPersonalesAlumno, FormDocumentoAnamnesis, FormDocumentoFonoaudiologica, FormDocumentoTecal, FormDocumentoSTSG, FormDocumentoTeprosif
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
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_hab_prag=True)
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
            }, datos_alumno=True, datos_hab_prag=True)
        except:
            pass
        
    context['form'] = FormDocumentoPautaCotejo

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)

        if form_base.is_valid():
            form = FormDocumentoPautaCotejo(request.POST)
            print(form_base)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))
                
                #Curso
                try:
                    alumn_curso = curso.nombre
                except:
                    alumn_curso = form_base.cleaned_data['curso']
                    if alumn_curso != None:
                        curso = Curso.objects.get(id=form_base.cleaned_data['curso'])
                        alumn_curso = curso.nombre

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'alumn_curso': alumn_curso if alumn_curso != None else "No asignado",
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
                    #response['Content-Disposition'] = content 
                    return response
        
        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoPautaCotejo(request.POST)

    return render(request, 'formularios/docs/form_cotejo_hab_prag.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_anamnesis(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_anamnesis=True)
    if rut:
        try:
            retirado = False
            alumno = FichaAlumno.objects.get(rut=rut)
            if alumno.curso:
                curso = alumno.curso
                nivel = Curso.objects.get(id=curso)
                nivel = nivel.nivel
            else:
                curso = ""
                try:
                    nivel = ListaEspera.objects.get(alumno=rut)
                    nivel = nivel.nivel
                except:
                    nivel = "1"
                    retirado = True
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
                'curso': curso,
                'nivel': nivel,
                'domicilio': alumno.direccion,
            }, datos_alumno=True, datos_anamnesis=True, datos_retirado=retirado)
        except:
            pass

    context['form'] = FormDocumentoAnamnesis

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_anamnesis=True)
        if form_base.is_valid():
            form = FormDocumentoAnamnesis(request.POST)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_curso': form_base.cleaned_data['curso'] if form_base.cleaned_data['curso'] != None else "No asignado",
                    'alumn_nivel': form_base.cleaned_data['nivel'] if form_base.cleaned_data['nivel'] != None else "No asignado",
                    'fecha_exam': fecha_hoy,
                }
                template = 'documentos/anamnesis.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "Anamnesis - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    #response['Content-Disposition'] = content 
                    return response
        
        if rut:
            form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_anamnesis=True, datos_retirado=retirado)
        else:
            form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_anamnesis=True)
        context['form'] = FormDocumentoAnamnesis(request.POST)

    return render(request, 'formularios/docs/form_anamnesis.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_tecal(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_hab_prag=True)
    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
            }, datos_alumno=True, datos_hab_prag=True)
        except:
            pass

    context['form'] = FormDocumentoTecal

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        if form_base.is_valid():
            form = FormDocumentoTecal(request.POST)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'alumn_edad': edad_anio,
                    'alumn_edad_mes': edad_mes,
                    'i1' : " " if form.cleaned_data['item1'] == 1  else form.cleaned_data["item1"] if form.cleaned_data["item1"] is not None else "NR",
                    'i2' : " " if form.cleaned_data['item2'] == 2  else form.cleaned_data["item2"] if form.cleaned_data["item2"] is not None else "NR",
                    'i3' : " " if form.cleaned_data['item3'] == 1  else form.cleaned_data["item3"] if form.cleaned_data["item3"] is not None else "NR",
                    'i4' : " " if form.cleaned_data['item4'] == 3  else form.cleaned_data["item4"] if form.cleaned_data["item4"] is not None else "NR",
                    'i5' : " " if form.cleaned_data['item5'] == 1  else form.cleaned_data["item5"] if form.cleaned_data["item5"] is not None else "NR",
                    'i6' : " " if form.cleaned_data['item6'] == 3  else form.cleaned_data["item6"] if form.cleaned_data["item6"] is not None else "NR",
                    'i7' : " " if form.cleaned_data['item7'] == 1  else form.cleaned_data["item7"] if form.cleaned_data["item7"] is not None else "NR",
                    'i8' : " " if form.cleaned_data['item8'] == 1  else form.cleaned_data["item8"] if form.cleaned_data["item8"] is not None else "NR",
                    'i9' : " " if form.cleaned_data['item9'] == 3  else form.cleaned_data["item9"] if form.cleaned_data["item9"] is not None else "NR",
                    'i10': " " if form.cleaned_data['item10'] == 2  else form.cleaned_data["item10"] if form.cleaned_data["item10"] is not None else "NR",
                    'i11': " " if form.cleaned_data['item11'] == 1  else form.cleaned_data["item11"] if form.cleaned_data["item11"] is not None else "NR",
                    'i12': " " if form.cleaned_data['item12'] == 3  else form.cleaned_data["item12"] if form.cleaned_data["item12"] is not None else "NR",
                    'i13': " " if form.cleaned_data['item13'] == 1  else form.cleaned_data["item13"] if form.cleaned_data["item13"] is not None else "NR",
                    'i14': " " if form.cleaned_data['item14'] == 2  else form.cleaned_data["item14"] if form.cleaned_data["item14"] is not None else "NR",
                    'i15': " " if form.cleaned_data['item15'] == 1  else form.cleaned_data["item15"] if form.cleaned_data["item15"] is not None else "NR",
                    'i16': " " if form.cleaned_data['item16'] == 3  else form.cleaned_data["item16"] if form.cleaned_data["item16"] is not None else "NR",
                    'i17': " " if form.cleaned_data['item17'] == 1  else form.cleaned_data["item17"] if form.cleaned_data["item17"] is not None else "NR",
                    'i18': " " if form.cleaned_data['item18'] == 2  else form.cleaned_data["item18"] if form.cleaned_data["item18"] is not None else "NR",
                    'i19': " " if form.cleaned_data['item19'] == 3  else form.cleaned_data["item19"] if form.cleaned_data["item19"] is not None else "NR",
                    'i20': " " if form.cleaned_data['item20'] == 1  else form.cleaned_data["item20"] if form.cleaned_data["item20"] is not None else "NR",
                    'i21': " " if form.cleaned_data['item21'] == 1  else form.cleaned_data["item21"] if form.cleaned_data["item21"] is not None else "NR",
                    'i22': " " if form.cleaned_data['item22'] == 3  else form.cleaned_data["item22"] if form.cleaned_data["item22"] is not None else "NR",
                    'i23': " " if form.cleaned_data['item23'] == 3  else form.cleaned_data["item23"] if form.cleaned_data["item23"] is not None else "NR",
                    'i24': " " if form.cleaned_data['item24'] == 2  else form.cleaned_data["item24"] if form.cleaned_data["item24"] is not None else "NR",
                    'i25': " " if form.cleaned_data['item25'] == 3  else form.cleaned_data["item25"] if form.cleaned_data["item25"] is not None else "NR",
                    'i26': " " if form.cleaned_data['item26'] == 4  else form.cleaned_data["item26"] if form.cleaned_data["item26"] is not None else "NR",
                    'i27': " " if form.cleaned_data['item27'] == 1  else form.cleaned_data["item27"] if form.cleaned_data["item27"] is not None else "NR",
                    'i28': " " if form.cleaned_data['item28'] == 2  else form.cleaned_data["item28"] if form.cleaned_data["item28"] is not None else "NR",
                    'i29': " " if form.cleaned_data['item29'] == 1  else form.cleaned_data["item29"] if form.cleaned_data["item29"] is not None else "NR",
                    'i30': " " if form.cleaned_data['item30'] == 1  else form.cleaned_data["item30"] if form.cleaned_data["item30"] is not None else "NR",
                    'i31': " " if form.cleaned_data['item31'] == 3  else form.cleaned_data["item31"] if form.cleaned_data["item31"] is not None else "NR",
                    'i32': " " if form.cleaned_data['item32'] == 3  else form.cleaned_data["item32"] if form.cleaned_data["item32"] is not None else "NR",
                    'i33': " " if form.cleaned_data['item33'] == 1  else form.cleaned_data["item33"] if form.cleaned_data["item33"] is not None else "NR",
                    'i34': " " if form.cleaned_data['item34'] == 2  else form.cleaned_data["item34"] if form.cleaned_data["item34"] is not None else "NR",
                    'i35': " " if form.cleaned_data['item35'] == 3  else form.cleaned_data["item35"] if form.cleaned_data["item35"] is not None else "NR",
                    'i36': " " if form.cleaned_data['item36'] == 2  else form.cleaned_data["item36"] if form.cleaned_data["item36"] is not None else "NR",
                    'i37': " " if form.cleaned_data['item37'] == 1  else form.cleaned_data["item37"] if form.cleaned_data["item37"] is not None else "NR",
                    'i38': " " if form.cleaned_data['item38'] == 1  else form.cleaned_data["item38"] if form.cleaned_data["item38"] is not None else "NR",
                    'i39': " " if form.cleaned_data['item39'] == 2  else form.cleaned_data["item39"] if form.cleaned_data["item39"] is not None else "NR",
                    'i40': " " if form.cleaned_data['item40'] == 3  else form.cleaned_data["item40"] if form.cleaned_data["item40"] is not None else "NR",
                    'i41': " " if form.cleaned_data['item41'] == 1  else form.cleaned_data["item41"] if form.cleaned_data["item41"] is not None else "NR",
                    'i42': " " if form.cleaned_data['item42'] == 2  else form.cleaned_data["item42"] if form.cleaned_data["item42"] is not None else "NR",
                    'i43': " " if form.cleaned_data['item43'] == 2  else form.cleaned_data["item43"] if form.cleaned_data["item43"] is not None else "NR",
                    'i44': " " if form.cleaned_data['item44'] == 1  else form.cleaned_data["item44"] if form.cleaned_data["item44"] is not None else "NR",
                    'i45': " " if form.cleaned_data['item45'] == 3  else form.cleaned_data["item45"] if form.cleaned_data["item45"] is not None else "NR",
                    'i46': " " if form.cleaned_data['item46'] == 2  else form.cleaned_data["item46"] if form.cleaned_data["item46"] is not None else "NR",
                    'i47': " " if form.cleaned_data['item47'] == 1  else form.cleaned_data["item47"] if form.cleaned_data["item47"] is not None else "NR",
                    'i48': " " if form.cleaned_data['item48'] == 2  else form.cleaned_data["item48"] if form.cleaned_data["item48"] is not None else "NR",
                    'i49': " " if form.cleaned_data['item49'] == 1  else form.cleaned_data["item49"] if form.cleaned_data["item49"] is not None else "NR",
                    'i50': " " if form.cleaned_data['item50'] == 1  else form.cleaned_data["item50"] if form.cleaned_data["item50"] is not None else "NR",
                    'i51': " " if form.cleaned_data['item51'] == 3  else form.cleaned_data["item51"] if form.cleaned_data["item51"] is not None else "NR",
                    'i52': " " if form.cleaned_data['item52'] == 2  else form.cleaned_data["item52"] if form.cleaned_data["item52"] is not None else "NR",
                    'i53': " " if form.cleaned_data['item53'] == 3  else form.cleaned_data["item53"] if form.cleaned_data["item53"] is not None else "NR",
                    'i54': " " if form.cleaned_data['item54'] == 2  else form.cleaned_data["item54"] if form.cleaned_data["item54"] is not None else "NR",
                    'i55': " " if form.cleaned_data['item55'] == 1  else form.cleaned_data["item55"] if form.cleaned_data["item55"] is not None else "NR",
                    'i56': " " if form.cleaned_data['item56'] == 2  else form.cleaned_data["item56"] if form.cleaned_data["item56"] is not None else "NR",
                    'i57': " " if form.cleaned_data['item57'] == 1  else form.cleaned_data["item57"] if form.cleaned_data["item57"] is not None else "NR",
                    'i58': " " if form.cleaned_data['item58'] == 1  else form.cleaned_data["item58"] if form.cleaned_data["item58"] is not None else "NR",
                    'i59': " " if form.cleaned_data['item59'] == 2  else form.cleaned_data["item59"] if form.cleaned_data["item59"] is not None else "NR",
                    'i60': " " if form.cleaned_data['item60'] == 1  else form.cleaned_data["item60"] if form.cleaned_data["item60"] is not None else "NR",
                    'i61': " " if form.cleaned_data['item61'] == 3  else form.cleaned_data["item61"] if form.cleaned_data["item61"] is not None else "NR",
                    'i62': " " if form.cleaned_data['item62'] == 3  else form.cleaned_data["item62"] if form.cleaned_data["item62"] is not None else "NR",
                    'i63': " " if form.cleaned_data['item63'] == 1  else form.cleaned_data["item63"] if form.cleaned_data["item63"] is not None else "NR",
                    'i64': " " if form.cleaned_data['item64'] == 1  else form.cleaned_data["item64"] if form.cleaned_data["item64"] is not None else "NR",
                    'i65': " " if form.cleaned_data['item65'] == 2  else form.cleaned_data["item65"] if form.cleaned_data["item65"] is not None else "NR",
                    'i66': " " if form.cleaned_data['item66'] == 1  else form.cleaned_data["item66"] if form.cleaned_data["item66"] is not None else "NR",
                    'i67': " " if form.cleaned_data['item67'] == 3  else form.cleaned_data["item67"] if form.cleaned_data["item67"] is not None else "NR",
                    'i68': " " if form.cleaned_data['item68'] == 1  else form.cleaned_data["item68"] if form.cleaned_data["item68"] is not None else "NR",
                    'i69': " " if form.cleaned_data['item69'] == 2  else form.cleaned_data["item69"] if form.cleaned_data["item69"] is not None else "NR",
                    'i70': " " if form.cleaned_data['item70'] == 1  else form.cleaned_data["item70"] if form.cleaned_data["item70"] is not None else "NR",
                    'i71': " " if form.cleaned_data['item71'] == 3  else form.cleaned_data["item71"] if form.cleaned_data["item71"] is not None else "NR",
                    'i72': " " if form.cleaned_data['item72'] == 2  else form.cleaned_data["item72"] if form.cleaned_data["item72"] is not None else "NR",
                    'i73': " " if form.cleaned_data['item73'] == 2  else form.cleaned_data["item73"] if form.cleaned_data["item73"] is not None else "NR",
                    'i74': " " if form.cleaned_data['item74'] == 3  else form.cleaned_data["item74"] if form.cleaned_data["item74"] is not None else "NR",
                    'i75': " " if form.cleaned_data['item75'] == 3  else form.cleaned_data["item75"] if form.cleaned_data["item75"] is not None else "NR",
                    'i76': " " if form.cleaned_data['item76'] == 3  else form.cleaned_data["item76"] if form.cleaned_data["item76"] is not None else "NR",
                    'i77': " " if form.cleaned_data['item77'] == 3  else form.cleaned_data["item77"] if form.cleaned_data["item77"] is not None else "NR",
                    'i78': " " if form.cleaned_data['item78'] == 1  else form.cleaned_data["item78"] if form.cleaned_data["item78"] is not None else "NR",
                    'i79': " " if form.cleaned_data['item79'] == 2  else form.cleaned_data["item79"] if form.cleaned_data["item79"] is not None else "NR",
                    'i80': " " if form.cleaned_data['item80'] == 1  else form.cleaned_data["item80"] if form.cleaned_data["item80"] is not None else "NR",
                    'i81': " " if form.cleaned_data['item81'] == 1  else form.cleaned_data["item81"] if form.cleaned_data["item81"] is not None else "NR",
                    'i82': " " if form.cleaned_data['item82'] == 3  else form.cleaned_data["item82"] if form.cleaned_data["item82"] is not None else "NR",
                    'i83': " " if form.cleaned_data['item83'] == 2  else form.cleaned_data["item83"] if form.cleaned_data["item83"] is not None else "NR",
                    'i84': " " if form.cleaned_data['item84'] == 3  else form.cleaned_data["item84"] if form.cleaned_data["item84"] is not None else "NR",
                    'i85': " " if form.cleaned_data['item85'] == 2  else form.cleaned_data["item85"] if form.cleaned_data["item85"] is not None else "NR",
                    'i86': " " if form.cleaned_data['item86'] == 2  else form.cleaned_data["item86"] if form.cleaned_data["item86"] is not None else "NR",
                    'i87': " " if form.cleaned_data['item87'] == 1  else form.cleaned_data["item87"] if form.cleaned_data["item87"] is not None else "NR",
                    'i88': " " if form.cleaned_data['item88'] == 3  else form.cleaned_data["item88"] if form.cleaned_data["item88"] is not None else "NR",
                    'i89': " " if form.cleaned_data['item89'] == 1  else form.cleaned_data["item89"] if form.cleaned_data["item89"] is not None else "NR",
                    'i90': " " if form.cleaned_data['item90'] == 1  else form.cleaned_data["item90"] if form.cleaned_data["item90"] is not None else "NR",
                    'i91': " " if form.cleaned_data['item91'] == 2  else form.cleaned_data["item91"] if form.cleaned_data["item91"] is not None else "NR",
                    'i92': " " if form.cleaned_data['item92'] == 1  else form.cleaned_data["item92"] if form.cleaned_data["item92"] is not None else "NR",
                    'i93': " " if form.cleaned_data['item93'] == 1  else form.cleaned_data["item93"] if form.cleaned_data["item93"] is not None else "NR",
                    'i94': " " if form.cleaned_data['item94'] == 3  else form.cleaned_data["item94"] if form.cleaned_data["item94"] is not None else "NR",
                    'i95': " " if form.cleaned_data['item95'] == 2  else form.cleaned_data["item95"] if form.cleaned_data["item95"] is not None else "NR",
                    'i96': " " if form.cleaned_data['item96'] == 1  else form.cleaned_data["item96"] if form.cleaned_data["item96"] is not None else "NR",
                    'i97': " " if form.cleaned_data['item97'] == 3  else form.cleaned_data["item97"] if form.cleaned_data["item97"] is not None else "NR",
                    'i98': " " if form.cleaned_data['item98'] == 3  else form.cleaned_data["item98"] if form.cleaned_data["item98"] is not None else "NR",
                    'i99': " " if form.cleaned_data['item99'] == 2  else form.cleaned_data["item99"] if form.cleaned_data["item99"] is not None else "NR",
                    'i100': " " if form.cleaned_data['item100'] == 2  else form.cleaned_data["item100"] if form.cleaned_data["item100"] is not None else "NR",
                    'i101': " " if form.cleaned_data['item101'] == 1  else form.cleaned_data["item101"] if form.cleaned_data["item101"] is not None else "NR",

                    'calif1' : "✔" if form.cleaned_data['item1'] == 1 else "O",
                    'calif2' : "✔" if form.cleaned_data['item2'] == 2 else "O",
                    'calif3' : "✔" if form.cleaned_data['item3'] == 1 else "O",
                    'calif4' : "✔" if form.cleaned_data['item4'] == 3 else "O",
                    'calif5' : "✔" if form.cleaned_data['item5'] == 1 else "O",
                    'calif6' : "✔" if form.cleaned_data['item6'] == 3 else "O",
                    'calif7' : "✔" if form.cleaned_data['item7'] == 1 else "O",
                    'calif8' : "✔" if form.cleaned_data['item8'] == 1 else "O",
                    'calif9' : "✔" if form.cleaned_data['item9'] == 3 else "O",
                    'calif10': "✔" if form.cleaned_data['item10'] == 2 else "O",
                    'calif11': "✔" if form.cleaned_data['item11'] == 1 else "O",
                    'calif12': "✔" if form.cleaned_data['item12'] == 3 else "O",
                    'calif13': "✔" if form.cleaned_data['item13'] == 1 else "O",
                    'calif14': "✔" if form.cleaned_data['item14'] == 2 else "O",
                    'calif15': "✔" if form.cleaned_data['item15'] == 1 else "O",
                    'calif16': "✔" if form.cleaned_data['item16'] == 3 else "O",
                    'calif17': "✔" if form.cleaned_data['item17'] == 1 else "O",
                    'calif18': "✔" if form.cleaned_data['item18'] == 2 else "O",
                    'calif19': "✔" if form.cleaned_data['item19'] == 3 else "O",
                    'calif20': "✔" if form.cleaned_data['item20'] == 1 else "O",
                    'calif21': "✔" if form.cleaned_data['item21'] == 1 else "O",
                    'calif22': "✔" if form.cleaned_data['item22'] == 3 else "O",
                    'calif23': "✔" if form.cleaned_data['item23'] == 3 else "O",
                    'calif24': "✔" if form.cleaned_data['item24'] == 2 else "O",
                    'calif25': "✔" if form.cleaned_data['item25'] == 3 else "O",
                    'calif26': "✔" if form.cleaned_data['item26'] == 4 else "O",
                    'calif27': "✔" if form.cleaned_data['item27'] == 1 else "O",
                    'calif28': "✔" if form.cleaned_data['item28'] == 2 else "O",
                    'calif29': "✔" if form.cleaned_data['item29'] == 1 else "O",
                    'calif30': "✔" if form.cleaned_data['item30'] == 1 else "O",
                    'calif31': "✔" if form.cleaned_data['item31'] == 3 else "O",
                    'calif32': "✔" if form.cleaned_data['item32'] == 3 else "O",
                    'calif33': "✔" if form.cleaned_data['item33'] == 1 else "O",
                    'calif34': "✔" if form.cleaned_data['item34'] == 2 else "O",
                    'calif35': "✔" if form.cleaned_data['item35'] == 3 else "O",
                    'calif36': "✔" if form.cleaned_data['item36'] == 2 else "O",
                    'calif37': "✔" if form.cleaned_data['item37'] == 1 else "O",
                    'calif38': "✔" if form.cleaned_data['item38'] == 1 else "O",
                    'calif39': "✔" if form.cleaned_data['item39'] == 2 else "O",
                    'calif40': "✔" if form.cleaned_data['item40'] == 3 else "O",
                    'calif41': "✔" if form.cleaned_data['item41'] == 1 else "O",
                    'calif42': "✔" if form.cleaned_data['item42'] == 2 else "O",
                    'calif43': "✔" if form.cleaned_data['item43'] == 2 else "O",
                    'calif44': "✔" if form.cleaned_data['item44'] == 1 else "O",
                    'calif45': "✔" if form.cleaned_data['item45'] == 3 else "O",
                    'calif46': "✔" if form.cleaned_data['item46'] == 2 else "O",
                    'calif47': "✔" if form.cleaned_data['item47'] == 1 else "O",
                    'calif48': "✔" if form.cleaned_data['item48'] == 2 else "O",
                    'calif49': "✔" if form.cleaned_data['item49'] == 1 else "O",
                    'calif50': "✔" if form.cleaned_data['item50'] == 1 else "O",
                    'calif51': "✔" if form.cleaned_data['item51'] == 3 else "O",
                    'calif52': "✔" if form.cleaned_data['item52'] == 2 else "O",
                    'calif53': "✔" if form.cleaned_data['item53'] == 3 else "O",
                    'calif54': "✔" if form.cleaned_data['item54'] == 2 else "O",
                    'calif55': "✔" if form.cleaned_data['item55'] == 1 else "O",
                    'calif56': "✔" if form.cleaned_data['item56'] == 2 else "O",
                    'calif57': "✔" if form.cleaned_data['item57'] == 1 else "O",
                    'calif58': "✔" if form.cleaned_data['item58'] == 1 else "O",
                    'calif59': "✔" if form.cleaned_data['item59'] == 2 else "O",
                    'calif60': "✔" if form.cleaned_data['item60'] == 1 else "O",
                    'calif61': "✔" if form.cleaned_data['item61'] == 3 else "O",
                    'calif62': "✔" if form.cleaned_data['item62'] == 3 else "O",
                    'calif63': "✔" if form.cleaned_data['item63'] == 1 else "O",
                    'calif64': "✔" if form.cleaned_data['item64'] == 1 else "O",
                    'calif65': "✔" if form.cleaned_data['item65'] == 2 else "O",
                    'calif66': "✔" if form.cleaned_data['item66'] == 1 else "O",
                    'calif67': "✔" if form.cleaned_data['item67'] == 3 else "O",
                    'calif68': "✔" if form.cleaned_data['item68'] == 1 else "O",
                    'calif69': "✔" if form.cleaned_data['item69'] == 2 else "O",
                    'calif70': "✔" if form.cleaned_data['item70'] == 1 else "O",
                    'calif71': "✔" if form.cleaned_data['item71'] == 3 else "O",
                    'calif72': "✔" if form.cleaned_data['item72'] == 2 else "O",
                    'calif73': "✔" if form.cleaned_data['item73'] == 2 else "O",
                    'calif74': "✔" if form.cleaned_data['item74'] == 3 else "O",
                    'calif75': "✔" if form.cleaned_data['item75'] == 3 else "O",
                    'calif76': "✔" if form.cleaned_data['item76'] == 3 else "O",
                    'calif77': "✔" if form.cleaned_data['item77'] == 3 else "O",
                    'calif78': "✔" if form.cleaned_data['item78'] == 1 else "O",
                    'calif79': "✔" if form.cleaned_data['item79'] == 2 else "O",
                    'calif80': "✔" if form.cleaned_data['item80'] == 1 else "O",
                    'calif81': "✔" if form.cleaned_data['item81'] == 1 else "O",
                    'calif82': "✔" if form.cleaned_data['item82'] == 3 else "O",
                    'calif83': "✔" if form.cleaned_data['item83'] == 2 else "O",
                    'calif84': "✔" if form.cleaned_data['item84'] == 3 else "O",
                    'calif85': "✔" if form.cleaned_data['item85'] == 2 else "O",
                    'calif86': "✔" if form.cleaned_data['item86'] == 2 else "O",
                    'calif87': "✔" if form.cleaned_data['item87'] == 1 else "O",
                    'calif88': "✔" if form.cleaned_data['item88'] == 3 else "O",
                    'calif89': "✔" if form.cleaned_data['item89'] == 1 else "O",
                    'calif90': "✔" if form.cleaned_data['item90'] == 1 else "O",
                    'calif91': "✔" if form.cleaned_data['item91'] == 2 else "O",
                    'calif92': "✔" if form.cleaned_data['item92'] == 1 else "O",
                    'calif93': "✔" if form.cleaned_data['item93'] == 1 else "O",
                    'calif94': "✔" if form.cleaned_data['item94'] == 3 else "O",
                    'calif95': "✔" if form.cleaned_data['item95'] == 2 else "O",
                    'calif96': "✔" if form.cleaned_data['item96'] == 1 else "O",
                    'calif97': "✔" if form.cleaned_data['item97'] == 3 else "O",
                    'calif98': "✔" if form.cleaned_data['item98'] == 3 else "O",
                    'calif99': "✔" if form.cleaned_data['item99'] == 2 else "O",
                    'calif100': "✔" if form.cleaned_data['item100'] == 2 else "O",
                    'calif101': "✔" if form.cleaned_data['item101'] == 1 else "O",
                }
                template = 'documentos/tecal.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "Tecal - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    #response['Content-Disposition'] = content 
                    return response
        
        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoTecal(request.POST)

    return render(request, 'formularios/docs/form_tecal.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_teprosif(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_teprosif=True)
    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
                'sexo': 'Femenino'
            }, datos_alumno=True, datos_teprosif=True)
        except:
            pass

    context['form'] = FormDocumentoTeprosif

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_teprosif=True)
        if form_base.is_valid():
            form = FormDocumentoTeprosif(request.POST)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_sexo': form_base.cleaned_data['sexo'],
                    'fecha_exam': fecha_hoy,
                }
                template = 'documentos/TEPROSIF-R.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "Hoja de rerspuesta TEPROSIF-R - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    #response['Content-Disposition'] = content 
                    return response

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_teprosif=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_teprosif=True)
        context['form'] = FormDocumentoTeprosif(request.POST)

    return render(request, 'formularios/docs/form_teprosif.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_fonoaudiologica(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_fonoaudio=True)
    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
                'rut': alumno.rut,
                'domicilio': alumno.direccion,
            }, datos_alumno=True, datos_fonoaudio=True)
        except:
            pass
        
    context['form'] = FormDocumentoFonoaudiologica

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_fonoaudio=True)
        if form_base.is_valid():
            form = FormDocumentoFonoaudiologica(request.POST)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'fecha_exam': fecha_hoy,
                }
                template = 'documentos/pauta_fono_palabritas.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "Observación clínica fonoaudiológica - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    #response['Content-Disposition'] = content 
                    return response

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_fonoaudio=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_fonoaudio=True)
        context['form'] = FormDocumentoPautaCotejo(request.POST)
    
    return render(request, 'formularios/docs/form_fonoaudiologica.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_stsg(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_hab_prag=True)

    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            context['form_base'] = FormDatosPersonalesAlumno(data={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
            }, datos_alumno=True, datos_hab_prag=True)
        except:
            pass

    context['form'] = FormDocumentoSTSG

    if request.method == 'POST':
        form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        if form_base.is_valid():
            form = FormDocumentoSTSG(request.POST)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))

                #Cálculo puntajes
                #Subprueba Receptiva
                rec_puntaje = 0
                res_rec = [val for key, val in form.cleaned_data.items() if 'rec_' in key]
                rec_puntaje = res_rec.count(True)

                #Subprueba Expresiva
                exp_puntaje = 0
                exp_rec = [val for key, val in form.cleaned_data.items() if 'exp_' in key]
                exp_puntaje = exp_rec.count(True)

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'fecha_exam': fecha_hoy,
                    'rec_uno_prim': "✔" if form.cleaned_data['rec_uno_prim'] == True else "O",
                    'rec_uno_segu': "✔" if form.cleaned_data['rec_uno_segu'] == True else "O",
                    'rec_dos_prim': "✔" if form.cleaned_data['rec_dos_prim'] == True else "O",
                    'rec_dos_segu': "✔" if form.cleaned_data['rec_dos_segu'] == True else "O",
                    'rec_tres_prim': "✔" if form.cleaned_data['rec_tres_prim'] == True else "O",
                    'rec_tres_segu': "✔" if form.cleaned_data['rec_tres_segu'] == True else "O",
                    'rec_cuatro_prim': "✔" if form.cleaned_data['rec_cuatro_prim'] == True else "O",
                    'rec_cuatro_segu': "✔" if form.cleaned_data['rec_cuatro_segu'] == True else "O",
                    'rec_cinco_prim': "✔" if form.cleaned_data['rec_cinco_prim'] == True else "O",
                    'rec_cinco_segu': "✔" if form.cleaned_data['rec_cinco_segu'] == True else "O",
                    'rec_seis_prim': "✔" if form.cleaned_data['rec_seis_prim'] == True else "O",
                    'rec_seis_segu': "✔" if form.cleaned_data['rec_seis_segu'] == True else "O",
                    'rec_siete_prim': "✔" if form.cleaned_data['rec_siete_prim'] == True else "O",
                    'rec_siete_segu': "✔" if form.cleaned_data['rec_siete_segu'] == True else "O",
                    'rec_ocho_prim': "✔" if form.cleaned_data['rec_ocho_prim'] == True else "O",
                    'rec_ocho_segu': "✔" if form.cleaned_data['rec_ocho_segu'] == True else "O",
                    'rec_nueve_prim': "✔" if form.cleaned_data['rec_nueve_prim'] == True else "O",
                    'rec_nueve_segu': "✔" if form.cleaned_data['rec_nueve_segu'] == True else "O",
                    'rec_diez_prim': "✔" if form.cleaned_data['rec_diez_prim'] == True else "O",
                    'rec_diez_segu': "✔" if form.cleaned_data['rec_diez_segu'] == True else "O",
                    'rec_once_prim': "✔" if form.cleaned_data['rec_once_prim'] == True else "O",
                    'rec_once_segu': "✔" if form.cleaned_data['rec_once_segu'] == True else "O",
                    'rec_doce_prim': "✔" if form.cleaned_data['rec_doce_prim'] == True else "O",
                    'rec_doce_segu': "✔" if form.cleaned_data['rec_doce_segu'] == True else "O",
                    'rec_trece_prim': "✔" if form.cleaned_data['rec_trece_prim'] == True else "O",
                    'rec_trece_segu': "✔" if form.cleaned_data['rec_trece_segu'] == True else "O",
                    'rec_catorce_prim': "✔" if form.cleaned_data['rec_catorce_prim'] == True else "O",
                    'rec_catorce_segu': "✔" if form.cleaned_data['rec_catorce_segu'] == True else "O",
                    'rec_quince_prim': "✔" if form.cleaned_data['rec_quince_prim'] == True else "O",
                    'rec_quince_segu': "✔" if form.cleaned_data['rec_quince_segu'] == True else "O",
                    'rec_dieciseis_prim': "✔" if form.cleaned_data['rec_dieciseis_prim'] == True else "O",
                    'rec_dieciseis_segu': "✔" if form.cleaned_data['rec_dieciseis_segu'] == True else "O",
                    'rec_diecisiete_prim': "✔" if form.cleaned_data['rec_diecisiete_prim'] == True else "O",
                    'rec_diecisiete_segu': "✔" if form.cleaned_data['rec_diecisiete_segu'] == True else "O",
                    'rec_dieciocho_prim': "✔" if form.cleaned_data['rec_dieciocho_prim'] == True else "O",
                    'rec_dieciocho_segu': "✔" if form.cleaned_data['rec_dieciocho_segu'] == True else "O",
                    'rec_diecinueve_prim': "✔" if form.cleaned_data['rec_diecinueve_prim'] == True else "O",
                    'rec_diecinueve_segu': "✔" if form.cleaned_data['rec_diecinueve_segu'] == True else "O",
                    'rec_veinte_prim': "✔" if form.cleaned_data['rec_veinte_prim'] == True else "O",
                    'rec_veinte_segu': "✔" if form.cleaned_data['rec_veinte_segu'] == True else "O",
                    'rec_veintiuno_prim': "✔" if form.cleaned_data['rec_veintiuno_prim'] == True else "O",
                    'rec_veintiuno_segu': "✔" if form.cleaned_data['rec_veintiuno_segu'] == True else "O",
                    'rec_veintidos_prim': "✔" if form.cleaned_data['rec_veintidos_prim'] == True else "O",
                    'rec_veintidos_segu': "✔" if form.cleaned_data['rec_veintidos_segu'] == True else "O",
                    'rec_veintitres_prim': "✔" if form.cleaned_data['rec_veintitres_prim'] == True else "O",
                    'rec_veintitres_segu': "✔" if form.cleaned_data['rec_veintitres_segu'] == True else "O",
                    'rec_puntaje': rec_puntaje,
                    'rec_observac': form.cleaned_data['rec_observac'],
                    'exp_uno_prim': "✔" if form.cleaned_data['exp_uno_prim'] == True else "O",
                    'exp_uno_segu': "✔" if form.cleaned_data['exp_uno_segu'] == True else "O",
                    'exp_dos_prim': "✔" if form.cleaned_data['exp_dos_prim'] == True else "O",
                    'exp_dos_segu': "✔" if form.cleaned_data['exp_dos_segu'] == True else "O",
                    'exp_tres_prim': "✔" if form.cleaned_data['exp_tres_prim'] == True else "O",
                    'exp_tres_segu': "✔" if form.cleaned_data['exp_tres_segu'] == True else "O",
                    'exp_cuatro_prim': "✔" if form.cleaned_data['exp_cuatro_prim'] == True else "O",
                    'exp_cuatro_segu': "✔" if form.cleaned_data['exp_cuatro_segu'] == True else "O",
                    'exp_cinco_prim': "✔" if form.cleaned_data['exp_cinco_prim'] == True else "O",
                    'exp_cinco_segu': "✔" if form.cleaned_data['exp_cinco_segu'] == True else "O",
                    'exp_seis_prim': "✔" if form.cleaned_data['exp_seis_prim'] == True else "O",
                    'exp_seis_segu': "✔" if form.cleaned_data['exp_seis_segu'] == True else "O",
                    'exp_siete_prim': "✔" if form.cleaned_data['exp_siete_prim'] == True else "O",
                    'exp_siete_segu': "✔" if form.cleaned_data['exp_siete_segu'] == True else "O",
                    'exp_ocho_prim': "✔" if form.cleaned_data['exp_ocho_prim'] == True else "O",
                    'exp_ocho_segu': "✔" if form.cleaned_data['exp_ocho_segu'] == True else "O",
                    'exp_nueve_prim': "✔" if form.cleaned_data['exp_nueve_prim'] == True else "O",
                    'exp_nueve_segu': "✔" if form.cleaned_data['exp_nueve_segu'] == True else "O",
                    'exp_diez_prim': "✔" if form.cleaned_data['exp_diez_prim'] == True else "O",
                    'exp_diez_segu': "✔" if form.cleaned_data['exp_diez_segu'] == True else "O",
                    'exp_once_prim': "✔" if form.cleaned_data['exp_once_prim'] == True else "O",
                    'exp_once_segu': "✔" if form.cleaned_data['exp_once_segu'] == True else "O",
                    'exp_doce_prim': "✔" if form.cleaned_data['exp_doce_prim'] == True else "O",
                    'exp_doce_segu': "✔" if form.cleaned_data['exp_doce_segu'] == True else "O",
                    'exp_trece_prim': "✔" if form.cleaned_data['exp_trece_prim'] == True else "O",
                    'exp_trece_segu': "✔" if form.cleaned_data['exp_trece_segu'] == True else "O",
                    'exp_catorce_prim': "✔" if form.cleaned_data['exp_catorce_prim'] == True else "O",
                    'exp_catorce_segu': "✔" if form.cleaned_data['exp_catorce_segu'] == True else "O",
                    'exp_quince_prim': "✔" if form.cleaned_data['exp_quince_prim'] == True else "O",
                    'exp_quince_segu': "✔" if form.cleaned_data['exp_quince_segu'] == True else "O",
                    'exp_dieciseis_prim': "✔" if form.cleaned_data['exp_dieciseis_prim'] == True else "O",
                    'exp_dieciseis_segu': "✔" if form.cleaned_data['exp_dieciseis_segu'] == True else "O",
                    'exp_diecisiete_prim': "✔" if form.cleaned_data['exp_diecisiete_prim'] == True else "O",
                    'exp_diecisiete_segu': "✔" if form.cleaned_data['exp_diecisiete_segu'] == True else "O",
                    'exp_dieciocho_prim': "✔" if form.cleaned_data['exp_dieciocho_prim'] == True else "O",
                    'exp_dieciocho_segu': "✔" if form.cleaned_data['exp_dieciocho_segu'] == True else "O",
                    'exp_diecinueve_prim': "✔" if form.cleaned_data['exp_diecinueve_prim'] == True else "O",
                    'exp_diecinueve_segu': "✔" if form.cleaned_data['exp_diecinueve_segu'] == True else "O",
                    'exp_veinte_prim': "✔" if form.cleaned_data['exp_veinte_prim'] == True else "O",
                    'exp_veinte_segu': "✔" if form.cleaned_data['exp_veinte_segu'] == True else "O",
                    'exp_veintiuno_prim': "✔" if form.cleaned_data['exp_veintiuno_prim'] == True else "O",
                    'exp_veintiuno_segu': "✔" if form.cleaned_data['exp_veintiuno_segu'] == True else "O",
                    'exp_veintidos_prim': "✔" if form.cleaned_data['exp_veintidos_prim'] == True else "O",
                    'exp_veintidos_segu': "✔" if form.cleaned_data['exp_veintidos_segu'] == True else "O",
                    'exp_veintitres_prim': "✔" if form.cleaned_data['exp_veintitres_prim'] == True else "O",
                    'exp_veintitres_segu': "✔" if form.cleaned_data['exp_veintitres_segu'] == True else "O",
                    'exp_puntaje': exp_puntaje,
                    'exp_observac': form.cleaned_data['exp_observac'],
                }
                template = 'documentos/STSG_Hoja_de_Respuestas.html'
                pdf = render_to_pdf(template, data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf') 
                    filename = "STSG - %s.pdf" %(data['alumn_nombre'])
                    content = 'attachment; filename="{}"'.format(filename)
                    #response['Content-Disposition'] = content 
                    return response

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoSTSG(request.POST)

    return render(request, 'formularios/docs/form_stsg.html', context)
