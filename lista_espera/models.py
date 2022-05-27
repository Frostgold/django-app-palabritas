from django.db import models
from fichas_alumnos.models import FichaAlumno
from cursos.models import Nivel

class ListaEspera(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.OneToOneField(FichaAlumno, on_delete=models.CASCADE)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Lista de espera'
        verbose_name_plural = 'Lista de espera'
        ordering = ['id']
        permissions = (
            ('can_avanzar_lista_espera', 'Puede avanzar lista de espera'),
        )

    def __str__(self):
        return self.alumno.rut
