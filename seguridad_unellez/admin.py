from django.contrib import admin
from .models import Guardia, Incidencia

# Registro del modelo de Guardias
@admin.register(Guardia)
class GuardiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'area_asignada', 'turno', 'estatus')
    list_filter = ('estatus', 'turno')
    search_fields = ('nombre', 'cedula')

# 🚨 REGISTRO DEL MODELO DE INCIDENCIAS (Esto es lo que falta)
@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('guardia', 'tipo', 'fecha_hora', 'creado_por')
    list_filter = ('tipo', 'fecha_hora')
    search_fields = ('guardia__nombre', 'descripcion')