# Generated by Django 2.2.6 on 2019-11-29 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0024_servicio_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='digiturno',
            name='general',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='digiturno',
            name='preferencial',
            field=models.BooleanField(default=False),
        ),
    ]