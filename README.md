# Plataforma de Reclutamiento (Zubiani Asociados)

Una plataforma de reclutamiento moderna y de alto rendimiento diseñada para automatizar y agilizar los procesos de selección mediante Inteligencia Artificial. Construida con **Django**, **Celery** y **Google Gemini AI**, esta plataforma gestiona el ciclo de vida completo del reclutamiento, desde la captación de candidatos hasta la oferta final.

## 🚀 Funcionalidades Clave

- **Sistema Multi-Rol**: Acceso seguro para tres tipos de usuarios distintos:
  - **Candidatos**: Portal profesional para postulaciones y gestión de perfil.
  - **Empresas/Clientes**: Interfaz para publicar vacantes y seguir el estado de los postulantes.
  - **Staff/Reclutadores**: Dashboard administrativo completo con un sistema de gestión de postulaciones estilo Kanban.
- **Análisis de Candidatos mediante IA**: Integración con **Google Gemini Flash (1.5/2.0)** para:
  - Extracción automática de datos desde CVs en formato PDF.
  - Identificación de "Match Scores" (puntuación de coincidencia) basados en los requisitos específicos de la vacante.
  - Resúmenes ejecutivos de evaluación con análisis de puntos positivos y negativos.
- **Sistema de Killer Questions**: Filtrado automático mediante preguntas de cribado personalizables por cada vacante.
- **Comunicación Transaccional**: Integrado con **Brevo (Mailing)** para el envío automatizado de verificaciones de cuenta, acuses de recibo de postulaciones y notificaciones de estado.
- **Procesamiento de Tareas Asíncronas**: Backend con **Celery & Redis** que gestiona procesos en segundo plano, como el análisis de IA y el envío de correos, garantizando una alta capacidad de respuesta.
- **Arquitectura Escalable**: Despliegue dockerizado con soporte para PostgreSQL (producción) y SQLite (desarrollo).

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+, Django 5.1
- **Base de Datos**: SQLite (Desarrollo) / PostgreSQL (Producción mediante `dj-database-url`)
- **Cola de Tareas**: Celery con broker Redis
- **Integración de IA**: SDK de Google GenAI (Suite Gemini)
- **Mailing**: Brevo (Relay SMTP)
- **Frontend**: HTML5 vanilla, CSS3 (Sistema de estilos personalizado "Zubiani Asociados"), JavaScript
- **Archivos Estáticos**: WhiteNoise
- **Seguridad**: Cloudflare Turnstile (Anti-spam), HSTS, Protección CSRF, Cookies Seguras
- **Contenedores**: Docker & Docker Compose

## 🏗️ Estructura del Proyecto

El proyecto sigue una arquitectura Django modular orientada a dominios:

- `applications/`: Lógica central de reclutamiento, gestión de estados y algoritmos de puntuación.
- `candidates/`: Gestión de perfiles, sistema de etiquetas y almacenamiento de archivos de CV.
- `clients/`: Soporte para múltiples empresas y lógica de publicación de vacantes.
- `dashboard/`: Portal para reclutadores e implementación del tablero Kanban.
- `hr_project/`: Núcleo del proyecto (configuración, enrutamiento de URLs, configuración de Celery).
- `utils/`: Servicios compartidos (plantillas de correo Brevo, integración de Gemini AI, Cloudflare Turnstile).

## 💻 Instalación y Configuración

### Requisitos
- Python 3.11+
- Redis (para Celery)
- Docker (opcional)

### Desarrollo Local
1. Clonar el repositorio.
2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno en `.env`:
   ```bash
   SECRET_KEY=...
   DEBUG=True
   GEMINI_API_KEY=...
   EMAIL_HOST_USER=... (Login de Brevo)
   EMAIL_HOST_PASSWORD=... (Master Password o Key SMTP de Brevo)
   CELERY_BROKER_URL=redis://127.0.0.1:6379/0
   ```
5. Ejecutar migraciones e iniciar el servidor:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
6. (Opcional) Iniciar el worker de Celery:
   ```bash
   celery -A hr_project worker --loglevel=info
   ```

### Despliegue con Docker
```bash
docker build -t hr-platform .
docker run -p 8000:8000 --env-file .env hr-platform
```

## 🔐 Seguridad y Optimización

- **Fiabilidad en Emails**: Migración de AWS SES a **Brevo** para mejorar las tasas de entrega y facilitar la gestión de la reputación de envío.
- **Precisión de IA**: Utiliza salidas estructuradas JSON y esquemas Pydantic para obtener respuestas consistentes de la IA.
- **Listo para Producción**: Configurado con **Gunicorn** y cabeceras de seguridad para entornos de alta disponibilidad como **Coolify**.

---
*Desarrollado por Gerardo de Martini (para Zubiani Asociados)*
