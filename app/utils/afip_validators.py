"""
Validadores específicos para AFIP Argentina
"""
import re
from typing import Optional
from datetime import datetime, date
from pydantic import validator

def validar_cuit(cuit: str) -> bool:
    """
    Validar CUIT argentino usando algoritmo oficial
    """
    if not cuit or len(cuit) != 11:
        return False
    
    if not cuit.isdigit():
        return False
    
    # Coeficientes para el cálculo del dígito verificador
    coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    # Calcular suma ponderada de los primeros 10 dígitos
    suma = sum(int(cuit[i]) * coeficientes[i] for i in range(10))
    
    # Calcular resto de la división por 11
    resto = suma % 11
    
    # Calcular dígito verificador según las reglas de AFIP
    if resto == 0:
        digito_verificador = 0
    elif resto == 1:
        digito_verificador = 9
    else:
        digito_verificador = 11 - resto
    
    # Verificar que el último dígito coincida
    return int(cuit[10]) == digito_verificador

def validar_formato_remito(numero_remito: str) -> bool:
    """
    Validar formato de número de remito
    Formato típico: R-XXXXXXXX (R- seguido de 8 dígitos)
    """
    if not numero_remito:
        return False
    
    patron = r'^R-\d{8}$'
    return bool(re.match(patron, numero_remito))

def validar_patente_argentina(patente: str) -> bool:
    """
    Validar formato de patente argentina
    Formatos válidos:
    - ABC123 (3 letras + 3 números)
    - AB123CD (2 letras + 3 números + 2 letras)
    """
    if not patente:
        return True  # Patente es opcional
    
    # Limpiar espacios y convertir a mayúsculas
    patente = patente.strip().upper()
    
    # Formato antiguo: 3 letras + 3 números
    patron_antiguo = r'^[A-Z]{3}\d{3}$'
    
    # Formato Mercosur: 2 letras + 3 números + 2 letras
    patron_mercosur = r'^[A-Z]{2}\d{3}[A-Z]{2}$'
    
    return bool(re.match(patron_antiguo, patente) or re.match(patron_mercosur, patente))

def validar_peso_carnico(peso: float) -> bool:
    """
    Validar peso cárnico según normativas AFIP
    - Debe ser positivo
    - Máximo 50 toneladas por remito típico
    """
    if peso is None:
        return False
    
    return 0 < peso <= 50000  # 50 toneladas en kg

def validar_fecha_emision(fecha: datetime) -> bool:
    """
    Validar fecha de emisión de remito
    - No puede ser futura
    - No puede ser muy antigua (más de 30 días)
    """
    if not fecha:
        return False
    
    hoy = datetime.now()
    hace_30_dias = datetime.now().replace(day=1) if hoy.day > 1 else datetime.now().replace(month=hoy.month-1 if hoy.month > 1 else 12)
    
    return hace_30_dias <= fecha <= hoy

def validar_razon_social(razon_social: str) -> bool:
    """
    Validar razón social según normativas AFIP
    """
    if not razon_social:
        return False
    
    # Debe tener entre 2 y 200 caracteres
    if len(razon_social.strip()) < 2 or len(razon_social.strip()) > 200:
        return False
    
    # No debe contener solo números
    if razon_social.strip().isdigit():
        return False
    
    return True

def validar_observaciones_afip(observaciones: Optional[str]) -> bool:
    """
    Validar observaciones según límites AFIP
    """
    if not observaciones:
        return True  # Observaciones son opcionales
    
    # Máximo 1000 caracteres para observaciones
    if len(observaciones) > 1000:
        return False
    
    # Caracteres no permitidos según AFIP
    caracteres_prohibidos = ['<', '>', '&', '"', "'", '\\']
    if any(char in observaciones for char in caracteres_prohibidos):
        return False
    
    return True

class AFIPValidationError(Exception):
    """Excepción para errores de validación AFIP"""
    pass

def validar_remito_completo(remito_data: dict) -> dict:
    """
    Validar un remito completo según normativas AFIP
    Retorna dict con errores encontrados
    """
    errores = {}
    
    # Validar CUIT emisor
    if not validar_cuit(remito_data.get('emisor_cuit', '')):
        errores['emisor_cuit'] = 'CUIT del emisor inválido'
    
    # Validar CUIT receptor
    if not validar_cuit(remito_data.get('receptor_cuit', '')):
        errores['receptor_cuit'] = 'CUIT del receptor inválido'
    
    # Validar CUIT transporte (opcional)
    cuit_transporte = remito_data.get('transporte_cuit')
    if cuit_transporte and not validar_cuit(cuit_transporte):
        errores['transporte_cuit'] = 'CUIT del transporte inválido'
    
    # Validar número de remito
    if not validar_formato_remito(remito_data.get('numero_remito', '')):
        errores['numero_remito'] = 'Formato de número de remito inválido (debe ser R-XXXXXXXX)'
    
    # Validar patente
    if not validar_patente_argentina(remito_data.get('patente_vehiculo', '')):
        errores['patente_vehiculo'] = 'Formato de patente inválido'
    
    # Validar peso
    peso = remito_data.get('peso_total')
    if peso is not None and not validar_peso_carnico(peso):
        errores['peso_total'] = 'Peso inválido (debe ser entre 0.1 y 50000 kg)'
    
    # Validar fecha emisión
    fecha_emision = remito_data.get('fecha_emision')
    if isinstance(fecha_emision, str):
        try:
            fecha_emision = datetime.fromisoformat(fecha_emision.replace('Z', '+00:00'))
        except:
            errores['fecha_emision'] = 'Formato de fecha inválido'
            fecha_emision = None
    
    if fecha_emision and not validar_fecha_emision(fecha_emision):
        errores['fecha_emision'] = 'Fecha de emisión inválida (no puede ser futura o muy antigua)'
    
    # Validar razones sociales
    if not validar_razon_social(remito_data.get('emisor_razon_social', '')):
        errores['emisor_razon_social'] = 'Razón social del emisor inválida'
    
    if not validar_razon_social(remito_data.get('receptor_razon_social', '')):
        errores['receptor_razon_social'] = 'Razón social del receptor inválida'
    
    # Validar observaciones
    if not validar_observaciones_afip(remito_data.get('observaciones')):
        errores['observaciones'] = 'Observaciones inválidas (máximo 1000 caracteres, sin caracteres especiales)'
    
    return errores

def generar_numero_remito_automatico(cuit_emisor: str, secuencia: int) -> str:
    """
    Generar número de remito automático
    Formato: R-{últimos 4 dígitos del CUIT}{secuencia de 4 dígitos}
    """
    if not validar_cuit(cuit_emisor):
        raise AFIPValidationError("CUIT del emisor inválido")
    
    ultimos_4_cuit = cuit_emisor[-4:]
    secuencia_str = str(secuencia).zfill(4)
    
    return f"R-{ultimos_4_cuit}{secuencia_str}"