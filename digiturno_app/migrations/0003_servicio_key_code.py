# Generated by Django 2.2.6 on 2019-10-03 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0002_auto_20191002_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='key_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
