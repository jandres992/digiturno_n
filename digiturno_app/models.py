from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Create your models here.

class Modulo(models.Model):
    modulo = models.CharField(max_length=30)
    usuario = models.ForeignKey(User,models.DO_NOTHING,blank=True,null=True)
    turno = models.CharField(max_length=4,blank=True,null=True)
    hora = models.DateTimeField(blank=True,null=True)
    habilitado = models.BooleanField(default=False)

    class Meta:
        db_table = 'MODULO'


class Servicio(models.Model):
    letra = models.CharField(max_length=1,blank=True, null=True)
    servicio = models.CharField(max_length=60)
    rango_ini = models.IntegerField()
    rango_fin = models.IntegerField()
    key_code = models.CharField(max_length=10, blank=True,null=True)
    color = models.CharField(max_length=30)
    icon = models.CharField(max_length=30)
    horario = models.CharField(max_length=250,blank=True,null=True)
    horario_fin = models.TimeField(blank=True,null=True)
    nombre = models.CharField(max_length=60)

    class Meta:
        db_table = 'SERVICIOS'


class Digiturno(models.Model):
    no_turno = models.IntegerField()
    servicio = models.ForeignKey('Servicio', models.DO_NOTHING)
    modulo = models.ForeignKey('Modulo', models.DO_NOTHING, blank=True, null=True)
    usuario = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    llamado = models.BooleanField(default=False)
    atencion = models.BooleanField(default=False)
    fecha = models.DateTimeField()
    fecha_atendido = models.DateTimeField(blank=True, null=True)
    aviso = models.BooleanField(default=False)
    general = models.BooleanField(default=False)
    preferencial = models.BooleanField(default=False)

    class Meta:
        db_table = 'DIGITURNO'


class Turno(models.Model):
    servicio = models.ForeignKey('Servicio', models.DO_NOTHING)
    turno = models.IntegerField()

    class Meta:
        db_table = 'TURNO'


class Listado_videos(models.Model):
    url = models.CharField(max_length=255)
    tema = models.TextField()
    order = models.IntegerField()

    class Meta:
        db_table = 'VIDEOS'


class Especialidad(models.Model):
    especialidad = models.CharField(max_length=255)
    estado = models.BooleanField(default=False)

    class Meta:
        db_table = 'ESPECIALIDAD'


class Agenda(models.Model):
    especialidad = models.ForeignKey('Especialidad', models.DO_NOTHING)
    fecha = models.DateField()

    class Meta:
        db_table = 'AGENDA'


class Usuario(models.Model):
    usuario = models.ForeignKey(User, models.DO_NOTHING)
    permiso = models.ForeignKey(Group, models.DO_NOTHING)

    class Meta:
        db_table = 'USUARIOS'