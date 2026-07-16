from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.conf import settings
from functools import wraps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from .models import Guardia, Solicitud, Incidencia, Mensaje
from .forms import GuardiaForm, RegistroUsuarioForm, IncidenciaForm, SolicitudForm, RegistroGuardiaForm

# =========================================================================
# DISEÑO INSTITUCIONAL (PDFs)
# =========================================================================
def dibujar_encabezado_unellez(p, width, height):
    """Encabezado institucional para los documentos PDF."""
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'seguridad_unellez', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 50, height - 90, width=60, height=60, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height - 50, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
    p.drawCentredString(width/2, height - 65, "DE LOS LLANOS OCCIDENTALES 'EZEQUIEL ZAMORA'")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height - 80, "VICE-RECTORADO DE PLANIFICACIÓN Y DESARROLLO SOCIAL")
    p.line(50, height - 95, 560, height - 95)

# =========================================================================
# DECORADOR DE PROTECCIÓN
# =========================================================================
def verificar_bloqueo(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        guardia = Guardia.objects.filter(user=request.user).first()
        if guardia and guardia.esta_bloqueado:
            messages.error(request, "Tu cuenta ha sido suspendida hasta nuevo aviso. Acceso denegado.")
            logout(request)
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# =========================================================================
# VISTAS: PANEL, AUTH, CHAT Y GESTIÓN
# =========================================================================

@login_required
@verificar_bloqueo
def panel_guardias(request):
    return render(request, 'seguridad_unellez/guardias.html', {
        'guardias': Guardia.objects.all(),
        'ultimas_incidencias': Incidencia.objects.all().order_by('-id')[:5]
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                guardia = Guardia.objects.filter(user=user).first()
                if guardia and guardia.esta_bloqueado:
                    messages.error(request, "Su cuenta ha sido suspendida. Contacte a un administrador.")
                    return render(request, 'seguridad_unellez/login.html', {'form': form})
                login(request, user)
                return redirect('panel_solicitudes_administrador' if user.is_staff else 'mis_solicitudes')
            messages.error(request, "Credenciales inválidas.")
    else:
        form = AuthenticationForm()
    return render(request, 'seguridad_unellez/login.html', {'form': form})

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroGuardiaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nuevo oficial registrado correctamente.")
            return redirect('lista_guardias')
    else:
        form = RegistroGuardiaForm()
    return render(request, 'seguridad_unellez/registrar_usuario.html', {'form': form})

@login_required
def enviar_alerta(request):
    if request.method == 'POST':
        messages.success(request, "¡Alerta de emergencia enviada!")
        return redirect('mi_perfil')
    return redirect('mi_perfil')

@login_required
@verificar_bloqueo
def chat_seguridad(request):
    otro_usuario = User.objects.exclude(id=request.user.id).first()
    if otro_usuario:
        return redirect('chat_directo', username=otro_usuario.username)
    return render(request, 'seguridad_unellez/chat_directo.html', {'error': 'No hay contactos disponibles'})

@login_required
@verificar_bloqueo
def chat_directo(request, username=None):
    guardias = Guardia.objects.exclude(user=request.user)
    mensajes = []
    receptor = None
    
    if username:
        receptor = User.objects.filter(username=username).first()
        if receptor:
            # MARCAR MENSAJES RECIBIDOS COMO LEÍDOS
            Mensaje.objects.filter(emisor__user=receptor, receptor=request.user, leido=False).update(leido=True)
            
            mensajes = Mensaje.objects.filter(
                (Q(emisor__user=request.user) & Q(receptor=receptor)) |
                (Q(emisor__user=receptor) & Q(receptor=request.user))
            ).order_by('fecha_envio')
        else:
            messages.error(request, "El usuario seleccionado no existe.")

    if request.method == 'POST' and receptor:
        contenido = request.POST.get('contenido')
        if contenido:
            emisor_guardia = Guardia.objects.filter(user=request.user).first()
            if emisor_guardia:
                Mensaje.objects.create(emisor=emisor_guardia, receptor=receptor, contenido=contenido)
        return redirect('chat_directo', username=username)

    return render(request, 'seguridad_unellez/chat_directo.html', {
        'guardias': guardias,
        'mensajes': mensajes,
        'receptor': receptor
    })

# API PARA NOTIFICACIONES
@login_required
def verificar_mensajes_nuevos(request):
    count = Mensaje.objects.filter(receptor=request.user, leido=False).count()
    return JsonResponse({'nuevos': count})

@login_required
@verificar_bloqueo
def registrar_incidencia(request):
    guardia_actual = Guardia.objects.filter(user=request.user).first()
    if request.method == 'POST':
        Incidencia.objects.create(guardia=guardia_actual, titulo=request.POST.get('titulo'),
                                  area_suceso=request.POST.get('area'), descripcion=request.POST.get('descripcion'),
                                  creado_por=request.user)
        messages.success(request, "Incidencia registrada.")
        return redirect('panel_guardias')
    return render(request, 'seguridad_unellez/registrar_incidencia.html', {'guardia': guardia_actual})

@login_required
def datos_grafica_incidencias(request):
    data = Incidencia.objects.values('tipo').annotate(total=Count('tipo'))
    return JsonResponse(list(data), safe=False)

@login_required
def panel_solicitudes_administrador(request):
    estado = request.GET.get('estado', 'PENDIENTE')
    solicitudes = Solicitud.objects.all().order_by('-creado_en')
    if estado != 'TODAS': solicitudes = solicitudes.filter(estado=estado)
    return render(request, 'seguridad_unellez/panel_solicitudes.html', {'solicitudes': solicitudes, 'estado_actual': estado})

@login_required
@verificar_bloqueo
def mis_solicitudes(request):
    guardia = Guardia.objects.filter(user=request.user).first()
    solicitudes = Solicitud.objects.filter(guardia=guardia).order_by('-creado_en') if guardia else []
    return render(request, 'seguridad_unellez/mis_solicitudes.html', {'guardia': guardia, 'solicitudes_historial': solicitudes})

@login_required
@verificar_bloqueo
def crear_solicitud(request):
    if request.method == 'POST':
        guardia_obj = Guardia.objects.filter(user=request.user).first()
        if guardia_obj:
            Solicitud.objects.create(guardia=guardia_obj, tipo=request.POST.get('tipo'),
                                     fecha_inicio=request.POST.get('fecha_inicio'), fecha_fin=request.POST.get('fecha_fin'),
                                     motivo=request.POST.get('descripcion'), estado='PENDIENTE')
            messages.success(request, "Solicitud enviada correctamente.")
        return redirect('mis_solicitudes')
    return render(request, 'seguridad_unellez/crear_solicitud.html')

@login_required
def procesar_solicitud(request, solicitud_id, accion):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    solicitud.estado = 'APROBADA' if accion == 'aprobar' else 'RECHAZADA'
    solicitud.save()
    messages.success(request, f"Solicitud {accion}ada.")
    return redirect('panel_solicitudes_administrador')

@login_required
def descargar_aprobacion_pdf(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="solicitud_{solicitud.id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    dibujar_encabezado_unellez(p, width, height)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 150, "COMPROBANTE DE SOLICITUD APROBADA")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 200, f"Oficial: {solicitud.guardia.nombre}")
    p.drawString(100, height - 220, f"Estado: {solicitud.estado}")
    p.drawString(100, height - 240, f"Motivo: {solicitud.motivo}")
    p.showPage()
    p.save()
    return response

# =========================================================================
# 4. CRUD Y PERFIL
# =========================================================================
@login_required
def lista_guardias(request):
    guardias = Guardia.objects.all()
    query = request.GET.get('q')
    if query: guardias = guardias.filter(Q(nombre__icontains=query) | Q(cedula__icontains=query))
    return render(request, 'seguridad_unellez/lista_guardias.html', {'guardias': guardias, 'incidencias': Incidencia.objects.all().order_by('-id')})

@login_required
def lista_negra(request):
    return render(request, 'seguridad_unellez/lista_negra.html', {'guardias': Guardia.objects.filter(esta_bloqueado=True)})

@login_required
def crear_guardia(request):
    return render(request, 'seguridad_unellez/registrar_guardia.html')

@login_required
def editar_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    if request.method == 'POST':
        guardia.nombre = request.POST.get('nombre')
        guardia.apellido = request.POST.get('apellido')
        guardia.email = request.POST.get('email')
        guardia.cedula = request.POST.get('cedula')
        guardia.turno = request.POST.get('turno')
        guardia.area_asignada = request.POST.get('area')
        guardia.save()
        messages.success(request, "Guardia actualizado.")
        return redirect('lista_guardias')
    return render(request, 'seguridad_unellez/registrar_guardia.html', {'guardia': guardia})

@login_required
def eliminar_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    if request.method == 'POST':
        guardia.delete()
        messages.success(request, "Guardia eliminado.")
        return redirect('lista_guardias')
    return render(request, 'seguridad_unellez/confirmar_eliminar.html', {'guardia': guardia})

@login_required
def alternar_bloqueo_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    guardia.esta_bloqueado = not guardia.esta_bloqueado
    guardia.save()
    return redirect('lista_guardias')

@login_required
def mi_perfil(request):
    return render(request, 'seguridad_unellez/mi_perfil.html', {'guardia': Guardia.objects.filter(user=request.user).first()})

@login_required
def actualizar_foto_perfil(request):
    messages.info(request, "Función de foto en desarrollo.")
    return redirect('mi_perfil')

@login_required
def descargar_ficha_pdf(request):
    guardia = Guardia.objects.filter(user=request.user).first()
    if not guardia: return HttpResponse("No se encontró el guardia.")
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_{guardia.nombre}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    p.setLineWidth(2)
    p.rect(30, 50, 550, 720)
    
    # --- Logo y Cabecera ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'seguridad_unellez', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, height - 120, width=80, height=80, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 70, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
    p.drawCentredString(width/2, height - 90, "DE LOS LLANOS OCCIDENTALES 'EZEQUIEL ZAMORA'")
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 120, "FICHA TÉCNICA DEL OFICIAL")
    p.line(50, height - 135, 560, height - 135)
    
    # --- Datos ---
    y = height - 200
    datos = [
        ("Nombre:", guardia.nombre.upper()),
        ("Apellido:", guardia.apellido.upper()),
        ("Cédula:", guardia.cedula),
        ("Email:", guardia.email),
        ("Turno:", guardia.turno.upper()),
        ("Estatus:", "BLOQUEADO" if guardia.esta_bloqueado else "ACTIVO"),
        ("Cargo:", "Oficial de Seguridad"),
    ]
    
    for label, value in datos:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(60, y, label)
        p.setFont("Helvetica", 11)
        p.drawString(220, y, str(value))
        p.line(60, y - 5, 550, y - 5)
        y -= 40
        
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(width/2, 80, "Documento emitido por el Sistema de Seguridad Unellez")
    p.showPage()
    p.save()
    return response