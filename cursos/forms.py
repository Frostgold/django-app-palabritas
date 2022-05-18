from django.forms import ModelForm, Textarea, FileInput
from .models import CronogramaActividad, Curso, DetalleDocente

class FormAgregarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['nivel', 'letra', 'cupos']


class FormModificarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['cupos']

class FormCronActividades(ModelForm):

    class Meta:
        model = CronogramaActividad
        fields = ['comentario', 'imagen']
        widgets = {
            'comentario': Textarea(attrs={'rows': 3, 'class': "form-control"}),
            'imagen': FileInput(attrs={'class': "form-control"}),
        }

class FormDetalleDocente(ModelForm):

    class Meta:
        model = DetalleDocente
        fields = ['docente', 'asignatura']

class FormModificarDetalleDocente(ModelForm):

    class Meta:
        model = DetalleDocente
        fields = ['asignatura']
