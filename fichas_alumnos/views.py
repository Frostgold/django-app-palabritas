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
from .forms import FormFichaAlumno, FormChangeFichaAlumno, FormAvanceAlumno, FormTrabajoAlumno, FormDocumentoAlumno, ApoderadoBaseFormSet, ListaEsperaBaseFormSet, FormDocumentoPautaCotejo, FormDatosPersonalesAlumno, FormDocumentoAnamnesis, FormDocumentoFonoaudiologica, FormDocumentoTecal, FormDocumentoSTSG, FormDocumentoTeprosif, FormDocumentoFinalTeprosif, FormTecalConfirmacion
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
                context['trabajoscurso'] = BancoTrabajoCurso.objects.filter(curso=alumno.alumno.curso)

                return render(request, 'ficha_alumno.html', context)

        return redirect('listado_fichas_alumnos')

    context['avance_form'] = FormAvanceAlumno
    context['trabajo_form'] = FormTrabajoAlumno
    context['documento_form'] = FormDocumentoAlumno
    context['ficha'] = FichaAlumno.objects.filter(rut=rut)
    if not context['ficha']:
        return redirect('listado_fichas_alumnos')
    context['apoderado'] = DetalleApoderado.objects.filter(alumno=rut)
    context['avances'] = AvanceAlumno.objects.filter(alumno=rut).order_by('-id')
    context['trabajos'] = BancoTrabajo.objects.filter(alumno=rut).order_by('-id')
    context['documentos'] = BancoDocumento.objects.filter(alumno=rut).order_by('-id')
    context['trabajoscurso'] = BancoTrabajoCurso.objects.filter(curso=alumno.curso)


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
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'alumn_curso': alumn_curso if alumn_curso != None else "No asignado",
                    'fecha_exam': fecha_hoy.strftime("%d/%m/%Y"),
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

                request.session['pdf_hab_prag'] = data
                return redirect('listado_fichas_alumnos')
        
        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoPautaCotejo(request.POST)

    return render(request, 'formularios/docs/form_cotejo_hab_prag.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_hab_prag(request):
    try:
        if request.session['pdf_hab_prag']:
            data = request.session['pdf_hab_prag']
            del request.session['pdf_hab_prag']

            template = 'documentos/PautadeCotejohabilidadespragmticas.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "Cotejo Habilidades Pragmáticas - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content 
            return response
    except:
        return redirect('listado_fichas_alumnos')


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
                nivel = nivel.nivel_id
            else:
                curso = ""
                try:
                    nivel = ListaEspera.objects.get(alumno=rut)
                    nivel = nivel.nivel_id
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
        post = request.POST.copy()
        if not 'nivel' in post:
            post['nivel'] = nivel
        
        form_base = FormDatosPersonalesAlumno(post, datos_alumno=True, datos_anamnesis=True)
        if form_base.is_valid():
            form = FormDocumentoAnamnesis(post)
            if form.is_valid():
                #Calculo fecha y edad
                fecha_hoy = datetime.date.today()
                fecha_nac = form_base.cleaned_data['fech_nac']
                edad_anio = fecha_hoy.year - fecha_nac.year - ((fecha_hoy.month, fecha_hoy.day) < (fecha_nac.month, fecha_nac.day))
                edad_mes = fecha_hoy.month - fecha_nac.month - ((fecha_hoy.day) < (fecha_nac.day))
                edad_mes = edad_mes if edad_mes >= 0 else (12 - (edad_mes*-1))
                domicilio = form_base.cleaned_data['domicilio']
                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_curso': form_base.cleaned_data['curso'] if form_base.cleaned_data['curso'] != None else "No asignado",
                    'alumn_nivel': "{}".format(form_base.cleaned_data['nivel']) if form_base.cleaned_data['nivel'] != None else "No asignado",
                    'fecha_exam': fecha_hoy.strftime("%d/%m/%Y"),
                    'domicilio': domicilio,
                    'esco_actual': form.cleaned_data['esco_actual'] if form.cleaned_data['esco_actual'] != "" else "-",
                    'histo_esco': form.cleaned_data['histo_esco'] if form.cleaned_data['histo_esco'] != "" else "-",
                    'nom_entrevis': form.cleaned_data['nom_entrevis'] if form.cleaned_data['nom_entrevis'] != "" else "-",
                    'esco_actual': form.cleaned_data['esco_actual'] if form.cleaned_data['esco_actual'] != "" else "-",
                    'datos_propor': form.cleaned_data['datos_propor'] if form.cleaned_data['datos_propor'] != "" else "-",

                    'nom_familiar_uno' : form.cleaned_data['nom_familiar_uno'] if form.cleaned_data['nom_familiar_uno'] != "" else "-",
                    'nom_familiar_dos' : form.cleaned_data['nom_familiar_dos'] if form.cleaned_data['nom_familiar_dos'] != "" else "-",
                    'nom_familiar_tres' : form.cleaned_data['nom_familiar_tres'] if form.cleaned_data['nom_familiar_tres'] != "" else "-",
                    'nom_familiar_cua' : form.cleaned_data['nom_familiar_cua'] if form.cleaned_data['nom_familiar_cua'] != "" else "-",
                    'nom_familiar_cin' : form.cleaned_data['nom_familiar_cin'] if form.cleaned_data['nom_familiar_cin'] != "" else "-",
                    
                    'parent_uno' : form.cleaned_data['parent_uno'],
                    'parent_dos' : form.cleaned_data['parent_dos'],
                    'parent_tres' : form.cleaned_data['parent_tres'],
                    'parent_cua' : form.cleaned_data['parent_cua'],
                    'parent_cin' : form.cleaned_data['parent_cin'],
                    
                    'edad_familiar_uno' : form.cleaned_data['edad_familiar_uno'] if form.cleaned_data['edad_familiar_uno'] is not None else "-",
                    'edad_familiar_dos' : form.cleaned_data['edad_familiar_dos'] if form.cleaned_data['edad_familiar_dos'] is not None else "-",
                    'edad_familiar_tres' : form.cleaned_data['edad_familiar_tres'] if form.cleaned_data['edad_familiar_tres'] is not None else "-",
                    'edad_familiar_cua' : form.cleaned_data['edad_familiar_cua'] if form.cleaned_data['edad_familiar_cua'] is not None else "-",
                    'edad_familiar_cin' : form.cleaned_data['edad_familiar_cin'] if form.cleaned_data['edad_familiar_cin'] is not None else "-",
                    
                    'ocupa_familiar_uno' : form.cleaned_data['ocupa_familiar_uno'] if form.cleaned_data['ocupa_familiar_uno'] != "" else "-",
                    'ocupa_familiar_dos' : form.cleaned_data['ocupa_familiar_dos'] if form.cleaned_data['ocupa_familiar_dos'] != "" else "-",
                    'ocupa_familiar_tres' : form.cleaned_data['ocupa_familiar_tres'] if form.cleaned_data['ocupa_familiar_tres'] != "" else "-",
                    'ocupa_familiar_cua' : form.cleaned_data['ocupa_familiar_cua'] if form.cleaned_data['ocupa_familiar_cua'] != "" else "-",
                    'ocupa_familiar_cin' : form.cleaned_data['ocupa_familiar_cin'] if form.cleaned_data['ocupa_familiar_cin'] != "" else "-",
                    
                    'alt_len_rsp' : form.cleaned_data['alt_len_rsp'] if form.cleaned_data['alt_len_rsp'] != "" else "-",
                    'tarta_rsp' : form.cleaned_data['tarta_rsp'] if form.cleaned_data['tarta_rsp'] != "" else "-",
                    'def_ate_rsp' : form.cleaned_data['def_ate_rsp'] if form.cleaned_data['def_ate_rsp'] != "" else "-",
                    'epilep_rsp' : form.cleaned_data['epilep_rsp'] if form.cleaned_data['epilep_rsp'] != "" else "-",
                    'sind_rsp' : form.cleaned_data['sind_rsp'] if form.cleaned_data['sind_rsp'] != "" else "-",
                    'def_rsp' : form.cleaned_data['def_rsp'] if form.cleaned_data['def_rsp'] != "" else "-",
                    'sord_rsp' : form.cleaned_data['sord_rsp'] if form.cleaned_data['sord_rsp'] != "" else "-",
                    'def_men_rsp' : form.cleaned_data['def_men_rsp'] if form.cleaned_data['def_men_rsp'] != "" else "-",
                    'otros_rsp' : form.cleaned_data['otros_rsp'] if form.cleaned_data['otros_rsp'] != "" else "-",

                    'embarazo_num': form.cleaned_data['embarazo_num'] if form.cleaned_data['embarazo_num'] is not None else "-",
                    'sem_gest': form.cleaned_data['sem_gest'] if form.cleaned_data['sem_gest'] is not None else "-",
                    'med_ant': "✔"  if form.cleaned_data['med_ant'] != False else "No",
                    'sangr': "✔"  if form.cleaned_data['sangr'] != False else "No",
                    'sint_perd': "✔"  if form.cleaned_data['sint_perd'] != False else "No",
                    'convul_per': "✔"  if form.cleaned_data['convul_per'] != False else "No",
                    'anemia': "✔"  if form.cleaned_data['anemia'] != False else "No",
                    'intoxi': "✔"  if form.cleaned_data['intoxi'] != False else "No",
                    'trauma_per': "✔"  if form.cleaned_data['trauma_per'] != False else "No",
                    'diabete': "✔"  if form.cleaned_data['diabete'] != False else "No",
                    'varic_rubeo': "✔"  if form.cleaned_data['varic_rubeo'] != False else "No",
                    'depre': "✔"  if form.cleaned_data['depre'] != False else "No",
                    'exp_rx': "✔"  if form.cleaned_data['exp_rx'] != False else "No",
                    'desp_place': "✔"  if form.cleaned_data['desp_place'] != False else "No",
                    'medi_inge': "✔"  if form.cleaned_data['medi_inge'] != False else "No",
                    'enf_infecci': "✔"  if form.cleaned_data['enf_infecci'] != False else "No",
                    
                    'lug_parto': form.cleaned_data['lug_parto'] if form.cleaned_data['lug_parto'] != "" else "-",
                    'espe_parto': "✔"  if form.cleaned_data['espe_parto'] != False else "No",
                    'tipo_parto': form.cleaned_data['tipo_parto'],
                    'mot_parto': form.cleaned_data['mot_parto'] if form.cleaned_data['mot_parto'] != "" else "-",

                    'ant_morb_circuello': "✔" if form.cleaned_data['ant_morb_circuello'] != False else "No",
                    'ant_morb_sufrfet': "✔" if form.cleaned_data['ant_morb_sufrfet'] != False else "No",
                    'ant_morb_placprev': "✔" if form.cleaned_data['ant_morb_placprev'] != False else "No",
                    'ant_morb_ingemeco': "✔" if form.cleaned_data['ant_morb_ingemeco'] != False else "No",
                    'ant_morb_otros': form.cleaned_data['ant_morb_otros'] if form.cleaned_data['ant_morb_otros'] != "" else "-",

                    'peso': form.cleaned_data['peso'] if form.cleaned_data['peso'] != "" else "-",
                    'talla': form.cleaned_data['talla'] if form.cleaned_data['talla'] != "" else "-",
                    'apgar': form.cleaned_data['apgar'] if form.cleaned_data['apgar'] != "" else "-",
                    'color': form.cleaned_data['color'] if form.cleaned_data['color'] != "" else "-",

                    'hospi_per': "✔" if form.cleaned_data['hospi_per'] != False else "No",
                    'mot_hospi': form.cleaned_data['mot_hospi'] if form.cleaned_data['mot_hospi'] != "" else "-",

                    'trata_medica': form.cleaned_data['trata_medica'] if form.cleaned_data['trata_medica'] != "" else "-",

                    'trauma_post': "✔" if form.cleaned_data['trauma_post'] != False else "No", 
                    'hospi_post': "✔" if form.cleaned_data['hospi_post'] != False else "No",
                    'meningitis': "✔" if form.cleaned_data['meningitis'] != False else "No",
                    'encefalitis': "✔" if form.cleaned_data['encefalitis'] != False else "No",
                    'fieb_alta': "✔" if form.cleaned_data['fieb_alta'] != False else "No",
                    'convul_post': "✔" if form.cleaned_data['convul_post'] != False else "No",
                    'epilep_post': "✔" if form.cleaned_data['epilep_post'] != False else "No",
                    'ausencias': "✔" if form.cleaned_data['ausencias'] != False else "No",
                    'bronquitis': "✔" if form.cleaned_data['bronquitis'] != False else "No",
                    'sbo': "✔" if form.cleaned_data['sbo'] != False else "No",
                    'amsa': "✔" if form.cleaned_data['amsa'] != False else "No",
                    'ira': "✔" if form.cleaned_data['ira'] != False else "No",
                    'desnutri': "✔" if form.cleaned_data['desnutri'] != False else "No",
                    'otros_morb': form.cleaned_data['otros_morb'] if form.cleaned_data['otros_morb'] != "" else "-",
                    'control_med': "✔" if form.cleaned_data['desnutri'] != False else "No",
                    'dr_tratante': form.cleaned_data['dr_tratante'] if form.cleaned_data['dr_tratante'] != "" else "-",
                    'vacu_dia': "✔" if form.cleaned_data['desnutri'] != False else "No",
                    'trata_dental': "✔" if form.cleaned_data['desnutri'] != False else "No",
                    'epoca_dental': form.cleaned_data['epoca_dental'] if form.cleaned_data['epoca_dental'] != "" else "-",
                    'per_derivacion': form.cleaned_data['per_derivacion'] if form.cleaned_data['per_derivacion'] != "" else "-",
                    'mot_dental': form.cleaned_data['mot_dental'] if form.cleaned_data['mot_dental'] != "" else "-",

                    'epoca_exam': form.cleaned_data['epoca_exam'] if form.cleaned_data['epoca_exam'] != "" else "-",
                    'per_deriva_exam': form.cleaned_data['per_deriva_exam'] if form.cleaned_data['per_deriva_exam'] != "" else "-",
                    'mot_exam': form.cleaned_data['mot_exam'] if form.cleaned_data['mot_exam'] != "" else "-",

                    'fij_cabeza': form.cleaned_data['fij_cabeza'] if form.cleaned_data['fij_cabeza'] is not None else "-",
                    'sento_solo': form.cleaned_data['sento_solo'] if form.cleaned_data['sento_solo'] is not None else "-",
                    'gateo': form.cleaned_data['gateo'] if form.cleaned_data['gateo'] is not None else "-",
                    'camino': form.cleaned_data['camino'] if form.cleaned_data['camino'] is not None else "-",
                    'vist_solo': form.cleaned_data['vist_solo'] if form.cleaned_data['vist_solo'] is not None else "-",
                    'ctl_esf_vdiurno': form.cleaned_data['ctl_esf_vdiurno'] if form.cleaned_data['ctl_esf_vdiurno'] is not None else "-",
                    'ctl_esf_vnoct': form.cleaned_data['ctl_esf_vnoct'] if form.cleaned_data['ctl_esf_vnoct'] is not None else "-",
                    'ctl_anal_diur': form.cleaned_data['ctl_anal_diur'] if form.cleaned_data['ctl_anal_diur'] is not None else "-",
                    'ctl_anal_noct': form.cleaned_data['ctl_anal_noct'] if form.cleaned_data['ctl_anal_noct'] is not None else "-",
                    'entrena_esf': "✔" if form.cleaned_data['entrena_esf'] != False else "No",
                    'retraso': "✔" if form.cleaned_data['retraso'] != False else "No",

                    'act_motora': form.cleaned_data['act_motora'],

                    'toni_muscular': form.cleaned_data['toni_muscular'],

                    'motrici_gruesa': form.cleaned_data['motrici_gruesa'],

                    'toma_cuchara': "✔" if form.cleaned_data['toma_cuchara'] != False else "No",
                    'mov_garra': "✔" if form.cleaned_data['mov_garra'] != False else "No",
                    'mov_presion': "✔" if form.cleaned_data['mov_presion'] != False else "No",
                    'mov_pinza': "✔" if form.cleaned_data['mov_pinza'] != False else "No",

                    'vocalizo': form.cleaned_data['vocalizo'] if form.cleaned_data['vocalizo'] is not None else "-",
                    'balbuceo': form.cleaned_data['balbuceo'] if form.cleaned_data['balbuceo'] is not None else "-",
                    'jerga': form.cleaned_data['jerga'] if form.cleaned_data['jerga'] is not None else "-",
                    'prim_palabra': form.cleaned_data['prim_palabra'] if form.cleaned_data['prim_palabra'] is not None else "-",
                    'holofrase': form.cleaned_data['holofrase'] if form.cleaned_data['holofrase'] is not None else "-",
                    'pivote': form.cleaned_data['pivote'] if form.cleaned_data['pivote'] is not None else "-",
                    'sintagma': form.cleaned_data['sintagma'] if form.cleaned_data['sintagma'] is not None else "-",

                    'texto_uno': form.cleaned_data['texto_uno'] if form.cleaned_data['texto_uno'] != "" else "-",
                    'texto_dos': form.cleaned_data['texto_dos'] if form.cleaned_data['texto_dos'] != "" else "-",
                    'texto_tres': form.cleaned_data['texto_tres'] if form.cleaned_data['texto_tres'] != "" else "-",
                    'texto_cuatro': form.cleaned_data['texto_cuatro'] if form.cleaned_data['texto_cuatro'] != "" else "-",
                    'texto_cinco': form.cleaned_data['texto_cinco'] if form.cleaned_data['texto_cinco'] != "" else "-",

                    'sonido': "✔" if form.cleaned_data['sonido'] != False else "No",
                    'luces': "✔" if form.cleaned_data['luces'] != False else "No",
                    'per_aje_cir': "✔" if form.cleaned_data['per_aje_cir'] != False else "No",
                    'ecolalia': "✔" if form.cleaned_data['ecolalia'] != False else "No",
                    'mov_estero': "✔" if form.cleaned_data['mov_estero'] != False else "No",
                    'autoagresion': "✔" if form.cleaned_data['autoagresion'] != False else "No",
                    'pataleta': "✔" if form.cleaned_data['pataleta'] != False else "No",
                    'dificul_adaptacion': "✔" if form.cleaned_data['dificul_adaptacion'] != False else "No",
                    
                    'texto_seis': form.cleaned_data['texto_seis'] if form.cleaned_data['texto_seis'] != "" else "-"
                }
                request.session['pdf_anamnesis'] = data
                return redirect('listado_fichas_alumnos')
        
        if rut:
            form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_anamnesis=True, datos_retirado=retirado)
        else:
            form_base = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_anamnesis=True)
        context['form'] = FormDocumentoAnamnesis(request.POST)

    return render(request, 'formularios/docs/form_anamnesis.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_anamnesis(request):
    try:
        if request.session['pdf_anamnesis']:
            data = request.session['pdf_anamnesis']
            del request.session['pdf_anamnesis']
            template = 'documentos/anamnesis.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "Anamnesis - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content 
            return response

    except:
        return redirect('listado_fichas_alumnos')    


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

                #Calculo de puntajes
                tot_voc = 0
                tot_mor = 0
                tot_sin = 0
                resp_corr = [1,2,1,3,1,3,1,1,3,2,1,3,1,2,1,3,1,2,3,1,1,3,3,2,3,4,1,2,1,1,3,3,1,2,3,2,1,1,2,3,1,2,2,1,3,2,1,2,1,1,3,
                            2,3,2,1,2,1,1,2,1,3,3,1,1,2,1,3,1,2,1,3,2,2,3,3,3,3,1,2,1,1,3,2,3,2,2,1,3,1,1,2,1,1,3,2,1,3,3,2,2,1]
                resp = [val for key, val in form.cleaned_data.items() if 'item' in key]
                for x in range(len(resp_corr)):
                    if resp[x] == resp_corr[x]:
                        if x >= 0 and x <= 40:
                            tot_voc += 1
                        elif x >= 41 and x <= 88:
                            tot_mor += 1
                        else:
                            tot_sin += 1
                
                #Calculo total
                tot = tot_voc + tot_mor + tot_sin

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'alumn_edad': "{}".format(edad_anio),
                    'alumn_edad_mes': "{}".format(edad_mes),
                    'i1' : " " if form.cleaned_data['item1_voc'] == 1  else form.cleaned_data["item1_voc"] if form.cleaned_data["item1_voc"] is not None else "NR",
                    'i2' : " " if form.cleaned_data['item2_voc'] == 2  else form.cleaned_data["item2_voc"] if form.cleaned_data["item2_voc"] is not None else "NR",
                    'i3' : " " if form.cleaned_data['item3_voc'] == 1  else form.cleaned_data["item3_voc"] if form.cleaned_data["item3_voc"] is not None else "NR",
                    'i4' : " " if form.cleaned_data['item4_voc'] == 3  else form.cleaned_data["item4_voc"] if form.cleaned_data["item4_voc"] is not None else "NR",
                    'i5' : " " if form.cleaned_data['item5_voc'] == 1  else form.cleaned_data["item5_voc"] if form.cleaned_data["item5_voc"] is not None else "NR",
                    'i6' : " " if form.cleaned_data['item6_voc'] == 3  else form.cleaned_data["item6_voc"] if form.cleaned_data["item6_voc"] is not None else "NR",
                    'i7' : " " if form.cleaned_data['item7_voc'] == 1  else form.cleaned_data["item7_voc"] if form.cleaned_data["item7_voc"] is not None else "NR",
                    'i8' : " " if form.cleaned_data['item8_voc'] == 1  else form.cleaned_data["item8_voc"] if form.cleaned_data["item8_voc"] is not None else "NR",
                    'i9' : " " if form.cleaned_data['item9_voc'] == 3  else form.cleaned_data["item9_voc"] if form.cleaned_data["item9_voc"] is not None else "NR",
                    'i10': " " if form.cleaned_data['item10_voc'] == 2  else form.cleaned_data["item10_voc"] if form.cleaned_data["item10_voc"] is not None else "NR",
                    'i11': " " if form.cleaned_data['item11_voc'] == 1  else form.cleaned_data["item11_voc"] if form.cleaned_data["item11_voc"] is not None else "NR",
                    'i12': " " if form.cleaned_data['item12_voc'] == 3  else form.cleaned_data["item12_voc"] if form.cleaned_data["item12_voc"] is not None else "NR",
                    'i13': " " if form.cleaned_data['item13_voc'] == 1  else form.cleaned_data["item13_voc"] if form.cleaned_data["item13_voc"] is not None else "NR",
                    'i14': " " if form.cleaned_data['item14_voc'] == 2  else form.cleaned_data["item14_voc"] if form.cleaned_data["item14_voc"] is not None else "NR",
                    'i15': " " if form.cleaned_data['item15_voc'] == 1  else form.cleaned_data["item15_voc"] if form.cleaned_data["item15_voc"] is not None else "NR",
                    'i16': " " if form.cleaned_data['item16_voc'] == 3  else form.cleaned_data["item16_voc"] if form.cleaned_data["item16_voc"] is not None else "NR",
                    'i17': " " if form.cleaned_data['item17_voc'] == 1  else form.cleaned_data["item17_voc"] if form.cleaned_data["item17_voc"] is not None else "NR",
                    'i18': " " if form.cleaned_data['item18_voc'] == 2  else form.cleaned_data["item18_voc"] if form.cleaned_data["item18_voc"] is not None else "NR",
                    'i19': " " if form.cleaned_data['item19_voc'] == 3  else form.cleaned_data["item19_voc"] if form.cleaned_data["item19_voc"] is not None else "NR",
                    'i20': " " if form.cleaned_data['item20_voc'] == 1  else form.cleaned_data["item20_voc"] if form.cleaned_data["item20_voc"] is not None else "NR",
                    'i21': " " if form.cleaned_data['item21_voc'] == 1  else form.cleaned_data["item21_voc"] if form.cleaned_data["item21_voc"] is not None else "NR",
                    'i22': " " if form.cleaned_data['item22_voc'] == 3  else form.cleaned_data["item22_voc"] if form.cleaned_data["item22_voc"] is not None else "NR",
                    'i23': " " if form.cleaned_data['item23_voc'] == 3  else form.cleaned_data["item23_voc"] if form.cleaned_data["item23_voc"] is not None else "NR",
                    'i24': " " if form.cleaned_data['item24_voc'] == 2  else form.cleaned_data["item24_voc"] if form.cleaned_data["item24_voc"] is not None else "NR",
                    'i25': " " if form.cleaned_data['item25_voc'] == 3  else form.cleaned_data["item25_voc"] if form.cleaned_data["item25_voc"] is not None else "NR",
                    'i26': " " if form.cleaned_data['item26_voc'] == 4  else form.cleaned_data["item26_voc"] if form.cleaned_data["item26_voc"] is not None else "NR",
                    'i27': " " if form.cleaned_data['item27_voc'] == 1  else form.cleaned_data["item27_voc"] if form.cleaned_data["item27_voc"] is not None else "NR",
                    'i28': " " if form.cleaned_data['item28_voc'] == 2  else form.cleaned_data["item28_voc"] if form.cleaned_data["item28_voc"] is not None else "NR",
                    'i29': " " if form.cleaned_data['item29_voc'] == 1  else form.cleaned_data["item29_voc"] if form.cleaned_data["item29_voc"] is not None else "NR",
                    'i30': " " if form.cleaned_data['item30_voc'] == 1  else form.cleaned_data["item30_voc"] if form.cleaned_data["item30_voc"] is not None else "NR",
                    'i31': " " if form.cleaned_data['item31_voc'] == 3  else form.cleaned_data["item31_voc"] if form.cleaned_data["item31_voc"] is not None else "NR",
                    'i32': " " if form.cleaned_data['item32_voc'] == 3  else form.cleaned_data["item32_voc"] if form.cleaned_data["item32_voc"] is not None else "NR",
                    'i33': " " if form.cleaned_data['item33_voc'] == 1  else form.cleaned_data["item33_voc"] if form.cleaned_data["item33_voc"] is not None else "NR",
                    'i34': " " if form.cleaned_data['item34_voc'] == 2  else form.cleaned_data["item34_voc"] if form.cleaned_data["item34_voc"] is not None else "NR",
                    'i35': " " if form.cleaned_data['item35_voc'] == 3  else form.cleaned_data["item35_voc"] if form.cleaned_data["item35_voc"] is not None else "NR",
                    'i36': " " if form.cleaned_data['item36_voc'] == 2  else form.cleaned_data["item36_voc"] if form.cleaned_data["item36_voc"] is not None else "NR",
                    'i37': " " if form.cleaned_data['item37_voc'] == 1  else form.cleaned_data["item37_voc"] if form.cleaned_data["item37_voc"] is not None else "NR",
                    'i38': " " if form.cleaned_data['item38_voc'] == 1  else form.cleaned_data["item38_voc"] if form.cleaned_data["item38_voc"] is not None else "NR",
                    'i39': " " if form.cleaned_data['item39_voc'] == 2  else form.cleaned_data["item39_voc"] if form.cleaned_data["item39_voc"] is not None else "NR",
                    'i40': " " if form.cleaned_data['item40_voc'] == 3  else form.cleaned_data["item40_voc"] if form.cleaned_data["item40_voc"] is not None else "NR",
                    'i41': " " if form.cleaned_data['item41_voc'] == 1  else form.cleaned_data["item41_voc"] if form.cleaned_data["item41_voc"] is not None else "NR",
                    'tot_voc': tot_voc,
                    'i42': " " if form.cleaned_data['item42_mor'] == 2  else form.cleaned_data["item42_mor"] if form.cleaned_data["item42_mor"] is not None else "NR",
                    'i43': " " if form.cleaned_data['item43_mor'] == 2  else form.cleaned_data["item43_mor"] if form.cleaned_data["item43_mor"] is not None else "NR",
                    'i44': " " if form.cleaned_data['item44_mor'] == 1  else form.cleaned_data["item44_mor"] if form.cleaned_data["item44_mor"] is not None else "NR",
                    'i45': " " if form.cleaned_data['item45_mor'] == 3  else form.cleaned_data["item45_mor"] if form.cleaned_data["item45_mor"] is not None else "NR",
                    'i46': " " if form.cleaned_data['item46_mor'] == 2  else form.cleaned_data["item46_mor"] if form.cleaned_data["item46_mor"] is not None else "NR",
                    'i47': " " if form.cleaned_data['item47_mor'] == 1  else form.cleaned_data["item47_mor"] if form.cleaned_data["item47_mor"] is not None else "NR",
                    'i48': " " if form.cleaned_data['item48_mor'] == 2  else form.cleaned_data["item48_mor"] if form.cleaned_data["item48_mor"] is not None else "NR",
                    'i49': " " if form.cleaned_data['item49_mor'] == 1  else form.cleaned_data["item49_mor"] if form.cleaned_data["item49_mor"] is not None else "NR",
                    'i50': " " if form.cleaned_data['item50_mor'] == 1  else form.cleaned_data["item50_mor"] if form.cleaned_data["item50_mor"] is not None else "NR",
                    'i51': " " if form.cleaned_data['item51_mor'] == 3  else form.cleaned_data["item51_mor"] if form.cleaned_data["item51_mor"] is not None else "NR",
                    'i52': " " if form.cleaned_data['item52_mor'] == 2  else form.cleaned_data["item52_mor"] if form.cleaned_data["item52_mor"] is not None else "NR",
                    'i53': " " if form.cleaned_data['item53_mor'] == 3  else form.cleaned_data["item53_mor"] if form.cleaned_data["item53_mor"] is not None else "NR",
                    'i54': " " if form.cleaned_data['item54_mor'] == 2  else form.cleaned_data["item54_mor"] if form.cleaned_data["item54_mor"] is not None else "NR",
                    'i55': " " if form.cleaned_data['item55_mor'] == 1  else form.cleaned_data["item55_mor"] if form.cleaned_data["item55_mor"] is not None else "NR",
                    'i56': " " if form.cleaned_data['item56_mor'] == 2  else form.cleaned_data["item56_mor"] if form.cleaned_data["item56_mor"] is not None else "NR",
                    'i57': " " if form.cleaned_data['item57_mor'] == 1  else form.cleaned_data["item57_mor"] if form.cleaned_data["item57_mor"] is not None else "NR",
                    'i58': " " if form.cleaned_data['item58_mor'] == 1  else form.cleaned_data["item58_mor"] if form.cleaned_data["item58_mor"] is not None else "NR",
                    'i59': " " if form.cleaned_data['item59_mor'] == 2  else form.cleaned_data["item59_mor"] if form.cleaned_data["item59_mor"] is not None else "NR",
                    'i60': " " if form.cleaned_data['item60_mor'] == 1  else form.cleaned_data["item60_mor"] if form.cleaned_data["item60_mor"] is not None else "NR",
                    'i61': " " if form.cleaned_data['item61_mor'] == 3  else form.cleaned_data["item61_mor"] if form.cleaned_data["item61_mor"] is not None else "NR",
                    'i62': " " if form.cleaned_data['item62_mor'] == 3  else form.cleaned_data["item62_mor"] if form.cleaned_data["item62_mor"] is not None else "NR",
                    'i63': " " if form.cleaned_data['item63_mor'] == 1  else form.cleaned_data["item63_mor"] if form.cleaned_data["item63_mor"] is not None else "NR",
                    'i64': " " if form.cleaned_data['item64_mor'] == 1  else form.cleaned_data["item64_mor"] if form.cleaned_data["item64_mor"] is not None else "NR",
                    'i65': " " if form.cleaned_data['item65_mor'] == 2  else form.cleaned_data["item65_mor"] if form.cleaned_data["item65_mor"] is not None else "NR",
                    'i66': " " if form.cleaned_data['item66_mor'] == 1  else form.cleaned_data["item66_mor"] if form.cleaned_data["item66_mor"] is not None else "NR",
                    'i67': " " if form.cleaned_data['item67_mor'] == 3  else form.cleaned_data["item67_mor"] if form.cleaned_data["item67_mor"] is not None else "NR",
                    'i68': " " if form.cleaned_data['item68_mor'] == 1  else form.cleaned_data["item68_mor"] if form.cleaned_data["item68_mor"] is not None else "NR",
                    'i69': " " if form.cleaned_data['item69_mor'] == 2  else form.cleaned_data["item69_mor"] if form.cleaned_data["item69_mor"] is not None else "NR",
                    'i70': " " if form.cleaned_data['item70_mor'] == 1  else form.cleaned_data["item70_mor"] if form.cleaned_data["item70_mor"] is not None else "NR",
                    'i71': " " if form.cleaned_data['item71_mor'] == 3  else form.cleaned_data["item71_mor"] if form.cleaned_data["item71_mor"] is not None else "NR",
                    'i72': " " if form.cleaned_data['item72_mor'] == 2  else form.cleaned_data["item72_mor"] if form.cleaned_data["item72_mor"] is not None else "NR",
                    'i73': " " if form.cleaned_data['item73_mor'] == 2  else form.cleaned_data["item73_mor"] if form.cleaned_data["item73_mor"] is not None else "NR",
                    'i74': " " if form.cleaned_data['item74_mor'] == 3  else form.cleaned_data["item74_mor"] if form.cleaned_data["item74_mor"] is not None else "NR",
                    'i75': " " if form.cleaned_data['item75_mor'] == 3  else form.cleaned_data["item75_mor"] if form.cleaned_data["item75_mor"] is not None else "NR",
                    'i76': " " if form.cleaned_data['item76_mor'] == 3  else form.cleaned_data["item76_mor"] if form.cleaned_data["item76_mor"] is not None else "NR",
                    'i77': " " if form.cleaned_data['item77_mor'] == 3  else form.cleaned_data["item77_mor"] if form.cleaned_data["item77_mor"] is not None else "NR",
                    'i78': " " if form.cleaned_data['item78_mor'] == 1  else form.cleaned_data["item78_mor"] if form.cleaned_data["item78_mor"] is not None else "NR",
                    'i79': " " if form.cleaned_data['item79_mor'] == 2  else form.cleaned_data["item79_mor"] if form.cleaned_data["item79_mor"] is not None else "NR",
                    'i80': " " if form.cleaned_data['item80_mor'] == 1  else form.cleaned_data["item80_mor"] if form.cleaned_data["item80_mor"] is not None else "NR",
                    'i81': " " if form.cleaned_data['item81_mor'] == 1  else form.cleaned_data["item81_mor"] if form.cleaned_data["item81_mor"] is not None else "NR",
                    'i82': " " if form.cleaned_data['item82_mor'] == 3  else form.cleaned_data["item82_mor"] if form.cleaned_data["item82_mor"] is not None else "NR",
                    'i83': " " if form.cleaned_data['item83_mor'] == 2  else form.cleaned_data["item83_mor"] if form.cleaned_data["item83_mor"] is not None else "NR",
                    'i84': " " if form.cleaned_data['item84_mor'] == 3  else form.cleaned_data["item84_mor"] if form.cleaned_data["item84_mor"] is not None else "NR",
                    'i85': " " if form.cleaned_data['item85_mor'] == 2  else form.cleaned_data["item85_mor"] if form.cleaned_data["item85_mor"] is not None else "NR",
                    'i86': " " if form.cleaned_data['item86_mor'] == 2  else form.cleaned_data["item86_mor"] if form.cleaned_data["item86_mor"] is not None else "NR",
                    'i87': " " if form.cleaned_data['item87_mor'] == 1  else form.cleaned_data["item87_mor"] if form.cleaned_data["item87_mor"] is not None else "NR",
                    'i88': " " if form.cleaned_data['item88_mor'] == 3  else form.cleaned_data["item88_mor"] if form.cleaned_data["item88_mor"] is not None else "NR",
                    'i89': " " if form.cleaned_data['item89_mor'] == 1  else form.cleaned_data["item89_mor"] if form.cleaned_data["item89_mor"] is not None else "NR",
                    'tot_mor' : tot_mor,
                    'i90': " " if form.cleaned_data['item90_sin'] == 1  else form.cleaned_data["item90_sin"] if form.cleaned_data["item90_sin"] is not None else "NR",
                    'i91': " " if form.cleaned_data['item91_sin'] == 2  else form.cleaned_data["item91_sin"] if form.cleaned_data["item91_sin"] is not None else "NR",
                    'i92': " " if form.cleaned_data['item92_sin'] == 1  else form.cleaned_data["item92_sin"] if form.cleaned_data["item92_sin"] is not None else "NR",
                    'i93': " " if form.cleaned_data['item93_sin'] == 1  else form.cleaned_data["item93_sin"] if form.cleaned_data["item93_sin"] is not None else "NR",
                    'i94': " " if form.cleaned_data['item94_sin'] == 3  else form.cleaned_data["item94_sin"] if form.cleaned_data["item94_sin"] is not None else "NR",
                    'i95': " " if form.cleaned_data['item95_sin'] == 2  else form.cleaned_data["item95_sin"] if form.cleaned_data["item95_sin"] is not None else "NR",
                    'i96': " " if form.cleaned_data['item96_sin'] == 1  else form.cleaned_data["item96_sin"] if form.cleaned_data["item96_sin"] is not None else "NR",
                    'i97': " " if form.cleaned_data['item97_sin'] == 3  else form.cleaned_data["item97_sin"] if form.cleaned_data["item97_sin"] is not None else "NR",
                    'i98': " " if form.cleaned_data['item98_sin'] == 3  else form.cleaned_data["item98_sin"] if form.cleaned_data["item98_sin"] is not None else "NR",
                    'i99': " " if form.cleaned_data['item99_sin'] == 2  else form.cleaned_data["item99_sin"] if form.cleaned_data["item99_sin"] is not None else "NR",
                    'i100': " " if form.cleaned_data['item100_sin'] == 2  else form.cleaned_data["item100_sin"] if form.cleaned_data["item100_sin"] is not None else "NR",
                    'i101': " " if form.cleaned_data['item101_sin'] == 1  else form.cleaned_data["item101_sin"] if form.cleaned_data["item101_sin"] is not None else "NR",
                    'tot_sin': tot_sin,
                    'total': tot,
                    'calif1' : "✔" if form.cleaned_data['item1_voc'] == 1 else "O",
                    'calif2' : "✔" if form.cleaned_data['item2_voc'] == 2 else "O",
                    'calif3' : "✔" if form.cleaned_data['item3_voc'] == 1 else "O",
                    'calif4' : "✔" if form.cleaned_data['item4_voc'] == 3 else "O",
                    'calif5' : "✔" if form.cleaned_data['item5_voc'] == 1 else "O",
                    'calif6' : "✔" if form.cleaned_data['item6_voc'] == 3 else "O",
                    'calif7' : "✔" if form.cleaned_data['item7_voc'] == 1 else "O",
                    'calif8' : "✔" if form.cleaned_data['item8_voc'] == 1 else "O",
                    'calif9' : "✔" if form.cleaned_data['item9_voc'] == 3 else "O",
                    'calif10': "✔" if form.cleaned_data['item10_voc'] == 2 else "O",
                    'calif11': "✔" if form.cleaned_data['item11_voc'] == 1 else "O",
                    'calif12': "✔" if form.cleaned_data['item12_voc'] == 3 else "O",
                    'calif13': "✔" if form.cleaned_data['item13_voc'] == 1 else "O",
                    'calif14': "✔" if form.cleaned_data['item14_voc'] == 2 else "O",
                    'calif15': "✔" if form.cleaned_data['item15_voc'] == 1 else "O",
                    'calif16': "✔" if form.cleaned_data['item16_voc'] == 3 else "O",
                    'calif17': "✔" if form.cleaned_data['item17_voc'] == 1 else "O",
                    'calif18': "✔" if form.cleaned_data['item18_voc'] == 2 else "O",
                    'calif19': "✔" if form.cleaned_data['item19_voc'] == 3 else "O",
                    'calif20': "✔" if form.cleaned_data['item20_voc'] == 1 else "O",
                    'calif21': "✔" if form.cleaned_data['item21_voc'] == 1 else "O",
                    'calif22': "✔" if form.cleaned_data['item22_voc'] == 3 else "O",
                    'calif23': "✔" if form.cleaned_data['item23_voc'] == 3 else "O",
                    'calif24': "✔" if form.cleaned_data['item24_voc'] == 2 else "O",
                    'calif25': "✔" if form.cleaned_data['item25_voc'] == 3 else "O",
                    'calif26': "✔" if form.cleaned_data['item26_voc'] == 4 else "O",
                    'calif27': "✔" if form.cleaned_data['item27_voc'] == 1 else "O",
                    'calif28': "✔" if form.cleaned_data['item28_voc'] == 2 else "O",
                    'calif29': "✔" if form.cleaned_data['item29_voc'] == 1 else "O",
                    'calif30': "✔" if form.cleaned_data['item30_voc'] == 1 else "O",
                    'calif31': "✔" if form.cleaned_data['item31_voc'] == 3 else "O",
                    'calif32': "✔" if form.cleaned_data['item32_voc'] == 3 else "O",
                    'calif33': "✔" if form.cleaned_data['item33_voc'] == 1 else "O",
                    'calif34': "✔" if form.cleaned_data['item34_voc'] == 2 else "O",
                    'calif35': "✔" if form.cleaned_data['item35_voc'] == 3 else "O",
                    'calif36': "✔" if form.cleaned_data['item36_voc'] == 2 else "O",
                    'calif37': "✔" if form.cleaned_data['item37_voc'] == 1 else "O",
                    'calif38': "✔" if form.cleaned_data['item38_voc'] == 1 else "O",
                    'calif39': "✔" if form.cleaned_data['item39_voc'] == 2 else "O",
                    'calif40': "✔" if form.cleaned_data['item40_voc'] == 3 else "O",
                    'calif41': "✔" if form.cleaned_data['item41_voc'] == 1 else "O",
                    'calif42': "✔" if form.cleaned_data['item42_mor'] == 2 else "O",
                    'calif43': "✔" if form.cleaned_data['item43_mor'] == 2 else "O",
                    'calif44': "✔" if form.cleaned_data['item44_mor'] == 1 else "O",
                    'calif45': "✔" if form.cleaned_data['item45_mor'] == 3 else "O",
                    'calif46': "✔" if form.cleaned_data['item46_mor'] == 2 else "O",
                    'calif47': "✔" if form.cleaned_data['item47_mor'] == 1 else "O",
                    'calif48': "✔" if form.cleaned_data['item48_mor'] == 2 else "O",
                    'calif49': "✔" if form.cleaned_data['item49_mor'] == 1 else "O",
                    'calif50': "✔" if form.cleaned_data['item50_mor'] == 1 else "O",
                    'calif51': "✔" if form.cleaned_data['item51_mor'] == 3 else "O",
                    'calif52': "✔" if form.cleaned_data['item52_mor'] == 2 else "O",
                    'calif53': "✔" if form.cleaned_data['item53_mor'] == 3 else "O",
                    'calif54': "✔" if form.cleaned_data['item54_mor'] == 2 else "O",
                    'calif55': "✔" if form.cleaned_data['item55_mor'] == 1 else "O",
                    'calif56': "✔" if form.cleaned_data['item56_mor'] == 2 else "O",
                    'calif57': "✔" if form.cleaned_data['item57_mor'] == 1 else "O",
                    'calif58': "✔" if form.cleaned_data['item58_mor'] == 1 else "O",
                    'calif59': "✔" if form.cleaned_data['item59_mor'] == 2 else "O",
                    'calif60': "✔" if form.cleaned_data['item60_mor'] == 1 else "O",
                    'calif61': "✔" if form.cleaned_data['item61_mor'] == 3 else "O",
                    'calif62': "✔" if form.cleaned_data['item62_mor'] == 3 else "O",
                    'calif63': "✔" if form.cleaned_data['item63_mor'] == 1 else "O",
                    'calif64': "✔" if form.cleaned_data['item64_mor'] == 1 else "O",
                    'calif65': "✔" if form.cleaned_data['item65_mor'] == 2 else "O",
                    'calif66': "✔" if form.cleaned_data['item66_mor'] == 1 else "O",
                    'calif67': "✔" if form.cleaned_data['item67_mor'] == 3 else "O",
                    'calif68': "✔" if form.cleaned_data['item68_mor'] == 1 else "O",
                    'calif69': "✔" if form.cleaned_data['item69_mor'] == 2 else "O",
                    'calif70': "✔" if form.cleaned_data['item70_mor'] == 1 else "O",
                    'calif71': "✔" if form.cleaned_data['item71_mor'] == 3 else "O",
                    'calif72': "✔" if form.cleaned_data['item72_mor'] == 2 else "O",
                    'calif73': "✔" if form.cleaned_data['item73_mor'] == 2 else "O",
                    'calif74': "✔" if form.cleaned_data['item74_mor'] == 3 else "O",
                    'calif75': "✔" if form.cleaned_data['item75_mor'] == 3 else "O",
                    'calif76': "✔" if form.cleaned_data['item76_mor'] == 3 else "O",
                    'calif77': "✔" if form.cleaned_data['item77_mor'] == 3 else "O",
                    'calif78': "✔" if form.cleaned_data['item78_mor'] == 1 else "O",
                    'calif79': "✔" if form.cleaned_data['item79_mor'] == 2 else "O",
                    'calif80': "✔" if form.cleaned_data['item80_mor'] == 1 else "O",
                    'calif81': "✔" if form.cleaned_data['item81_mor'] == 1 else "O",
                    'calif82': "✔" if form.cleaned_data['item82_mor'] == 3 else "O",
                    'calif83': "✔" if form.cleaned_data['item83_mor'] == 2 else "O",
                    'calif84': "✔" if form.cleaned_data['item84_mor'] == 3 else "O",
                    'calif85': "✔" if form.cleaned_data['item85_mor'] == 2 else "O",
                    'calif86': "✔" if form.cleaned_data['item86_mor'] == 2 else "O",
                    'calif87': "✔" if form.cleaned_data['item87_mor'] == 1 else "O",
                    'calif88': "✔" if form.cleaned_data['item88_mor'] == 3 else "O",
                    'calif89': "✔" if form.cleaned_data['item89_mor'] == 1 else "O",
                    'calif90': "✔" if form.cleaned_data['item90_sin'] == 1 else "O",
                    'calif91': "✔" if form.cleaned_data['item91_sin'] == 2 else "O",
                    'calif92': "✔" if form.cleaned_data['item92_sin'] == 1 else "O",
                    'calif93': "✔" if form.cleaned_data['item93_sin'] == 1 else "O",
                    'calif94': "✔" if form.cleaned_data['item94_sin'] == 3 else "O",
                    'calif95': "✔" if form.cleaned_data['item95_sin'] == 2 else "O",
                    'calif96': "✔" if form.cleaned_data['item96_sin'] == 1 else "O",
                    'calif97': "✔" if form.cleaned_data['item97_sin'] == 3 else "O",
                    'calif98': "✔" if form.cleaned_data['item98_sin'] == 3 else "O",
                    'calif99': "✔" if form.cleaned_data['item99_sin'] == 2 else "O",
                    'calif100': "✔" if form.cleaned_data['item100_sin'] == 2 else "O",
                    'calif101': "✔" if form.cleaned_data['item101_sin'] == 1 else "O",
                }
                
                request.session['data'] = data
                return redirect('confirmation_tecal')
        
        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoTecal(request.POST)

    return render(request, 'formularios/docs/form_tecal.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def confirmation_tecal(request):
    try:
        data = request.session['data']
    except:
        return redirect(request.META.get('HTTP_REFERER'))
    #del request.session['data']
    context = {}
    context['total'] = data['total']
    context['tot_voc'] = data['tot_voc']
    context['tot_mor'] = data['tot_mor']
    context['tot_sin'] = data['tot_sin']
    
    context['form'] = FormTecalConfirmacion
    if request.method == 'POST':
        form = FormTecalConfirmacion(request.POST)
        if form.is_valid():
            data['ds_tot'] = form.cleaned_data['ds_tot']
            data['ds_voc'] = form.cleaned_data['ds_voc']
            data['ds_mor'] = form.cleaned_data['ds_mor']
            data['ds_sin'] = form.cleaned_data['ds_sin']

            request.session['pdf_tecal'] = data
            return redirect('listado_fichas_alumnos')
    
    return render(request, 'formularios/docs/form_tecal_confirmation.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_tecal(request):
    try:
        if request.session['pdf_tecal']:
            data = request.session['pdf_tecal']
            del request.session['pdf_tecal']
            template = 'documentos/tecal.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "Tecal - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content
            return response
    except:
        return redirect('listado_fichas_alumnos')


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_teprosif(request, rut=None):
    context = {}
    context['form_base'] = FormDatosPersonalesAlumno(datos_alumno=False, datos_teprosif=True)
    if rut:
        try:
            alumno = FichaAlumno.objects.get(rut=rut)
            context['form_base'] = FormDatosPersonalesAlumno(initial={
                'nombre': alumno.nombre,
                'fech_nac': alumno.fecha_nacimiento,
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

                #Cálculo puntajes
                #Est. Silabica
                estsil_puntaje = [val for key, val in form.cleaned_data.items() if key.startswith('est_sil')]
                estsil_puntaje = sum(estsil_puntaje, 0)
                #Asimilacion
                asimi_puntaje = [val for key, val in form.cleaned_data.items() if key.startswith('asimi')]
                asimi_puntaje = sum(asimi_puntaje, 0)
                #Sustitucion
                sustitu_puntaje = [val for key, val in form.cleaned_data.items() if key.startswith('sustitu')]
                sustitu_puntaje = sum(sustitu_puntaje, 0)

                #Comprobación PSF Barrido o Completo
                puntos = [val for key, val in form.cleaned_data.items() if key.startswith(('est_sil', 'asimi', 'sustitu'))]
                barrido = True
                for i in range(len(puntos)):
                    if i > 44:
                        if puntos[i] > 0:
                            barrido = False

                registro = [val for key, val in form.cleaned_data.items() if key.startswith('reg')]
                for i in range(len(registro)):
                    if i > 14:
                        if registro[i] != "":
                            barrido = False

                otra_respuesta = [val for key, val in form.cleaned_data.items() if key.startswith('otr_resp')]
                for i in range(len(otra_respuesta)):
                    if i > 14:
                        if otra_respuesta[i] != "":
                            barrido = False


                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_sexo': form_base.cleaned_data['sexo'],
                    'fecha_exam': fecha_hoy.strftime("%d/%m/%Y") ,
                    'reg1': form.cleaned_data['reg1'] if form.cleaned_data['reg1'] != 0 else "",
                    'est_sil1': form.cleaned_data['est_sil1'] if form.cleaned_data['est_sil1'] != 0 else "",
                    'asimi1': form.cleaned_data['asimi1'] if form.cleaned_data['asimi1'] != 0 else "",
                    'sustitu1': form.cleaned_data['sustitu1'] if form.cleaned_data['sustitu1'] != 0 else "",
                    'total1': sum([form.cleaned_data['est_sil1'], form.cleaned_data['asimi1'], form.cleaned_data['sustitu1']], 0) if sum([form.cleaned_data['est_sil1'], form.cleaned_data['asimi1'], form.cleaned_data['sustitu1']], 0) > 0 else "",
                    'otr_resp1': form.cleaned_data['otr_resp1'],
                    'reg2': form.cleaned_data['reg2'] if form.cleaned_data['reg2'] != 0 else "",
                    'est_sil2': form.cleaned_data['est_sil2'] if form.cleaned_data['est_sil2'] != 0 else "",
                    'asimi2': form.cleaned_data['asimi2'] if form.cleaned_data['asimi2'] != 0 else "",
                    'sustitu2': form.cleaned_data['sustitu2'] if form.cleaned_data['sustitu2'] != 0 else "",
                    'total2': sum([form.cleaned_data['est_sil2'], form.cleaned_data['asimi2'], form.cleaned_data['sustitu2']], 0) if sum([form.cleaned_data['est_sil2'], form.cleaned_data['asimi2'], form.cleaned_data['sustitu2']], 0) > 0 else "",
                    'otr_resp2': form.cleaned_data['otr_resp2'],
                    'reg3': form.cleaned_data['reg3'] if form.cleaned_data['reg3'] != 0 else "",
                    'est_sil3': form.cleaned_data['est_sil3'] if form.cleaned_data['est_sil3'] != 0 else "",
                    'asimi3': form.cleaned_data['asimi3'] if form.cleaned_data['asimi3'] != 0 else "",
                    'sustitu3': form.cleaned_data['sustitu3'] if form.cleaned_data['sustitu3'] != 0 else "",
                    'total3': sum([form.cleaned_data['est_sil3'], form.cleaned_data['asimi3'], form.cleaned_data['sustitu3']], 0) if sum([form.cleaned_data['est_sil3'], form.cleaned_data['asimi3'], form.cleaned_data['sustitu3']], 0) > 0 else "",
                    'otr_resp3': form.cleaned_data['otr_resp3'],
                    'reg4': form.cleaned_data['reg4'] if form.cleaned_data['reg4'] != 0 else "",
                    'est_sil4': form.cleaned_data['est_sil4'] if form.cleaned_data['est_sil4'] != 0 else "",
                    'asimi4': form.cleaned_data['asimi4'] if form.cleaned_data['asimi4'] != 0 else "",
                    'sustitu4': form.cleaned_data['sustitu4'] if form.cleaned_data['sustitu4'] != 0 else "",
                    'total4': sum([form.cleaned_data['est_sil4'], form.cleaned_data['asimi4'], form.cleaned_data['sustitu4']], 0) if sum([form.cleaned_data['est_sil4'], form.cleaned_data['asimi4'], form.cleaned_data['sustitu4']], 0) > 0 else "",
                    'otr_resp4': form.cleaned_data['otr_resp4'],
                    'reg5': form.cleaned_data['reg5'] if form.cleaned_data['reg5'] != 0 else "",
                    'est_sil5': form.cleaned_data['est_sil5'] if form.cleaned_data['est_sil5'] != 0 else "",
                    'asimi5': form.cleaned_data['asimi5'] if form.cleaned_data['asimi5'] != 0 else "",
                    'sustitu5': form.cleaned_data['sustitu5'] if form.cleaned_data['sustitu5'] != 0 else "",
                    'total5': sum([form.cleaned_data['est_sil5'], form.cleaned_data['asimi5'], form.cleaned_data['sustitu5']], 0) if sum([form.cleaned_data['est_sil5'], form.cleaned_data['asimi5'], form.cleaned_data['sustitu5']], 0) > 0 else "",
                    'otr_resp5': form.cleaned_data['otr_resp5'],
                    'reg6': form.cleaned_data['reg6'] if form.cleaned_data['reg6'] != 0 else "",
                    'est_sil6': form.cleaned_data['est_sil6'] if form.cleaned_data['est_sil6'] != 0 else "",
                    'asimi6': form.cleaned_data['asimi6'] if form.cleaned_data['asimi6'] != 0 else "",
                    'sustitu6': form.cleaned_data['sustitu6'] if form.cleaned_data['sustitu6'] != 0 else "",
                    'total6': sum([form.cleaned_data['est_sil6'], form.cleaned_data['asimi6'], form.cleaned_data['sustitu6']], 0) if sum([form.cleaned_data['est_sil6'], form.cleaned_data['asimi6'], form.cleaned_data['sustitu6']], 0) > 0 else "",
                    'otr_resp6': form.cleaned_data['otr_resp6'],
                    'reg7': form.cleaned_data['reg7'] if form.cleaned_data['reg7'] != 0 else "",
                    'est_sil7': form.cleaned_data['est_sil7'] if form.cleaned_data['est_sil7'] != 0 else "",
                    'asimi7': form.cleaned_data['asimi7'] if form.cleaned_data['asimi7'] != 0 else "",
                    'sustitu7': form.cleaned_data['sustitu7'] if form.cleaned_data['sustitu7'] != 0 else "",
                    'total7': sum([form.cleaned_data['est_sil7'], form.cleaned_data['asimi7'], form.cleaned_data['sustitu7']], 0) if sum([form.cleaned_data['est_sil7'], form.cleaned_data['asimi7'], form.cleaned_data['sustitu7']], 0) > 0 else "",
                    'otr_resp7': form.cleaned_data['otr_resp7'],
                    'reg8': form.cleaned_data['reg8'] if form.cleaned_data['reg8'] != 0 else "",
                    'est_sil8': form.cleaned_data['est_sil8'] if form.cleaned_data['est_sil8'] != 0 else "",
                    'asimi8': form.cleaned_data['asimi8'] if form.cleaned_data['asimi8'] != 0 else "",
                    'sustitu8': form.cleaned_data['sustitu8'] if form.cleaned_data['sustitu8'] != 0 else "",
                    'total8': sum([form.cleaned_data['est_sil8'], form.cleaned_data['asimi8'], form.cleaned_data['sustitu8']], 0) if sum([form.cleaned_data['est_sil8'], form.cleaned_data['asimi8'], form.cleaned_data['sustitu8']], 0) > 0 else "",
                    'otr_resp8': form.cleaned_data['otr_resp8'],
                    'reg9': form.cleaned_data['reg9'] if form.cleaned_data['reg9'] != 0 else "",
                    'est_sil9': form.cleaned_data['est_sil9'] if form.cleaned_data['est_sil9'] != 0 else "",
                    'asimi9': form.cleaned_data['asimi9'] if form.cleaned_data['asimi9'] != 0 else "",
                    'sustitu9': form.cleaned_data['sustitu9'] if form.cleaned_data['sustitu9'] != 0 else "",
                    'total9': sum([form.cleaned_data['est_sil9'], form.cleaned_data['asimi9'], form.cleaned_data['sustitu9']], 0) if sum([form.cleaned_data['est_sil9'], form.cleaned_data['asimi9'], form.cleaned_data['sustitu9']], 0) > 0 else "",
                    'otr_resp9': form.cleaned_data['otr_resp9'],
                    'reg10': form.cleaned_data['reg10'] if form.cleaned_data['reg10'] != 0 else "",
                    'est_sil10': form.cleaned_data['est_sil10'] if form.cleaned_data['est_sil10'] != 0 else "",
                    'asimi10': form.cleaned_data['asimi10'] if form.cleaned_data['asimi10'] != 0 else "",
                    'sustitu10': form.cleaned_data['sustitu10'] if form.cleaned_data['sustitu10'] != 0 else "",
                    'total10':sum([form.cleaned_data['est_sil10'], form.cleaned_data['asimi10'], form.cleaned_data['sustitu10']], 0) if sum([form.cleaned_data['est_sil10'], form.cleaned_data['asimi10'], form.cleaned_data['sustitu10']], 0) > 0 else "",
                    'otr_resp10': form.cleaned_data['otr_resp10'],
                    'reg11': form.cleaned_data['reg11'] if form.cleaned_data['reg11'] != 0 else "",
                    'est_sil11': form.cleaned_data['est_sil11'] if form.cleaned_data['est_sil11'] != 0 else "",
                    'asimi11': form.cleaned_data['asimi11'] if form.cleaned_data['asimi11'] != 0 else "",
                    'sustitu11': form.cleaned_data['sustitu11'] if form.cleaned_data['sustitu11'] != 0 else "",
                    'total11': sum([form.cleaned_data['est_sil11'], form.cleaned_data['asimi11'], form.cleaned_data['sustitu11']], 0) if sum([form.cleaned_data['est_sil11'], form.cleaned_data['asimi11'], form.cleaned_data['sustitu11']], 0) > 0 else "",
                    'otr_resp11': form.cleaned_data['otr_resp11'],
                    'reg12': form.cleaned_data['reg12'] if form.cleaned_data['reg12'] != 0 else "",
                    'est_sil12': form.cleaned_data['est_sil12'] if form.cleaned_data['est_sil12'] != 0 else "",
                    'asimi12': form.cleaned_data['asimi12'] if form.cleaned_data['asimi12'] != 0 else "",
                    'sustitu12': form.cleaned_data['sustitu12'] if form.cleaned_data['sustitu12'] != 0 else "",
                    'total12': sum([form.cleaned_data['est_sil12'], form.cleaned_data['asimi12'], form.cleaned_data['sustitu12']], 0) if sum([form.cleaned_data['est_sil12'], form.cleaned_data['asimi12'], form.cleaned_data['sustitu12']], 0) > 0 else "",
                    'otr_resp12': form.cleaned_data['otr_resp12'],
                    'reg13': form.cleaned_data['reg13'] if form.cleaned_data['reg13'] != 0 else "",
                    'est_sil13': form.cleaned_data['est_sil13'] if form.cleaned_data['est_sil13'] != 0 else "",
                    'asimi13': form.cleaned_data['asimi13'] if form.cleaned_data['asimi13'] != 0 else "",
                    'sustitu13': form.cleaned_data['sustitu13'] if form.cleaned_data['sustitu13'] != 0 else "",
                    'total13': sum([form.cleaned_data['est_sil13'], form.cleaned_data['asimi13'], form.cleaned_data['sustitu13']], 0) if sum([form.cleaned_data['est_sil13'], form.cleaned_data['asimi13'], form.cleaned_data['sustitu13']], 0) > 0 else "",
                    'otr_resp13': form.cleaned_data['otr_resp13'],
                    'reg14': form.cleaned_data['reg14'] if form.cleaned_data['reg14'] != 0 else "",
                    'est_sil14': form.cleaned_data['est_sil14'] if form.cleaned_data['est_sil14'] != 0 else "",
                    'asimi14': form.cleaned_data['asimi14'] if form.cleaned_data['asimi14'] != 0 else "",
                    'sustitu14': form.cleaned_data['sustitu14'] if form.cleaned_data['sustitu14'] != 0 else "",
                    'total14': sum([form.cleaned_data['est_sil14'], form.cleaned_data['asimi14'], form.cleaned_data['sustitu14']], 0) if sum([form.cleaned_data['est_sil14'], form.cleaned_data['asimi14'], form.cleaned_data['sustitu14']], 0) > 0 else "",
                    'otr_resp14': form.cleaned_data['otr_resp14'],
                    'reg15': form.cleaned_data['reg15'] if form.cleaned_data['reg15'] != 0 else "",
                    'est_sil15': form.cleaned_data['est_sil15'] if form.cleaned_data['est_sil15'] != 0 else "",
                    'asimi15': form.cleaned_data['asimi15'] if form.cleaned_data['asimi15'] != 0 else "",
                    'sustitu15': form.cleaned_data['sustitu15'] if form.cleaned_data['sustitu15'] != 0 else "",
                    'total15': sum([form.cleaned_data['est_sil15'], form.cleaned_data['asimi15'], form.cleaned_data['sustitu15']], 0) if sum([form.cleaned_data['est_sil15'], form.cleaned_data['asimi15'], form.cleaned_data['sustitu15']], 0) > 0 else "",
                    'otr_resp15': form.cleaned_data['otr_resp15'],
                    'reg16': form.cleaned_data['reg16'] if form.cleaned_data['reg16'] != 0 else "",
                    'est_sil16': form.cleaned_data['est_sil16'] if form.cleaned_data['est_sil16'] != 0 else "",
                    'asimi16': form.cleaned_data['asimi16'] if form.cleaned_data['asimi16'] != 0 else "",
                    'sustitu16': form.cleaned_data['sustitu16'] if form.cleaned_data['sustitu16'] != 0 else "",
                    'total16': sum([form.cleaned_data['est_sil16'], form.cleaned_data['asimi16'], form.cleaned_data['sustitu16']], 0) if sum([form.cleaned_data['est_sil16'], form.cleaned_data['asimi16'], form.cleaned_data['sustitu16']], 0) > 0 else "",
                    'otr_resp16': form.cleaned_data['otr_resp16'],
                    'reg17': form.cleaned_data['reg17'] if form.cleaned_data['reg17'] != 0 else "",
                    'est_sil17': form.cleaned_data['est_sil17'] if form.cleaned_data['est_sil17'] != 0 else "",
                    'asimi17': form.cleaned_data['asimi17'] if form.cleaned_data['asimi17'] != 0 else "",
                    'sustitu17': form.cleaned_data['sustitu17'] if form.cleaned_data['sustitu17'] != 0 else "",
                    'total17': sum([form.cleaned_data['est_sil17'], form.cleaned_data['asimi17'], form.cleaned_data['sustitu17']], 0) if sum([form.cleaned_data['est_sil17'], form.cleaned_data['asimi17'], form.cleaned_data['sustitu17']], 0) > 0 else "",
                    'otr_resp17': form.cleaned_data['otr_resp17'],
                    'reg18': form.cleaned_data['reg18'] if form.cleaned_data['reg18'] != 0 else "",
                    'est_sil18': form.cleaned_data['est_sil18'] if form.cleaned_data['est_sil18'] != 0 else "",
                    'asimi18': form.cleaned_data['asimi18'] if form.cleaned_data['asimi18'] != 0 else "",
                    'sustitu18': form.cleaned_data['sustitu18'] if form.cleaned_data['sustitu18'] != 0 else "",
                    'total18': sum([form.cleaned_data['est_sil18'], form.cleaned_data['asimi18'], form.cleaned_data['sustitu18']], 0) if sum([form.cleaned_data['est_sil18'], form.cleaned_data['asimi18'], form.cleaned_data['sustitu18']], 0) > 0 else "",
                    'otr_resp18': form.cleaned_data['otr_resp18'],
                    'reg19': form.cleaned_data['reg19'] if form.cleaned_data['reg19'] != 0 else "",
                    'est_sil19': form.cleaned_data['est_sil19'] if form.cleaned_data['est_sil19'] != 0 else "",
                    'asimi19': form.cleaned_data['asimi19'] if form.cleaned_data['asimi19'] != 0 else "",
                    'sustitu19': form.cleaned_data['sustitu19'] if form.cleaned_data['sustitu19'] != 0 else "",
                    'total19': sum([form.cleaned_data['est_sil19'], form.cleaned_data['asimi19'], form.cleaned_data['sustitu19']], 0) if sum([form.cleaned_data['est_sil19'], form.cleaned_data['asimi19'], form.cleaned_data['sustitu19']], 0) > 0 else "",
                    'otr_resp19': form.cleaned_data['otr_resp19'],
                    'reg20': form.cleaned_data['reg20'] if form.cleaned_data['reg20'] != 0 else "",
                    'est_sil20': form.cleaned_data['est_sil20'] if form.cleaned_data['est_sil20'] != 0 else "",
                    'asimi20': form.cleaned_data['asimi20'] if form.cleaned_data['asimi20'] != 0 else "",
                    'sustitu20': form.cleaned_data['sustitu20'] if form.cleaned_data['sustitu20'] != 0 else "",
                    'total20': sum([form.cleaned_data['est_sil20'], form.cleaned_data['asimi20'], form.cleaned_data['sustitu20']], 0) if sum([form.cleaned_data['est_sil20'], form.cleaned_data['asimi20'], form.cleaned_data['sustitu20']], 0) > 0 else "",
                    'otr_resp20': form.cleaned_data['otr_resp20'],
                    'reg21': form.cleaned_data['reg21'] if form.cleaned_data['reg21'] != 0 else "",
                    'est_sil21': form.cleaned_data['est_sil21'] if form.cleaned_data['est_sil21'] != 0 else "",
                    'asimi21': form.cleaned_data['asimi21'] if form.cleaned_data['asimi21'] != 0 else "",
                    'sustitu21': form.cleaned_data['sustitu21'] if form.cleaned_data['sustitu21'] != 0 else "",
                    'total21': sum([form.cleaned_data['est_sil21'], form.cleaned_data['asimi21'], form.cleaned_data['sustitu21']], 0) if sum([form.cleaned_data['est_sil21'], form.cleaned_data['asimi21'], form.cleaned_data['sustitu21']], 0) > 0 else "",
                    'otr_resp21': form.cleaned_data['otr_resp21'],
                    'reg22': form.cleaned_data['reg22'] if form.cleaned_data['reg22'] != 0 else "",
                    'est_sil22': form.cleaned_data['est_sil22'] if form.cleaned_data['est_sil22'] != 0 else "",
                    'asimi22': form.cleaned_data['asimi22'] if form.cleaned_data['asimi22'] != 0 else "",
                    'sustitu22': form.cleaned_data['sustitu22'] if form.cleaned_data['sustitu22'] != 0 else "",
                    'total22': sum([form.cleaned_data['est_sil22'], form.cleaned_data['asimi22'], form.cleaned_data['sustitu22']], 0) if sum([form.cleaned_data['est_sil22'], form.cleaned_data['asimi22'], form.cleaned_data['sustitu22']], 0) > 0 else "",
                    'otr_resp22': form.cleaned_data['otr_resp22'],
                    'reg23': form.cleaned_data['reg23'] if form.cleaned_data['reg23'] != 0 else "",
                    'est_sil23': form.cleaned_data['est_sil23'] if form.cleaned_data['est_sil23'] != 0 else "",
                    'asimi23': form.cleaned_data['asimi23'] if form.cleaned_data['asimi23'] != 0 else "",
                    'sustitu23': form.cleaned_data['sustitu23'] if form.cleaned_data['sustitu23'] != 0 else "",
                    'total23': sum([form.cleaned_data['est_sil23'], form.cleaned_data['asimi23'], form.cleaned_data['sustitu23']], 0) if sum([form.cleaned_data['est_sil23'], form.cleaned_data['asimi23'], form.cleaned_data['sustitu23']], 0) > 0 else "",
                    'otr_resp23': form.cleaned_data['otr_resp23'],
                    'reg24': form.cleaned_data['reg24'] if form.cleaned_data['reg24'] != 0 else "",
                    'est_sil24': form.cleaned_data['est_sil24'] if form.cleaned_data['est_sil24'] != 0 else "",
                    'asimi24': form.cleaned_data['asimi24'] if form.cleaned_data['asimi24'] != 0 else "",
                    'sustitu24': form.cleaned_data['sustitu24'] if form.cleaned_data['sustitu24'] != 0 else "",
                    'total24': sum([form.cleaned_data['est_sil24'], form.cleaned_data['asimi24'], form.cleaned_data['sustitu24']], 0) if sum([form.cleaned_data['est_sil24'], form.cleaned_data['asimi24'], form.cleaned_data['sustitu24']], 0) > 0 else "",
                    'otr_resp24': form.cleaned_data['otr_resp24'],
                    'reg25': form.cleaned_data['reg25'] if form.cleaned_data['reg25'] != 0 else "",
                    'est_sil25': form.cleaned_data['est_sil25'] if form.cleaned_data['est_sil25'] != 0 else "",
                    'asimi25': form.cleaned_data['asimi25'] if form.cleaned_data['asimi25'] != 0 else "",
                    'sustitu25': form.cleaned_data['sustitu25'] if form.cleaned_data['sustitu25'] != 0 else "",
                    'total25': sum([form.cleaned_data['est_sil25'], form.cleaned_data['asimi25'], form.cleaned_data['sustitu25']], 0) if sum([form.cleaned_data['est_sil25'], form.cleaned_data['asimi25'], form.cleaned_data['sustitu25']], 0) > 0 else "",
                    'otr_resp25': form.cleaned_data['otr_resp25'],
                    'reg26': form.cleaned_data['reg26'] if form.cleaned_data['reg26'] != 0 else "",
                    'est_sil26': form.cleaned_data['est_sil26'] if form.cleaned_data['est_sil26'] != 0 else "",
                    'asimi26': form.cleaned_data['asimi26'] if form.cleaned_data['asimi26'] != 0 else "",
                    'sustitu26': form.cleaned_data['sustitu26'] if form.cleaned_data['sustitu26'] != 0 else "",
                    'total26': sum([form.cleaned_data['est_sil26'], form.cleaned_data['asimi26'], form.cleaned_data['sustitu26']], 0) if sum([form.cleaned_data['est_sil26'], form.cleaned_data['asimi26'], form.cleaned_data['sustitu26']], 0) > 0 else "",
                    'otr_resp26': form.cleaned_data['otr_resp26'],
                    'reg27': form.cleaned_data['reg27'] if form.cleaned_data['reg27'] != 0 else "",
                    'est_sil27': form.cleaned_data['est_sil27'] if form.cleaned_data['est_sil27'] != 0 else "",
                    'asimi27': form.cleaned_data['asimi27'] if form.cleaned_data['asimi27'] != 0 else "",
                    'sustitu27': form.cleaned_data['sustitu27'] if form.cleaned_data['sustitu27'] != 0 else "",
                    'total27': sum([form.cleaned_data['est_sil27'], form.cleaned_data['asimi27'], form.cleaned_data['sustitu27']], 0) if sum([form.cleaned_data['est_sil27'], form.cleaned_data['asimi27'], form.cleaned_data['sustitu27']], 0) > 0 else "",
                    'otr_resp27': form.cleaned_data['otr_resp27'],
                    'reg28': form.cleaned_data['reg28'] if form.cleaned_data['reg28'] != 0 else "",
                    'est_sil28': form.cleaned_data['est_sil28'] if form.cleaned_data['est_sil28'] != 0 else "",
                    'asimi28': form.cleaned_data['asimi28'] if form.cleaned_data['asimi28'] != 0 else "",
                    'sustitu28': form.cleaned_data['sustitu28'] if form.cleaned_data['sustitu28'] != 0 else "",
                    'total28': sum([form.cleaned_data['est_sil28'], form.cleaned_data['asimi28'], form.cleaned_data['sustitu28']], 0) if sum([form.cleaned_data['est_sil28'], form.cleaned_data['asimi28'], form.cleaned_data['sustitu28']], 0) > 0 else "",
                    'otr_resp28': form.cleaned_data['otr_resp28'],
                    'reg29': form.cleaned_data['reg29'] if form.cleaned_data['reg29'] != 0 else "",
                    'est_sil29': form.cleaned_data['est_sil29'] if form.cleaned_data['est_sil29'] != 0 else "",
                    'asimi29': form.cleaned_data['asimi29'] if form.cleaned_data['asimi29'] != 0 else "",
                    'sustitu29': form.cleaned_data['sustitu29'] if form.cleaned_data['sustitu29'] != 0 else "",
                    'total29': sum([form.cleaned_data['est_sil29'], form.cleaned_data['asimi29'], form.cleaned_data['sustitu29']], 0) if sum([form.cleaned_data['est_sil29'], form.cleaned_data['asimi29'], form.cleaned_data['sustitu29']], 0) > 0 else "",
                    'otr_resp29': form.cleaned_data['otr_resp29'],
                    'reg30': form.cleaned_data['reg30'] if form.cleaned_data['reg30'] != 0 else "",
                    'est_sil30': form.cleaned_data['est_sil30'] if form.cleaned_data['est_sil30'] != 0 else "",
                    'asimi30': form.cleaned_data['asimi30'] if form.cleaned_data['asimi30'] != 0 else "",
                    'sustitu30': form.cleaned_data['sustitu30'] if form.cleaned_data['sustitu30'] != 0 else "",
                    'total30': sum([form.cleaned_data['est_sil30'], form.cleaned_data['asimi30'], form.cleaned_data['sustitu30']], 0) if sum([form.cleaned_data['est_sil30'], form.cleaned_data['asimi30'], form.cleaned_data['sustitu30']], 0) > 0 else "",
                    'otr_resp30': form.cleaned_data['otr_resp30'],
                    'reg31': form.cleaned_data['reg31'] if form.cleaned_data['reg31'] != 0 else "",
                    'est_sil31': form.cleaned_data['est_sil31'] if form.cleaned_data['est_sil31'] != 0 else "",
                    'asimi31': form.cleaned_data['asimi31'] if form.cleaned_data['asimi31'] != 0 else "",
                    'sustitu31': form.cleaned_data['sustitu31'] if form.cleaned_data['sustitu31'] != 0 else "",
                    'total31': sum([form.cleaned_data['est_sil31'], form.cleaned_data['asimi31'], form.cleaned_data['sustitu31']], 0) if sum([form.cleaned_data['est_sil31'], form.cleaned_data['asimi31'], form.cleaned_data['sustitu31']], 0) > 0 else "",
                    'otr_resp31': form.cleaned_data['otr_resp31'],
                    'reg32': form.cleaned_data['reg32'] if form.cleaned_data['reg32'] != 0 else "",
                    'est_sil32': form.cleaned_data['est_sil32'] if form.cleaned_data['est_sil32'] != 0 else "",
                    'asimi32': form.cleaned_data['asimi32'] if form.cleaned_data['asimi32'] != 0 else "",
                    'sustitu32': form.cleaned_data['sustitu32'] if form.cleaned_data['sustitu32'] != 0 else "",
                    'total32': sum([form.cleaned_data['est_sil32'], form.cleaned_data['asimi32'], form.cleaned_data['sustitu32']], 0) if sum([form.cleaned_data['est_sil32'], form.cleaned_data['asimi32'], form.cleaned_data['sustitu32']], 0) > 0 else "",
                    'otr_resp32': form.cleaned_data['otr_resp32'],
                    'reg33': form.cleaned_data['reg33'] if form.cleaned_data['reg33'] != 0 else "",
                    'est_sil33': form.cleaned_data['est_sil33'] if form.cleaned_data['est_sil33'] != 0 else "",
                    'asimi33': form.cleaned_data['asimi33'] if form.cleaned_data['asimi33'] != 0 else "",
                    'sustitu33': form.cleaned_data['sustitu33'] if form.cleaned_data['sustitu33'] != 0 else "",
                    'total33': sum([form.cleaned_data['est_sil33'], form.cleaned_data['asimi33'], form.cleaned_data['sustitu33']], 0) if sum([form.cleaned_data['est_sil33'], form.cleaned_data['asimi33'], form.cleaned_data['sustitu33']], 0) > 0 else "",
                    'otr_resp33': form.cleaned_data['otr_resp33'],
                    'reg34': form.cleaned_data['reg34'] if form.cleaned_data['reg34'] != 0 else "",
                    'est_sil34': form.cleaned_data['est_sil34'] if form.cleaned_data['est_sil34'] != 0 else "",
                    'asimi34': form.cleaned_data['asimi34'] if form.cleaned_data['asimi34'] != 0 else "",
                    'sustitu34': form.cleaned_data['sustitu34'] if form.cleaned_data['sustitu34'] != 0 else "",
                    'total34': sum([form.cleaned_data['est_sil34'], form.cleaned_data['asimi34'], form.cleaned_data['sustitu34']], 0) if sum([form.cleaned_data['est_sil34'], form.cleaned_data['asimi34'], form.cleaned_data['sustitu34']], 0) > 0 else "",
                    'otr_resp34': form.cleaned_data['otr_resp34'],
                    'reg35': form.cleaned_data['reg35'] if form.cleaned_data['reg35'] != 0 else "",
                    'est_sil35': form.cleaned_data['est_sil35'] if form.cleaned_data['est_sil35'] != 0 else "",
                    'asimi35': form.cleaned_data['asimi35'] if form.cleaned_data['asimi35'] != 0 else "",
                    'sustitu35': form.cleaned_data['sustitu35'] if form.cleaned_data['sustitu35'] != 0 else "",
                    'total35': sum([form.cleaned_data['est_sil35'], form.cleaned_data['asimi35'], form.cleaned_data['sustitu35']], 0) if sum([form.cleaned_data['est_sil35'], form.cleaned_data['asimi35'], form.cleaned_data['sustitu35']], 0) > 0 else "",
                    'otr_resp35': form.cleaned_data['otr_resp35'],
                    'reg36': form.cleaned_data['reg36'] if form.cleaned_data['reg36'] != 0 else "",
                    'est_sil36': form.cleaned_data['est_sil36'] if form.cleaned_data['est_sil36'] != 0 else "",
                    'asimi36': form.cleaned_data['asimi36'] if form.cleaned_data['asimi36'] != 0 else "",
                    'sustitu36': form.cleaned_data['sustitu36'] if form.cleaned_data['sustitu36'] != 0 else "",
                    'total36': sum([form.cleaned_data['est_sil36'], form.cleaned_data['asimi36'], form.cleaned_data['sustitu36']], 0) if sum([form.cleaned_data['est_sil36'], form.cleaned_data['asimi36'], form.cleaned_data['sustitu36']], 0) > 0 else "",
                    'otr_resp36': form.cleaned_data['otr_resp36'],
                    'reg37': form.cleaned_data['reg37'] if form.cleaned_data['reg37'] != 0 else "",
                    'est_sil37': form.cleaned_data['est_sil37'] if form.cleaned_data['est_sil37'] != 0 else "",
                    'asimi37': form.cleaned_data['asimi37'] if form.cleaned_data['asimi37'] != 0 else "",
                    'sustitu37': form.cleaned_data['sustitu37'] if form.cleaned_data['sustitu37'] != 0 else "",
                    'total37': sum([form.cleaned_data['est_sil37'], form.cleaned_data['asimi37'], form.cleaned_data['sustitu37']], 0) if sum([form.cleaned_data['est_sil37'], form.cleaned_data['asimi37'], form.cleaned_data['sustitu37']], 0) > 0 else "",
                    'otr_resp37': form.cleaned_data['otr_resp37'],
                    'psf_barrido_total': "",
                    'psf_total': "",
                }

                if barrido:
                    data['psf_barrido_est_sil'] = estsil_puntaje
                    data['psf_barrido_asimi'] = asimi_puntaje
                    data['psf_barrido_sustitu'] = sustitu_puntaje
                    data['psf_barrido_total'] = estsil_puntaje + asimi_puntaje + sustitu_puntaje
                else:
                    data['psf_total_est_sil'] = estsil_puntaje
                    data['psf_total_asimi'] = asimi_puntaje
                    data['psf_total_sustitu'] = sustitu_puntaje
                    data['psf_total'] = estsil_puntaje + asimi_puntaje + sustitu_puntaje

                request.session['data'] = data
                return redirect('teprosif_puntajes')

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_teprosif=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_teprosif=True)
        context['form'] = FormDocumentoTeprosif(request.POST)

    return render(request, 'formularios/docs/form_teprosif.html', context)

@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_doc_final_teprosif(request):
    data = request.session['data']
    #del request.session['data']
    context = {}

    barrido = True if data['psf_barrido_total'] != "" else False
    context['form'] = FormDocumentoFinalTeprosif(barrido=barrido)
    
    context['psf_barrido_total'] = data['psf_barrido_total']
    context['psf_total'] = data['psf_total']

    if request.method == 'POST':
        form = FormDocumentoFinalTeprosif(request.POST, barrido=barrido)
        if form.is_valid():

            data['nvl_desemp_barrido'] = form.cleaned_data['nvl_desemp_barrido']
            data['nvl_desemp_teprosif'] = form.cleaned_data['nvl_desemp_teprosif']

            request.session['pdf_teprosif'] = data
            return redirect('listado_fichas_alumnos')

    return render(request, 'formularios/docs/form_final_teprosif.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_teprosif(request):
    try:
        if request.session['pdf_teprosif']:
            data = request.session['pdf_teprosif']
            del request.session['pdf_teprosif']
            template = 'documentos/TEPROSIF-R.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "Hoja de respuesta TEPROSIF-R - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content 
            return response

    except:
        return redirect('listado_fichas_alumnos')


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
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'alumn_dir': form_base.cleaned_data['domicilio'],
                    'alumn_rut': form_base.cleaned_data['rut'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'fecha_eval': fecha_hoy.strftime("%d/%m/%Y"),
                    'antdes_leng': form.cleaned_data['antdes_leng'],
                    'antdes_natal': form.cleaned_data['antdes_natal'],
                    'antdes_balbuceo': form.cleaned_data['antdes_balbuceo'],
                    'antdes_palabras': form.cleaned_data['antdes_palabras'],
                    'antdes_motor': form.cleaned_data['antdes_motor'],
                    'antdes_frases': form.cleaned_data['antdes_frases'],
                    'antdes_comactual': form.cleaned_data['antdes_comactual'],
                    'antdes_morbidos': form.cleaned_data['antdes_morbidos'],
                    'desarrollo_social': form.cleaned_data['desarrollo_social'],
                    'antfam_lenguaje': "✔" if form.cleaned_data['antfam_lenguaje'] == True else " ",
                    'antfam_psiquia': "✔" if form.cleaned_data['antfam_psiquia'] == True else " ",
                    'antfam_epilepsia': "✔" if form.cleaned_data['antfam_epilepsia'] == True else " ",
                    'antfam_auditivo': "✔" if form.cleaned_data['antfam_auditivo'] == True else " ",
                    'antfam_cognitivo': "✔" if form.cleaned_data['antfam_cognitivo'] == True else " ",
                    'antfam_aprendizaje': "✔" if form.cleaned_data['antfam_aprendizaje'] == True else " ",
                    'antfam_observaciones': form.cleaned_data['antfam_observaciones'],
                    'resp_tipo': form.cleaned_data['resp_tipo'],
                    'resp_modo': form.cleaned_data['resp_modo'],
                    'resp_cfr': form.cleaned_data['resp_cfr'],
                    'deglucion': form.cleaned_data['deglucion'],
                    'labios_forma': form.cleaned_data['labios_forma'],
                    'labios_fuerza': form.cleaned_data['labios_fuerza'],
                    'labprax_protunsion': form.cleaned_data['labprax_protunsion'],
                    'labprax_retrusion': form.cleaned_data['labprax_retrusion'],
                    'labprax_percusion': form.cleaned_data['labprax_percusion'],
                    'labprax_vibracion': form.cleaned_data['labprax_vibracion'],
                    'dientes_implantacion': form.cleaned_data['dientes_implantacion'],
                    'mordida': form.cleaned_data['mordida'],
                    'maxilar_forma': form.cleaned_data['maxilar_forma'],
                    'maxilar_praxias': form.cleaned_data['maxilar_praxias'],
                    'paladaros_forma': form.cleaned_data['paladaros_forma'],
                    'velpal_movilidad': form.cleaned_data['velpal_movilidad'],
                    'velpal_uvula': form.cleaned_data['velpal_uvula'],
                    'amigdalas': form.cleaned_data['amigdalas'],
                    'lengua_tamano': form.cleaned_data['lengua_tamano'],
                    'lengua_fuerza': form.cleaned_data['lengua_fuerza'],
                    'lengua_frenillo': form.cleaned_data['lengua_frenillo'],
                    'lengprax_elevacion': form.cleaned_data['lengprax_elevacion'],
                    'lengprax_depresion': form.cleaned_data['lengprax_depresion'],
                    'lengprax_chasqueo': form.cleaned_data['lengprax_chasqueo'],
                    'lengprax_vibracion': form.cleaned_data['lengprax_vibracion'],
                    'lengprax_comisuras': form.cleaned_data['lengprax_comisuras'],
                    'lengprax_vestibular': form.cleaned_data['lengprax_vestibular'],
                    'cara_forma': form.cleaned_data['cara_forma'],
                    'caraprax_bilateral': form.cleaned_data['caraprax_bilateral'],
                    'caraprax_unilateral': form.cleaned_data['caraprax_unilateral'],
                    'voz_calidad': form.cleaned_data['voz_calidad'],
                    'voz_intensidad': form.cleaned_data['voz_intensidad'],
                    'tono': form.cleaned_data['tono'],
                    'tono_resonancia': form.cleaned_data['tono_resonancia'],
                    'tono_timbre': form.cleaned_data['tono_timbre'],
                    'audicion': form.cleaned_data['audicion'],
                    'discriminacion': form.cleaned_data['discriminacion'],
                    'habla_velocidad': form.cleaned_data['habla_velocidad'],
                    'habla_fluidez': form.cleaned_data['habla_fluidez'],
                    'artic_b': "✔" if form.cleaned_data['artic_b'] == True else " ",
                    'artic_p': "✔" if form.cleaned_data['artic_p'] == True else " ",
                    'artic_m': "✔" if form.cleaned_data['artic_m'] == True else " ",
                    'artic_f': "✔" if form.cleaned_data['artic_f'] == True else " ",
                    'artic_d': "✔" if form.cleaned_data['artic_d'] == True else " ",
                    'artic_t': "✔" if form.cleaned_data['artic_t'] == True else " ",
                    'artic_s': "✔" if form.cleaned_data['artic_s'] == True else " ",
                    'artic_n': "✔" if form.cleaned_data['artic_n'] == True else " ",
                    'artic_l': "✔" if form.cleaned_data['artic_l'] == True else " ",
                    'artic_r': "✔" if form.cleaned_data['artic_r'] == True else " ",
                    'artic_rr': "✔" if form.cleaned_data['artic_rr'] == True else " ",
                    'artic_y': "✔" if form.cleaned_data['artic_y'] == True else " ",
                    'artic_n': "✔" if form.cleaned_data['artic_n'] == True else " ",
                    'artic_ch': "✔" if form.cleaned_data['artic_ch'] == True else " ",
                    'artic_j': "✔" if form.cleaned_data['artic_j'] == True else " ",
                    'artic_g': "✔" if form.cleaned_data['artic_g'] == True else " ",
                    'artic_k': "✔" if form.cleaned_data['artic_k'] == True else " ",
                    'difvoc_ai': "✔" if form.cleaned_data['difvoc_ai'] == True else " ",
                    'difvoc_au': "✔" if form.cleaned_data['difvoc_au'] == True else " ",
                    'difvoc_ei': "✔" if form.cleaned_data['difvoc_ei'] == True else " ",
                    'difvoc_eu': "✔" if form.cleaned_data['difvoc_eu'] == True else " ",
                    'difvoc_ia': "✔" if form.cleaned_data['difvoc_ia'] == True else " ",
                    'difvoc_ie': "✔" if form.cleaned_data['difvoc_ie'] == True else " ",
                    'difvoc_io': "✔" if form.cleaned_data['difvoc_io'] == True else " ",
                    'difvoc_iu': "✔" if form.cleaned_data['difvoc_iu'] == True else " ",
                    'difvoc_oi': "✔" if form.cleaned_data['difvoc_oi'] == True else " ",
                    'difvoc_ua': "✔" if form.cleaned_data['difvoc_ua'] == True else " ",
                    'difvoc_ue': "✔" if form.cleaned_data['difvoc_ue'] == True else " ",
                    'difvoc_ui': "✔" if form.cleaned_data['difvoc_ui'] == True else " ",
                    'difvoc_uo': "✔" if form.cleaned_data['difvoc_uo'] == True else " ",
                    'difcon_bl': "✔" if form.cleaned_data['difcon_bl'] == True else " ",
                    'difcon_pl': "✔" if form.cleaned_data['difcon_pl'] == True else " ",
                    'difcon_fl': "✔" if form.cleaned_data['difcon_fl'] == True else " ",
                    'difcon_gl': "✔" if form.cleaned_data['difcon_gl'] == True else " ",
                    'difcon_cl': "✔" if form.cleaned_data['difcon_cl'] == True else " ",
                    'difcon_tl': "✔" if form.cleaned_data['difcon_tl'] == True else " ",
                    'difcon_br': "✔" if form.cleaned_data['difcon_br'] == True else " ",
                    'difcon_pr': "✔" if form.cleaned_data['difcon_pr'] == True else " ",
                    'difcon_fr': "✔" if form.cleaned_data['difcon_fr'] == True else " ",
                    'difcon_gr': "✔" if form.cleaned_data['difcon_gr'] == True else " ",
                    'difcon_cr': "✔" if form.cleaned_data['difcon_cr'] == True else " ",
                    'difcon_tr': "✔" if form.cleaned_data['difcon_tr'] == True else " ",
                    'difcon_dr': "✔" if form.cleaned_data['difcon_dr'] == True else " ",
                    'nvlsem_vocab': form.cleaned_data['nvlsem_vocab'],
                    'nvlsem_lexica': form.cleaned_data['nvlsem_lexica'],
                    'nvlsem_hiponimia': form.cleaned_data['nvlsem_hiponimia'],
                    'nvlsem_expresafun': form.cleaned_data['nvlsem_expresafun'],
                    'nvlsem_hiperonimia': form.cleaned_data['nvlsem_hiperonimia'],
                    'nvlsem_lengrep_nom': form.cleaned_data['nvlsem_lengrep_nom'],
                    'nvlsem_lengrep_des': form.cleaned_data['nvlsem_lengrep_des'],
                    'nvlsem_lengrep_int': form.cleaned_data['nvlsem_lengrep_int'],
                    'nvlmorf_exp_sustan': form.cleaned_data['nvlmorf_exp_sustan'],
                    'nvlmorf_exp_articu': form.cleaned_data['nvlmorf_exp_articu'],
                    'nvlmorf_exp_verbos': form.cleaned_data['nvlmorf_exp_verbos'],
                    'nvlmorf_exp_adverb': form.cleaned_data['nvlmorf_exp_adverb'],
                    'nvlmorf_exp_prepos': form.cleaned_data['nvlmorf_exp_prepos'],
                    'nvlmorf_exp_pronom': form.cleaned_data['nvlmorf_exp_pronom'],
                    'nvlmorf_observaciones': form.cleaned_data['nvlmorf_observaciones'],
                    'aspcomp_discriminacion': form.cleaned_data['aspcomp_discriminacion'],
                    'aspcomp_memverbal': form.cleaned_data['aspcomp_memverbal'],
                    'aspcomp_asociacion': form.cleaned_data['aspcomp_asociacion'],
                    'obs_nvlsem_vocabpasivo': form.cleaned_data['obs_nvlsem_vocabpasivo'],
                    'obs_nvlsem_defuso': form.cleaned_data['obs_nvlsem_defuso'],
                    'obs_nvlsem_absvisuales': form.cleaned_data['obs_nvlsem_absvisuales'],
                    'obs_nvlsem_analogias': form.cleaned_data['obs_nvlsem_analogias'],
                    'obs_nvlsem_relopuestas': form.cleaned_data['obs_nvlsem_relopuestas'],
                    'obs_nvlsin_ordsimples': form.cleaned_data['obs_nvlsin_ordsimples'],
                    'obs_nvlsin_ordcomplejas2': form.cleaned_data['obs_nvlsin_ordcomplejas2'],
                    'obs_nvlsin_ordcomplejas3': form.cleaned_data['obs_nvlsin_ordcomplejas3'],
                    'obs_nvlsin_vozpasiva': form.cleaned_data['obs_nvlsin_vozpasiva'],
                    'obs_nvlsin_observaciones': form.cleaned_data['obs_nvlsin_observaciones'],
                    'obs_aspgram_contocular': form.cleaned_data['obs_aspgram_contocular'],
                    'obs_aspgram_postura': form.cleaned_data['obs_aspgram_postura'],
                    'obs_aspgram_dialogo': form.cleaned_data['obs_aspgram_dialogo'],
                    'obs_aspgram_topico': form.cleaned_data['obs_aspgram_topico'],
                    'obs_aspgram_facultades': form.cleaned_data['obs_aspgram_facultades'],
                    'obs_aspgram_intcomunic': form.cleaned_data['obs_aspgram_intcomunic'],
                    'obs_pruebas_aplicadas': form.cleaned_data['obs_pruebas_aplicadas'],
                    'obs_diagnostico': form.cleaned_data['obs_diagnostico'],
                    'obs_indicaciones': form.cleaned_data['obs_indicaciones'],
                }
                request.session['pdf_fonoaudio'] = data
                return redirect('listado_fichas_alumnos')

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_fonoaudio=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_fonoaudio=True)
        context['form'] = FormDocumentoFonoaudiologica(request.POST)
    
    return render(request, 'formularios/docs/form_fonoaudiologica.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_fonoaudiologica(request):
    try:
        if request.session['pdf_fonoaudio']:
            data = request.session['pdf_fonoaudio']
            del request.session['pdf_fonoaudio']
            template = 'documentos/pauta_fono_palabritas.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "Observación clínica fonoaudiológica - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content 
            return response

    except:
        return redirect('listado_fichas_alumnos')


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
                    'alumn_nacim': form_base.cleaned_data['fech_nac'].strftime("%d/%m/%Y"),
                    'fecha_exam': fecha_hoy.strftime("%d/%m/%Y"),
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
                
                request.session['pdf_stsg'] = data
                return redirect('listado_fichas_alumnos')

        if rut:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=True, datos_hab_prag=True)
        else:
            context['form_base'] = FormDatosPersonalesAlumno(request.POST, datos_alumno=False, datos_hab_prag=True)
        context['form'] = FormDocumentoSTSG(request.POST)

    return render(request, 'formularios/docs/form_stsg.html', context)


@login_required
@permission_required('fichas_alumnos.add_bancodocumento')
def generate_pdf_stsg(request):
    try:
        if request.session['pdf_stsg']:
            data = request.session['pdf_stsg']
            del request.session['pdf_stsg']
            template = 'documentos/STSG_Hoja_de_Respuestas.html'
            pdf = render_to_pdf(template, data)
            response = HttpResponse(pdf, content_type='application/pdf') 
            filename = "STSG - %s.pdf" %(data['alumn_nombre'])
            content = 'attachment; filename="{}"'.format(filename)
            response['Content-Disposition'] = content 
            return response

    except:
        return redirect('listado_fichas_alumnos')
