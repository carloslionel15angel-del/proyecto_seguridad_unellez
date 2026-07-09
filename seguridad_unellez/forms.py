from django import forms
from django.contrib.auth.models import User
from .models import Guardia, Incidencia, Solicitud

class GuardiaForm(forms.ModelForm):
    class Meta:
        model = Guardia
        fields = [
            'nombre', 
            'cedula', 
            'turno', 
            'area_asignada', 
            'horas_trabajadas', 
            'dias_trabajados', 
            'estatus'
        ]
        
        labels = {
            'nombre': 'Nombre completo',
            'cedula': 'Cédula',
            'turno': 'Turno de guardia',
            'area_asignada': 'Área asignada',
            'horas_trabajadas': 'Total horas acumuladas',
            'dias_trabajados': 'Días de asistencia',
            'estatus': 'Estatus del oficial',
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Brayan Gonzalez'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 24256265'}),
            'turno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Nocturno'}),
            'area_asignada': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Laboratorios'}),
            'horas_trabajadas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'dias_trabajados': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'estatus': forms.Select(choices=Guardia.ESTATUS_CHOICES, attrs={'class': 'form-select'}),
        }


class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'new-password' 
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data


# 🔥 FORMULARIO PARA EL MÓDULO DE INCIDENCIAS
class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['guardia', 'tipo', 'descripcion']
        labels = {
            'guardia': 'Oficial / Guardia Responsable',
            'tipo': 'Tipo de Novedad o Incidencia',
            'descripcion': 'Detalles de lo ocurrido',
        }
        widgets = {
            'guardia': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describa detalladamente los hechos, bienes afectados, condiciones, etc...'
            }),
        }


# 📅 NUEVO FORMULARIO: GESTIÓN DE SOLICITUDES (VACACIONES / PERMISOS)
class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['tipo', 'fecha_inicio', 'fecha_fin', 'motivo']
        labels = {
            'tipo': 'Tipo de Solicitud',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'motivo': 'Justificación / Motivo',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Explique de forma detallada el motivo de su solicitud o el cambio requerido...'
            }),
        }

# ==========================================================
# AGREGADO: Formulario para Registro de Nuevo Guardia/Usuario
# ==========================================================
class RegistroGuardiaForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Guardia
        fields = ['nombre', 'cedula', 'area_asignada', 'turno']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'area_asignada': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Crea el usuario en el sistema usando la cédula como usuario
        user = User.objects.create_user(
            username=self.cleaned_data['cedula'], 
            password=self.cleaned_data['password']
        )
        guardia = super().save(commit=False)
        guardia.usuario = user
        if commit:
            guardia.save()
        return guardia