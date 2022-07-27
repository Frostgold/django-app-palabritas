# Generated by Django 3.2.5 on 2022-07-27 16:13

from django.db import migrations


def migrar_imagenes(apps, schema_editor):
    CronogramaActividad = apps.get_model('cursos', 'CronogramaActividad')
    for actividad in CronogramaActividad.objects.all():
        if(actividad.imagen is not None):
            actividad.archivo = actividad.imagen
            actividad.save()

class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0008_cronogramaactividad_archivo'),
    ]

    operations = [
        migrations.RunPython(migrar_imagenes)
    ]
