"""
Utilidades generales para el proyecto
"""
import re
from datetime import datetime
from typing import Optional

def validar_cuit(cuit: str) -> bool:
    """
    Validar formato y dígito verificador de CUIT argentino
    """
    if not cuit or len(cuit) != 11:
        return False
    
    if not cuit.isdigit():
        return False
    
    # Algoritmo de validación de CUIT
    multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(cuit[i]) * multiplicadores[i] for i in range(10))
    
    resto = suma % 11
    if resto == 0:
        digito_verificador = 0
    elif resto == 1:
        return False  # CUIT inválido
    else:
        digito_verificador = 11 - resto
    
    return int(cuit[10]) == digito_verificador

def formatear_cuit(cuit: str) -> str:
    """
    Formatear CUIT con guiones: XX-XXXXXXXX-X
    """
    if len(cuit) == 11 and cuit.isdigit():
        return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
    return cuit

def limpiar_cuit(cuit: str) -> str:
    """
    Limpiar CUIT removiendo guiones y espacios
    """
    return re.sub(r'[^0-9]', '', cuit)

def generar_numero_remito(prefijo: str = "REM") -> str:
    """
    Generar número de remito único basado en timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefijo}-{timestamp}"

def validar_patente(patente: str) -> bool:
    """
    Validar formato de patente argentina
    Formatos válidos: ABC123, ABC1234, AB123CD
    """
    if not patente:
        return False
    
    patente = patente.upper().replace(" ", "")
    
    # Formato viejo: ABC123 (3 letras + 3 números)
    if re.match(r'^[A-Z]{3}[0-9]{3}$', patente):
        return True
    
    # Formato nuevo: AB123CD (2 letras + 3 números + 2 letras)
    if re.match(r'^[A-Z]{2}[0-9]{3}[A-Z]{2}$', patente):
        return True
    
    # Formato mercosur: AB123CD o ABC1234
    if re.match(r'^[A-Z]{3}[0-9]{4}$', patente):
        return True
    
    return False

def formatear_peso(peso: float) -> str:
    """
    Formatear peso con 2 decimales y unidad
    """
    return f"{peso:.2f} kg"

def formatear_fecha(fecha: datetime) -> str:
    """
    Formatear fecha en formato DD/MM/YYYY HH:MM
    """
    return fecha.strftime("%d/%m/%Y %H:%M")

def es_cuit_valido_afip(cuit: str) -> bool:
    """
    Validación adicional de CUIT para servicios de AFIP
    """
    cuit_limpio = limpiar_cuit(cuit)
    
    if not validar_cuit(cuit_limpio):
        return False
    
    # Verificar que no sea un CUIT de prueba o inválido
    cuits_invalidos = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999"
    ]
    
    return cuit_limpio not in cuits_invalidos