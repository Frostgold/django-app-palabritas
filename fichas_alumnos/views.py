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
                    'i1': "✔" if form.cleaned_data['item1'] == "1" else "item1",
                    'i2': "✔" if form.cleaned_data['item2'] == "2" else "item2",
                    'i3': "✔" if form.cleaned_data['item3'] == "1" else "item3",
                    'i4': "✔" if form.cleaned_data['item4'] == "3" else "item4",
                    'i5': "✔" if form.cleaned_data['item5'] == "1" else "item5",
                    'i6': "✔" if form.cleaned_data['item6'] == "3" else "item6",
                    'i7': "✔" if form.cleaned_data['item7'] == "1" else "item7",
                    'i8': "✔" if form.cleaned_data['item8'] == "1" else "item8",
                    'i9': "✔" if form.cleaned_data['item9'] == "3" else "item9",
                    'i10': "✔" if form.cleaned_data['item10'] == "2" else "item10",
                    'i11': "✔" if form.cleaned_data['item11'] == "1" else "item11",
                    'i12': "✔" if form.cleaned_data['item12'] == "3" else "item12",
                    'i13': "✔" if form.cleaned_data['item13'] == "1" else "item13",
                    'i14': "✔" if form.cleaned_data['item14'] == "2" else "item14",
                    'i15': "✔" if form.cleaned_data['item15'] == "1" else "item15",
                    'i16': "✔" if form.cleaned_data['item16'] == "3" else "item16",
                    'i17': "✔" if form.cleaned_data['item17'] == "1" else "item17",
                    'i18': "✔" if form.cleaned_data['item18'] == "2" else "item18",
                    'i19': "✔" if form.cleaned_data['item19'] == "3" else "item19",
                    'i20': "✔" if form.cleaned_data['item20'] == "1" else "item20",
                    'i21': "✔" if form.cleaned_data['item21'] == "1" else "item21",
                    'i22': "✔" if form.cleaned_data['item22'] == "3" else "item22",
                    'i23': "✔" if form.cleaned_data['item23'] == "3" else "item23",
                    'i24': "✔" if form.cleaned_data['item24'] == "2" else "item24",
                    'i25': "✔" if form.cleaned_data['item25'] == "3" else "item25",
                    'i26': "✔" if form.cleaned_data['item26'] == "4" else "item26",
                    'i27': "✔" if form.cleaned_data['item27'] == "1" else "item27",
                    'i28': "✔" if form.cleaned_data['item28'] == "2" else "item28",
                    'i29': "✔" if form.cleaned_data['item29'] == "1" else "item29",
                    'i30': "✔" if form.cleaned_data['item30'] == "1" else "item30",
                    'i31': "✔" if form.cleaned_data['item31'] == "3" else "item31",
                    'i32': "✔" if form.cleaned_data['item32'] == "3" else "item32",
                    'i33': "✔" if form.cleaned_data['item33'] == "1" else "item33",
                    'i34': "✔" if form.cleaned_data['item34'] == "2" else "item34",
                    'i35': "✔" if form.cleaned_data['item35'] == "3" else "item35",
                    'i36': "✔" if form.cleaned_data['item36'] == "2" else "item36",
                    'i37': "✔" if form.cleaned_data['item37'] == "1" else "item37",
                    'i38': "✔" if form.cleaned_data['item38'] == "1" else "item38",
                    'i39': "✔" if form.cleaned_data['item39'] == "2" else "item39",
                    'i40': "✔" if form.cleaned_data['item40'] == "3" else "item40",
                    'i41': "✔" if form.cleaned_data['item41'] == "1" else "item41",
                    'i42': "✔" if form.cleaned_data['item42'] == "2" else "item42",
                    'i43': "✔" if form.cleaned_data['item43'] == "2" else "item43",
                    'i44': "✔" if form.cleaned_data['item44'] == "1" else "item44",
                    'i45': "✔" if form.cleaned_data['item45'] == "3" else "item45",
                    'i46': "✔" if form.cleaned_data['item46'] == "2" else "item46",
                    'i47': "✔" if form.cleaned_data['item47'] == "1" else "item47",
                    'i48': "✔" if form.cleaned_data['item48'] == "2" else "item48",
                    'i49': "✔" if form.cleaned_data['item49'] == "1" else "item49",
                    'i50': "✔" if form.cleaned_data['item50'] == "1" else "item50",
                    'i51': "✔" if form.cleaned_data['item51'] == "3" else "item51",
                    'i52': "✔" if form.cleaned_data['item52'] == "2" else "item52",
                    'i53': "✔" if form.cleaned_data['item53'] == "3" else "item53",
                    'i54': "✔" if form.cleaned_data['item54'] == "2" else "item54",
                    'i55': "✔" if form.cleaned_data['item55'] == "1" else "item55",
                    'i56': "✔" if form.cleaned_data['item56'] == "2" else "item56",
                    'i57': "✔" if form.cleaned_data['item57'] == "1" else "item57",
                    'i58': "✔" if form.cleaned_data['item58'] == "1" else "item58",
                    'i59': "✔" if form.cleaned_data['item59'] == "2" else "item59",
                    'i60': "✔" if form.cleaned_data['item60'] == "1" else "item60",
                    'i61': "✔" if form.cleaned_data['item61'] == "3" else "item61",
                    'i62': "✔" if form.cleaned_data['item62'] == "3" else "item62",
                    'i63': "✔" if form.cleaned_data['item63'] == "1" else "item63",
                    'i64': "✔" if form.cleaned_data['item64'] == "1" else "item64",
                    'i65': "✔" if form.cleaned_data['item65'] == "2" else "item65",
                    'i66': "✔" if form.cleaned_data['item66'] == "1" else "item66",
                    'i67': "✔" if form.cleaned_data['item67'] == "3" else "item67",
                    'i68': "✔" if form.cleaned_data['item68'] == "1" else "item68",
                    'i69': "✔" if form.cleaned_data['item69'] == "2" else "item69",
                    'i70': "✔" if form.cleaned_data['item70'] == "1" else "item70",
                    'i71': "✔" if form.cleaned_data['item71'] == "3" else "item71",
                    'i72': "✔" if form.cleaned_data['item72'] == "2" else "item72",
                    'i73': "✔" if form.cleaned_data['item73'] == "2" else "item73",
                    'i74': "✔" if form.cleaned_data['item74'] == "3" else "item74",
                    'i75': "✔" if form.cleaned_data['item75'] == "3" else "item75",
                    'i76': "✔" if form.cleaned_data['item76'] == "3" else "item76",
                    'i77': "✔" if form.cleaned_data['item77'] == "3" else "item77",
                    'i78': "✔" if form.cleaned_data['item78'] == "1" else "item78",
                    'i79': "✔" if form.cleaned_data['item79'] == "2" else "item79",
                    'i80': "✔" if form.cleaned_data['item80'] == "1" else "item80",
                    'i81': "✔" if form.cleaned_data['item81'] == "1" else "item81",
                    'i82': "✔" if form.cleaned_data['item82'] == "3" else "item82",
                    'i83': "✔" if form.cleaned_data['item83'] == "2" else "item83",
                    'i84': "✔" if form.cleaned_data['item84'] == "3" else "item84",
                    'i85': "✔" if form.cleaned_data['item85'] == "2" else "item85",
                    'i86': "✔" if form.cleaned_data['item86'] == "2" else "item86",
                    'i87': "✔" if form.cleaned_data['item87'] == "1" else "item87",
                    'i88': "✔" if form.cleaned_data['item88'] == "3" else "item88",
                    'i89': "✔" if form.cleaned_data['item89'] == "1" else "item89",
                    'i90': "✔" if form.cleaned_data['item90'] == "1" else "item90",
                    'i91': "✔" if form.cleaned_data['item91'] == "2" else "item91",
                    'i92': "✔" if form.cleaned_data['item92'] == "1" else "item92",
                    'i93': "✔" if form.cleaned_data['item93'] == "1" else "item93",
                    'i94': "✔" if form.cleaned_data['item94'] == "3" else "item94",
                    'i95': "✔" if form.cleaned_data['item95'] == "2" else "item95",
                    'i96': "✔" if form.cleaned_data['item96'] == "1" else "item96",
                    'i97': "✔" if form.cleaned_data['item97'] == "3" else "item97",
                    'i98': "✔" if form.cleaned_data['item98'] == "3" else "item98",
                    'i99': "✔" if form.cleaned_data['item99'] == "2" else "item99",
                    'i100': "✔" if form.cleaned_data['item100'] =="2" else "item100",
                    'i101': "✔" if form.cleaned_data['item101'] == "1" else "item101",
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

                data = {
                    'alumn_nombre': form_base.cleaned_data['nombre'],
                    'alumn_edad': "{} y {}".format("{} años".format(edad_anio) if edad_anio != 1 else "{} año".format(edad_anio), "{} meses".format(edad_mes) if edad_mes != 1 else "{} mes".format(edad_mes)),
                    'alumn_nacim': form_base.cleaned_data['fech_nac'],
                    'fecha_exam': fecha_hoy,
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
