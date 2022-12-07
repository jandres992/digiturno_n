import json, datetime, locale, wave, os, time, re, paramiko
from wakeonlan import send_magic_packet
from random import randint
from django.shortcuts import render
from .validador import *
from django.db import transaction
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from digiturno.settings import SOUNDS_ROOT, BASE_DIR

locale.setlocale(locale.LC_ALL, 'es_CO.utf8')

def login(request):
    if request.method == 'GET':
        modulos = Modulo.objects.all().order_by('modulo')
        if 'aviso' in request.session:
            aviso_s = request.session['aviso']
            aviso = aviso_s['aviso']
            ind = aviso_s['ind']
            del request.session['aviso']
        else:
            aviso = "Bienvenido, Ingrese su usuario y contraseña para continuar"
            ind = 1

        return render(request, 'login/login.html', {'aviso': aviso, 'ind': ind,'modulos':modulos})

    if request.method == 'POST':
        validador = FormLoginValidator(request.POST)
        validador.required = ['username', 'password']

        if validador.is_valid():
            auth_login(request, validador.acceso)
            if request.POST['modulo'] == "0":
                grupo_usr = Usuario.objects.filter(usuario__username=request.POST['username'])
                cont = 0
                for g in grupo_usr:
                    if g.permiso.name == 'Administrador' or g.permiso.name == 'Usuario':
                        return HttpResponseRedirect('/menu')
                    else:
                        cont = cont + 1

                    if cont == len(grupo_usr):
                        request.session['aviso'] = {'aviso':"No tiene permisos para ingresar al administrador",'ind':0}
                        return HttpResponseRedirect('/login')
            else:
                request.session['modulo'] = request.POST['modulo']
                modulo = Modulo.objects.get(modulo=request.POST['modulo'])
                modulo.habilitado = True
                modulo.usuario = request.user
                modulo.turno = "DISP"
                modulo.save()

                return HttpResponseRedirect('/digiturno')
        else:
            request.session['aviso'] = {'aviso': "Usuaro o contraseña invalido", 'ind': 0}
            return HttpResponseRedirect('/login')


def inicio(request):
    if request.method == "GET":
        img = os.listdir(BASE_DIR +'/static/img/slide/')
        modulos = Modulo.objects.filter(habilitado=True).order_by('modulo')
        hoy = datetime.date.today()
        
        return render(request, 'digiturno/digiturno_pantalla.html', {'modulos':modulos,'imgs': img})

def inicio2(request):
    if request.method == "GET":
        img = os.listdir(BASE_DIR +'/static/img/slide/')
        return render(request, 'digiturno/digiturno_pantalla2.html', {'imgs': img, 'base_dir':str(BASE_DIR)})


def estado_modulo(request):
    if request.method == 'GET':
        modulos = Modulo.objects.all().order_by('id')
        digiturno = Digiturno.objects.filter(llamado=True,fecha__gt=datetime.date.today()).order_by("-fecha")
        estado_digiturno = Digiturno.objects.filter(llamado=False,fecha__gt=datetime.date.today()).order_by("-fecha")
        hora_actual = datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M"),"%H:%M")
        output = ""
        for m in modulos:
            if m.turno != "DISP":
                list = digiturno.filter(modulo__modulo=m.modulo)[:1]
                if list.exists():
                    u_fecha = datetime.datetime.strptime(datetime.datetime.strftime(list[0].fecha_atendido,"%H:%M"),"%H:%M")
                    if hora_actual.hour-u_fecha.hour >= 1:
                        update = m
                        update.usuario = None
                        update.turno = "N/D"
                        update.save()
                        output = True
                    else:
                        pass
                else:
                    pass

                if not estado_digiturno.exists() and m.turno != "N/D":
                    update = m
                    update.turno = "DISP"
                    update.save()
                    output = True
            else:
                pass

        return HttpResponse(json.dumps(output), content_type="application/json")


@login_required(login_url="/login")
def digiturno(request):
    if request.method == 'GET':
        servicios_list = []
        servicios = Servicio.objects.all().order_by('id')
        perfiles = Usuario.objects.filter(usuario=request.user)
        especialidad = Especialidad.objects.all().order_by('especialidad')
        cont_especialidad = len(especialidad)
        for s in servicios:
            for p in perfiles:
                if p.permiso.name == s.servicio:
                    servicios_list.append({'id':s.id,'servicio':s.servicio})

        modulo = ""
        if 'modulo' in request.session:
            modulo = request.session['modulo']
            del request.session['modulo']

        if modulo == "":
            return HttpResponseRedirect("/logout")
        else:
            return render(request, 'digiturno/digiturno_llamado.html', {'servicios':servicios_list,'modulo':modulo,'especialidad':especialidad, 'cont_especialidad':cont_especialidad})

def anuncio_save(request):
    if request.method == 'GET':
        update = Digiturno.objects.get(id=request.GET['id-digiturno'])
        update.aviso = True
        update.save()
        data = "ok"
        return HttpResponse(json.dumps(data), content_type="application/json")


def anuncio(request):
    time.sleep(5)
    if request.method == 'GET':
        digiturno = Digiturno.objects.filter(aviso=False, llamado=True, fecha__gt=datetime.date.today()).order_by('id')[:1]
        if digiturno:
            d = digiturno[0]
            outfile = llamado_turno(d)
            lista = {'id': d.id, 'modulo':d.modulo.modulo,'turno':d.no_turno, 'audio': outfile}
        else:
            lista = ""

        return HttpResponse(json.dumps(lista), content_type="application/json")


def rellamar_turno(request):
    if request.method == 'GET':
        turno = Digiturno.objects.get(id=request.GET['id_turno'])
        turno.aviso = False
        turno.atencion = False
        turno.save()

        return HttpResponse(json.dumps("ok"), content_type="application/json")


def rechazo_turno(request):
    if request.method == 'GET':
        turno = Digiturno.objects.get(id=request.GET['id_turno'])
        turno.atencion = False
        turno.save()

        return HttpResponse(json.dumps("ok"), content_type="application/json")


def llamado_turno(d):
    if os.path.exists(SOUNDS_ROOT + "/modulos/" + str(d.modulo.modulo) + "-" + str(d.no_turno) + ".wav") == False:
        if os.path.exists(SOUNDS_ROOT + "/numeros/" + str(d.no_turno) + ".wav") == False:
            cifras = len(str(d.no_turno))
            if cifras == 3:
                cifra1 = str(d.no_turno)[0] + "00"
                if str(d.no_turno)[1:2] == "0":
                    cifra2 = str(d.no_turno)[2]
                else:
                    cifra2 = str(d.no_turno)[1:]

                if int(d.no_turno) > 100 and int(d.no_turno) < 200:
                    audio1 = SOUNDS_ROOT + "/ciento.wav"
                else:
                    audio1 = SOUNDS_ROOT + "/numeros/" + cifra1 + ".wav"

                audio2 = SOUNDS_ROOT + "/numeros/" + cifra2 + ".wav"
                mezclar_audio(audio1, audio2, SOUNDS_ROOT + "/numeros/" + str(d.no_turno) + ".wav")

        audio1 = SOUNDS_ROOT + "/turno.wav"
        audio2 = SOUNDS_ROOT + "/numeros/" + str(d.no_turno) + ".wav"
        outfile1 = mezclar_audio(audio1, audio2, SOUNDS_ROOT + "/tmp/" + str(d.no_turno) + "1.wav")
        audio3 = SOUNDS_ROOT + "/modulo.wav"
        audio4 = SOUNDS_ROOT + "/numeros/" + str(d.modulo.modulo) + ".wav"
        outfile2 = mezclar_audio(audio3, audio4, SOUNDS_ROOT + "/tmp/" + str(d.no_turno) + "2.wav")
        mezclar_audio(outfile1, outfile2,
                      SOUNDS_ROOT + "/modulos/" + str(d.modulo.modulo) + "-" + str(d.no_turno) + ".wav")
        os.remove(SOUNDS_ROOT + "/tmp/" + str(d.no_turno) + "1.wav")
        os.remove(SOUNDS_ROOT + "/tmp/" + str(d.no_turno) + "2.wav")

    outfile = "/static/sounds/modulos/" + str(d.modulo.modulo) + "-" + str(d.no_turno) + ".wav"
    return outfile


def mezclar_audio(audio1,audio2,ruta):
    data = []
    infiles =[audio1,audio2]
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    outfile = ruta
    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    output.writeframes(data[0][1])
    output.writeframes(data[1][1])
    output.close()
    return outfile


def asignar_turno(request):
    if request.method == "GET":
        servicio = request.GET['servicio']
        modulo = request.GET['modulo']
        turnos = Digiturno.objects.filter(llamado=False, general=True,fecha__gt=datetime.date.today(), servicio__id=servicio).order_by('fecha')[:1]
        update = Modulo.objects.filter(modulo=modulo)
        id_turno = ""
        no_turno = ""
        if update.filter(usuario=request.user).exists():
            if turnos.exists():
                update_modulo = update[0]
                update_modulo.turno = turnos[0].no_turno
                update_modulo.hora = datetime.datetime.now()
                update_modulo.save()

                updated = turnos[0]
                updated.modulo = update[0]
                updated.llamado = True
                updated.atencion = True
                updated.fecha_atendido = timezone.now()
                updated.usuario = request.user
                updated.save()

                id_turno = updated.id
                no_turno = updated.no_turno
            output = {"id_turno":str(id_turno),'turno':str(no_turno)}
        else:
            output = 0

        return HttpResponse(json.dumps(output), content_type="application/json")


@login_required(login_url="/login")
def asignar_turno_preferencial(request):
    if request.method == "GET":
        id_turno = request.GET['id_turno']
        modulo = request.GET['modulo']
        turno = Digiturno.objects.get(id=id_turno)
        update = Modulo.objects.get(modulo=modulo)

        update_modulo = update
        update_modulo.turno = turno.no_turno
        update_modulo.hora = datetime.datetime.now()
        update_modulo.save()

        updated = turno
        updated.modulo = update
        updated.llamado = True
        updated.atencion = True
        updated.fecha_atendido = timezone.now()
        updated.usuario = request.user
        updated.save()

        id_turno = updated.id
        no_turno = updated.no_turno
        output = {'ind':"ok",'id_turno':id_turno,'no_turno':no_turno}

        return HttpResponse(json.dumps(output), content_type="application/json")


def consulta_modulo(request):
    if request.method == "GET":
        modulos = Modulo.objects.filter(habilitado=True).order_by("modulo")
        lista = []
        for m in modulos:
            lista.append({'id':m.id,'modulo':m.modulo,'turno':m.turno})
        output = lista

        return HttpResponse(json.dumps(output), content_type="application/json")


def consulta_turno(request):
    if request.method == "GET":
        servicio = Servicio.objects.all()
        hoy = datetime.date.today()
        turnos = Digiturno.objects.filter(fecha__gt=hoy).order_by('id','fecha')
        lista = []
        conteo = []
        for s in servicio:
            conteo.append({'servicio':s.id,'valor':len(turnos.filter(llamado=False,servicio_id=s.id,general=True))})
        for t in turnos:
            dic = {'id':t.id,'turno':t.no_turno,'fecha':datetime.datetime.strftime(t.fecha,"%I:%M:%S %p"),'servicio':t.servicio.id,
                   'letra':t.servicio.letra,'llamado':t.llamado,'general':t.general,'preferencial':t.preferencial,
                   'servicio_text':t.servicio.servicio}
            lista.append(dic)

        output = {'lista':lista,'conteo':conteo}
        return HttpResponse(json.dumps(output), content_type="application/json")


@login_required(login_url="/login")
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/login")


def logout_in_user(request):
    if request.method == 'GET':
        modulo = request.GET['modulo']
        if modulo != "":
            modulos = Modulo.objects.get(modulo=modulo)
            modulos.usuario = None
            modulos.turno = "N/D"
            modulos.save()
            auth_logout(request)
            output = '1'
        else:
            output = '0'

        return HttpResponse(json.dumps(output), content_type="application/json")


@login_required(login_url="/login")
def menu_admin(request):
    if request.method == 'GET':
        list_permisos = check_permisos(request)
        aviso = {'aviso': str('Bienvenido, '+request.user.first_name +' '+request.user.last_name).title(), 'ind': 1}
        servicios_n = []
        estadistica = []
        servicio = Servicio.objects.all().order_by('id')
        modulos = Modulo.objects.all().order_by('modulo')
        digiturno_a = Digiturno.objects.filter(llamado=True,fecha__gt=datetime.date.today()).order_by('fecha')
        digiturno_n = Digiturno.objects.filter(llamado=False, fecha__gt=datetime.date.today()).order_by('fecha')
        estadistica_fac = []
        usuarios = Usuario.objects.all()
        facturadores = []

        for s in servicio:
            no_turnos = len(digiturno_n.filter(servicio__id=s.id))
            servicios_n.append({'id':s.id,'nombre':str(s.servicio).title(),'color': s.color,'icon': s.icon,'no_turnos':no_turnos})
            no_turnos_a = []
            for m in modulos:
                no_turno = len(digiturno_a.filter(servicio=s,modulo=m))
                no_turnos_a.append(no_turno)
            estadistica.append({'servicio':s.servicio,'turnos':no_turnos_a,'color':s.color})

        for us in usuarios:
            if us.permiso.name == 'FACT. SERVICIOS MEDICOS':
                facturadores.append({'id':us.usuario.id,'nombre':us.usuario.first_name+" "+us.usuario.last_name})

        for f in facturadores:
            turnos_a = len(digiturno_a.filter(usuario__id=f['id'],servicio__letra="F"))
            estadistica_fac.append({'facturador':f['nombre'],'turnos_a':turnos_a,'color':"rgb("+str(randint(0,255))+","+ str(randint(0,255))+","+str(randint(0,255))+")"})

        total = len(digiturno_a.filter(servicio__letra="F"))

        return render(request, 'admin/inicio/inicio.html',{'aviso':aviso['aviso'], 'ind':aviso['ind'],
                                                           'permisos':list_permisos,'turnos':servicios_n,'modulos':modulos,
                                                           'estadistica':estadistica, 'facturadores':estadistica_fac,'total':total})
    else:
        return HttpResponseRedirect('/login')


def check_permisos(request):
    permisos = Usuario.objects.filter(usuario=request.user)
    list_permisos = []
    for p in permisos:
        list_permisos.append(p.permiso.name)
    return list_permisos


@login_required(login_url="/login")
def usuario_sistema(request):
    if request.method == 'GET':
        grupo = Group.objects.all().order_by('name')
        users = User.objects.all().order_by('username').exclude(username=request.user.username)
        perfiles = Usuario.objects.all().order_by('usuario__username').exclude(usuario__username=request.user.username)
        usuarios = []
        for u in users:
            permiso = []
            for p in perfiles:
                if p.usuario.id == u.id:
                    permiso.append(p.permiso.name)
            usuarios.append({'id':u.id,'username':u.username,'nombre':u.first_name+" "+u.last_name,'perfil':permiso,'is_active':u.is_active})

        if 'habilitar_usuario' in request.GET:
            user = User.objects.get(id=request.GET['habilitar_usuario'])
            user.is_active = True
            user.save()

            request.session['aviso'] = {'aviso': 'El usuario ha sido activado', 'ind': 2}
            return HttpResponseRedirect('/usuarios')

        if 'inhabilitar_usuario' in request.GET:
            user = User.objects.get(id=request.GET['inhabilitar_usuario'])
            user.is_active = False
            user.save()

            request.session['aviso'] = {'aviso': 'El usuario ha sido desactivado', 'ind': 2}
            return HttpResponseRedirect('/usuarios')

        if 'aviso' in request.session:
            aviso = request.session['aviso']
            del request.session['aviso']
        else:
            aviso = {'aviso': 'diligencie los datos del formulario para crear un usuario nuevo', 'ind': 1}

        return render(request, 'admin/configuracion/usuario_sistema.html',{'aviso':aviso['aviso'], 'ind':aviso['ind'],
                                                                     'grupo':grupo,'usuarios':usuarios,'permisos':check_permisos(request)})
    if request.method == 'POST':
        try:
            crear = User()
            crear.username = str(request.POST['username']).lower()
            crear.first_name = str(request.POST['nombre']).title()
            crear.last_name = str(request.POST['apellido']).title()
            crear.email = str(request.POST['email'])
            if request.POST['password'] == request.POST['rpassword']:
                crear.password = make_password(request.POST['password'])
            else:
                request.session['aviso'] = {'aviso':'Las contraseñas no coinciden'}
                return HttpResponseRedirect('/usuarios')

            crear.save()

            grupo = Group.objects.get(id=request.POST['grupo'])
            extra = Usuario()
            extra.usuario_id = crear.id
            extra.permiso = grupo
            extra.save()

            request.session['aviso'] = {'aviso': 'El usuario ha sido creado correctamente', 'ind': 2}
        except:
            request.session['aviso'] = {'aviso': 'Error en el servidor, comuniquese con el area de sistemas', 'ind': 0}

        return HttpResponseRedirect('/usuarios')
    else:
        return HttpResponseRedirect('/logout')


def generacion_turno(request):
    if request.method == 'GET':
        servicios = Servicio.objects.all().order_by('id')
        return render(request, 'digiturno/digiturno_turnos.html',{'servicios':servicios})

    if request.method == 'POST':
        tipo_turno = request.POST['tipo_turno']
        id_servicio = request.POST['id_servicio']

        servicio_act = Servicio.objects.get(id=id_servicio)
        horario_fin = servicio_act.horario_fin
        actual = datetime.datetime.now().time()
        if actual <= horario_fin:
            rango_ini = servicio_act.rango_ini
            rango_fin = servicio_act.rango_fin

            turno = Turno.objects.get(servicio__id=id_servicio)
            turno_act = int(turno.turno)
            if turno_act >= rango_fin:
                new_turno = rango_ini
            else:
                new_turno = turno_act + 1

            new_digiturno = Digiturno()
            new_digiturno.no_turno = new_turno
            new_digiturno.fecha = datetime.datetime.now()
            new_digiturno.servicio_id = id_servicio
            new_digiturno.aviso = False
            new_digiturno.llamado = False
            new_digiturno.atencion = False
            if tipo_turno == "o":
                tipo_turno_text = "TURNO GENERAL:"
                new_digiturno.general = True
                new_digiturno.preferencial = False
            else:
                tipo_turno_text = "TURNO PREFERENCIAL:"
                new_digiturno.general = False
                new_digiturno.preferencial = True
            new_digiturno.save()

            act_turno = turno
            act_turno.turno = new_turno
            act_turno.save()

            if int(new_turno) <= 9:
                turno_text = "00" + new_turno
            elif int(new_turno) >= 10 and int(new_turno) < 100:
                turno_text = "0" + str(new_turno)
            else:
                turno_text = new_turno

            fecha_text = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y %I:%M:%S %p")
            servicio_text = str(servicio_act.servicio).upper()

            output = {'ind':1,'turno':turno_text,'fecha':fecha_text,'servicio':servicio_text,'rango_ini':rango_ini,'rango_fin':rango_fin, 'tipo_turno':tipo_turno_text}
        else:
            servicio_text = str(servicio_act.servicio).upper()
            output = {'ind':0,'horario':servicio_act.horario,'servicio':servicio_text}

        return HttpResponse(json.dumps(output), content_type="application/json")


def ticket_turno(request):
    return render(request, 'digiturno/ticket_turno.html')
