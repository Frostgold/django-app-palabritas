from django.forms import Form, ModelForm, DateInput, Textarea, FileInput, BaseInlineFormSet, ValidationError, CharField,  ChoiceField, DateField, ModelChoiceField, BooleanField
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

SEXO_F = 'Femenino'
SEXO_M = 'Masculino'
SEXO_CHOICES = [
    (SEXO_F, ('Femenino')),
    (SEXO_M, ('Masculino')),
]

REGEX_RUT_VALIDATOR = r"^(\d{1,3}(?:\d{3}){2}-[\dkK])$"

class FormDatosPersonalesAlumno(Form):
    rut = CharField(required=False, max_length= 11, label="RUT Alumno", help_text="El rut debe ser ingresado sin puntos y con guión.", error_messages={'required': ("Campo RUT requerido."),}, validators=[RegexValidator(REGEX_RUT_VALIDATOR)],)
    nombre = CharField(required=False, max_length= 255, label="Nombre alumno", error_messages={'required': ("Campo nombre requerido.")}, )
    fech_nac = DateField(required=False, label="Fecha Nacimiento", widget=DateInput(format=('%Y-%m-%d'), attrs={'type': "date", 'max':datetime.date.today()}), error_messages={'required': ("Campo fecha de nacimiento requerido."),})
    sexo = ChoiceField(required=False, label="Sexo", choices=SEXO_CHOICES)
    curso = ModelChoiceField(required=False, queryset=Curso.objects.all(), label="Curso")
    nivel = ModelChoiceField(required=False, queryset=Nivel.objects.all(), label="Nivel")
    domicilio = CharField(required=False, max_length= 255, label="Domicilio", error_messages={'required': ("Campo domicilio requerido."),}, )

    def __init__(self, *args, **kwargs):
            datos_hab_prag = kwargs.pop('datos_hab_prag')
            super(FormDatosPersonalesAlumno, self).__init__(*args, **kwargs)
            if datos_hab_prag:
                self.fields['nombre'].widget.attrs['readonly'] = True
                self.fields['fech_nac'].widget.attrs['readonly'] = True
                self.fields['curso'].widget.attrs['disabled'] = True
            else:
                self.fields['nombre'].required = True
                self.fields['fech_nac'].required = True
    


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

# Prim. Grado
PARENT_PAD = 'Padre'
PARENT_MAD = 'Madre'
PARENT_HIO = 'Hijo'
PARENT_HIA = 'Hija'
# Seg. Grado
PARENT_NIO = 'Nieto'
PARENT_NIA = 'Nieta'
PARENT_HEO = 'Hermano'
PARENT_HEA = 'Hermana'
PARENT_ABUO = 'Abuelo'
PARENT_ABUA = 'Abuela'
# Ter. Grado
PARENT_BIZO = 'Biznieto'
PARENT_BIZA = 'Biznieta'
PARENT_SOO = 'Sobrino'
PARENT_SOA = 'Sobrina'
PARENT_TIO = 'Tio'
PARENT_TIA = 'Tia'
PARENT_BISO = 'Bisabuelo'
PARENT_BISA = 'Bisabuela'
# Cuarto grado
PARENT_PRO = 'Primo'
PARENT_PRA = 'Prima'

PARENT_CHOICES = [
    (PARENT_PAD, ('Padre')),
    (PARENT_MAD, ('Madre')),
    (PARENT_HIO, ('Hijo')),
    (PARENT_HIA, ('Hija')),
    (PARENT_NIO, ('Nieto')),
    (PARENT_NIA, ('Nieta')),
    (PARENT_HEO, ('Hermano')),
    (PARENT_HEA, ('Hermana')),
    (PARENT_ABUO, ('Abuelo')),
    (PARENT_ABUA, ('Abuela')),
    (PARENT_BIZO, ('Biznieto')),
    (PARENT_BIZA, ('Biznieta')),
    (PARENT_SOO, ('Sobrino')),
    (PARENT_SOA, ('Sobrina')),
    (PARENT_TIO, ('Tio')),
    (PARENT_TIA, ('Tia')),
    (PARENT_BISO, ('Bisabuelo')),
    (PARENT_BISA, ('Bisabuela')),
    (PARENT_PRO, ('Primo')),
    (PARENT_PRA, ('Prima'))
]
## Actividad motora
ACTI_NORM = 'Normal'
ACTI_HIPERA = 'Hiperactivo'
ACTI_HIPOA = 'Hipoactivo'
ACTI_MOTORA = [ 
    (ACTI_NORM, ('Normal')),
    (ACTI_HIPERA, ('Hiperactivo')),
    (ACTI_HIPOA, ('Hipoactivo'))
]
## Tonalidad muscular
TONA_NORM = 'Normal'
TONA_HIPERT = 'Hipertonico'
TONA_HIPOTO = 'Hipotonico'
TONA_HIPERL = 'Hiperlaxo'
TONA_MUSCULAR = [ 
    (TONA_NORM, ('Normal')),
    (TONA_HIPERT, ('Hipertonico')),
    (TONA_HIPOTO, ('Hipotonico')),
    (TONA_HIPERL, ('Hiperlaxo'))
]
## Motricidad gruesa
GRUE_DOM = 'Dominancia'
GRUE_INES = 'Inestabilidad'
GRUE_CAIDA = 'Caidas'
MOTRI_GRUESA = [ 
    (GRUE_DOM, ('Dominancia')),
    (GRUE_INES, ('Inestabilidad al caminar')),
    (GRUE_CAIDA, ('Caidas frecuentes'))
]

class FormDocumentoAnamnesis(Form):

    # I.
    ## a) Atecedentes familiares
    ### Nombre familiares
    nom_familiar_uno = CharField(required=True, max_length= 50, label="Nombre primer familiar")
    nom_familiar_dos = CharField(required=True, max_length= 50, label="Nombre segundo familiar")
    nom_familiar_tres = CharField(required=True, max_length= 50, label="Nombre tercer familiar")
    nom_familiar_cua = CharField(required=True, max_length= 50, label="Nombre cuarto familiar")
    nom_familiar_cin = CharField(required=True, max_length= 50, label="Nombre quinto familiar")
    ### Parentesco
    parent_uno = ChoiceField(required=False, choices=PARENT_CHOICES, label="Parentesco primer familiar")
    parent_dos = ChoiceField(required=False, choices=PARENT_CHOICES, label="Parentesco segundo familiar")
    parent_tres = ChoiceField(required=False, choices=PARENT_CHOICES, label="Parentesco tercer familiar")
    parent_cua = ChoiceField(required=False, choices=PARENT_CHOICES, label="Parentesco cuarto familiar")
    parent_cin = ChoiceField(required=False, choices=PARENT_CHOICES, label="Parentesco quinto familiar")
    ### Edad
    edad_familiar_uno = CharField(required=True, max_length= 3, label="Edad primer familiar")
    edad_familiar_dos = CharField(required=True, max_length= 3, label="Edad segundo familiar")
    edad_familiar_tres = CharField(required=True, max_length= 3, label="Edad tercer familiar")
    edad_familiar_cua = CharField(required=True, max_length= 3, label="Edad cuarto familiar")
    edad_familiar_cin = CharField(required=True, max_length= 3, label="Edad quinto familiar")
    ### Ocupacion
    ocupa_familiar_uno = CharField(required=True, max_length= 50, label="Ocupación primer familiar")
    ocupa_familiar_dos = CharField(required=True, max_length= 50, label="Ocupación segundo familiar")
    ocupa_familiar_tres = CharField(required=True, max_length= 50, label="Ocupación tercer familiar")
    ocupa_familiar_cua = CharField(required=True, max_length= 50, label="Ocupación cuarto familiar")
    ocupa_familiar_cin = CharField(required=True, max_length= 50, label="Ocupación quinto familiar")
    ## b) Antecedentes Morbidos familiares
    alt_len_rsp = CharField(required=True, max_length= 50, label="Alt. Lenguaje")
    tarta_rsp = CharField(required=True, max_length= 50, label="Tartamudez")
    def_ate_rsp = CharField(required=True, max_length= 50, label="Déf. Atencional")
    epilep_rsp = CharField(required=True, max_length= 50, label="Epilepsia")
    sind_rsp = CharField(required=True, max_length= 50, label="Síndrome")
    def_rsp = CharField(required=True, max_length= 50, label="Deficiencia")
    sord_rsp = CharField(required=True, max_length= 50, label="Sordera")
    def_men_rsp = CharField(required=True, max_length= 50, label="Deficiencia Mental")
    otros_rsp = CharField(required=True, max_length= 50, label="Otros")
    # III.
    ## a) Desarrollo prenatal
    embarazo_num = CharField(required=True, max_length= 2, label="Embarazo N°")
    sem_gest = CharField(required=True, max_length= 3, label="Semanas de gestación")
    med_ant = BooleanField(required=True, label="Medidas anticonceptivas")
    sangr = BooleanField(required=True, label="Sangramiento")
    sint_perd = BooleanField(required=True, label="Sintomas de perdida")
    convul_per = BooleanField(required=True, label="Convulsiones")
    anemia = BooleanField(required=True, label="Anemia")
    intoxi = BooleanField(required=True, label="Intoxicaciones")
    trauma_per = BooleanField(required=True, label="Traumatismos")
    diabete = BooleanField(required=True, label="Diabetes")
    varic_rubeo = BooleanField(required=True, label="Varicela/Rubéola")
    depre = BooleanField(required=True, label="Depresión")
    exp_rx = BooleanField(required=True, label="Exposición a RX")
    desp_place = BooleanField(required=True, label="Despr. Placenta")
    medi_inge = BooleanField(required=True, label="Medicamentos ingeridos")
    enf_infecci = BooleanField(required=True, label="Enfermedades infecciosas")
    ## b) Desarrollo perinatal
    lug_parto = CharField(required=True, max_length=20, label="Lugar de parto")
    espe_parto = BooleanField(required=True, label="Especialista")
    tipo_parto_norm = BooleanField(required=True, label="Parto normal")
    tipo_parto_indu = BooleanField(required=True, label="Inducido")
    tipo_parto_forcep = BooleanField(required=True, label="Fórceps")
    mot_parto = CharField(required=True, max_length=70, label="Motivo")
    cesarea = BooleanField(required=True, label="Cesárea")
    mot_cesarea = CharField(required=True, max_length=70, label="Motivo")

    ant_morb_circuello = BooleanField(required=True, label="Circular al cuello")
    ant_morb_sufrfet = BooleanField(required=True, label="Sufrimiento fetal")
    ant_morb_placprev = BooleanField(required=True, label="Placenta previa")
    ant_morb_ingemeco = BooleanField(required=True, label="Ingesta meconio")
    ant_morb_otros = CharField(required=True, max_length=70, label="Otros")

    peso = CharField(required=True, max_length=10, label="Peso")
    talla = CharField(required=True, max_length=5, label="Talla")
    apgar = CharField(required=True, max_length=20, label="Apgar")
    color = CharField(required=True, max_length=10, label="Color")

    hospi_per = BooleanField(required=True, label="")
    mot_hospi = CharField(required=True, max_length=70, label="")

    trata_medica = CharField(required=True, max_length=100, label="")
    ## c) Antecedentes postnatales
    trauma_post = BooleanField(required=True, label="Traumatismos")
    hospi_post = BooleanField(required=True, label="Hospitalización")
    meningitis = BooleanField(required=True, label="Meningitis")
    encefalitis = BooleanField(required=True, label="Encefalitis")
    fieb_alta = BooleanField(required=True, label="Fiebres altas")
    convul_post = BooleanField(required=True, label="")
    epilep_post = BooleanField(required=True, label="")
    ausencias = BooleanField(required=True, label="")
    bronquitis = BooleanField(required=True, label="")
    sbo = BooleanField(required=True, label="")
    amsa = BooleanField(required=True, label="")
    ira = BooleanField(required=True, label="")
    desnutri = BooleanField(required=True, label="")
    control_med = BooleanField(required=True, label="")
    dr_tratante = CharField(required=True, max_length=40, label="")
    vacu_dia = BooleanField(required=True, label="")
    trata_dental = BooleanField(required=True, label="")
    epoca_dental = CharField(required=True, max_length=20, label="")
    per_derivacion = CharField(required=True, max_length=20, label="")
    mot_dental = CharField(required=True, max_length=70, label="")
    ## d) Examenes realizados
    epoca_exam = CharField(required=True, max_length=20, label="")
    per_deriva_exam = CharField(required=True, max_length=20, label="")
    mot_exam = CharField(required=True, max_length=20, label="")
    # IV.
    ## Edad en que
    fij_cabeza = CharField(required=True, max_length= 2, label="")
    sento_solo = CharField(required=True, max_length= 2, label="")
    gateo = CharField(required=True, max_length= 2, label="")
    camino = CharField(required=True, max_length= 2, label="")
    vist_solo = CharField(required=True, max_length= 2, label="")
    ctl_esf_vdiurno = CharField(required=True, max_length= 2, label="")
    ctl_esf_vnoct = CharField(required=True, max_length= 2, label="")
    ctl_anal_diur = CharField(required=True, max_length= 2, label="")
    ctl_anal_noct = CharField(required=True, max_length= 2, label="")
    entrena_esf = BooleanField(required=True, label="")
    retraso = BooleanField(required=True, label="")
    ## Actividad motora
    act_motora = ChoiceField(required=True, choices=ACTI_MOTORA, label="")
    ## Tonicidad muscular
    toni_muscular = ChoiceField(required=True, choices=TONA_MUSCULAR, label="")
    ## Motricidad gruesa
    motrici_gruesa = ChoiceField(required=True, choices=MOTRI_GRUESA, label="")
    ## Motricidad fina
    toma_cuchara = BooleanField(required=True, label="")
    mov_garra = BooleanField(required=True, label="")
    mov_presion = BooleanField(required=True, label="")
    mov_pinza = BooleanField(required=True, label="")
    # V.
    vocalizo = CharField(required=True, max_length= 2, label="")
    balbuceo = CharField(required=True, max_length= 2, label="")
    jerga = CharField(required=True, max_length= 2, label="")
    prim_palabra = CharField(required=True, max_length= 2, label="")
    holofrase = CharField(required=True, max_length= 2, label="")
    pivote = CharField(required=True, max_length= 2, label="")
    sintagma = CharField(required=True, max_length= 2, label="")
    ## Textos
    texto_uno = CharField(required=True, max_length= 300, label="")
    texto_dos = CharField(required=True, max_length= 300, label="")
    texto_tres = CharField(required=True, max_length= 300, label="")
    texto_cuatro =CharField(required=True, max_length= 300, label="")
    #VI.
    texto_cinco = CharField(required=True, max_length= 300, label="")
    ## Reacciona desmesuradamente ante
    sonido = BooleanField(required=True, label="")
    luces = BooleanField(required=True, label="")
    per_aje_cir = BooleanField(required=True, label="")
    ecolalia = BooleanField(required=True, label="")
    mov_estero = BooleanField(required=True, label="")
    autoagresion = BooleanField(required=True, label="")
    pataleta = BooleanField(required=True, label="")
    dificul_adaptacion = BooleanField(required=True, label="")
    # VII.
    texto_seis = CharField(required=True, max_length= 300, label="")

    class Meta:
        fields = ['__all__']
