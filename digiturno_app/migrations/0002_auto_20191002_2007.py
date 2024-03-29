# Generated by Django 2.2.6 on 2019-10-02 20:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digiturno_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servicio', models.CharField(max_length=60)),
                ('rango_ini', models.IntegerField()),
                ('rango_fin', models.IntegerField()),
            ],
            options={
                'db_table': 'SERVICIOS',
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turno', models.IntegerField()),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='digiturno_app.Servicio')),
            ],
            options={
                'db_table': 'TURNO',
            },
        ),
        migrations.AddField(
            model_name='modulo',
            name='usuario',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='digiturno',
            name='modulo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='digiturno_app.Modulo'),
        ),
        migrations.DeleteModel(
            name='Digiturno_ref',
        ),
        migrations.AddField(
            model_name='digiturno',
            name='servicio',
            field=models.ForeignKey(default=-5, on_delete=django.db.models.deletion.DO_NOTHING, to='digiturno_app.Servicio'),
            preserve_default=False,
        ),
    ]
