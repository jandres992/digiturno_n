# Generated by Django 2.2.6 on 2019-10-10 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0009_digiturno_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='digiturno',
            name='fecha_atendido',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]