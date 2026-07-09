from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Guardia, Solicitud, Incidencia
from .forms import GuardiaForm, RegistroUsuarioForm, IncidenciaForm, SolicitudForm, RegistroGuardiaForm

# =========================================================================
# DECORADOR DE PROTECCIÓN
# =========================================================================
def verificar_bloqueo(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        guardia = Guardia.objects.filter(usuario=request.user).first()
        if guardia and guardia.esta_bloqueado:
            messages.error(request, "Tu cuenta ha sido suspendida hasta nuevo aviso. Acceso denegado.")
            logout(request)
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# =========================================================================
# 1. PANEL DE MONITOREO
# =========================================================================
@login_required
@verificar_bloqueo
def panel_guardias(request):
    return render(request, 'seguridad_unellez/guardias.html', {
        'guardias': Guardia.objects.all(),
        'ultimas_incidencias': Incidencia.objects.all().order_by('-id')[:5]
    })

# =========================================================================
# 2. AUTENTICACIÓN Y REGISTRO
# =========================================================================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                guardia = Guardia.objects.filter(usuario=user).first()
                if guardia and guardia.esta_bloqueado:
                    messages.error(request, "Su cuenta ha sido suspendida hasta nuevo aviso. Contacte a un administrador.")
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

# =========================================================================
# 3. SOLICITUDES E INCIDENCIAS
# =========================================================================
@login_required
@verificar_bloqueo
def registrar_incidencia(request):
    guardia_actual = Guardia.objects.filter(usuario=request.user).first()
    if request.method == 'POST':
        Incidencia.objects.create(
            guardia=guardia_actual,
            titulo=request.POST.get('titulo'),
            area_suceso=request.POST.get('area'),
            descripcion=request.POST.get('descripcion'),
            creado_por=request.user
        )
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
    if estado != 'TODAS':
        solicitudes = solicitudes.filter(estado=estado)
    return render(request, 'seguridad_unellez/panel_solicitudes.html', {
        'solicitudes': solicitudes, 
        'estado_actual': estado
    })

@login_required
@verificar_bloqueo
def mis_solicitudes(request):
    guardia = Guardia.objects.filter(usuario=request.user).first()
    solicitudes = Solicitud.objects.filter(guardia=guardia).order_by('-creado_en') if guardia else []
    return render(request, 'seguridad_unellez/mis_solicitudes.html', {'guardia': guardia, 'solicitudes_historial': solicitudes})

@login_required
@verificar_bloqueo
def crear_solicitud(request):
    if request.method == 'POST':
        guardia_obj = Guardia.objects.filter(usuario=request.user).first()
        Solicitud.objects.create(
            guardia=guardia_obj,
            tipo=request.POST.get('tipo'),
            fecha_inicio=request.POST.get('fecha_inicio'),
            fecha_fin=request.POST.get('fecha_fin'),
            motivo=request.POST.get('descripcion'), 
            estado='PENDIENTE'
        )
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
    messages.info(request, "Función PDF en desarrollo.")
    return redirect('panel_solicitudes_administrador')

# =========================================================================
# 4. CRUD DE GUARDIAS, PERFIL, LISTA NEGRA Y BITÁCORA
# =========================================================================
@login_required
def lista_guardias(request):
    query = request.GET.get('q')
    area = request.GET.get('area')
    turno = request.GET.get('turno')
    guardias = Guardia.objects.all()
    if query:
        guardias = guardias.filter(Q(nombre__icontains=query) | Q(cedula__icontains=query))
    if area:
        guardias = guardias.filter(area_asignada=area)
    if turno:
        guardias = guardias.filter(turno__icontains=turno)
    incidencias = Incidencia.objects.all().order_by('-id')
    return render(request, 'seguridad_unellez/lista_guardias.html', {
        'guardias': guardias,
        'incidencias': incidencias
    })

@login_required
def lista_negra(request):
    guardias_bloqueados = Guardia.objects.filter(esta_bloqueado=True)
    return render(request, 'seguridad_unellez/lista_negra.html', {'guardias': guardias_bloqueados})

@login_required
def crear_guardia(request):
    return render(request, 'seguridad_unellez/registrar_guardia.html')

@login_required
def editar_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    if request.method == 'POST':
        # Procesamiento manual para evitar problemas con el formulario manual en HTML
        guardia.nombre = request.POST.get('nombre')
        guardia.cedula = request.POST.get('cedula')
        guardia.turno = request.POST.get('turno')
        guardia.area_asignada = request.POST.get('area')
        guardia.save()
        messages.success(request, "Guardia actualizado correctamente.")
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
@verificar_bloqueo
def mi_perfil(request):
    guardia = Guardia.objects.filter(usuario=request.user).first()
    return render(request, 'seguridad_unellez/mi_perfil.html', {'guardia': guardia})

@login_required
def actualizar_foto_perfil(request):
    messages.info(request, "Función de foto en desarrollo.")
    return redirect('mi_perfil')

@login_required
def descargar_ficha_pdf(request):
    messages.info(request, "Función PDF en desarrollo.")
    return redirect('mi_perfil')