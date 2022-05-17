from django.forms import ModelForm, DateInput, Textarea, FileInput
import datetime

from .models import FichaAlumno, AvanceAlumno, BancoTrabajo, BancoDocumento, DetalleApoderado

class FormFichaAlumno(ModelForm):
    
    class Meta:
        model = FichaAlumno
        fields = ['rut', 'nombre', 'fecha_nacimiento', 'estado',]
        widgets = {
            'fecha_nacimiento': DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}),
        }
        labels = {
            'nombre': ('Nombre completo'),
            'fecha_nacimiento': ('Fecha de nacimiento'),
        }
        error_messages = {
            'rut': {
                'unique': ("La ficha de este alumno ya se encuentra creada."),
                'required': ("Campo rut alumno requerido."),
            },
            'nombre': {
                'required': ("Campo nombre requerido."),
            },
            'fecha_nacimiento': {
                'required': ("Campo fecha de nacimiento requerido."),
            },
        }

class FormChangeFichaAlumno(ModelForm):
    
    class Meta:
        model = FichaAlumno
        fields = ['nombre', 'fecha_nacimiento',]
        widgets = {
            'fecha_nacimiento': DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}),
        }
        labels = {
            'nombre': ('Nombre completo'),
            'fecha_nacimiento': ('Fecha de nacimiento'),
        }
        error_messages = {
            'nombre': {
                'required': ("Campo nombre requerido."),
            },
            'fecha_nacimiento': {
                'required': ("Campo fecha de nacimiento requerido."),
            },
        }

class FormAvanceAlumno(ModelForm):
    
    class Meta:
        model = AvanceAlumno
        fields = ['comentario',]
        widgets = {
            'comentario': Textarea(attrs={'rows': 3, 'class': "form-control"}),
        }
        labels = {
            'comentario': (''),
        }
        error_messages = {
            'comentario': {
                'required': ("Este campo no se puede ingresar vacío."),
            },
        }

class FormTrabajoAlumno(ModelForm):
    
    class Meta:
        model = BancoTrabajo
        fields = ['trabajo',]
        widgets = {
            'trabajo': FileInput(attrs={'class': "form-control"}),
        }

class FormDocumentoAlumno(ModelForm):
    
    class Meta:
        model = BancoDocumento
        fields = ['documento',]
        widgets = {
            'documento': FileInput(attrs={'class': "form-control"}),
        }

