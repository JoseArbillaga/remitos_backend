#!/usr/bin/env python3
"""
Rutas específicas para integración AFIP con certificado sgpatagon25
Endpoints para extracción de datos de AFIP en entorno de testing
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os

# Añadir el directorio api_afip al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api_afip'))

try:
    from api_afip.sgpatagon25_client import AFIPClientSgpatagon25
    from api_afip.config_afip import CERTIFICADO_ID, AMBIENTE, SERVICIOS_ACTIVOS
except ImportError as e:
    print(f"⚠️ Error importando módulos AFIP: {e}")
    AFIPClientSgpatagon25 = None

from app.dependencies.auth import get_current_active_user
from app.schemas.user import User

# Router para endpoints AFIP
router = APIRouter(prefix="/afip", tags=["AFIP Integration"])

@router.get("/", summary="Estado del sistema AFIP")
async def afip_status():
    """Obtiene el estado actual del sistema AFIP"""
    return {
        "sistema": "AFIP Integration",
        "certificado": CERTIFICADO_ID,
        "ambiente": AMBIENTE,
        "servicios_activos": SERVICIOS_ACTIVOS,
        "timestamp": datetime.now().isoformat(),
        "estado": "operativo" if AFIPClientSgpatagon25 else "configuracion_requerida"
    }

@router.get("/diagnostico", summary="Diagnóstico completo AFIP")
async def afip_diagnostico(current_user: User = Depends(get_current_active_user)):
    """
    Ejecuta un diagnóstico completo del sistema AFIP
    Requiere autenticación de usuario
    """
    if not AFIPClientSgpatagon25:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP no disponible. Verificar configuración."
        )
    
    try:
        cliente = AFIPClientSgpatagon25()
        resultados = cliente.run_diagnostico_completo()
        
        return {
            "usuario": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "certificado": CERTIFICADO_ID,
            "diagnostico": resultados,
            "recomendaciones": generar_recomendaciones(resultados)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en diagnóstico AFIP: {str(e)}"
        )

@router.get("/padron-a4/{cuit}", summary="Consultar Padrón A4")
async def consultar_padron_a4(
    cuit: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Consulta datos del Padrón A4 de AFIP para un CUIT específico
    Padrón A4: Constancia de Inscripción
    """
    if not AFIPClientSgpatagon25:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP no disponible"
        )
    
    # Validar formato CUIT
    if not validar_cuit_format(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido. Debe ser 11 dígitos."
        )
    
    try:
        cliente = AFIPClientSgpatagon25()
        datos = cliente.obtener_padron_a4(cuit)
        
        return {
            "cuit_consultado": cuit,
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "datos_padron_a4": datos,
            "fuente": "AFIP Padrón A4",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando Padrón A4: {str(e)}"
        )

@router.get("/padron-a5/{cuit}", summary="Consultar Padrón A5")
async def consultar_padron_a5(
    cuit: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Consulta datos del Padrón A5 de AFIP para un CUIT específico
    Padrón A5: Padrón de Alcance General (más completo)
    """
    if not AFIPClientSgpatagon25:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP no disponible"
        )
    
    if not validar_cuit_format(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPClientSgpatagon25()
        datos = cliente.obtener_padron_a5(cuit)
        
        return {
            "cuit_consultado": cuit,
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "datos_padron_a5": datos,
            "fuente": "AFIP Padrón A5",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando Padrón A5: {str(e)}"
        )

@router.get("/datos-completos/{cuit}", summary="Extracción completa de datos")
async def extraer_datos_completos(
    cuit: str,
    incluir_padron_a4: bool = Query(True, description="Incluir datos del Padrón A4"),
    incluir_padron_a5: bool = Query(True, description="Incluir datos del Padrón A5"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Extrae datos completos de AFIP para un CUIT
    Combina múltiples fuentes de información
    """
    if not AFIPClientSgpatagon25:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP no disponible"
        )
    
    if not validar_cuit_format(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPClientSgpatagon25()
        datos_completos = cliente.extraer_datos_completos(cuit)
        
        # Filtrar datos según parámetros
        if not incluir_padron_a4:
            datos_completos.pop("padron_a4", None)
            
        if not incluir_padron_a5:
            datos_completos.pop("padron_a5", None)
        
        return {
            "cuit_consultado": cuit,
            "usuario_consulta": current_user.username,
            "parametros": {
                "incluir_padron_a4": incluir_padron_a4,
                "incluir_padron_a5": incluir_padron_a5
            },
            "timestamp": datetime.now().isoformat(),
            "datos_afip": datos_completos,
            "certificado_usado": CERTIFICADO_ID,
            "ambiente": AMBIENTE,
            "servicios_disponibles": SERVICIOS_ACTIVOS
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en extracción completa: {str(e)}"
        )

@router.post("/batch-consulta", summary="Consulta en lote")
async def consulta_batch(
    cuits: List[str],
    tipo_consulta: str = Query("padron-a5", description="Tipo de consulta: padron-a4, padron-a5, completa"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Realiza consultas en lote para múltiples CUITs
    Útil para procesar grandes cantidades de datos
    """
    if not AFIPClientSgpatagon25:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP no disponible"
        )
    
    if len(cuits) > 50:
        raise HTTPException(
            status_code=400,
            detail="Máximo 50 CUITs por consulta batch"
        )
    
    # Validar todos los CUITs
    cuits_invalidos = [cuit for cuit in cuits if not validar_cuit_format(cuit)]
    if cuits_invalidos:
        raise HTTPException(
            status_code=400,
            detail=f"CUITs con formato inválido: {cuits_invalidos}"
        )
    
    try:
        cliente = AFIPClientSgpatagon25()
        resultados = []
        errores = []
        
        for cuit in cuits:
            try:
                if tipo_consulta == "padron-a4":
                    datos = cliente.obtener_padron_a4(cuit)
                elif tipo_consulta == "padron-a5":
                    datos = cliente.obtener_padron_a5(cuit)
                elif tipo_consulta == "completa":
                    datos = cliente.extraer_datos_completos(cuit)
                else:
                    raise ValueError(f"Tipo de consulta inválido: {tipo_consulta}")
                
                resultados.append({
                    "cuit": cuit,
                    "estado": "exitoso",
                    "datos": datos
                })
                
            except Exception as e:
                errores.append({
                    "cuit": cuit,
                    "error": str(e)
                })
        
        return {
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "tipo_consulta": tipo_consulta,
            "total_procesados": len(cuits),
            "exitosos": len(resultados),
            "errores": len(errores),
            "resultados": resultados,
            "errores_detalle": errores if errores else None,
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en consulta batch: {str(e)}"
        )

# Funciones auxiliares

def validar_cuit_format(cuit: str) -> bool:
    """Valida el formato básico del CUIT"""
    if not cuit.isdigit():
        return False
    if len(cuit) != 11:
        return False
    return True

def generar_recomendaciones(resultados: Dict[str, Any]) -> List[str]:
    """Genera recomendaciones basadas en los resultados del diagnóstico"""
    recomendaciones = []
    
    if not resultados.get("archivos_ok"):
        recomendaciones.append("Verificar que existan todos los archivos de certificado")
    
    if not resultados.get("certificado_ok"):
        recomendaciones.append("Revisar el formato del certificado AFIP")
    
    if not resultados.get("clave_privada_ok"):
        recomendaciones.append("Verificar la clave privada RSA")
    
    if not resultados.get("wsaa_ok"):
        recomendaciones.append("Problemas de conectividad con WSAA - verificar red/firewall")
    
    if not resultados.get("extraccion_ok"):
        recomendaciones.append("Revisar configuración de servicios AFIP")
    
    if not recomendaciones:
        recomendaciones.append("Sistema AFIP funcionando correctamente")
    
    return recomendaciones