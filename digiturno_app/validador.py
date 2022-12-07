# -*- encoding: utf-8 -*-
from .models import *
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class Validator(object):
    _post  = None
    required = []
    _message = ''

    def __init__(self, post):
        """
        Carga los datos provenientes de un formulario atraves de POST
        @param post: Datos que proviene de POST
        """
        self._post = post

    def is_empty(self, field):
        """
        Verifica si un campo de formulario es vacio
        @param field: nombre del campo de formulario
        """
        if field == '' or field is None:
            return True
        return False

    def is_valid(self):
        """
        Indica si existen errores de formuarlio
        @return Boolean
        """
        # validar campos vacios
        for field in self.required:
            if self.is_empty(self._post[field]):

                self._message = 'El campo %s no puede estar vacio' %  field
                return False

        return True

    def getMessage(self):
        return self._message

class ValidatorGet(object):
    _get  = None
    required = []
    _message = ''

    def __init__(self, get):
        """
        Carga los datos provenientes de un formulario atraves de POST
        @param post: Datos que proviene de POST
        """
        self._get = get

    def is_empty(self, field):
        """
        Verifica si un campo de formulario es vacio
        @param field: nombre del campo de formulario
        """
        if field == '' or field is None:
            return True
        return False

    def is_valid(self):
        """
        Indica si existen errores de formuarlio
        @return Boolean
        """
        # validar campos vacios
        for field in self.required:
            if self.is_empty(self._get[field]):

                self._message = 'El campo %s no puede quedar vacio' %  field
                return False

        return True

    def getMessage(self):
        return self._message

class FormUsuarioValidator(Validator):

    def is_valid(self):
        if not super(FormUsuarioValidator, self).is_valid():
            return False

        if  self._post['dependencia'] =='' and self._post['grupo'] =='' and self._post['identificacion'] =='' and self._post['username'] == '':
            self._message = 'Algunos campos fueron enviados vacios'
            return False

        if self._post['password'] == '' and self._post['rpassword'] == '':
            self._message = 'Los campos de contraseña estan vacios'
            return False

        elif not self._post['password'] == self._post['rpassword']:
            self._message = 'Las contraseñas no  coinciden'
            return False

        if User.objects.filter(username= self._post['username']).exists():
            self._message = 'El usuario ya ha sido creado'
            return False

        if not Group.objects.filter(id= self._post['grupo']).exists():
            self._message = 'El grupo ingresado no fue encontrado'
            return False

        return True

class FormLoginValidator(Validator):
    acceso = None

    def is_valid(self):
        if not super(FormLoginValidator, self).is_valid():
            return False

        usuario = self._post['username']
        clave = self._post['password']

        self.acceso = auth.authenticate(username = usuario, password = clave )
        if self.acceso is None:
            self._message = 'Usuario o contraseña inválido'
            return False
        return True
