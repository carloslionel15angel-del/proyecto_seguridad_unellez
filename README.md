# Sistema de Seguridad UNELLEZ
Sistema de control académico y registro de guardias para Ingeniería en Informática.

## Características
- Registro de Oficiales con estatus dinámico.
- Control de horas y asistencia.
- Interfaz moderna con Bootstrap 5 y Glassmorphism.

## Instalación
1. Clonar el repositorio.
2. Crear entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Migrar base de datos: `python manage.py migrate`.
5. Ejecutar: `python manage.py runserver`.