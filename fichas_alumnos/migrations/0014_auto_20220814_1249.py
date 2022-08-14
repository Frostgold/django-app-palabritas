# Generated by Django 3.2.5 on 2022-08-14 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichas_alumnos', '0013_alter_fichaalumno_rut'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichaalumno',
            name='autorizacion_eval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='colacion_celebracion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='entrega_textos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='eval_diagnostica',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='ficha_matricula',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='formulario_fudei',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='formulario_reeval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='informe_padres',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='informe_semestral',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='otros_docs_admin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='peval_semestral',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fichaalumno',
            name='solicitud_textos',
            field=models.BooleanField(default=False),
        ),
    ]
