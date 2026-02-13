from django.db import models

class Guardia(models.Model):
    # Campos que ya tenías
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10)
    turno = models.CharField(max_length=20)
    area_asignada = models.CharField(max_length=100)
    fecha_registro = models.DateField(auto_now_add=True)

    # --- NUEVOS CAMPOS ---
    horas_trabajadas = models.PositiveIntegerField(default=0, verbose_name="Horas Totales")
    dias_trabajados = models.PositiveIntegerField(default=0, verbose_name="Días Cumplidos")
    
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Inactivo', 'Inactivo'),
    ]
    estatus = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='Activo'
    )

    def __str__(self):
        return f"{self.nombre} - {self.area_asignada}"