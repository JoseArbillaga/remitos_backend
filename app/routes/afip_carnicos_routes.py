#!/usr/bin/env python3
"""
Endpoints específicos para automatización de remitos cárnicos con AFIP
Integración completa con SENASA y trazabilidad del sector cárnico
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os
from pydantic import BaseModel, Field

# Añadir el directorio api_afip al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api_afip'))

try:
    from api_afip.afip_carnico_client import AFIPCarnicoClient
    from api_afip.config_afip import CERTIFICADO_ID, AMBIENTE
except ImportError as e:
    print(f"⚠️ Error importando módulos AFIP cárnicos: {e}")
    AFIPCarnicoClient = None

from app.dependencies.auth import get_current_active_user
from app.schemas.user import User

# Modelos Pydantic para remitos cárnicos
class ProductoCarnico(BaseModel):
    descripcion: str = Field(..., description="Descripción del producto cárnico")
    cantidad: float = Field(..., gt=0, description="Cantidad del producto")
    peso_unitario: float = Field(..., gt=0, description="Peso unitario en kg")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario en pesos")
    tipo_producto: Optional[str] = Field("FRESCO", description="Tipo: FRESCO, ELABORADO, CONGELADO")

class RemitoCarnicoRequest(BaseModel):
    cuit_origen: str = Field(..., min_length=11, max_length=11, description="CUIT del establecimiento origen")
    cuit_destino: str = Field(..., min_length=11, max_length=11, description="CUIT del establecimiento destino")
    productos: List[ProductoCarnico] = Field(..., min_items=1, description="Lista de productos cárnicos")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    transporte: Optional[Dict[str, str]] = Field(None, description="Datos del transporte")

# Router para endpoints cárnicos
router = APIRouter(prefix="/afip/carnicos", tags=["AFIP Cárnicos"])

@router.get("/", summary="Estado sistema cárnico AFIP")
async def estado_sistema_carnico():
    """Obtiene el estado del sistema de integración AFIP para el sector cárnico"""
    return {
        "sistema": "AFIP Integración Cárnica",
        "certificado": CERTIFICADO_ID,
        "ambiente": AMBIENTE,
        "servicios_carnicos": [
            "SENASA WebServices",
            "Sistema Trazabilidad",
            "RENSPA",
            "Remitos Electrónicos Cárnicos"
        ],
        "timestamp": datetime.now().isoformat(),
        "estado": "operativo" if AFIPCarnicoClient else "configuracion_requerida"
    }

@router.get("/establecimientos/{cuit}", summary="Obtener establecimientos cárnicos")
async def obtener_establecimientos_carnicos(
    cuit: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todos los establecimientos cárnicos registrados para un CUIT
    Incluye datos de SENASA, RENSPA y habilitaciones
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    if not _validar_cuit(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        establecimientos = cliente.obtener_establecimientos_carnicos(cuit)
        
        return {
            "cuit_consultado": cuit,
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "establecimientos": establecimientos,
            "fuente": "SENASA-AFIP",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo establecimientos cárnicos: {str(e)}"
        )

@router.get("/productos", summary="Catálogo productos cárnicos")
async def obtener_catalogo_productos_carnicos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría: bovinos, porcinos, elaborados"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el catálogo completo de productos cárnicos autorizados
    Con códigos SENASA, AFIP y especificaciones técnicas
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        catalogo = cliente.obtener_productos_carnicos_autorizados()
        
        # Filtrar por categoría si se especifica
        if categoria and categoria in catalogo["categorias"]:
            catalogo_filtrado = {
                "categorias": {categoria: catalogo["categorias"][categoria]},
                "normativas": catalogo["normativas"],
                "fecha_actualizacion": catalogo["fecha_actualizacion"],
                "fuente": catalogo["fuente"]
            }
        else:
            catalogo_filtrado = catalogo
        
        return {
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "categoria_filtro": categoria,
            "catalogo": catalogo_filtrado,
            "fuente": "SENASA-AFIP",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo catálogo productos cárnicos: {str(e)}"
        )

@router.get("/trazabilidad/{cuit}", summary="Datos de trazabilidad")
async def obtener_trazabilidad_carnica(
    cuit: str,
    incluir_movimientos: bool = Query(True, description="Incluir movimientos recientes"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene datos completos de trazabilidad para una empresa cárnica
    Incluye SNIG, SIGP y movimientos de animales
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    if not _validar_cuit(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        trazabilidad = cliente.obtener_datos_trazabilidad(cuit)
        
        if not incluir_movimientos:
            trazabilidad.pop("movimientos_recientes", None)
        
        return {
            "cuit_consultado": cuit,
            "usuario_consulta": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "incluir_movimientos": incluir_movimientos,
            "trazabilidad": trazabilidad,
            "fuente": "Sistema Trazabilidad SENASA",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo trazabilidad: {str(e)}"
        )

@router.post("/remito-automatico", summary="Generar remito cárnico automático")
async def generar_remito_carnico_automatico(
    remito_request: RemitoCarnicoRequest,
    validar_establecimientos: bool = Query(True, description="Validar habilitaciones de establecimientos"),
    incluir_trazabilidad: bool = Query(True, description="Incluir datos de trazabilidad"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera automáticamente un remito cárnico completo
    Obtiene datos de AFIP/SENASA y aplica normativas del sector
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    # Validaciones
    if not _validar_cuit(remito_request.cuit_origen):
        raise HTTPException(status_code=400, detail="CUIT origen inválido")
    
    if not _validar_cuit(remito_request.cuit_destino):
        raise HTTPException(status_code=400, detail="CUIT destino inválido")
    
    if remito_request.cuit_origen == remito_request.cuit_destino:
        raise HTTPException(status_code=400, detail="CUIT origen y destino no pueden ser iguales")
    
    try:
        cliente = AFIPCarnicoClient()
        
        # Convertir productos Pydantic a dict
        productos_dict = [producto.dict() for producto in remito_request.productos]
        
        # Generar remito automático
        remito = cliente.generar_remito_automatico(
            remito_request.cuit_origen,
            remito_request.cuit_destino,
            productos_dict
        )
        
        # Añadir datos adicionales de la request
        if remito_request.observaciones:
            remito["observaciones"] = remito_request.observaciones
        
        if remito_request.transporte:
            remito["transporte"] = remito_request.transporte
        
        # Añadir datos de trazabilidad si se solicita
        if incluir_trazabilidad:
            trazabilidad_origen = cliente.obtener_datos_trazabilidad(remito_request.cuit_origen)
            remito["trazabilidad_detalle"] = trazabilidad_origen
        
        return {
            "usuario_generador": current_user.username,
            "timestamp_generacion": datetime.now().isoformat(),
            "parametros": {
                "validar_establecimientos": validar_establecimientos,
                "incluir_trazabilidad": incluir_trazabilidad
            },
            "remito_carnico": remito,
            "estado_generacion": "EXITOSO",
            "listo_para_envio": True,
            "certificado_usado": CERTIFICADO_ID,
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando remito automático: {str(e)}"
        )

@router.post("/batch-remitos", summary="Generación masiva de remitos")
async def generar_remitos_batch(
    remitos_requests: List[RemitoCarnicoRequest],
    procesamiento_asincrono: bool = Query(False, description="Procesar de forma asíncrona"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera múltiples remitos cárnicos automáticamente
    Útil para procesamiento masivo y operaciones batch
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    if len(remitos_requests) > 20:
        raise HTTPException(
            status_code=400,
            detail="Máximo 20 remitos por batch"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        resultados = []
        errores = []
        
        for i, remito_request in enumerate(remitos_requests):
            try:
                # Validaciones básicas
                if not _validar_cuit(remito_request.cuit_origen) or not _validar_cuit(remito_request.cuit_destino):
                    raise ValueError("CUITs inválidos")
                
                # Convertir productos
                productos_dict = [producto.dict() for producto in remito_request.productos]
                
                # Generar remito
                remito = cliente.generar_remito_automatico(
                    remito_request.cuit_origen,
                    remito_request.cuit_destino,
                    productos_dict
                )
                
                resultados.append({
                    "index_batch": i,
                    "numero_remito": remito["numero_remito"],
                    "cuit_origen": remito_request.cuit_origen,
                    "cuit_destino": remito_request.cuit_destino,
                    "productos_count": len(productos_dict),
                    "valor_total": remito["totales"]["valor_total"],
                    "estado": "GENERADO",
                    "remito_completo": remito
                })
                
            except Exception as e:
                errores.append({
                    "index_batch": i,
                    "cuit_origen": remito_request.cuit_origen,
                    "cuit_destino": remito_request.cuit_destino,
                    "error": str(e)
                })
        
        return {
            "usuario_batch": current_user.username,
            "timestamp_batch": datetime.now().isoformat(),
            "procesamiento_asincrono": procesamiento_asincrono,
            "total_solicitados": len(remitos_requests),
            "exitosos": len(resultados),
            "errores": len(errores),
            "resultados": resultados,
            "errores_detalle": errores if errores else None,
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en generación batch: {str(e)}"
        )

@router.get("/validaciones/establecimiento/{cuit}", summary="Validar establecimiento cárnico")
async def validar_establecimiento_carnico(
    cuit: str,
    numero_senasa: Optional[str] = Query(None, description="Número específico de establecimiento SENASA"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Valida si un establecimiento cárnico está habilitado
    Verifica estado en SENASA, RENSPA y permisos
    """
    if not AFIPCarnicoClient:
        raise HTTPException(
            status_code=503,
            detail="Cliente AFIP cárnico no disponible"
        )
    
    if not _validar_cuit(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        establecimientos = cliente.obtener_establecimientos_carnicos(cuit)
        
        # Validación específica por número SENASA
        if numero_senasa:
            establecimiento_especifico = next(
                (est for est in establecimientos["establecimientos"] if est["numero_senasa"] == numero_senasa),
                None
            )
            
            if not establecimiento_especifico:
                return {
                    "cuit": cuit,
                    "numero_senasa": numero_senasa,
                    "valido": False,
                    "motivo": "Establecimiento no encontrado",
                    "timestamp": datetime.now().isoformat()
                }
            
            validacion = {
                "cuit": cuit,
                "numero_senasa": numero_senasa,
                "valido": establecimiento_especifico["estado"] == "HABILITADO",
                "establecimiento": establecimiento_especifico,
                "validaciones": {
                    "habilitado": establecimiento_especifico["estado"] == "HABILITADO",
                    "categoria_valida": establecimiento_especifico["categoria"] in ["A", "B"],
                    "actividades_autorizadas": len(establecimiento_especifico["actividades_autorizadas"]) > 0,
                    "veterinario_asignado": "veterinario_responsable" in establecimiento_especifico
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Validación general de todos los establecimientos
            establecimientos_habilitados = [
                est for est in establecimientos["establecimientos"] 
                if est["estado"] == "HABILITADO"
            ]
            
            validacion = {
                "cuit": cuit,
                "total_establecimientos": len(establecimientos["establecimientos"]),
                "establecimientos_habilitados": len(establecimientos_habilitados),
                "valido": len(establecimientos_habilitados) > 0,
                "establecimientos": establecimientos_habilitados,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "usuario_validacion": current_user.username,
            "validacion": validacion,
            "fuente": "SENASA-AFIP",
            "ambiente": AMBIENTE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validando establecimiento: {str(e)}"
        )

@router.get("/consultar-remitos/{cuit}", summary="Consultar remitos emitidos por CUIT")
async def consultar_remitos_emitidos(
    cuit: str,
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)")
):
    """
    Consulta remitos emitidos por un CUIT específico en el sector cárnico
    
    Este endpoint permite consultar todos los remitos emitidos por una empresa
    del sector cárnico, con filtros opcionales de fecha.
    
    Args:
        cuit: CUIT del emisor (11 dígitos)
        fecha_desde: Fecha desde para filtrar (opcional)
        fecha_hasta: Fecha hasta para filtrar (opcional)
    
    Returns:
        Información completa de remitos emitidos con detalles de productos
    """
    if not _validar_cuit(cuit):
        raise HTTPException(
            status_code=400,
            detail="Formato de CUIT inválido"
        )
    
    try:
        cliente = AFIPCarnicoClient()
        remitos = cliente.consultar_remitos_emitidos(cuit, fecha_desde, fecha_hasta)
        
        return {
            "cuit_consultado": cuit,
            "filtros": {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            },
            "timestamp": datetime.now().isoformat(),
            "datos": remitos,
            "fuente": "AFIP-Carnicos",
            "ambiente": AMBIENTE,
            "certificado": CERTIFICADO_ID
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando remitos: {str(e)}"
        )

# Funciones auxiliares
def _validar_cuit(cuit: str) -> bool:
    """Valida el formato básico del CUIT"""
    if not cuit.isdigit() or len(cuit) != 11:
        return False
    return True