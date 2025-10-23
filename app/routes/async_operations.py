"""
Rutas para operaciones asíncronas con Celery
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_database_session
from app.dependencies.auth import get_current_active_user, require_permission
from app.models.user import User
from app.tasks.afip_tasks import (
    enviar_remito_afip_async,
    enviar_lote_remitos_afip,
    consultar_estado_lote_afip
)
from app.core.celery_config import celery_app

router = APIRouter()

class RemitosLoteRequest(BaseModel):
    """Esquema para solicitud de lote de remitos"""
    remitos_ids: List[int]

class TaskStatusResponse(BaseModel):
    """Respuesta del estado de una tarea"""
    task_id: str
    status: str
    result: dict = None
    meta: dict = None

@router.post("/async/remitos/{remito_id}/enviar-afip")
async def enviar_remito_afip_async_endpoint(
    remito_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("send_afip"))
):
    """Enviar remito a AFIP de forma asíncrona"""
    
    # Verificar que el remito existe y el usuario tiene acceso
    from app.services.remito_service import RemitoService
    service = RemitoService(db)
    
    remito = service.obtener_remito_por_id(remito_id)
    if not remito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remito no encontrado"
        )
    
    if not current_user.can_access_remito(remito.emisor_cuit):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para operar este remito"
        )
    
    # Crear tarea asíncrona
    task = enviar_remito_afip_async.delay(remito_id, current_user.id)
    
    return {
        "message": "Remito enviado a cola de procesamiento",
        "task_id": task.id,
        "remito_id": remito_id,
        "status": "PENDING"
    }

@router.post("/async/remitos/lote/enviar-afip")
async def enviar_lote_remitos_afip_endpoint(
    lote_data: RemitosLoteRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("send_afip"))
):
    """Enviar lote de remitos a AFIP de forma asíncrona"""
    
    if not lote_data.remitos_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un remito"
        )
    
    if len(lote_data.remitos_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100 remitos por lote"
        )
    
    # Verificar que todos los remitos existen y el usuario tiene acceso
    from app.services.remito_service import RemitoService
    service = RemitoService(db)
    
    for remito_id in lote_data.remitos_ids:
        remito = service.obtener_remito_por_id(remito_id)
        if not remito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Remito {remito_id} no encontrado"
            )
        
        if not current_user.can_access_remito(remito.emisor_cuit):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para operar el remito {remito_id}"
            )
    
    # Crear tarea asíncrona para el lote
    task = enviar_lote_remitos_afip.delay(lote_data.remitos_ids, current_user.id)
    
    return {
        "message": f"Lote de {len(lote_data.remitos_ids)} remitos enviado a cola de procesamiento",
        "task_id": task.id,
        "total_remitos": len(lote_data.remitos_ids),
        "status": "PENDING"
    }

@router.post("/async/remitos/lote/consultar-estado")
async def consultar_estado_lote_endpoint(
    lote_data: RemitosLoteRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("read_afip"))
):
    """Consultar estado de lote de remitos en AFIP de forma asíncrona"""
    
    if not lote_data.remitos_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un remito"
        )
    
    # Verificar acceso a los remitos
    from app.services.remito_service import RemitoService
    service = RemitoService(db)
    
    for remito_id in lote_data.remitos_ids:
        remito = service.obtener_remito_por_id(remito_id)
        if not remito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Remito {remito_id} no encontrado"
            )
        
        if not current_user.can_access_remito(remito.emisor_cuit):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para consultar el remito {remito_id}"
            )
    
    # Crear tarea asíncrona
    task = consultar_estado_lote_afip.delay(lote_data.remitos_ids)
    
    return {
        "message": f"Consulta de estado para {len(lote_data.remitos_ids)} remitos iniciada",
        "task_id": task.id,
        "total_remitos": len(lote_data.remitos_ids),
        "status": "PENDING"
    }

@router.get("/async/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estado de una tarea asíncrona"""
    
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                "task_id": task_id,
                "status": "PENDING",
                "result": None,
                "meta": {"message": "Tarea en cola, esperando procesamiento..."}
            }
        elif task.state == 'PROGRESS':
            response = {
                "task_id": task_id,
                "status": "PROGRESS",
                "result": None,
                "meta": task.info
            }
        elif task.state == 'SUCCESS':
            response = {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": task.result,
                "meta": None
            }
        elif task.state == 'FAILURE':
            response = {
                "task_id": task_id,
                "status": "FAILURE",
                "result": None,
                "meta": {
                    "error": str(task.info),
                    "traceback": task.traceback if hasattr(task, 'traceback') else None
                }
            }
        else:
            response = {
                "task_id": task_id,
                "status": task.state,
                "result": task.result,
                "meta": task.info
            }
        
        return TaskStatusResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea no encontrada: {str(e)}"
        )

@router.delete("/async/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancelar una tarea asíncrona"""
    
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state in ['PENDING', 'PROGRESS']:
            task.revoke(terminate=True)
            return {"message": f"Tarea {task_id} cancelada exitosamente"}
        else:
            return {"message": f"Tarea {task_id} no se puede cancelar (estado: {task.state})"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error cancelando tarea: {str(e)}"
        )