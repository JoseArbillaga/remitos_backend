# Configuración para Cliente AFIP
# CONFIGURACIÓN ACTUALIZADA PARA: sgpatagon25_23ad6985d1bcb772
# Certificado: sgpatagon25
# Entorno: Testing
# Fecha: 2025-10-23

# Archivos de certificado específicos para sgpatagon25
CERTIFICADO_AFIP = "sgpatagon25_certificado.crt"  # Certificado sgpatagon25
CLAVE_PRIVADA_AFIP = "sgpatagon25_private_key.key"  # Clave generada
CLAVE_PUBLICA_AFIP = "sgpatagon25_public_key.pem"   # Clave pública generada

# Identificación del certificado
CERTIFICADO_ID = "sgpatagon25_23ad6985d1bcb772"
CERTIFICADO_NOMBRE = "sgpatagon25"

# Ambiente de trabajo
AMBIENTE = "testing"  # Cambiar a "production" para producción

# Servicios disponibles para sgpatagon25 (activar según autorizaciones AFIP)
SERVICIOS_ACTIVOS = [
    "wsaa",            # Web Service de Autenticación y Autorización
    "wsfev1",          # Web Service de Facturación Electrónica v1
    "wsfe",            # Web Service de Facturación Electrónica
    "wslsp",           # Web Service de Liquidación Sector Pecuario
    "mtxca",           # Factura Electrónica Web Service  
    "remcarneservice", # Webservice Remitos Electrónicos Cárnicos
    "padron-a4",       # Padrón A4 (Constancia de Inscripción)
    "padron-a5",       # Padrón A5 (Padrón de Alcance General)
]

# Configuración de tickets y autenticación
HORAS_VALIDEZ_TICKET = 12  # Horas de validez del ticket de acceso
CUIT_EMPRESA = "30999999999"  # CUIT de la empresa (placeholder - configurar según sgpatagon25)
PUNTO_VENTA = 1  # Punto de venta autorizado

# Configuración específica para testing
TESTING_CONFIG = {
    "ambiente": "testing",
    "debug": True,
    "log_requests": True,
    "timeout": 30,  # segundos
    "reintentos": 3
}

# URLs de servicios AFIP para TESTING
URLS_TESTING = {
    "wsaa": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms",
    "wsfev1": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx",
    "wsfe": "https://wswhomo.afip.gov.ar/wsfe/service.asmx",
    "padron-a4": "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA4",
    "padron-a5": "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5",
}

# URLs de servicios AFIP para PRODUCCIÓN
URLS_PRODUCCION = {
    "wsaa": "https://wsaa.afip.gov.ar/ws/services/LoginCms",
    "wsfev1": "https://servicios1.afip.gov.ar/wsfev1/service.asmx",
    "wsfe": "https://servicios1.afip.gov.ar/wsfe/service.asmx",
    "padron-a4": "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA4",
    "padron-a5": "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5",
}

# Función para obtener URL según ambiente
def get_service_url(servicio, ambiente=AMBIENTE):
    """Obtiene la URL del servicio según el ambiente configurado"""
    urls = URLS_TESTING if ambiente == "testing" else URLS_PRODUCCION
    return urls.get(servicio)

# NOTA: Configuración completada para sgpatagon25_23ad6985d1bcb772
# - Certificado: sgpatagon25 (archivo .crt requerido)
# - Clave privada: sgpatagon25_private_key.key ✅ GENERADA
# - Clave pública: sgpatagon25_public_key.pem ✅ GENERADA
# - Ambiente: Testing (homologación AFIP)
# - Servicios: Configurados para extracción de datos