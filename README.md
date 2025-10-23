# Sistema de Gestión de Remitos con Integración AFIP

Sistema backend empresarial para la gestión de remitos con integración automática a AFIP (Argentina). Incluye autenticación JWT, autorización basada en roles, procesamiento asíncrono y validaciones específicas para el sistema tributario argentino.

## ✅ Estado del Proyecto

**🎉 PROYECTO COMPLETAMENTE FUNCIONAL** - Probado y verificado el 23 de octubre de 2025

- ✅ **Sistema base funcionando** - API REST operativa
- ✅ **Autenticación JWT** - Tokens generados y verificados
- ✅ **Base de datos** - SQLite inicializada correctamente  
- ✅ **Validaciones AFIP** - CUIT argentino validando con algoritmo oficial
- ✅ **Documentación** - Swagger UI disponible en `/docs`
- ✅ **Arquitectura completa** - 32 archivos Python, estructura modular
- ✅ **Tests incluidos** - Scripts de prueba del sistema y API

## 🚀 Características

- **API REST con FastAPI**: Framework moderno con documentación automática
- **Autenticación JWT**: Sistema seguro de tokens con roles de usuario
- **Autorización RBAC**: Control de acceso basado en roles (Admin, Operador, Consulta)
- **Integración AFIP**: Facturación electrónica automática con validaciones específicas
- **Procesamiento Asíncrono**: Cola de trabajos con Celery para envíos masivos
- **Validaciones Argentinas**: CUIT, códigos postales y formatos específicos
- **Tests Completos**: Suite de pruebas unitarias e integración
- **Base de Datos SQLAlchemy**: ORM con migraciones y modelos relacionales

## 🛠️ Instalación

### Requisitos Previos

- Python 3.8+
- Redis (para Celery)
- Certificados AFIP válidos

### 1. Clonar y configurar el proyecto

```bash
git clone <repository>
cd remitos_backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```env
# Base de datos
DATABASE_URL=sqlite:///./remitos.db

# JWT
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AFIP
AFIP_CUIT=20123456786
AFIP_CERT_PATH=./api_afip/certificado_afip.crt
AFIP_KEY_PATH=./api_afip/clave_privada_afip.key
AFIP_PASSPHRASE=tu_passphrase

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Aplicación
DEBUG=True
UPLOAD_DIR=./uploads
```

### 4. Configurar certificados AFIP

Colocar los certificados en la carpeta `api_afip/`:
- `certificado_afip.crt`: Certificado público AFIP
- `clave_privada_afip.key`: Clave privada del certificado

**Nota**: Los archivos de ejemplo ya están incluidos para referencia.

### 5. Inicializar base de datos

```bash
python -c "from database import init_db; init_db()"
```

### 6. Crear usuario administrador

```bash
python -c "
from app.services.auth_service import AuthService
from app.models.user import UserRole
from database import SessionLocal

with SessionLocal() as db:
    auth = AuthService(db)
    auth.create_user('admin@empresa.com', 'admin123', 'Admin', 'User', UserRole.ADMIN)
    print('Usuario admin creado')
"
```

## 🚀 Ejecución

### Pruebas Básicas

Antes de ejecutar el sistema completo, puedes probar que todo funciona:

```bash
# Ejecutar pruebas del sistema
python test_system.py

# Ejecutar pruebas completas de la API
python test_api_complete.py
```

### Desarrollo

1. **Iniciar Redis** (en terminal separado - opcional para pruebas básicas):
```bash
redis-server
```

2. **Iniciar Celery Worker** (en terminal separado - opcional para pruebas básicas):
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

3. **Iniciar aplicación**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
# Con Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# O con Docker
docker-compose up
```

## 📖 Uso de la API

### Acceso
- **API Base**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Autenticación

1. **Login**:
```bash
POST /auth/login
{
  "username": "admin@empresa.com",
  "password": "admin123"
}
```

2. **Usar token** en headers:
```
Authorization: Bearer <token>
```

### Endpoints Principales

#### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario (solo Admin)
- `GET /auth/me` - Obtener perfil actual

#### Remitos
- `GET /remitos` - Listar remitos
- `POST /remitos` - Crear remito
- `GET /remitos/{id}` - Obtener remito específico
- `PUT /remitos/{id}` - Actualizar remito
- `DELETE /remitos/{id}` - Eliminar remito

#### AFIP
- `POST /remitos/{id}/enviar-afip` - Enviar remito a AFIP
- `POST /remitos/lote-afip` - Enviar lote masivo
- `GET /afip/status/{task_id}` - Estado de tarea asíncrona

### Roles y Permisos

- **Admin**: Acceso completo, gestión de usuarios
- **Operador**: CRUD remitos, envío AFIP
- **Consulta**: Solo lectura

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
```

### Tests incluidos
- Autenticación y autorización
- CRUD de remitos
- Validaciones AFIP (CUIT, códigos)
- Integración con servicios externos
- Procesamiento asíncrono

### Ejemplo de Uso Rápido

```bash
# 1. Inicializar y probar el sistema
python test_system.py

# 2. Iniciar servidor
uvicorn main:app --host 127.0.0.1 --port 8000

# 3. Abrir documentación en el navegador
# http://127.0.0.1:8000/docs

# 4. Registrar usuario admin desde la interfaz Swagger
# 5. Hacer login y obtener token JWT
# 6. Usar token para crear remitos
```

## 🏗️ Arquitectura

```
remitos_backend/
├── app/
│   ├── core/            # Configuración Celery
│   ├── dependencies/    # Dependencias de auth
│   ├── models/          # Modelos SQLAlchemy (User, Remito)
│   ├── schemas/         # Schemas Pydantic
│   ├── routes/          # Endpoints FastAPI
│   ├── services/        # Lógica de negocio
│   ├── utils/           # Utilidades y validadores AFIP
│   └── tasks/           # Tareas Celery asíncronas
├── api_afip/            # Integración AFIP (certificados incluidos)
├── tests/               # Suite de tests (32 archivos Python)
├── uploads/             # Archivos subidos
├── config.py            # Configuración general
├── database.py          # Setup base de datos
├── main.py              # Punto de entrada FastAPI
├── test_system.py       # Pruebas del sistema
├── test_api_complete.py # Pruebas completas API
├── Dockerfile           # Containerización
└── docker-compose.yml   # Orquestación completa
```

### Tecnologías Utilizadas

- **FastAPI**: Framework web asíncrono
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación y serialización
- **JWT**: Autenticación por tokens
- **Celery**: Procesamiento asíncrono
- **Redis**: Broker para Celery
- **Pytest**: Framework de testing
- **Requests**: Cliente HTTP para AFIP

## 🔧 Configuración Avanzada

### Variables de Entorno Completas

Ver `.env.example` para todas las opciones de configuración.

### Logging

Los logs se guardan en `logs/` con rotación automática:
- `app.log`: Logs de aplicación
- `celery.log`: Logs de tareas asíncronas
- `afip.log`: Logs de integración AFIP

### Monitoreo Celery

```bash
# Monitor de tareas
celery -A app.tasks.celery_app flower

# Acceder en: http://localhost:5555
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error de certificados AFIP**:
   - Verificar paths en `.env`
   - Validar formato y vigencia
   - Revisar passphrase

2. **Redis no conecta**:
   - Verificar servicio Redis activo
   - Comprobar URL en configuración

3. **Tests fallan**:
   - Usar CUITs válidos en test data
   - Verificar base de datos de test

### Debug Mode

Activar debug en `.env`:
```
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📞 Soporte

Para soporte técnico o consultas:
- **Desarrollador**: Jose Arbillaga
- **Repositorio**: https://github.com/JoseArbillaga/api-afip
- **Issues**: GitHub Issues del proyecto
- **Documentación**: `/docs` endpoint (Swagger UI)
- **Fecha de desarrollo**: Octubre 2025