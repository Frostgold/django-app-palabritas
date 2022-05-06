import os
from django.db import models
from django.core.validators import RegexValidator

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

    REGEX_RUT_VALIDATOR = r"^(\d{1,2}(?:\d{3}){2}-[\dkK])$"

    rut = models.CharField(
            max_length=10, 
            primary_key=True, 
            validators=[RegexValidator(REGEX_RUT_VALIDATOR)],
            verbose_name="Rut alumno",
            help_text="El rut debe ser ingresado sin puntos y con guión."
            )
    nombre = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    estado = models.CharField(
       max_length=32,
       choices=ESTADO,
       default=LISTAESPERA,
    )
    #curso = models.CharField()

    class Meta:
        verbose_name = 'Ficha Alumno'
        verbose_name_plural = 'Fichas Alumnos'
        ordering = ['rut']

    def __str__(self):
        return self.nombre


def alumno_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/alumno_<rut>/<filename>
    return 'banco_documento/alumno_{0}/{1}'.format(instance.alumno.rut, filename)


class BancoDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(FichaAlumno, on_delete=models.CASCADE)
    documento = models.FileField(max_length=500, upload_to=alumno_directory_path)

    class Meta:
        verbose_name = 'Banco documento'
        verbose_name_plural = 'Banco documentos'
        ordering = ['id']

    def __str__(self):
        return self.documento.name

    def filename(self):
        return os.path.basename(self.documento.name)