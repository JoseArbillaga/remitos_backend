# 🇦🇷 Cliente AFIP - Sistema de Integración con Servicios Web

Sistema completo para integración con servicios web de AFIP (Argentina) que implementa el protocolo WSAA (Web Service de Autenticación y Autorización) según especificación oficial.

## 🎯 **Servicios Soportados**

- **WSLSP** - Web Service de Liquidación Sector Pecuario
- **MTXCA** - Factura Electrónica Web Service (Monotributo)
- **RemCarneService** - Webservice Remitos Electrónicos Cárnicos

## 🔧 **Instalación**

### 1. Requisitos del Sistema
- Python 3.8+
- OpenSSL (agregado al PATH)
- Certificado AFIP válido emitido por AC de confianza

### 2. Configuración del Entorno
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements_afip.txt
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

## 🚀 **Uso**

### Comandos Principales
```bash
# Verificar configuración
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

## 📋 **Requisitos AFIP**

### 1. Certificado Digital
- Emitido por Autoridad Certificante reconocida por AFIP
- Formato X.509v3 en PEM
- Vigente y no revocado

### 2. Autorizaciones de Servicios
- Solicitar autorizaciones en AFIP → Administrador de Relaciones
- Asociar certificado a los servicios requeridos
- Verificar estado "Autorizado"

### 3. Configuración de Red
- Conexión HTTPS a servicios AFIP
- Sin proxy restrictivo para dominios *.afip.gov.ar

## 🔐 **Seguridad**

- ⚠️ **NUNCA** compartas tu clave privada
- ✅ Usa ambiente `testing` para pruebas
- ✅ Cambia a `production` solo cuando esté validado
- ✅ Mantén backups seguros de certificados

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
proyecto_api/
├── afip_client.py          # Cliente principal AFIP WSAA
├── config_afip.py          # Configuración centralizada
├── ejecutar_afip.py        # Interfaz CLI
├── extraer_clave_afip.py   # Extractor de claves .p12
├── certificado_afip.crt    # Tu certificado AFIP (requerido)
├── clave_privada_afip.key  # Tu clave privada (requerido)
└── requirements_afip.txt   # Dependencias Python
```

## 🔧 **Solución de Problemas**

### Error: OpenSSL no encontrado
```bash
# Descargar e instalar OpenSSL
# Agregar al PATH: C:\Program Files\OpenSSL-Win64\bin
```

### Error: Certificado no válido
- Verificar que sea emitido por AC de confianza AFIP
- Confirmar que no esté expirado
- Validar formato PEM

### Error: Clave privada no coincide
```bash
# Verificar correspondencia
python extraer_clave_afip.py
```

## 📞 **Soporte**

- **Documentación AFIP:** https://www.afip.gob.ar/ws/
- **Mesa de Ayuda AFIP:** https://www.afip.gob.ar/sitio/externos/default.asp

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

**🇦🇷 Sistema desarrollado según especificaciones oficiales de AFIP Argentina**