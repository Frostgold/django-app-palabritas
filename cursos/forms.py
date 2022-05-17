from django.forms import ModelForm
from .models import Curso

class FormAgregarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['nivel', 'letra', 'cupos']


class FormModificarCurso(ModelForm):

    class Meta:
        model = Curso
        fields = ['cupos']