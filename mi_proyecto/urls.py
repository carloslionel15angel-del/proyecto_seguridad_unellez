from django.contrib import admin
from django.urls import path
from seguridad_unellez import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login y Logout
    path('', auth_views.LoginView.as_view(template_name='seguridad_unellez/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro de Usuarios
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),

    # --- FLUJO DE RECUPERACIÓN DE CONTRASEÑA ---
    path('recuperar/', auth_views.PasswordResetView.as_view(
        template_name='seguridad_unellez/password_reset.html',
        email_template_name='seguridad_unellez/password_reset_email.html',
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
    # ------------------------------------------

    # CRUD de Guardias
    path('guardias/', views.lista_guardias, name='lista_guardias'),
    path('guardias/nuevo/', views.crear_guardia, name='crear_guardia'),
    path('guardias/editar/<int:id>/', views.editar_guardia, name='editar_guardia'),
    path('guardias/eliminar/<int:id>/', views.eliminar_guardia, name='eliminar_guardia'),
]