# 🇦🇷 API AFIP - Servicios Web REST para AFIP Argentina

**API REST completa** construida con FastAPI que integra servicios web oficiales de AFIP (Administración Federal de Ingresos Públicos). Proporciona endpoints HTTP para autenticación y autorización WSAA según especificación oficial.

## 🚀 **Características Principales**

### API REST FastAPI
- ✅ **Endpoints HTTP** - API REST completa con documentación automática
- ✅ **FastAPI** - Framework moderno con validación automática
- ✅ **Swagger UI** - Documentación interactiva en `/docs`
- ✅ **CORS habilitado** - Listo para integración frontend
- ✅ **Manejo de errores** - Respuestas HTTP estructuradas
- ✅ **Logging completo** - Seguimiento de todas las operaciones

### Integración AFIP 🇦🇷
- ✅ **100% Especificación Oficial** - Protocolo WSAA completo
- ✅ **Múltiples servicios** - WSLSP, MTXCA, RemCarneService
- ✅ **Ambientes configurables** - Testing y Producción
- ✅ **Manejo de certificados** - X.509v3 y archivos .p12
- ✅ **CLI incluido** - Interfaz línea de comandos adicional

## 🔧 **Instalación**

### 1. Requisitos del Sistema
- Python 3.8+
- OpenSSL (agregado al PATH)
- Certificado AFIP válido emitido por AC de confianza

### 2. Configuración del Entorno
```bash
# Clonar repositorio
git clone https://github.com/JoseArbillaga/api-afip.git
cd api-afip

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Certificados

#### **Método 1: Archivos separados (Recomendado)**
```bash
# Si ya tienes archivos separados:
# - certificado_afip.crt (certificado público)
# - clave_privada_afip.key (clave privada)
# Simplemente colócalos en el directorio del proyecto
```

#### **Método 2: Archivo .p12/.pfx de AFIP**
```bash
# Si AFIP te entregó un archivo .p12 o .pfx:

# Extraer certificado:
openssl pkcs12 -in tu_archivo_afip.p12 -out certificado_afip.crt -clcerts -nokeys

# Extraer clave privada:
openssl pkcs12 -in tu_archivo_afip.p12 -out clave_privada_afip.key -nocerts -nodes

# Te pedirá la contraseña del archivo .p12
```

#### **Verificar correspondencia**
```bash
# Verificar que certificado y clave coincidan:
openssl x509 -noout -modulus -in certificado_afip.crt | openssl md5
openssl rsa -noout -modulus -in clave_privada_afip.key | openssl md5
# Los hashes deben ser idénticos
```

### 4. Configuración Final
```bash
# Editar config_afip.py con tus datos:
# - Verificar rutas de certificados
# - Configurar ambiente (testing/production)
# - Activar servicios requeridos
```

## 🚀 **Uso**

### Iniciar la API REST
```bash
# Método 1: Directamente con Python
python main.py

# Método 2: Con uvicorn
uvicorn main:app --reload

# La API estará disponible en:
# http://127.0.0.1:8000
# Documentación: http://127.0.0.1:8000/docs
```

### Usar la API REST

#### Obtener ticket para un servicio específico
```bash
# GET request
curl http://127.0.0.1:8000/afip/ticket/wslsp

# POST request  
curl -X POST http://127.0.0.1:8000/afip/ticket/wslsp
```

#### Verificar configuración
```bash
curl http://127.0.0.1:8000/afip/configuracion
```

#### Obtener todos los tickets
```bash
curl -X POST http://127.0.0.1:8000/afip/tickets/todos
```

### Usar CLI (Alternativo)
```bash
# Verificar configuración completa
python ejecutar_afip.py --verificar

# Verificar conectividad con AFIP
python ejecutar_afip.py --conectividad

# Mostrar servicios disponibles
python ejecutar_afip.py --servicios

# Obtener ticket para servicio específico
python ejecutar_afip.py --servicio wslsp
python ejecutar_afip.py --servicio mtxca
python ejecutar_afip.py --servicio remcarneservice

# Obtener tickets para todos los servicios
python ejecutar_afip.py --todos

# Usar ambiente de producción
python ejecutar_afip.py --servicio wslsp --produccion
```

### Ejemplo de Uso Programático
```python
import requests

# URL base de tu API
API_BASE = "http://127.0.0.1:8000"

# Obtener ticket para WSLSP
response = requests.post(f"{API_BASE}/afip/ticket/wslsp")
ticket = response.json()

print(f"Token: {ticket['token']}")
print(f"Sign: {ticket['sign']}")
print(f"Válido hasta: {ticket['expiration_time']}")

# Verificar configuración
config = requests.get(f"{API_BASE}/afip/configuracion").json()
print(f"Ambiente: {config['ambiente']}")
print(f"Certificado OK: {config['certificado_configurado']}")
```

## 📋 **Requisitos AFIP**

### 1. Certificado Digital
- ✅ Emitido por Autoridad Certificante reconocida por AFIP
- ✅ Formato X.509v3 en PEM
- ✅ Vigente y no revocado
- ✅ Asociado a tu CUIT en AFIP

### 2. Autorizaciones de Servicios
- ✅ Solicitar autorizaciones en AFIP → Administrador de Relaciones
- ✅ Asociar certificado a los servicios requeridos
- ✅ Verificar estado "Autorizado"

### 3. Configuración de Red
- ✅ Conexión HTTPS a servicios AFIP
- ✅ Sin proxy restrictivo para dominios *.afip.gov.ar

## 🔐 **Seguridad**

- ⚠️ **NUNCA** compartas tu clave privada
- ✅ Usa ambiente `testing` para pruebas
- ✅ Cambia a `production` solo cuando esté validado
- ✅ Mantén backups seguros de certificados
- ✅ Verifica certificados antes de usar

## 📊 **URLs Oficiales AFIP**

### Testing (Homologación)
- **WSAA:** https://wsaahomo.afip.gov.ar/ws/services/LoginCms
- **WSLSP:** https://wswhomo.afip.gov.ar/wslsp/LspService
- **MTXCA:** https://wswhomo.afip.gov.ar/wsmtxca/services/MTXCAService
- **RemCarne:** https://wswhomo.afip.gov.ar/remcarne/RemCarneService

### Producción
- **WSAA:** https://wsaa.afip.gov.ar/ws/services/LoginCms
- **WSLSP:** https://serviciosjava.afip.gob.ar/wslsp/LspService
- **MTXCA:** https://serviciosjava.afip.gob.ar/wsmtxca/services/MTXCAService
- **RemCarne:** https://serviciosjava.afip.gob.ar/remcarne/RemCarneService

## 🛠️ **Estructura del Proyecto**

```
api-afip/
├── main.py                           # 🚀 API REST FastAPI principal
├── afip_client.py                    # 🔐 Cliente AFIP WSAA
├── config_afip.py                    # ⚙️ Configuración centralizada
├── ejecutar_afip.py                  # 💻 Interfaz CLI (alternativa)
├── certificado_afip.crt              # 📄 Tu certificado AFIP (requerido)
├── clave_privada_afip.key            # 🔑 Tu clave privada (requerido)
├── certificado_afip.crt.ejemplo      # 📋 Template certificado
├── clave_privada_afip.key.ejemplo    # 📋 Template clave privada
├── requirements.txt                  # 📦 Dependencias Python
├── .gitignore                        # 🚫 Archivos ignorados por Git
├── README.md                         # 📖 Este archivo
├── README_AFIP.md                    # 📚 Documentación técnica detallada
└── LICENSE                           # 📄 Licencia MIT
```

## 🔧 **Solución de Problemas**

### Error: OpenSSL no encontrado
```bash
# Windows: Descargar e instalar OpenSSL
# Agregar al PATH: C:\Program Files\OpenSSL-Win64\bin
```

### Error: Certificado no válido
- ✅ Verificar que sea emitido por AC de confianza AFIP
- ✅ Confirmar que no esté expirado
- ✅ Validar formato PEM

### Error: Clave privada no coincide
```bash
# Verificar correspondencia con comandos OpenSSL mostrados arriba
```

### Error: Servicio no autorizado
- ✅ Verificar autorizaciones en AFIP → Administrador de Relaciones
- ✅ Confirmar que certificado esté asociado al servicio

## 🧪 **Testing**

```bash
# Verificar configuración completa
python ejecutar_afip.py --verificar

# Test de conectividad
python ejecutar_afip.py --conectividad

# Test con ambiente de homologación
python ejecutar_afip.py --servicio wslsp --testing
```

## 📚 **Documentación Adicional**

- **README_AFIP.md** - Documentación técnica completa
- **Documentación AFIP oficial:** https://www.afip.gob.ar/ws/
- **Mesa de Ayuda AFIP:** https://www.afip.gob.ar/sitio/externos/default.asp

## 🤝 **Contribuir**

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Realizar cambios y agregar tests
4. Commit con mensaje descriptivo
5. Push a la rama (`git push origin feature/nueva-funcionalidad`)
6. Crear Pull Request

## 📝 **Historial de Cambios**

### v1.0.0 (2025-10-12)
- ✅ Implementación completa protocolo WSAA
- ✅ Soporte servicios WSLSP, MTXCA, RemCarneService
- ✅ CLI funcional con todas las operaciones
- ✅ Manejo de certificados y validaciones
- ✅ Documentación completa

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

**🇦🇷 Sistema desarrollado según especificaciones oficiales de AFIP Argentina**  
**⚡ Listo para usar en producción con certificados válidos**