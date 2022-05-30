from django.forms import ModelForm, DateInput, Textarea, FileInput, BaseInlineFormSet, ValidationError
import datetime

from .models import FichaAlumno, AvanceAlumno, BancoTrabajo, BancoDocumento, DetalleApoderado

class FormFichaAlumno(ModelForm):
    
    class Meta:
        model = FichaAlumno
        fields = [
            'rut', 
            'nombre', 
            'fecha_nacimiento', 
            'direccion',
            'nombre_padre',
            'nombre_madre',
            'telefono',
            'ficha_social',
            'formulario_salud',
            'certif_nacimiento',
            'consent_fonoaudiologia',
            'consent_vidasana',
        ]
        widgets = {
            'fecha_nacimiento': DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}),
        }
        labels = {
            'nombre': ('Nombre completo'),
            'fecha_nacimiento': ('Fecha de nacimiento'),
            'direccion': ('Dirección del domicilio'),
            'nombre_padre': ('Nombre del padre'),
            'nombre_madre': ('Nombre de la madre'),
            'telefono': ('Teléfono'),
            'ficha_social': ('Ficha social'),
            'formulario_salud': ('Formulario de salud'),
            'certif_nacimiento': ('Certificado de nacimiento'),
            'consent_fonoaudiologia': ('Consentimiento evaluación fonoaudióloga'),
            'consent_vidasana': ('Consentimiento Vida Sana'),
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


# Opciones cambio estado ficha alumno
LISTAESPERA = 'lista_espera'
DOCUMENTOSPENDIENTE = 'documentos_pendientes'
CURSOASIGNADO = 'curso_asignado'
RETIRADO = 'retirado'
HAS_CURSO_CHOICES = [
    (DOCUMENTOSPENDIENTE, ('Documentos pendientes')),
    (CURSOASIGNADO, ('Curso asignado')),
]
HASNT_CURSO_CHOICES = [
    (LISTAESPERA, ('En lista de espera')),
    (DOCUMENTOSPENDIENTE, ('Documentos pendientes')),
]

class FormChangeFichaAlumno(ModelForm):

    def __init__(self, *args, **kwargs):
            has_curso = kwargs.pop('has_curso')
            is_retirado = kwargs.pop('is_retirado')
            super(FormChangeFichaAlumno, self).__init__(*args, **kwargs)
            if has_curso:
                self.fields['estado'].choices = HAS_CURSO_CHOICES
            else:
                self.fields['estado'].choices = HASNT_CURSO_CHOICES
            if is_retirado:
                self.fields['estado'].choices = [(RETIRADO, ('Alumno retirado'))]
                self.fields['estado'].disabled = True
    
    class Meta:
        model = FichaAlumno
        fields = [
            'nombre', 
            'fecha_nacimiento', 
            'estado',
            'direccion',
            'nombre_padre',
            'nombre_madre',
            'telefono',
            'ficha_social',
            'formulario_salud',
            'certif_nacimiento',
            'consent_fonoaudiologia',
            'consent_vidasana',
            ]
        widgets = {
            'fecha_nacimiento': DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}),
        }
        labels = {
            'nombre': ('Nombre completo'),
            'fecha_nacimiento': ('Fecha de nacimiento'),
            'direccion': ('Dirección del domicilio'),
            'nombre_padre': ('Nombre del padre'),
            'nombre_madre': ('Nombre de la madre'),
            'telefono': ('Teléfono'),
            'ficha_social': ('Ficha social'),
            'formulario_salud': ('Formulario de salud'),
            'certif_nacimiento': ('Certificado de nacimiento'),
            'consent_fonoaudiologia': ('Consentimiento evaluación fonoaudióloga'),
            'consent_vidasana': ('Consentimiento Vida Sana'),
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

class ApoderadoBaseFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self:
            form.fields['apoderado'].required = False

class ListaEsperaBaseFormSet(BaseInlineFormSet):
    def clean(self):
        if self.has_changed() == False:
            raise ValidationError('Debe seleccionar el nivel.') 
