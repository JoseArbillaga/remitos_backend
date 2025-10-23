"""
Tareas asíncronas para AFIP
"""
from celery import current_task
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.celery_config import celery_app
from app.services.remito_service import RemitoService
from app.services.afip_service import AFIPRemitoService
from database import SessionLocal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="enviar_remito_afip_async")
def enviar_remito_afip_async(self, remito_id: int, user_id: int) -> Dict[str, Any]:
    """
    Enviar remito individual a AFIP de forma asíncrona
    """
    db = SessionLocal()
    try:
        # Actualizar estado de la tarea
        current_task.update_state(
            state="PROGRESS",
            meta={
                "remito_id": remito_id,
                "status": "Iniciando envío a AFIP...",
                "progress": 0
            }
        )
        
        service = RemitoService(db)
        
        # Verificar que el remito existe
        remito = service.obtener_remito_por_id(remito_id)
        if not remito:
            return {
                "success": False,
                "error": "Remito no encontrado",
                "remito_id": remito_id
            }
        
        # Actualizar progreso
        current_task.update_state(
            state="PROGRESS",
            meta={
                "remito_id": remito_id,
                "status": "Enviando a AFIP...",
                "progress": 50
            }
        )
        
        # Enviar a AFIP
        resultado = service.enviar_remito_afip(remito_id)
        
        # Actualizar progreso final
        current_task.update_state(
            state="PROGRESS",
            meta={
                "remito_id": remito_id,
                "status": "Completado",
                "progress": 100
            }
        )
        
        logger.info(f"Remito {remito_id} procesado: {'éxito' if resultado.get('success') else 'error'}")
        
        return {
            "remito_id": remito_id,
            "user_id": user_id,
            "resultado": resultado
        }
        
    except Exception as e:
        logger.error(f"Error procesando remito {remito_id}: {str(e)}")
        
        current_task.update_state(
            state="FAILURE",
            meta={
                "remito_id": remito_id,
                "error": str(e)
            }
        )
        
        return {
            "success": False,
            "error": str(e),
            "remito_id": remito_id
        }
        
    finally:
        db.close()

@celery_app.task(bind=True, name="enviar_lote_remitos_afip")
def enviar_lote_remitos_afip(self, remitos_ids: List[int], user_id: int) -> Dict[str, Any]:
    """
    Enviar lote de remitos a AFIP de forma asíncrona
    """
    db = SessionLocal()
    try:
        total_remitos = len(remitos_ids)
        resultados = []
        errores = []
        
        # Actualizar estado inicial
        current_task.update_state(
            state="PROGRESS",
            meta={
                "total": total_remitos,
                "processed": 0,
                "success": 0,
                "errors": 0,
                "status": "Iniciando procesamiento de lote..."
            }
        )
        
        service = RemitoService(db)
        
        for i, remito_id in enumerate(remitos_ids):
            try:
                # Actualizar progreso
                progress = int((i / total_remitos) * 100)
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "total": total_remitos,
                        "processed": i,
                        "success": len(resultados),
                        "errors": len(errores),
                        "status": f"Procesando remito {remito_id}...",
                        "progress": progress
                    }
                )
                
                # Procesar remito
                resultado = service.enviar_remito_afip(remito_id)
                
                if resultado.get("success"):
                    resultados.append({
                        "remito_id": remito_id,
                        "cae": resultado.get("cae"),
                        "status": "success"
                    })
                else:
                    errores.append({
                        "remito_id": remito_id,
                        "error": resultado.get("error", "Error desconocido"),
                        "status": "error"
                    })
                
                # Pausa entre remitos para no saturar AFIP
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error procesando remito {remito_id} en lote: {str(e)}")
                errores.append({
                    "remito_id": remito_id,
                    "error": str(e),
                    "status": "error"
                })
        
        # Estado final
        current_task.update_state(
            state="SUCCESS",
            meta={
                "total": total_remitos,
                "processed": total_remitos,
                "success": len(resultados),
                "errors": len(errores),
                "status": "Lote completado",
                "progress": 100
            }
        )
        
        logger.info(f"Lote procesado: {len(resultados)} éxitos, {len(errores)} errores")
        
        return {
            "success": True,
            "total": total_remitos,
            "success_count": len(resultados),
            "error_count": len(errores),
            "resultados": resultados,
            "errores": errores,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error procesando lote: {str(e)}")
        
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "total": len(remitos_ids),
                "processed": len(resultados) if 'resultados' in locals() else 0
            }
        )
        
        return {
            "success": False,
            "error": str(e),
            "total": len(remitos_ids)
        }
        
    finally:
        db.close()

@celery_app.task(bind=True, name="consultar_estado_lote_afip")
def consultar_estado_lote_afip(self, remitos_ids: List[int]) -> Dict[str, Any]:
    """
    Consultar estado de múltiples remitos en AFIP
    """
    db = SessionLocal()
    try:
        service = RemitoService(db)
        resultados = []
        
        total = len(remitos_ids)
        
        for i, remito_id in enumerate(remitos_ids):
            try:
                # Actualizar progreso
                progress = int((i / total) * 100)
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "total": total,
                        "processed": i,
                        "progress": progress,
                        "status": f"Consultando remito {remito_id}..."
                    }
                )
                
                resultado = service.consultar_estado_afip(remito_id)
                resultados.append({
                    "remito_id": remito_id,
                    "estado": resultado
                })
                
            except Exception as e:
                resultados.append({
                    "remito_id": remito_id,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total": total,
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"Error consultando estados: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close()