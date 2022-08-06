from django.forms import Form, ModelForm, DateInput, Textarea, FileInput, BaseInlineFormSet, ValidationError, CharField,  ChoiceField, DateField, ModelChoiceField
import datetime
from django.core.validators import RegexValidator

from cursos.models import Curso

from .models import FichaAlumno, AvanceAlumno, BancoTrabajo, BancoDocumento, DetalleApoderado
from cursos.models import Nivel, Curso
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
            'anamnesis',
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
            'anamnesis': ('Anamnesis'),
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
            'anamnesis',
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
            'anamnesis': ('Anamnesis'),
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


SI = 'si'
NO = 'no'
A_VECES = 'av'
COTEJO_CHOICES = [
    (NO, ('No')),
    (SI, ('Sí')),
    (A_VECES, ('A veces')),
]

SEXO_F = 'F'
SEXO_M = 'M'
SEXO_CHOICES = [
    (SEXO_F, ('Femenino')),
    (SEXO_M, ('Masculino')),
]

REGEX_RUT_VALIDATOR = r"^(\d{1,3}(?:\d{3}){2}-[\dkK])$"

class FormDatosPersonalesAlumno(Form):
    rut = CharField(required=True, max_length= 11, label="RUT Alumno", help_text="El rut debe ser ingresado sin puntos y con guión.", error_messages={'required': ("Campo RUT requerido."),}, validators=[RegexValidator(REGEX_RUT_VALIDATOR)],)
    nombre = CharField(required=True, max_length= 255, label="Nombre alumno", error_messages={'required': ("Campo nombre requerido.")}, )
    fech_nac = DateField(required=True, label="Fecha Nacimiento", widget=DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}), error_messages={'required': ("Campo fecha de nacimiento requerido."),})
    sexo = ChoiceField(required=True, label="Sexo", choices=SEXO_CHOICES)
    curso = ModelChoiceField(required=True, queryset=Curso.objects.all(), label="Curso")
    nivel = ModelChoiceField(required=True, queryset=Nivel.objects.all(), label="Nivel")
    domicilio = CharField(required=True, max_length= 255, label="Domicilio", error_messages={'required': ("Campo domicilio requerido."),}, )
    


class DocumentoPautaCotejo(Form):
    cinetica = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Usa gestos adecuados para comunicarse.", label="Cinética")
    proxemica = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Mantiene distancias y posturas.", label="Proxémica")
    intencion = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Comunica sus deseos y/o necesidades.", label="Intención")
    cont_visual = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Mantiene contacto visual adecuado.", label="Contacto Visual")
    exp_facial = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Corresponde al mensaje e interpreta expresiones.", label="Expresión Facial")
    fac_conversacional = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Sabe conversar, iniciar, responder, preguntar, interrumpir, etc.", label="Facultades Conversacional")
    var_estilisticas = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Adapta su conversación al auditorio y a las circunstancias.", label="Variaciones Estilísticas")
    alt_reciproca = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Sabe mantener un diálogo.", label="Alternancia Recíproca")
    tematizacion = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Puede mantenerse en el tema.", label="Tematización")
    peticiones = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Formula peticiones completas.", label="Peticiones")
    aclar_rep = ChoiceField(required=True, choices=COTEJO_CHOICES, help_text="Pide y entrega aclaraciones en caso de dudas.", label="Aclaración y Reparación")

    class Meta:
        fields = ['__all__']
