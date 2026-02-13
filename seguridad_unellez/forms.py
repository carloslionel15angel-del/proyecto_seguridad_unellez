from django import forms
from django.contrib.auth.models import User
from .models import Guardia

class GuardiaForm(forms.ModelForm):
    class Meta:
        model = Guardia
        # Incluimos los campos básicos y los nuevos de control académico
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
            'estatus': forms.Select(attrs={'class': 'form-select'}), # Usamos Select para las opciones del modelo
        }

class RegistroUsuarioForm(forms.ModelForm):
    # Campos de contraseña con validación de seguridad
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