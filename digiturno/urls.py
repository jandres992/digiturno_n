from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from digiturno_app.views import *

urlpatterns = [
    path('', inicio, name='inicio'),
    path('inicio2/', inicio2, name='inicio2'),
    path('digiturno/', digiturno, name='digiturno'),
    path('turnos/', consulta_turno, name='consulta_turnos'),
    path('asignar_turnos/', asignar_turno, name='asignar_turnos'),
    path('asignar_turno_preferencial/', asignar_turno_preferencial, name='asignar_turno_preferencial'),
    path('proyeccion/', consulta_modulo, name='proyeccion_turnos'),
    path('anuncio/', anuncio, name='anuncios'),
    path('anuncio_gdr/', anuncio_save, name='anuncio_save'),
    path('logout/', logout, name='salir'),
    path('login/', login, name='entrar'),
    path('menu/', menu_admin, name='menu_admin'),
    path('usuarios/', usuario_sistema, name='usuarios'),
    path('logout_user/', logout_in_user, name='logout'),
    path('modulos/', estado_modulo, name='estado_modulo'),
    path('turno/', rellamar_turno, name='rellamar_turno'),
    path('no_turno/', rechazo_turno, name='rechazo_turno'),
    path('generacion_turnos/', generacion_turno, name='generacion_turnos'),
    path('ticket_turno/', ticket_turno, name='ticket_turno'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)