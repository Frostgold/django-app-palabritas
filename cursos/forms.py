from django.forms import ModelForm, Textarea, FileInput
from .models import CronogramaActividad, Curso, DetalleDocente

class FormAgregarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['nivel', 'letra', 'cupos', 'docente_jefe',]


class FormModificarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['cupos', 'docente_jefe',]

class FormCronActividades(ModelForm):

    class Meta:
        model = CronogramaActividad
        fields = ['comentario', 'archivo']
        widgets = {
            'comentario': Textarea(attrs={'rows': 3, 'class': "form-control"}),
            'archivo': FileInput(attrs={'class': "form-control"}),
        }

class FormDetalleDocente(ModelForm):

    class Meta:
        model = DetalleDocente
        fields = ['docente', 'asignatura']

class FormModificarDetalleDocente(ModelForm):

    class Meta:
        model = DetalleDocente
        fields = ['asignatura']
