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
            datos_alumno = kwargs.pop('datos_alumno')
            #Configuración para campos de habilidades pragmáticas
            try:
                datos_hab_prag = kwargs.pop('datos_hab_prag')
            except:
                pass
            #Configuración para campos de fonoaudiológica
            try:
                datos_fonoaudio = kwargs.pop('datos_fonoaudio')
            except:
                pass
            #Configuración para campos de teprosif
            try:
                datos_teprosif = kwargs.pop('datos_teprosif')
            except:
                pass
            #Configuración para campos de anamnesis
            try:
                datos_anamnesis = kwargs.pop('datos_anamnesis')
            except:
                pass
            try:
                datos_retirado = kwargs.pop('datos_retirado')
            except:
                pass

            super(FormDatosPersonalesAlumno, self).__init__(*args, **kwargs)
            #Configuración para campos de habilidades pragmáticas
            try:
                if datos_hab_prag:
                    self.fields['nombre'].required = True
                    self.fields['fech_nac'].required = True
                    if datos_alumno:
                        self.fields['nombre'].widget.attrs['readonly'] = True
                        self.fields['fech_nac'].widget.attrs['readonly'] = True
                        self.fields['curso'].widget.attrs['disabled'] = True
            except:
                pass

            #Configuración para campos de fonoaudiológica
            try:
                if datos_fonoaudio:
                    self.fields['nombre'].required = True
                    self.fields['fech_nac'].required = True
                    self.fields['domicilio'].required = True
                    self.fields['rut'].required = True
                    if datos_alumno:
                        self.fields['nombre'].widget.attrs['readonly'] = True
                        self.fields['fech_nac'].widget.attrs['readonly'] = True
                        self.fields['domicilio'].widget.attrs['readonly'] = True
                        self.fields['rut'].widget.attrs['readonly'] = True
            except:
                pass

            #Configuración para campos de teprosif
            try:
                if datos_teprosif:
                    self.fields['nombre'].required = True
                    self.fields['fech_nac'].required = True
                    self.fields['sexo'].required = True
                    if datos_alumno:
                        self.fields['nombre'].widget.attrs['readonly'] = True
                        self.fields['fech_nac'].widget.attrs['readonly'] = True
            except:
                pass

            #Configuración para campos de anamnesis
            try:
                if datos_anamnesis:
                    self.fields['nombre'].required = True
                    self.fields['fech_nac'].required = True
                    self.fields['nivel'].required = True
                    self.fields['domicilio'].required = True
                    if datos_alumno:
                        self.fields['nombre'].widget.attrs['readonly'] = True
                        self.fields['fech_nac'].widget.attrs['readonly'] = True
                        self.fields['curso'].widget.attrs['disabled'] = True
                        if not datos_retirado:
                            self.fields['nivel'].widget.attrs['disabled'] = True
                        self.fields['domicilio'].widget.attrs['readonly'] = True
            except:
                pass


class FormDocumentoPautaCotejo(Form):
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
    esco_actual = CharField(required=True, max_length=20, label="Escolaridad actual")
    histo_esco = CharField(required=True, max_length=20, label="Historia escolar")
    nom_entrevis = CharField(required=True, max_length=20, label="Nombre entrevistador")
    datos_propor = CharField(required=True, max_length=20, label="Datos proporcionados por")
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
    med_ant = BooleanField(required=False, label="Medidas anticonceptivas")
    sangr = BooleanField(required=False, label="Sangramiento")
    sint_perd = BooleanField(required=False, label="Sintomas de perdida")
    convul_per = BooleanField(required=False, label="Convulsiones")
    anemia = BooleanField(required=False, label="Anemia")
    intoxi = BooleanField(required=False, label="Intoxicaciones")
    trauma_per = BooleanField(required=False, label="Traumatismos")
    diabete = BooleanField(required=False, label="Diabetes")
    varic_rubeo = BooleanField(required=False, label="Varicela/Rubéola")
    depre = BooleanField(required=False, label="Depresión")
    exp_rx = BooleanField(required=False, label="Exposición a RX")
    desp_place = BooleanField(required=False, label="Despr. Placenta")
    medi_inge = BooleanField(required=False, label="Medicamentos ingeridos")
    enf_infecci = BooleanField(required=False, label="Enfermedades infecciosas")
    ## b) Desarrollo perinatal
    lug_parto = CharField(required=True, max_length=20, label="Lugar de parto")
    espe_parto = BooleanField(required=False, label="Especialista")
    tipo_parto_norm = BooleanField(required=False, label="Parto normal")
    tipo_parto_indu = BooleanField(required=False, label="Inducido")
    tipo_parto_forcep = BooleanField(required=False, label="Fórceps")
    mot_parto = CharField(required=False, max_length=70, label="Motivo")
    cesarea = BooleanField(required=False, label="Cesárea")
    mot_cesarea = CharField(required=False, max_length=70, label="Motivo")

    ant_morb_circuello = BooleanField(required=False, label="Circular al cuello")
    ant_morb_sufrfet = BooleanField(required=False, label="Sufrimiento fetal")
    ant_morb_placprev = BooleanField(required=False, label="Placenta previa")
    ant_morb_ingemeco = BooleanField(required=False, label="Ingesta meconio")
    ant_morb_otros = CharField(required=True, max_length=70, label="Otros")

    peso = CharField(required=True, max_length=10, label="Peso")
    talla = CharField(required=True, max_length=5, label="Talla")
    apgar = CharField(required=True, max_length=20, label="Apgar")
    color = CharField(required=True, max_length=10, label="Color")

    hospi_per = BooleanField(required=False, label="Hospitalización")
    mot_hospi = CharField(required=False, max_length=70, label="Motivo")

    trata_medica = CharField(required=True, max_length=100, label="Tratamiento / Medicamentos")
    ## c) Antecedentes postnatales
    trauma_post = BooleanField(required=False, label="Traumatismos")
    hospi_post = BooleanField(required=False, label="Hospitalización")
    meningitis = BooleanField(required=False, label="Meningitis")
    encefalitis = BooleanField(required=False, label="Encefalitis")
    fieb_alta = BooleanField(required=False, label="Fiebres altas")
    convul_post = BooleanField(required=False, label="Convulsiones")
    epilep_post = BooleanField(required=False, label="Epilepsia")
    ausencias = BooleanField(required=False, label="Ausensias")
    bronquitis = BooleanField(required=False, label="Bronquitis")
    sbo = BooleanField(required=False, label="SBO")
    amsa = BooleanField(required=False, label="Asma")
    ira = BooleanField(required=False, label="IRA")
    desnutri = BooleanField(required=False, label="Desnutrición")
    otros_morb = CharField(required=True, max_length=40, label="Otros eventos mórbidos")
    control_med = BooleanField(required=False, label="Asiste a controles médicos periódicos")
    dr_tratante = CharField(required=True, max_length=40, label="Dr. Tratante")
    vacu_dia = BooleanField(required=False, label="Vacunas al día")
    trata_dental = BooleanField(required=False, label="Tratamientos dentales")
    epoca_dental = CharField(required=True, max_length=20, label="Época")
    per_derivacion = CharField(required=True, max_length=20, label="Persona que lo derivó")
    mot_dental = CharField(required=True, max_length=70, label="Motivo")
    ## d) Examenes realizados
    epoca_exam = CharField(required=True, max_length=20, label="Época")
    per_deriva_exam = CharField(required=True, max_length=20, label="Persona que lo derivó")
    mot_exam = CharField(required=True, max_length=20, label="Motivo")
    # IV.
    ## Edad en que
    fij_cabeza = CharField(required=True, max_length= 2, label="Fijó la cabeza")
    sento_solo = CharField(required=True, max_length= 2, label="Se sentó solo")
    gateo = CharField(required=True, max_length= 2, label="Gateó")
    camino = CharField(required=True, max_length= 2, label="Caminó")
    vist_solo = CharField(required=True, max_length= 2, label="Se vistió solo")
    ctl_esf_vdiurno = CharField(required=True, max_length= 2, label="Vesical Diurno")
    ctl_esf_vnoct = CharField(required=True, max_length= 2, label="Nocturno")
    ctl_anal_diur = CharField(required=True, max_length= 2, label="Anal diurno")
    ctl_anal_noct = CharField(required=True, max_length= 2, label="Nocturno")
    entrena_esf = BooleanField(required=False, label="¿Hubo entrenamiento en control de esfínter?")
    retraso = BooleanField(required=False, label="Retraso")
    ## Actividad motora
    act_motora = ChoiceField(required=True, choices=ACTI_MOTORA, label="Actividad motora")
    ## Tonicidad muscular
    toni_muscular = ChoiceField(required=True, choices=TONA_MUSCULAR, label="Tonacidad muscular")
    ## Motricidad gruesa
    motrici_gruesa = ChoiceField(required=True, choices=MOTRI_GRUESA, label="Motricidad gruesa")
    ## Motricidad fina
    toma_cuchara = BooleanField(required=False, label="Toma adecuadamente la cuchara")
    mov_garra = BooleanField(required=False, label="Garra")
    mov_presion = BooleanField(required=False, label="Presión")
    mov_pinza = BooleanField(required=False, label="Pinza")
    # V.
    vocalizo = CharField(required=True, max_length= 2, label="Vocalizó")
    balbuceo = CharField(required=True, max_length= 2, label="Balbuceó")
    jerga = CharField(required=True, max_length= 2, label="Jerga")
    prim_palabra = CharField(required=True, max_length= 2, label="1° Palabra")
    holofrase = CharField(required=True, max_length= 2, label="Holofrases")
    pivote = CharField(required=True, max_length= 2, label="Pivotes")
    sintagma = CharField(required=True, max_length= 2, label="Sintagma")
    ## Textos
    texto_uno = CharField(required=True, max_length= 300, label=" ", help_text="Indicar edad primeras palabras, edad primeras frases, otros.")
    texto_dos = CharField(required=True, max_length= 300, label="", help_text="Indicar cómo se comunica, si presenta intencionalidad comunicativa, si se aprecia comprensión, otros")
    texto_tres = CharField(required=True, max_length= 300, label="", help_text="Indicar cómo se percibe la acuidad auditiva del niño, si busca la fuente de sonido, si se necesita repetir varias veces información determinada, si se necesita subir tono de voz para llamar su atención, otros.")
    texto_cuatro =CharField(required=True, max_length= 300, label="", help_text="Indicar si les leen cuentos en casa, de qué tipo, cuántas veces a la semana, cómo se los presentan, ¿les hacen preguntas respecto a personajes, trama, contexto, palabras nuevas (vocabulario), problema y solución de la historia? (conducta lectora)")
    #VI.
    texto_cinco = CharField(required=True, max_length= 300, label="", help_text="Indicar tipo de juegos preferidos, si juega sólo o busca compañía, relación con sus pares, relación con adultos, reacción frente a la frustración, respeta normas, recibe castigos o sanciones, otros.")
    ## Reacciona desmesuradamente ante
    sonido = BooleanField(required=False, label="Sonido")
    luces = BooleanField(required=False, label="Luces")
    per_aje_cir = BooleanField(required=False, label="Personas ajenas a su círculo")
    ecolalia = BooleanField(required=False, label="Ecolalia")
    mov_estero = BooleanField(required=False, label="Mov. Estereotipados")
    autoagresion = BooleanField(required=False, label="Autoagresiones")
    pataleta = BooleanField(required=False, label="Realiza pataletas frecuentes y exageradas")
    dificul_adaptacion = BooleanField(required=False, label="Presenta dificultades para adaptarse a nuevas situaciones")
    # VII.
    texto_seis = CharField(required=True, max_length= 300, label="VII. Observaciones relevantes", )

    class Meta:
        fields = ['__all__']


class FormDocumentoTecal(Form):

    item1 = CharField(required=True, max_length= 1, label="Item 1", help_text="Respuesta correcta: 1")
    item2 = CharField(required=True, max_length= 1, label="Item 2", help_text="Respuesta correcta: 2")
    item3 = CharField(required=True, max_length= 1, label="Item 3", help_text="Respuesta correcta: 1")
    item4 = CharField(required=True, max_length= 1, label="Item 4", help_text="Respuesta correcta: 3")
    item5 = CharField(required=True, max_length= 1, label="Item 5", help_text="Respuesta correcta: 1")
    item6 = CharField(required=True, max_length= 1, label="Item 6", help_text="Respuesta correcta: 3")
    item7 = CharField(required=True, max_length= 1, label="Item 7", help_text="Respuesta correcta: 1")
    item8 = CharField(required=True, max_length= 1, label="Item 8", help_text="Respuesta correcta: 1")
    item9 = CharField(required=True, max_length= 1, label="Item 9", help_text="Respuesta correcta: 3")
    item10 = CharField(required=True, max_length=1, label="Item 10", help_text="Respuesta correcta: 2")

    item11 = CharField(required=True, max_length= 1, label="Item 11", help_text="Respuesta correcta: 1")
    item12 = CharField(required=True, max_length= 1, label="Item 12", help_text="Respuesta correcta: 3")
    item13 = CharField(required=True, max_length= 1, label="Item 13", help_text="Respuesta correcta: 1")
    item14 = CharField(required=True, max_length= 1, label="Item 14", help_text="Respuesta correcta: 2")
    item15 = CharField(required=True, max_length= 1, label="Item 15", help_text="Respuesta correcta: 1")
    item16 = CharField(required=True, max_length= 1, label="Item 16", help_text="Respuesta correcta: 3")
    item17 = CharField(required=True, max_length= 1, label="Item 17", help_text="Respuesta correcta: 1")
    item18 = CharField(required=True, max_length= 1, label="Item 18", help_text="Respuesta correcta: 2")
    item19 = CharField(required=True, max_length= 1, label="Item 19", help_text="Respuesta correcta: 3")
    item20 = CharField(required=True, max_length= 1, label="Item 20", help_text="Respuesta correcta: 1")

    item21 = CharField(required=True, max_length= 1, label="Item 21", help_text="Respuesta correcta: 1")
    item22 = CharField(required=True, max_length= 1, label="Item 22", help_text="Respuesta correcta: 3")
    item23 = CharField(required=True, max_length= 1, label="Item 23", help_text="Respuesta correcta: 3")
    item24 = CharField(required=True, max_length= 1, label="Item 24", help_text="Respuesta correcta: 2")
    item25 = CharField(required=True, max_length= 1, label="Item 25", help_text="Respuesta correcta: 3")
    item26 = CharField(required=True, max_length= 1, label="Item 26", help_text="Respuesta correcta: 4")
    item27 = CharField(required=True, max_length= 1, label="Item 27", help_text="Respuesta correcta: 1")
    item28 = CharField(required=True, max_length= 1, label="Item 28", help_text="Respuesta correcta: 2")
    item29 = CharField(required=True, max_length= 1, label="Item 29", help_text="Respuesta correcta: 1")
    item30 = CharField(required=True, max_length= 1, label="Item 30", help_text="Respuesta correcta: 1")

    item31 = CharField(required=True, max_length= 1, label="Item 31", help_text="Respuesta correcta: 3")
    item32 = CharField(required=True, max_length= 1, label="Item 32", help_text="Respuesta correcta: 3")
    item33 = CharField(required=True, max_length= 1, label="Item 33", help_text="Respuesta correcta: 1")
    item34 = CharField(required=True, max_length= 1, label="Item 34", help_text="Respuesta correcta: 2")
    item35 = CharField(required=True, max_length= 1, label="Item 35", help_text="Respuesta correcta: 3")
    item36 = CharField(required=True, max_length= 1, label="Item 36", help_text="Respuesta correcta: 2")
    item37 = CharField(required=True, max_length= 1, label="Item 37", help_text="Respuesta correcta: 1")
    item38 = CharField(required=True, max_length= 1, label="Item 38", help_text="Respuesta correcta: 1")
    item39 = CharField(required=True, max_length= 1, label="Item 39", help_text="Respuesta correcta: 2")
    item40 = CharField(required=True, max_length= 1, label="Item 40", help_text="Respuesta correcta: 3")

    item41 = CharField(required=True, max_length= 1, label="Item 41", help_text="Respuesta correcta: 1")
    item42 = CharField(required=True, max_length= 1, label="Item 42", help_text="Respuesta correcta: 2")
    item43 = CharField(required=True, max_length= 1, label="Item 43", help_text="Respuesta correcta: 2")
    item44 = CharField(required=True, max_length= 1, label="Item 44", help_text="Respuesta correcta: 1")
    item45 = CharField(required=True, max_length= 1, label="Item 45", help_text="Respuesta correcta: 3")
    item46 = CharField(required=True, max_length= 1, label="Item 46", help_text="Respuesta correcta: 2")
    item47 = CharField(required=True, max_length= 1, label="Item 47", help_text="Respuesta correcta: 1")
    item48 = CharField(required=True, max_length= 1, label="Item 48", help_text="Respuesta correcta: 2")
    item49 = CharField(required=True, max_length= 1, label="Item 49", help_text="Respuesta correcta: 1")
    item50 = CharField(required=True, max_length= 1, label="Item 50", help_text="Respuesta correcta: 1")

    item51 = CharField(required=True, max_length= 1, label="Item 51", help_text="Respuesta correcta: 3")
    item52 = CharField(required=True, max_length= 1, label="Item 52", help_text="Respuesta correcta: 2")
    item53 = CharField(required=True, max_length= 1, label="Item 53", help_text="Respuesta correcta: 3")
    item54 = CharField(required=True, max_length= 1, label="Item 54", help_text="Respuesta correcta: 2")
    item55 = CharField(required=True, max_length= 1, label="Item 55", help_text="Respuesta correcta: 1")
    item56 = CharField(required=True, max_length= 1, label="Item 56", help_text="Respuesta correcta: 2")
    item57 = CharField(required=True, max_length= 1, label="Item 57", help_text="Respuesta correcta: 1")
    item58 = CharField(required=True, max_length= 1, label="Item 58", help_text="Respuesta correcta: 1")
    item59 = CharField(required=True, max_length= 1, label="Item 59", help_text="Respuesta correcta: 2")
    item60 = CharField(required=True, max_length= 1, label="Item 60", help_text="Respuesta correcta: 1")

    item61 = CharField(required=True, max_length= 1, label="Item 61", help_text="Respuesta correcta: 3")
    item62 = CharField(required=True, max_length= 1, label="Item 62", help_text="Respuesta correcta: 3")
    item63 = CharField(required=True, max_length= 1, label="Item 63", help_text="Respuesta correcta: 1")
    item64 = CharField(required=True, max_length= 1, label="Item 64", help_text="Respuesta correcta: 1")
    item65 = CharField(required=True, max_length= 1, label="Item 65", help_text="Respuesta correcta: 2")
    item66 = CharField(required=True, max_length= 1, label="Item 66", help_text="Respuesta correcta: 1")
    item67 = CharField(required=True, max_length= 1, label="Item 67", help_text="Respuesta correcta: 3")
    item68 = CharField(required=True, max_length= 1, label="Item 68", help_text="Respuesta correcta: 1")
    item69 = CharField(required=True, max_length= 1, label="Item 69", help_text="Respuesta correcta: 2")
    item70 = CharField(required=True, max_length= 1, label="Item 70", help_text="Respuesta correcta: 1")

    item71 = CharField(required=True, max_length= 1, label="Item 71", help_text="Respuesta correcta: 3")
    item72 = CharField(required=True, max_length= 1, label="Item 72", help_text="Respuesta correcta: 2")
    item73 = CharField(required=True, max_length= 1, label="Item 73", help_text="Respuesta correcta: 2")
    item74 = CharField(required=True, max_length= 1, label="Item 74", help_text="Respuesta correcta: 3")
    item75 = CharField(required=True, max_length= 1, label="Item 75", help_text="Respuesta correcta: 3")
    item76 = CharField(required=True, max_length= 1, label="Item 76", help_text="Respuesta correcta: 3")
    item77 = CharField(required=True, max_length= 1, label="Item 77", help_text="Respuesta correcta: 3")
    item78 = CharField(required=True, max_length= 1, label="Item 78", help_text="Respuesta correcta: 1")
    item79 = CharField(required=True, max_length= 1, label="Item 79", help_text="Respuesta correcta: 2")
    item80 = CharField(required=True, max_length= 1, label="Item 80", help_text="Respuesta correcta: 1")

    item81 = CharField(required=True, max_length= 1, label="Item 81", help_text="Respuesta correcta: 1")
    item82 = CharField(required=True, max_length= 1, label="Item 82", help_text="Respuesta correcta: 3")
    item83 = CharField(required=True, max_length= 1, label="Item 83", help_text="Respuesta correcta: 2")
    item84 = CharField(required=True, max_length= 1, label="Item 84", help_text="Respuesta correcta: 3")
    item85 = CharField(required=True, max_length= 1, label="Item 85", help_text="Respuesta correcta: 2")
    item86 = CharField(required=True, max_length= 1, label="Item 86", help_text="Respuesta correcta: 2")
    item87 = CharField(required=True, max_length= 1, label="Item 87", help_text="Respuesta correcta: 1")
    item88 = CharField(required=True, max_length= 1, label="Item 88", help_text="Respuesta correcta: 3")
    item89 = CharField(required=True, max_length= 1, label="Item 89", help_text="Respuesta correcta: 1")
    item90 = CharField(required=True, max_length= 1, label="Item 90", help_text="Respuesta correcta: 1")

    item91 = CharField(required=True, max_length= 1, label="Item 91", help_text="Respuesta correcta: 2")
    item92 = CharField(required=True, max_length= 1, label="Item 92", help_text="Respuesta correcta: 1")
    item93 = CharField(required=True, max_length= 1, label="Item 93", help_text="Respuesta correcta: 1")
    item94 = CharField(required=True, max_length= 1, label="Item 94", help_text="Respuesta correcta: 3")
    item95 = CharField(required=True, max_length= 1, label="Item 95", help_text="Respuesta correcta: 2")
    item96 = CharField(required=True, max_length= 1, label="Item 96", help_text="Respuesta correcta: 1")
    item97 = CharField(required=True, max_length= 1, label="Item 97", help_text="Respuesta correcta: 3")
    item98 = CharField(required=True, max_length= 1, label="Item 98", help_text="Respuesta correcta: 3")
    item99 = CharField(required=True, max_length= 1, label="Item 99", help_text="Respuesta correcta: 2")
    item100 = CharField(required=True, max_length=1, label="Item 100", help_text="Respuesta correcta: 2")

    item101 = CharField(required=True, max_length= 1, label="Item 101", help_text="Respuesta correcta: 1")

    class Meta:
        fields = ['__all__']


#Opciones para Documento Obs. Fonoaudiológica
_BLANK = ''
_CFR_SI = 'si'
_CFR_NO = 'no'
CHOICES_CFR = [
    (_CFR_SI, ('Sí')),
    (_CFR_NO, ('No')),
]

#Opciones respiracion
_RESP_TIPO_COSTA = 'costal-sup'
_RESP_TIPO_DIAFRAGMA = 'costo-diafrag'
_RESP_TIPO_ABDOMINAL = 'abdominal'
CHOICES_RESP_TIPO = [
    (_RESP_TIPO_COSTA, ('Costal sup.')),
    (_RESP_TIPO_DIAFRAGMA, ('Costo-driafrag.')),
    (_RESP_TIPO_ABDOMINAL, ('Abdominal')),
]
_RESP_MODO_NASAL = 'nasal'
_RESP_MODO_BUCAL = 'bucal'
_RESP_MODO_MIXTO = 'mixto'
CHOICES_RESP_MODO = [
    (_RESP_MODO_NASAL, ('Nasal')),
    (_RESP_MODO_BUCAL, ('Bucal')),
    (_RESP_MODO_MIXTO, ('Mixto')),
]

#Deglución
_NORMAL = 'normal'
_ATIPICA = 'atipica'
CHOICES_DEGLUCION = [
    (_NORMAL, ('Normal')),
    (_ATIPICA, ('Atípica')),
]

#Exámen anátomo funcional de los órganos fonoarticulatorios
#Labios
_CORTO = 'corto'
_FISURADO = 'fisurado'
CHOICES_LABIO_FORMA = [
    (_NORMAL, ('Normal')),
    (_CORTO, ('Corto')),
    (_FISURADO, ('Fisurado')),
]
_HIPOTONICO = 'hipotonico'
_HIPERTONICO = 'hipertonico'
CHOICES_LABIO_FUERZA = [
    (_NORMAL, ('Normal')),
    (_HIPOTONICO, ('Hipotónico')),
    (_HIPERTONICO, ('Hipertónico')),
]
_INSUFICIENTE = 'insuficiente'
_NULA = 'nula'
CHOICES_PRAXIAS_LABIO = [
    (_NORMAL, ('Normal')),
    (_INSUFICIENTE, ('Insuficiente')),
    (_NULA, ('Nula')),
]

#Dientes
_TEMPORAL = 'temporal'
_ALTERADA = 'alterada'
CHOICES_DIENTES_IMP = [
    (_NORMAL, ('Normal')),
    (_TEMPORAL, ('Temporal')),
    (_ALTERADA, ('Alterada')),
]

#Mordida
_CUBIERTA = 'cubierta'
_CRUZADA = 'cruzada'
_ABIERTA = 'abierta'
_BISABIS = 'bisabis'
CHOICES_MORDIDA = [
    (_NORMAL, ('Normal')),
    (_CUBIERTA, ('Cubierta')),
    (_CRUZADA, ('Cruzada')),
    (_ABIERTA, ('Abierta')),
    (_BISABIS, ('Bis a bis invertida')),
]

#Maxilar
_PROGNATISMO = 'prognatismo'
_PREGNATISMO = 'pregnatismo'
CHOICES_MAX_FORMA = [
    (_NORMAL, ('Normal')),
    (_PROGNATISMO, ('Prognatismo')),
    (_PREGNATISMO, ('Pregnatismo')),
]

#Paladar oseo
_ALTO = 'alto'
_OJIVAL = 'ojival'
CHOICES_PALADAR_FORMA = [
    (_NORMAL, ('Normal')),
    (_ALTO, ('Alto')),
    (_OJIVAL, ('Ojival')),
    (_FISURADO, ('Fisurado')),
]

#Velo paladar
_PARETICO = 'paretico'
_RIGIDO = 'rigido'
CHOICES_PALADAR_MOV = [
    (_NORMAL, ('Normal')),
    (_PARETICO, ('Parético')),
    (_RIGIDO, ('Rígido')),
]
_BIFIDA = 'bifida'
_AUSENTE = 'ausente'
CHOICES_PALADAR_UVULA = [
    (_NORMAL, ('Normal')),
    (_BIFIDA, ('Bífida')),
    (_AUSENTE, ('Ausente')),
]

#Amigdalas
_HIPERTROFICAS = 'hipertroficas'
_AUSENTES = 'ausentes'
CHOICES_AMIGDALAS = [
    (_NORMAL, ('Normal')),
    (_HIPERTROFICAS, ('Hipertróficas')),
    (_AUSENTES, ('Ausentes')),
]

#Lengua
_MACROGLOSIA = 'macroglosia'
_MICROGLOSIA = 'microglosia'
CHOICES_LENGUA_TAMANO = [
    (_NORMAL, ('Normal')),
    (_MACROGLOSIA, ('Macroglosia')),
    (_MICROGLOSIA, ('Microglosia')),
]
_DEBIL = 'debil'
CHOICES_LENGUA_FUERZA = [
    (_NORMAL, ('Normal')),
    (_DEBIL, ('Débil')),
]
CHOICES_LENGUA_FRENILLO = [
    (_NORMAL, ('Normal')),
    (_CORTO, ('Corto funcional')),
    (_AUSENTE, ('Ausente')),
]
CHOICES_PRAXIAS_LENGUA = [
    (_NORMAL, ('Normal')),
    (_INSUFICIENTE, ('Insuficiente')),
    (_AUSENTE, ('Ausente')),
]

#Cara
_SIMETRICA = 'simetrica'
_ASIMETRICA = 'asimetrica'
CHOICES_CARA_FORMA = [
    (_SIMETRICA, ('Simétrica')),
    (_ASIMETRICA, ('Asimétrica')),
]

#Voz
_DISFONICA = 'disfonica'
CHOICES_VOZ_CALIDAD = [
    (_NORMAL, ('Normal')),
    (_DISFONICA, ('Disfónica')),
]
_AUMENTADA = 'aumentada'
CHOICES_VOZ_INTEN = [
    (_NORMAL, ('Normal')),
    (_AUMENTADA, ('Aumentada')),
    (_DEBIL, ('Débil')),
]

#Tono
_AGUDO = 'agudo'
_GRAVE = 'grave'
_BITONAL = 'bitonal'
CHOICES_TONO = [
    (_NORMAL, ('Normal')),
    (_AGUDO, ('Agudo')),
    (_GRAVE, ('Grave')),
    (_BITONAL, ('Bitonal')),
]
_FARINGE = 'faringe'
_HIPERNASAL = 'hipernasal'
_HIPONASAL = 'hiponasal'
CHOICES_TONO_RESON = [
    (_NORMAL, ('Normal')),
    (_FARINGE, ('Faringe')),
    (_HIPERNASAL, ('Hipernasal')),
    (_HIPONASAL, ('Hiponasal')),
]
_ESTRIDENTE = 'estridente'
_OPACO = 'opaco'
CHOICES_TONO_TIMBRE = [
    (_NORMAL, ('Normal')),
    (_ESTRIDENTE, ('Estrindente')),
    (_OPACO, ('Opaco')),
]

#Habla
_TRAQUILALIA = 'traquilalia'
_BRADILALIA = 'bradilalia'
CHOICES_HABLA_VEL = [
    (_NORMAL, ('Normal')),
    (_TRAQUILALIA, ('Traquilalia')),
    (_BRADILALIA, ('Bradilalia')),
]
_ESPASMOS = 'espasmos'
CHOICES_HABLA_FLUIDEZ = [
    (_NORMAL, ('Normal')),
    (_ESPASMOS, ('Espasmos')),
]

#NIVEL SEMÁNTICO
#Vocabulario
_ADECUADO = 'adecuado'
_FUNCIONAL = 'funcional'
_DEFICIENTE = 'deficiente'
CHOICES_VOCAB = [
    (_ADECUADO, ('Adecuado')),
    (_FUNCIONAL, ('Funcional')),
    (_DEFICIENTE, ('Deficiente')),
]
CHOICES_FLUIDEZ_LEX = [
    (_ADECUADO, ('Adecuada')),
    (_DEFICIENTE, ('Deficiente')),
]

#Lenguaje reproductivo
_NOMINA = 'nomina'
_DESCRIBE = 'describe'
_INTERPRETA = 'interpreta'
CHOICES_LENG_REPROD = [
    (_NOMINA, ('Nomina')),
    (_DESCRIBE, ('Describe')),
    (_INTERPRETA, ('Interpreta')),
]

#NIVEL MORFOSINTACTICO
#Expresión espontánea
_SUSTANTIVOS = 'sustantivos'
_ARTICULOS = 'articulos'
_VERBOS = 'verbos'
_ADVERBIOS = 'adverbios'
_PREPOSICIONES = 'preposiciones'
_PRONOMBRE = 'pronombre'
CHOICES_EXPRESION_ESP = [
    (_SUSTANTIVOS, ('Sustantivos')),
    (_ARTICULOS, ('Artículos')),
    (_VERBOS, ('Verbos')),
    (_ADVERBIOS, ('Adverbios')),
    (_PREPOSICIONES, ('Preposiciones')),
    (_PRONOMBRE, ('Pronombre')),
]

#ASPECTO COMPRENSIVO
CHOICES_ASP_COMPREN = [
    (_NORMAL, ('Normal')),
    (_DEFICIENTE, ('Deficiente')),
]

class FormDocumentoFonoaudiologica(Form):
    #Antecedentes del desarrollo
    antdes_leng = CharField(required=False, label="Desarrollo del lenguaje",)
    antdes_natal = CharField(required=False, label="Antecedentes natales",)
    antdes_balbuceo = CharField(required=False, label="Balbuceo",)
    antdes_palabras = CharField(required=False, label="Primeras palabras",)
    antdes_motor = CharField(required=False, label="Desarrollo motor",)
    antdes_frases = CharField(required=False, label="Primeras frases",)
    antdes_comactual = CharField(required=False, label="Comunicación actual",)
    antdes_morbidos = CharField(required=False, label="Antecedentes mórbidos",)

    desarrollo_social = CharField(required=False, label="Desarrollo social",)

    #Antecedentes familiares
    antfam = BooleanField(required=False, label="Antecedentes familiares",)
    antfam_lenguaje = BooleanField(required=False, label="Transtornos del lenguaje",)
    antfam_psiquia = BooleanField(required=False, label="Transtorno psiquiátrico",)
    antfam_epilepsia = BooleanField(required=False, label="Epilepsia",)
    antfam_auditivo = BooleanField(required=False, label="Déficit auditivo",)
    antfam_cognitivo = BooleanField(required=False, label="Déficit cognitivo",)
    antfam_aprendizaje = BooleanField(required=False, label="Transtorno de aprendizaje",)
    antfam_observaciones = CharField(required=False, label="Observaciones",)

    #EXPLORACIÓN FONOARTICULATORIA
    #Funciones prelinguísticas
    resp_tipo = ChoiceField(label="Tipo respiración", choices=CHOICES_RESP_TIPO)
    resp_modo = ChoiceField(label="Modo respiración", choices=CHOICES_RESP_MODO)
    resp_cfr = ChoiceField(label="C.F.R. respiración", choices=CHOICES_CFR)
    deglucion = ChoiceField(label="Deglución", choices=CHOICES_DEGLUCION)

    #Exámen anátomo funcional de los órganos fonoarticulatorios
    #Labios
    labios_forma = ChoiceField(label="Forma de labios", choices=CHOICES_LABIO_FORMA)
    labios_fuerza = ChoiceField(label="Fuerza de labios", choices=CHOICES_LABIO_FUERZA)
    #praxias
    labprax_protunsion = ChoiceField(label="Protunsión", choices=CHOICES_PRAXIAS_LABIO)
    labprax_retrusion = ChoiceField(label="Retrusión", choices=CHOICES_PRAXIAS_LABIO)
    labprax_percusion = ChoiceField(label="Precusión", choices=CHOICES_PRAXIAS_LABIO)
    labprax_vibracion = ChoiceField(label="Vibración", choices=CHOICES_PRAXIAS_LABIO)

    #Dientes
    dientes_implantacion = ChoiceField(label="Implantación dientes", choices=CHOICES_DIENTES_IMP)

    #Mordida
    mordida = ChoiceField(label="Tipo de mordida", choices=CHOICES_MORDIDA)

    #Maxilar
    maxilar_forma = ChoiceField(label="Forma maxilar", choices=CHOICES_MAX_FORMA)
    maxilar_praxias = ChoiceField(label="Praxias maxilares", choices=CHOICES_PRAXIAS_LABIO)

    #Paladar oseo
    paladaros_forma = ChoiceField(label="Forma de paladar oseo", choices=CHOICES_PALADAR_FORMA)

    #Velo paladar
    velpal_movilidad = ChoiceField(label="Movilidad", choices=CHOICES_PALADAR_MOV)
    velpal_uvula = ChoiceField(label="Uvula", choices=CHOICES_PALADAR_UVULA)

    #Amigdalas
    amigdalas = ChoiceField(label="Amígdalas", choices=CHOICES_AMIGDALAS)

    #Lengua
    lengua_tamano = ChoiceField(label="Tamaño", choices=CHOICES_LENGUA_TAMANO)
    lengua_fuerza = ChoiceField(label="Fuerza", choices=CHOICES_LENGUA_FUERZA)
    lengua_frenillo = ChoiceField(label="Frenillo", choices=CHOICES_LENGUA_FRENILLO)
    #praxias
    lengprax_elevacion = ChoiceField(label="Elevación", choices=CHOICES_PRAXIAS_LENGUA)
    lengprax_depresion = ChoiceField(label="Depresión", choices=CHOICES_PRAXIAS_LENGUA)
    lengprax_chasqueo = ChoiceField(label="Chasqueo", choices=CHOICES_PRAXIAS_LENGUA)
    lengprax_vibracion = ChoiceField(label="Vibración", choices=CHOICES_PRAXIAS_LENGUA)
    lengprax_comisuras = ChoiceField(label="Tocar comisuras", choices=CHOICES_PRAXIAS_LENGUA)
    lengprax_vestibular = ChoiceField(label="Mov. vestibular", choices=CHOICES_PRAXIAS_LENGUA)

    #Cara
    cara_forma = ChoiceField(label="Forma de cara", choices=CHOICES_CARA_FORMA)
    #praxias
    caraprax_bilateral = ChoiceField(label="Movimientos bilaterales", choices=CHOICES_PRAXIAS_LENGUA)
    caraprax_unilateral = ChoiceField(label="Movimientos unilaterales", choices=CHOICES_PRAXIAS_LENGUA)

    #Voz
    voz_calidad = ChoiceField(label="Calidad", choices=CHOICES_VOZ_CALIDAD)
    voz_intensidad = ChoiceField(label='Intensidad', choices=CHOICES_VOZ_INTEN)

    #Tono
    tono = ChoiceField(label="Tono", choices=CHOICES_TONO)
    tono_resonancia = ChoiceField(label="Resonancia", choices=CHOICES_TONO_RESON)
    tono_timbre = ChoiceField(label="Timbre", choices=CHOICES_TONO_TIMBRE)

    #Audicion
    audicion = CharField(required=False, label="Audición",)
    #Discriminacion
    discriminacion = CharField(required=False, label="Discriminación",)

    #Habla
    habla_velocidad = ChoiceField(label="Velocidad del habla", choices=CHOICES_HABLA_VEL)
    habla_fluidez = ChoiceField(label="Fluidez del habla", choices=CHOICES_HABLA_FLUIDEZ)

    #PAGINA 2 ----------------------------------------------------
    #Articulación a la repetición
    artic_b = BooleanField(required=False, label="B",)
    artic_p = BooleanField(required=False, label="P",)
    artic_m = BooleanField(required=False, label="M",)
    artic_f = BooleanField(required=False, label="F",)
    artic_d = BooleanField(required=False, label="D",)
    artic_t = BooleanField(required=False, label="T",)
    artic_s = BooleanField(required=False, label="S",)
    artic_n = BooleanField(required=False, label="N",)
    artic_l = BooleanField(required=False, label="L",)
    artic_r = BooleanField(required=False, label="R",)
    artic_rr = BooleanField(required=False, label="RR",)
    artic_y = BooleanField(required=False, label="Y",)
    artic_n = BooleanField(required=False, label="N",)
    artic_ch = BooleanField(required=False, label="CH",)
    artic_j = BooleanField(required=False, label="J",)
    artic_g = BooleanField(required=False, label="G",)
    artic_k = BooleanField(required=False, label="K",)

    #Dífonos vocálicos
    difvoc_ai = BooleanField(required=False, label="ai",)
    difvoc_au = BooleanField(required=False, label="au",)
    difvoc_ei = BooleanField(required=False, label="ei",)
    difvoc_eu = BooleanField(required=False, label="eu",)
    difvoc_ia = BooleanField(required=False, label="ia",)
    difvoc_ie = BooleanField(required=False, label="ie",)
    difvoc_io = BooleanField(required=False, label="io",)
    difvoc_iu = BooleanField(required=False, label="io",)
    difvoc_oi = BooleanField(required=False, label="oi",)
    difvoc_ua = BooleanField(required=False, label="ua",)
    difvoc_ue = BooleanField(required=False, label="ue",)
    difvoc_ui = BooleanField(required=False, label="ui",)
    difvoc_uo = BooleanField(required=False, label="uo",)

    #Dífonos consonánticos
    difcon_bl = BooleanField(required=False, label="bl",)
    difcon_pl = BooleanField(required=False, label="pl",)
    difcon_fl = BooleanField(required=False, label="fl",)
    difcon_gl = BooleanField(required=False, label="gl",)
    difcon_cl = BooleanField(required=False, label="cl",)
    difcon_tl = BooleanField(required=False, label="tl",)
    difcon_br = BooleanField(required=False, label="br",)
    difcon_pr = BooleanField(required=False, label="pr",)
    difcon_fr = BooleanField(required=False, label="fr",)
    difcon_gr = BooleanField(required=False, label="gr",)
    difcon_cr = BooleanField(required=False, label="cr",)
    difcon_tr = BooleanField(required=False, label="tr",)
    difcon_dr = BooleanField(required=False, label="dr",)

    #NIVEL SEMÁNTICO
    nvlsem_vocab = ChoiceField(label="Vocabulario", choices=CHOICES_VOCAB)
    nvlsem_lexica = ChoiceField(label="Fluidez léxica", choices=CHOICES_FLUIDEZ_LEX)
    nvlsem_hiponimia = CharField(required=False, label="Hiponimia",)
    nvlsem_expresafun = CharField(required=False, label="Expresa función",)
    nvlsem_hiperonimia = CharField(required=False, label="Hiperonimia",)
    #Lenguaje reproductivo
    nvlsem_lengrep = ChoiceField(label="Lenguaje reproductivo", choices=CHOICES_LENG_REPROD)

    #NIVEL MORFOSINTÁCTICO
    nvlmorf_expresion_esp = ChoiceField(label="Uso de", choices=CHOICES_EXPRESION_ESP)
    nvlmorf_observaciones = CharField(required=False, label="Observaciones",)

    #ASPECTO COMPRENSIVO
    aspcomp_discriminacion = ChoiceField(label="Discriminación auditiva", choices=CHOICES_ASP_COMPREN)
    aspcomp_memverbal = ChoiceField(label="Memoria verbal auditiva", choices=CHOICES_ASP_COMPREN)
    aspcomp_asociacion = ChoiceField(label=" Asociación auditiva", choices=CHOICES_ASP_COMPREN)

    #Observaciones finales
    obs_nvlsem_vocabpasivo = CharField(required=False, label="Vocabulario pasivo",)
    obs_nvlsem_defuso = CharField(required=False, label="Definiciones por uso",)
    obs_nvlsem_absvisuales = CharField(required=False, label="Absurdos visuales",)
    obs_nvlsem_analogias = CharField(required=False, label="Analogías",)
    obs_nvlsem_relopuestas = CharField(required=False, label="Relaciones opuestas",)
    obs_nvlsin_ordsimples = CharField(required=False, label="Ordenes simples",)
    obs_nvlsin_ordcomplejas2 = CharField(required=False, label="Ordenes complejas (2 verbos)",)
    obs_nvlsin_ordcomplejas3 = CharField(required=False, label="Ordenes complejas (3 o más)",)
    obs_nvlsin_vozpasiva = CharField(required=False, label="Voz pasiva",)
    obs_nvlsin_observaciones = CharField(required=False, label="Obersvaciones",)
    obs_aspgram_contocular = CharField(required=False, label="Contacto ocular",)
    obs_aspgram_postura = CharField(required=False, label="Mantiene postura y distancias",)
    obs_aspgram_dialogo = CharField(required=False, label="Inicia diálogo",)
    obs_aspgram_topico = CharField(required=False, label="Mantiene tópico",)
    obs_aspgram_facultades = CharField(required=False, label="Facultades conversacionales",)
    obs_aspgram_intcomunic = CharField(required=False, label="Intenciones comunicativas",)
    obs_pruebas_aplicadas = CharField(required=False, label="Pruebas aplicadas",)
    obs_diagnostico = CharField(label="Diagnóstico",)
    obs_indicaciones = CharField(label="Indicaciones",)

    class Meta:
        fields = ['__all__']


class FormDocumentoTeprosif(Form):
    reg1 = CharField(required=False, label="Ítem 1", help_text="PLANCHA")
    est_sil1 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi1 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu1 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc1 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp1 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg2 = CharField(required=False, label="Ítem 2" ,help_text="RUEDA")
    est_sil2 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi2 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu2 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc2 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp2 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg3 = CharField(required=False, label="Ítem 3" ,help_text="MARIPOSA")
    est_sil3 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi3 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu3 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc3 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp3 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg4 = CharField(required=False, label="Ítem 4" ,help_text="BICICLETA")
    est_sil4 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi4 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu4 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc4 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp4 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg5 = CharField(required=False, label="Ítem 5" ,help_text="HELICÓPTERO")
    est_sil5 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi5 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu5 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc5 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp5 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg6 = CharField(required=False, label="Ítem 6" ,help_text="BUFANDA")
    est_sil6 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi6 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu6 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc6 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp6 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg7 = CharField(required=False, label="Ítem 7" ,help_text="CAPERUCITA")
    est_sil7 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi7 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu7 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc7 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp7 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg8 = CharField(required=False, label="Ítem 8" ,help_text="ALFOMBRA")
    est_sil8 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi8 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu8 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc8 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp8 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg9 = CharField(required=False, label="Ítem 9" ,help_text="REFRIGERADOR")
    est_sil9 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi9 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu9 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc9 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp9 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg10 = CharField(required=False, label="Ítem 10" ,help_text="EDIFICIO")
    est_sil10 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi10 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu10 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc10 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp10 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg11 = CharField(required=False, label="Ítem 11" ,help_text="CALCETÍN")
    est_sil11 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi11 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu11 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc11 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp11 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg12 = CharField(required=False, label="Ítem 12" ,help_text="DINOSAURIO")
    est_sil12 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi12 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu12 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc12 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp12 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg13 = CharField(required=False, label="Ítem 13" ,help_text="TELÉFONO")
    est_sil13 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi13 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu13 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc13 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp13 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg14 = CharField(required=False, label="Ítem 14" ,help_text="REMEDIO")
    est_sil14 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi14 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu14 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc14 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp14 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg15 = CharField(required=False, label="Ítem 15" ,help_text="PEINETA")
    est_sil15 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi15 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu15 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc15 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp15 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg16 = CharField(required=False, label="Ítem 16" ,help_text="AUTO")
    est_sil16 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi16 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu16 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc16 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp16 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg17 = CharField(required=False, label="Ítem 17" ,help_text="INDIO")
    est_sil17 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi17 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu17 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc17 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp17 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg18 = CharField(required=False, label="Ítem 18" ,help_text="PANTALÓN")
    est_sil18 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi18 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu18 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc18 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp18 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg19 = CharField(required=False, label="Ítem 19" ,help_text="CAMIÓN")
    est_sil19 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi19 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu19 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc19 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp19 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg20 = CharField(required=False, label="Ítem 20" ,help_text="CUADERNO")
    est_sil20 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi20 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu20 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc20 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp20 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg21 = CharField(required=False, label="Ítem 21" ,help_text="MICRO")
    est_sil21 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi21 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu21 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc21 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp21 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg22 = CharField(required=False, label="Ítem 22" ,help_text="TREN")
    est_sil22 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi22 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu22 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc22 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp22 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg23 = CharField(required=False, label="Ítem 23" ,help_text="PLÁTANO")
    est_sil23 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi23 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu23 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc23 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp23 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg24 = CharField(required=False, label="Ítem 24" ,help_text="JUGO")
    est_sil24 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi24 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu24 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc24 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp24 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg25 = CharField(required=False, label="Ítem 25" ,help_text="ENCHUFE")
    est_sil25 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi25 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu25 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc25 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp25 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg26 = CharField(required=False, label="Ítem 26" ,help_text="JABÓN")
    est_sil26 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi26 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu26 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc26 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp26 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg27 = CharField(required=False, label="Ítem 27" ,help_text="TAMBOR")
    est_sil27 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi27 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu27 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc27 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp27 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg28 = CharField(required=False, label="Ítem 28" ,help_text="VOLANTÍN")
    est_sil28 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi28 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu28 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc28 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp28 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg29 = CharField(required=False, label="Ítem 29" ,help_text="JIRAFA")
    est_sil29 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi29 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu29 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc29 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp29 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg30 = CharField(required=False, label="Ítem 30" ,help_text="GORRO")
    est_sil30 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi30 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu30 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc30 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp30 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg31 = CharField(required=False, label="Ítem 31" ,help_text="ÁRBOL")
    est_sil31 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi31 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu31 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc31 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp31 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg32 = CharField(required=False, label="Ítem 32" ,help_text="DULCE")
    est_sil32 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi32 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu32 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc32 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp32 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg33 = CharField(required=False, label="Ítem 33" ,help_text="GUITARRA")
    est_sil33 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi33 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu33 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc33 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp33 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg34 = CharField(required=False, label="Ítem 34" ,help_text="GUANTE")
    est_sil34 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi34 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu34 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc34 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp34 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg35 = CharField(required=False, label="Ítem 35" ,help_text="RELOJ")
    est_sil35 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi35 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu35 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc35 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp35 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg36 = CharField(required=False, label="Ítem 36" ,help_text="JAULA")
    est_sil36 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi36 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu36 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc36 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp36 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    reg37 = CharField(required=False, label="Ítem 37" ,help_text="PUENTE")
    est_sil37 = CharField(required=False, max_length=3, label="" ,help_text="Est. Silbica")
    asimi37 = CharField(required=False, max_length=3, label="" ,help_text="Asimilación")
    sustitu37 = CharField(required=False, max_length=3, label="" ,help_text="Sustitución")
    tot_proc37 = CharField(required=False, max_length=3 ,label="" ,help_text="Total Proc")
    otr_resp37 = CharField(required=False, max_length=3 ,label="" ,help_text="Otras respuestas")
    

    class Meta:
        fields = ['__all__']


class FormDocumentoSTSG(Form):
    #Subprueba receptiva
    rec_uno_prim = BooleanField(required=False, label="El niño está sentado*",)
    rec_uno_segu = BooleanField(required=False, label="El niño no está sentado",)
    rec_dos_prim = BooleanField(required=False, label="El gato está encima de la caja",)
    rec_dos_segu = BooleanField(required=False, label="El gato está adentro de la caja*",)
    rec_tres_prim = BooleanField(required=False, label="El está subiendo.",)
    rec_tres_segu = BooleanField(required=False, label="Ella está subiendo.*",)
    rec_cuatro_prim = BooleanField(required=False, label="El perro está detrás de la silla.*",)
    rec_cuatro_segu = BooleanField(required=False, label="El perro está debajo de la silla.",)
    rec_cinco_prim = BooleanField(required=False, label="Están comiendo.",)
    rec_cinco_segu = BooleanField(required=False, label="Está comiendo.*",)
    rec_seis_prim = BooleanField(required=False, label="El libro es de él.*",)
    rec_seis_segu = BooleanField(required=False, label="El libro es de ella.",)
    rec_siete_prim = BooleanField(required=False, label="El niño se cayó.*",)
    rec_siete_segu = BooleanField(required=False, label="El niño se cae.",)
    rec_ocho_prim = BooleanField(required=False, label="Alguien está en la mesa.",)
    rec_ocho_segu = BooleanField(required=False, label="Algo está en la mesa.*",)
    rec_nueve_prim = BooleanField(required=False, label="El niño la está llamando.",)
    rec_nueve_segu = BooleanField(required=False, label="El niño lo está llamando.*",)
    rec_diez_prim = BooleanField(required=False, label="Este es mi papá.*",)
    rec_diez_segu = BooleanField(required=False, label="Aquel es mi papá.",)
    rec_once_prim = BooleanField(required=False, label="El niño está tomando helado.*",)
    rec_once_segu = BooleanField(required=False, label="El niño estaba tomando helado.",)
    rec_doce_prim = BooleanField(required=False, label="¿Dónde está la niña?.",)
    rec_doce_segu = BooleanField(required=False, label="¿Quién es la niña?.*",)
    rec_trece_prim = BooleanField(required=False, label="El niño tiene el pájaro.*",)
    rec_trece_segu = BooleanField(required=False, label="El niño tenía el pájaro.",)
    rec_catorce_prim = BooleanField(required=False, label="La niña las tiene.",)
    rec_catorce_segu = BooleanField(required=False, label="La niña la tiene.",)
    rec_quince_prim = BooleanField(required=False, label="Esta es mi cama.",)
    rec_quince_segu = BooleanField(required=False, label="Esta es nuestra cama.*",)
    rec_dieciseis_prim = BooleanField(required=False, label="El niño se ve.",)
    rec_dieciseis_segu = BooleanField(required=False, label="El niño lo ve.*",)
    rec_diecisiete_prim = BooleanField(required=False, label="La niña subirá.*",)
    rec_diecisiete_segu = BooleanField(required=False, label="La niña subió.",)
    rec_dieciocho_prim = BooleanField(required=False, label="Mira a quien llegó.",)
    rec_dieciocho_segu = BooleanField(required=False, label="Mira lo que llegó.*",)
    rec_diecinueve_prim = BooleanField(required=False, label='La mamá dice, "Se lo dio".',)
    rec_diecinueve_segu = BooleanField(required=False, label='La mamá dice, "Me lo dio".*',)
    rec_veinte_prim = BooleanField(required=False, label="La mamá va a comprar pan.*",)
    rec_veinte_segu = BooleanField(required=False, label="La mamá fue a comprar pan.",)
    rec_veintiuno_prim = BooleanField(required=False, label="Este es un avión.*",)
    rec_veintiuno_segu = BooleanField(required=False, label="Ese es un avión.",)
    rec_veintidos_prim = BooleanField(required=False, label="El papá es alto.",)
    rec_veintidos_segu = BooleanField(required=False, label="El papá está alto.*",)
    rec_veintitres_prim = BooleanField(required=False, label="El niño es llamado por la  niña.*",)
    rec_veintitres_segu = BooleanField(required=False, label="La niña es llamada por el niño.",)
    rec_observac = CharField(label="Observaciones")

    #Subprueba expresiva
    exp_uno_prim = BooleanField(required=False, label="La puerta no está cerrada.*",)
    exp_uno_segu = BooleanField(required=False, label="La puerta está cerrada.",)
    exp_dos_prim = BooleanField(required=False, label="El perro está encima del auto.*",)
    exp_dos_segu = BooleanField(required=False, label="El perro está adentro del auto.",)
    exp_tres_prim = BooleanField(required=False, label="El gato está debajo de la silla.",)
    exp_tres_segu = BooleanField(required=False, label="El gato está detrás de la silla.*",)
    exp_cuatro_prim = BooleanField(required=False, label="El ve al gato.*",)
    exp_cuatro_segu = BooleanField(required=False, label="Ella ve al gato.",)
    exp_cinco_prim = BooleanField(required=False, label="Alguien está en la silla.",)
    exp_cinco_segu = BooleanField(required=False, label="Algo está en la silla.*",)
    exp_seis_prim = BooleanField(required=False, label="El sombrero es de ella.",)
    exp_seis_segu = BooleanField(required=False, label="El sombrero es de él.*",)
    exp_siete_prim = BooleanField(required=False, label="Está durmiendo.",)
    exp_siete_segu = BooleanField(required=False, label="Están durmiendo.*",)
    exp_ocho_prim = BooleanField(required=False, label="El niño se vistió.*",)
    exp_ocho_segu = BooleanField(required=False, label="El niño se viste.",)
    exp_nueve_prim = BooleanField(required=False, label="La niña está escribiendo.*",)
    exp_nueve_segu = BooleanField(required=False, label="La niña estaba escribiendo.",)
    exp_diez_prim = BooleanField(required=False, label="La niña la ve.",)
    exp_diez_segu = BooleanField(required=False, label="La niña lo ve.*",)
    exp_once_prim = BooleanField(required=False, label="El niño tenía el globo.*",)
    exp_once_segu = BooleanField(required=False, label="El niño tiene el globo.",)
    exp_doce_prim = BooleanField(required=False, label="La niña lo lleva.*",)
    exp_doce_segu = BooleanField(required=False, label="La niña los lleva.",)
    exp_trece_prim = BooleanField(required=False, label="Este es mi amigo.",)
    exp_trece_segu = BooleanField(required=False, label="Aquel es mi amigo.*",)
    exp_catorce_prim = BooleanField(required=False, label="El niño lo lava.",)
    exp_catorce_segu = BooleanField(required=False, label="El niño se lava.*",)
    exp_quince_prim = BooleanField(required=False, label="Este es nuestro perro.",)
    exp_quince_segu = BooleanField(required=False, label="Este es nuestro perro.",)
    exp_dieciseis_prim = BooleanField(required=False, label="La niña comió.*",)
    exp_dieciseis_segu = BooleanField(required=False, label="La niña comerá.",)
    exp_diecisiete_prim = BooleanField(required=False, label="Esa es mi muñeca.",)
    exp_diecisiete_segu = BooleanField(required=False, label="Esta es mi muñeca.*",)
    exp_dieciocho_prim = BooleanField(required=False, label="¿Quién está en la puerta?.*",)
    exp_dieciocho_segu = BooleanField(required=False, label="¿Qué está en la puerta?",)
    exp_diecinueve_prim = BooleanField(required=False, label="¿Dónde está el niño?",)
    exp_diecinueve_segu = BooleanField(required=False, label="¿Quién es el niño?.*",)
    exp_veinte_prim = BooleanField(required=False, label="El niño va a cortarse el pelo.",)
    exp_veinte_segu = BooleanField(required=False, label="El niño fue a cortarse el pelo.*",)
    exp_veintiuno_prim = BooleanField(required=False, label='El niño dice, "Me la dio".*',)
    exp_veintiuno_segu = BooleanField(required=False, label='El niño dice, "Se la dio".',)
    exp_veintidos_prim = BooleanField(required=False, label="El niño es alto.",)
    exp_veintidos_segu = BooleanField(required=False, label="El niño está alto.*",)
    exp_veintitres_prim = BooleanField(required=False, label="La niña es empujada por el niño.*",)
    exp_veintitres_segu = BooleanField(required=False, label="El niño es empujado por la niña.",)
    exp_observac = CharField(label="Observaciones")

    class Meta:
        fields = ['__all__']
