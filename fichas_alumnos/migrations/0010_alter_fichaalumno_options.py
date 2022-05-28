# Generated by Django 3.2.5 on 2022-05-25 23:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fichas_alumnos', '0009_alter_detalleapoderado_apoderado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fichaalumno',
            options={'ordering': ['rut'], 'permissions': (('can_view_listado_fichas', 'Puede ver listado fichas alumnos'), ('can_view_ficha_completa', 'Puede ver ficha alumno completa'), ('can_retirar_ficha_alumno', 'Puede retirar ficha alumno')), 'verbose_name': 'Ficha Alumno', 'verbose_name_plural': 'Fichas Alumnos'},
        ),
    ]