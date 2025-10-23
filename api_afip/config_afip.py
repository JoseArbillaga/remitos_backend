# Configuración para Cliente AFIP
# INSTRUCCIONES DE USO:
# 1. Coloca tu certificado AFIP como "certificado_afip.crt"
# 2. Coloca tu clave privada como "clave_privada_afip.key"
# 3. Ajusta el AMBIENTE según necesites (testing/production)

# Archivos de certificado (DEBES PROPORCIONAR TUS ARCHIVOS)
CERTIFICADO_AFIP = "certificado_afip.crt"
CLAVE_PRIVADA_AFIP = "clave_privada_afip.key"

# Ambiente de trabajo
AMBIENTE = "testing"  # Cambiar a "production" para producción

# Servicios disponibles (activar según tus autorizaciones AFIP)
SERVICIOS_ACTIVOS = [
    "wslsp",           # Web Service de Liquidación Sector Pecuario
    "mtxca",           # Factura Electrónica Web Service  
    "remcarneservice"  # Webservice Remitos Electrónicos Cárnicos
]

# Configuración de tickets
HORAS_VALIDEZ_TICKET = 12  # Horas de validez del ticket de acceso

# NOTA: Para usar este sistema necesitas:
# - Certificado digital válido emitido por AC de confianza AFIP
# - Autorizaciones para los servicios que deseas usar
# - Clave privada correspondiente al certificado

# URLs de servicios (automático según ambiente)
# No modificar estas URLs a menos que AFIP las cambie oficialmente