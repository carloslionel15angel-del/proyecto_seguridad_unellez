from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Guardia
from .forms import GuardiaForm, RegistroUsuarioForm

# ============================
#   CRUD DE GUARDIAS
# ============================

@login_required
def lista_guardias(request):
    guardias = Guardia.objects.all()
    return render(request, 'seguridad_unellez/lista_guardias.html', {'guardias': guardias})

@login_required
def crear_guardia(request):
    if request.method == 'POST':
        formulario = GuardiaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Guardia registrado exitosamente.")
            return redirect('lista_guardias')
        else:
            messages.error(request, "Error al registrar el guardia. Verifique los datos.")
    else:
        formulario = GuardiaForm()
    
    return render(request, 'seguridad_unellez/registrar_guardia.html', {'formulario': formulario})

@login_required
def editar_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    if request.method == 'POST':
        formulario = GuardiaForm(request.POST, instance=guardia)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, f"Datos de {guardia.nombre} actualizados.")
            return redirect('lista_guardias')
    else:
        formulario = GuardiaForm(instance=guardia)
    
    return render(request, 'seguridad_unellez/editar_guardia.html', {'formulario': formulario})

@login_required
def eliminar_guardia(request, id):
    guardia = get_object_or_404(Guardia, id=id)
    if request.method == 'POST':
        nombre_guardia = guardia.nombre
        guardia.delete()
        messages.warning(request, f"Guardia {nombre_guardia} eliminado del sistema.")
        return redirect('lista_guardias')
    
    return render(request, 'seguridad_unellez/eliminar_guardia.html', {'guardia': guardia})

# ============================
#   REGISTRO DE USUARIOS
# ============================

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, "Cuenta creada con éxito. Ahora puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "No se pudo crear la cuenta. Revisa los errores en el formulario.")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'seguridad_unellez/registrar_usuario.html', {'form': form})