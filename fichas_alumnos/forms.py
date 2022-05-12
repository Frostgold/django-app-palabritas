from django.forms import ModelForm, DateInput, Textarea, FileInput
import datetime

from .models import FichaAlumno, AvanceAlumno, BancoTrabajo, BancoDocumento, DetalleApoderado

class AgregarFichaAlumno(ModelForm):
    
    class Meta:
        model = FichaAlumno
        fields = ['rut', 'nombre', 'fecha_nacimiento',]
        widgets = {
            'fecha_nacimiento': DateInput(attrs={'type':"date", 'max':datetime.date.today()}),
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

class AgregarAvanceAlumno(ModelForm):
    
    class Meta:
        model = AvanceAlumno
        fields = ['comentario',]
        widgets = {
            'comentario': Textarea(attrs={'rows': 3, 'class': "form-control"}),
        }

class AgregarTrabajoAlumno(ModelForm):
    
    class Meta:
        model = BancoTrabajo
        fields = ['trabajo',]
        widgets = {
            'trabajo': FileInput(attrs={'class': "form-control"}),
        }

class AgregarDocumentoAlumno(ModelForm):
    
    class Meta:
        model = BancoDocumento
        fields = ['documento',]
        widgets = {
            'documento': FileInput(attrs={'class': "form-control"}),
        }

