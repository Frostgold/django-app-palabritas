# Generated by Django 3.2.5 on 2022-05-16 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0003_alter_curso_options'),
        ('fichas_alumnos', '0007_fichaalumno_curso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichaalumno',
            name='curso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cursos.curso'),
        ),
    ]