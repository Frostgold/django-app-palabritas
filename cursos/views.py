from django.shortcuts import redirect, render
from django.db.models import Q
from .models import Curso, DetalleDocente
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import inlineformset_factory

@login_required
@permission_required('cursos.view_curso', raise_exception=True)
def listado_cursos_view(request):

    context = {}

    # Revisa si el usuario es docente y si es que tiene cursos asginados
    if not request.user.has_perm('cursos.can_view_listado_cursos'):
        lista_cursos = []

        cursos = DetalleDocente.objects.filter(docente=request.user)
        if cursos:
            for curso in cursos:
                lista_cursos.append(curso.curso.id)
            
            listado = Curso.objects.filter(id__in=lista_cursos)

            try:
                if listado:
                    context['listado'] = listado
            except:
                pass

    else:
        context['listado'] = Curso.objects.all()

    return render(request, 'listado_cursos.html', context)
