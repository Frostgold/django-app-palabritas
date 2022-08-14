import os
from django.db import models
from django.core.validators import RegexValidator
from autenticacion.models import Usuario
from cursos.models import Curso

class FichaAlumno(models.Model):
    LISTAESPERA = 'lista_espera'
    DOCUMENTOSPENDIENTE = 'documentos_pendientes'
    CURSOASIGNADO = 'curso_asignado'
    RETIRADO = 'retirado'
    ESTADO = [
        (LISTAESPERA, ('En lista de espera')),
        (DOCUMENTOSPENDIENTE, ('Documentos pendientes')),
        (CURSOASIGNADO, ('Curso asignado')),
        (RETIRADO, ('Retirado')),
    ]

    REGEX_RUT_VALIDATOR = r"^(\d{1,3}(?:\d{3}){2}-[\dkK])$"

    rut = models.CharField(
            max_length=11,
            primary_key=True,
            validators=[RegexValidator(REGEX_RUT_VALIDATOR)],
            verbose_name="Rut alumno",
            help_text="El rut debe ser ingresado sin puntos y con guión."
            )
    nombre = models.CharField(max_length=255, null=False, blank=False)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=255, null=False, blank=False)
    nombre_padre = models.CharField(max_length=255, null=False, blank=False)
    nombre_madre = models.CharField(max_length=255, null=False, blank=False)
    telefono = models.CharField(max_length=255, null=False, blank=False)
    ficha_social = models.BooleanField(default=False)
    formulario_salud = models.BooleanField(default=False)
    anamnesis = models.BooleanField(default=False)
    certif_nacimiento = models.BooleanField(default=False)
    consent_fonoaudiologia = models.BooleanField(default=False)
    consent_vidasana = models.BooleanField(default=False)
    solicitud_textos = models.BooleanField(default=False)
    entrega_textos = models.BooleanField(default=False)
    colacion_celebracion = models.BooleanField(default=False)
    ficha_matricula = models.BooleanField(default=False)
    autorizacion_eval = models.BooleanField(default=False)
    formulario_reeval = models.BooleanField(default=False)
    formulario_fudei = models.BooleanField(default=False)
    informe_padres = models.BooleanField(default=False)
    eval_diagnostica = models.BooleanField(default=False)
    informe_semestral = models.BooleanField(default=False)
    peval_semestral = models.BooleanField(default=False)
    otros_docs_admin = models.CharField(max_length=255, null=True, blank=True)

    estado = models.CharField(
       max_length=32,
       choices=ESTADO,
       default=LISTAESPERA,
    )
    curso = models.ForeignKey(Curso, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        verbose_name = 'Ficha Alumno'
        verbose_name_plural = 'Fichas Alumnos'
        ordering = ['rut']
        permissions = (
            ('can_view_listado_fichas', 'Puede ver listado fichas alumnos'),
            ('can_view_ficha_completa', 'Puede ver ficha alumno completa'),
            ('can_retirar_ficha_alumno', 'Puede retirar ficha alumno'),
        )

    def __str__(self):
        return self.nombre

    def rut_formatted(self):

        rut = ""

        if len(self.rut) == 11:
            rut_1 = self.rut[:3]
            rut_2 = self.rut[3:6]
            rut_3 = self.rut[-5:]
            rut = (rut_1+"."+rut_2+"."+rut_3)
        if len(self.rut) == 10:
            rut_1 = self.rut[:2]
            rut_2 = self.rut[2:5]
            rut_3 = self.rut[-5:]
            rut = (rut_1+"."+rut_2+"."+rut_3)
        if len(self.rut) == 9:
            rut_1 = self.rut[:1]
            rut_2 = self.rut[1:4]
            rut_3 = self.rut[-5:]
            rut = (rut_1+"."+rut_2+"."+rut_3)

        return rut.upper()

    def asignar_curso(self, curso:Curso):
        if curso:
            self.curso = curso
            if self.estado == 'lista_espera':
                self.estado = 'curso_asignado'
            self.save()



def documento_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/alumno_<rut>/<filename>
    return 'banco_documento/alumno_{0}/{1}'.format(instance.alumno.rut, filename)

class BancoDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(FichaAlumno, on_delete=models.CASCADE)
    documento = models.FileField(max_length=500, upload_to=documento_directory_path)

    class Meta:
        verbose_name = 'Banco documento'
        verbose_name_plural = 'Banco documentos'
        ordering = ['id']
    def filename(self):
        return os.path.basename(self.documento.name)


def trabajo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/alumno_<rut>/<filename>
    return 'trabajo/alumno_{0}/{1}'.format(instance.alumno.rut, filename)

class BancoTrabajo(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(FichaAlumno, on_delete=models.CASCADE)
    trabajo = models.FileField(max_length=500, upload_to=trabajo_directory_path)

    class Meta:
        verbose_name = 'Trabajo'
        verbose_name_plural = 'Trabajos'
        ordering = ['id']

    def filename(self):
        return os.path.basename(self.trabajo.name)


class AvanceAlumno(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(FichaAlumno, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=1000, null=False, blank=False)
    editor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_edicion = models.DateField(auto_now=True)
    modificado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Avance'
        verbose_name_plural = 'Avances'
        ordering = ['id']

    def geteditor(self):
        return self.editor.nombre


class DetalleApoderado(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(FichaAlumno, on_delete=models.CASCADE)
    apoderado = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'groups__name': "Apoderado"})

    class Meta:
        verbose_name = 'Detalle Apoderado'
        verbose_name_plural = 'Detalle Apoderados'
        ordering = ['id']

    def getapoderado(self):
        return self.apoderado.nombre
