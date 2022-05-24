import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .models import ListaEspera
from cursos.models import Nivel, Curso
from fichas_alumnos.models import FichaAlumno

@login_required
@permission_required('lista_espera.view_listaespera', raise_exception=True)
def listado_lista_espera_view(request):

    context = {}

    # Consigue listado de nivel cursos
    context['nivel'] = Nivel.objects.all()

    context['listado'] = ListaEspera.objects.all()
    context['cupos'] = "No"

    if 'error' in request.session:
        context['error'] = request.session['error']
        del request.session['error']
    if 'success' in request.session:
        context['success'] = request.session['success']
        del request.session['success']

    if request.method == 'GET':

        if request.GET.get('nivel') and request.GET.get('nivel') != "":
            query = request.GET.get('nivel')

            try:
                print(int(query))
            except ValueError:
                return redirect('listado_lista_espera')

            object_list = context['listado'].filter(
                Q(nivel=query)
            )
            context['listado'] = object_list
            context['query'] = Nivel.objects.get(id=query)

            cursos = Curso.objects.filter(Q(nivel=query) & Q(periodo=datetime.datetime.now().year))
            context['cupos'] = 0
            for curso in cursos:
                alumnos = FichaAlumno.objects.filter(curso_id=curso.id).count()
                context['cupos']+=curso.cupos
                context['cupos']-=alumnos

            context['avanzan'] = object_list.count()
            if context['avanzan'] > context['cupos']:
                context['avanzan'] = context['cupos']

    return render(request, 'listado_lista_espera.html', context)


@login_required
@permission_required('lista_espera.can_avanzar_lista_espera', raise_exception=True)
def avanzar_lista_espera_view(request, kwargs):

    # Verifica que se ingrese a la vista desde la redirección del bóton avanzar lista de espera
    redirect_from = request.META.get('HTTP_REFERER')
    if "/lista_espera/" in str(redirect_from) or "/detalle_curso/" in str(redirect_from):
        cupos = 0
        if "/lista_espera/" in str(redirect_from):
            query_nivel = kwargs
            cursos = Curso.objects.filter(Q(nivel=query_nivel) & Q(periodo=datetime.datetime.now().year)).order_by()
            for curso in cursos:
                lista_espera = ListaEspera.objects.filter(nivel=query_nivel).order_by()
                if not lista_espera:
                    break
                alumnos = FichaAlumno.objects.filter(curso_id=curso.id).count()
                cupos+=curso.cupos
                cupos-=alumnos
                for ficha in lista_espera:
                    if cupos == 0:
                        break
                    alumno = FichaAlumno.objects.get(rut=ficha.alumno.rut)
                    alumno.asignar_curso(curso)
                    ficha.delete()
                    cupos-=1
                    request.session['success'] = "Se avanzó la lista de espera del nivel {0}.".format(curso.nivel.descripcion)

        if "/detalle_curso/" in str(redirect_from):
            curso = Curso.objects.get(Q(id=kwargs) & Q(periodo=datetime.datetime.now().year))
            lista_espera = ListaEspera.objects.filter(nivel=curso.nivel).order_by()
            if not lista_espera:
                request.session['error'] = "No hay alumnos en lista de espera para este nivel."
            alumnos = FichaAlumno.objects.filter(curso_id=curso.id).count()
            cupos+=curso.cupos
            cupos-=alumnos
            for ficha in lista_espera:
                if cupos == 0:
                    break
                alumno = FichaAlumno.objects.get(rut=ficha.alumno.rut)
                alumno.asignar_curso(curso)
                ficha.delete()
                cupos-=1
                request.session['success'] = "Se avanzó la lista de espera del nivel {0} en el curso {1}.".format(curso.nivel.descripcion, curso.nombre)

        return redirect(redirect_from)


    return redirect('inicio')
