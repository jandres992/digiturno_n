# Generated by Django 2.2.6 on 2019-10-11 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0010_digiturno_fecha_atendido'),
    ]

    operations = [
        migrations.CreateModel(
            name='Listado_videos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('tema', models.TextField()),
                ('order', models.IntegerField()),
            ],
            options={
                'db_table': 'VIDEOS',
            },
        ),
    ]
