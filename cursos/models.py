from django.db import models
import datetime
import os
from django.core.validators import RegexValidator
from autenticacion.models import Usuario

class Nivel(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, unique=True, blank=False, null=False)

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering = ['id']

    def __str__(self):
        return self.descripcion


class Curso(models.Model):
    REGEX_LETRA = r"([a-zA-Z])"

    id = models.CharField(primary_key=True, max_length=20)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    letra = models.CharField(
            max_length=1,
            blank=False, 
            null=False,
            validators=[RegexValidator(REGEX_LETRA)],
            )
    nombre = models.CharField(max_length=100, blank=False, null=False)
    periodo = models.CharField(max_length=4, default=datetime.datetime.now().year, blank=False, null=False)
    cupos = models.PositiveIntegerField(null=False)
    docente_jefe = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, blank=True, null=True, limit_choices_to={'groups__name': "Docente"})

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['id']
        permissions = (
            ('can_view_listado_cursos', 'Can view listado cursos'),
        )

    def __str__(self):
        return self.id


def actividad_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/alumno_<rut>/<filename>
    return 'cronograma_act/curso_{0}/{1}'.format(instance.curso.id, filename)

class CronogramaActividad(models.Model):
    id = models.AutoField(primary_key=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=1000, null=False, blank=False)
    imagen = models.ImageField(max_length=500, upload_to=actividad_directory_path, null=True, blank=True)
    editor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_edicion = models.DateField(auto_now=True)
    modificado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Cronograma actividad'
        verbose_name_plural = 'Cronograma de actividades'
        ordering = ['id']

    def geteditor(self):
        return self.editor.nombre

    def getcurso(self):
        return self.curso.nombre

    def filename(self):
        return os.path.basename(self.imagen.name)


class DetalleDocente(models.Model):
    id = models.AutoField(primary_key=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    docente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'groups__name': "Docente"})
    asignatura = models.CharField(max_length=250, blank=False, null=False)

    class Meta:
        verbose_name = 'Detalle docente'
        verbose_name_plural = 'Detalle docentes'
        ordering = ['id']

    def getdocente(self):
        return self.docente.nombre

    def getcurso(self):
        return self.curso.nombre
