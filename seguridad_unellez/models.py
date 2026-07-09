from django.db import models
from django.contrib.auth.models import User

class Guardia(models.Model):
    # 👤 ENLACE AL USUARIO: Conecta el guardia con su cuenta para iniciar sesión
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario de Sistema")
    
    # Campos actuales
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20)
    turno = models.CharField(max_length=50)
    area_asignada = models.CharField(max_length=100)
    horas_trabajadas = models.IntegerField(default=0)
    dias_trabajados = models.IntegerField(default=0)
    
    # 🌟 NUEVO CAMPO: Foto de Perfil del Oficial
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    # 🌟 LISTA DE OPCIONES PARA EL ESTATUS (Se incluye 'Bloqueado' de forma consistente)
    ESTATUS_CHOICES = [
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Inactivo', 'Inactivo'),
        ('Bloqueado', 'Bloqueado'),
    ]
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='Activo')

    # 🔒 CONTROL DE SEGURIDAD INTERNA: Atributo técnico para suspender e impedir accesos
    esta_bloqueado = models.BooleanField(default=False, verbose_name="¿Cuenta Bloqueada?")

    def __str__(self):
        return self.nombre


# 🚨 CLASE DE INCIDENCIAS / NOVEDADES MODIFICADA
class Incidencia(models.Model):
    TIPO_CHOICES = [
        ('ROBO', 'Robo / Hurto'),
        ('FALLA', 'Falla de Infraestructura (Luz, Agua, Estructura)'),
        ('PERDIDA', 'Pérdida de Bienes'),
        ('ALTERCADO', 'Altercado / Pelea'),
        ('OTROS', 'Otros Eventos'),
    ]

    guardia = models.ForeignKey(Guardia, on_delete=models.CASCADE, related_name='incidencias', verbose_name="Guardia que reporta")
    
    # 🌟 Nuevos campos para coincidir exactamente con el formulario web
    titulo = models.CharField(max_length=200, default="Reporte de Guardia", verbose_name="Título o Asunto")
    area_suceso = models.CharField(max_length=150, blank=True, null=True, verbose_name="Ubicación o Área")
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='OTROS')
    descripcion = models.TextField(verbose_name="Descripción de la novedad")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora del evento")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario del sistema")

    # 🌟 NUEVO CAMPO MULTIMEDIA: Soporta imágenes o videos cargados desde el formulario
    archivo_evidencia = models.FileField(upload_to='evidencias_incidencias/', null=True, blank=True, verbose_name="Archivo de Evidencia (Imagen/Video)")

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.titulo} - {self.guardia.nombre}"


# 📅 NUEVO MÓDULO: CONTROL DE SOLICITUDES OPERATIVAS
class Solicitud(models.Model):
    TIPO_CHOICES = [
        ('VACACIONES', 'Vacaciones'),
        ('PERMISO', 'Permiso Remunerado'),
        ('LICENCIA', 'Licencia por Salud / Familiar'),
        ('CAMBIO_TURNO', 'Cambio de Turno'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    guardia = models.ForeignKey(Guardia, on_delete=models.CASCADE, related_name='solicitudes', verbose_name="Oficial solicitante")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='VACACIONES', verbose_name="Tipo de Solicitud")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Finalización")
    motivo = models.TextField(verbose_name="Justificación / Motivo")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado de Petición")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    revisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_revisadas', verbose_name="Administrador que revisó")

    class Meta:
        ordering = ['-creado_en']
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"

    def __str__(self):
        return f"Solicitud de {self.get_tipo_display()} - {self.guardia.nombre} ({self.get_estado_display()})"