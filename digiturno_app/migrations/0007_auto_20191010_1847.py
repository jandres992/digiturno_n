# Generated by Django 2.2.6 on 2019-10-10 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0006_auto_20191010_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulo',
            name='hora',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Turno',
        ),
    ]
