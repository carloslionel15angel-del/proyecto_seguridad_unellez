from django.contrib import admin
from django.urls import path
from seguridad_unellez import views
from django.contrib.auth import views as auth_views

# 🌟 IMPORTACIONES CLAVE PARA SOPORTAR ARCHIVOS MULTIMEDIA
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔐 LOGIN Y AUTENTICACIÓN
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),

    # --- FLUJO DE RECUPERACIÓN DE CONTRASEÑA ---
    path('recuperar/', auth_views.PasswordResetView.as_view(
        template_name='seguridad_unellez/password_reset.html',
        success_url='/recuperar/enviado/'
    ), name='password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='seguridad_unellez/password_reset_done.html'
    ), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='seguridad_unellez/password_reset_confirm.html',
        success_url='/recuperar/completo/'
    ), name='password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='seguridad_unellez/password_reset_complete.html'
    ), name='password_reset_complete'),

    # 📋 PANEL DE MONITOREO
    path('guardias/', views.panel_guardias, name='panel_guardias'),
    
    # 🚨 RUTA DE EMERGENCIA
    path('enviar-alerta/', views.enviar_alerta, name='enviar_alerta'),

    # 📊 API PARA GRÁFICAS EN TIEMPO REAL
    path('api/incidencias-datos/', views.datos_grafica_incidencias, name='api_incidencias'),

    # 💂‍♂️ CRUD DE GUARDIAS Y LISTA NEGRA
    path('guardias/lista/', views.lista_guardias, name='lista_guardias'),
    path('guardias/lista-negra/', views.lista_negra, name='lista_negra'),
    path('guardias/nuevo/', views.crear_guardia, name='crear_guardia'),
    path('guardias/editar/<int:id>/', views.editar_guardia, name='editar_guardia'),
    path('guardias/eliminar/<int:id>/', views.eliminar_guardia, name='eliminar_guardia'),
    path('guardias/bloquear/<int:id>/', views.alternar_bloqueo_guardia, name='alternar_bloqueo_guardia'),

    # 👤 PORTAL PERSONAL
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('mi-perfil/actualizar-foto/', views.actualizar_foto_perfil, name='actualizar_foto_perfil'),
    path('mi-perfil/descargar-ficha/', views.descargar_ficha_pdf, name='descargar_ficha_pdf'),

    # 🚨 INCIDENCIAS
    path('incidencias/nueva/', views.registrar_incidencia, name='registrar_incidencia'),

    # 📅 GESTIÓN DE SOLICITUDES
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('guardias/solicitudes-recibidas/', views.panel_solicitudes_administrador, name='panel_solicitudes_administrador'),
    path('solicitudes/procesar/<int:solicitud_id>/<str:accion>/', views.procesar_solicitud, name='procesar_solicitud'),
    path('solicitudes/<int:solicitud_id>/descargar-pdf/', views.descargar_aprobacion_pdf, name='descargar_aprobacion_pdf'),

    # 💬 CANAL DE COMUNICACIÓN
    path('chat/', views.chat_seguridad, name='chat_seguridad'),
    path('chat/<str:username>/', views.chat_directo, name='chat_directo'),
    path('api/mensajes-nuevos/', views.verificar_mensajes_nuevos, name='verificar_mensajes_nuevos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)