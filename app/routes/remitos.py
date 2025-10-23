"""
Rutas para gestión de remitos con autenticación y autorización
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database_session
from app.schemas.remito import RemitoCreate, RemitoUpdate, RemitoResponse
from app.services.remito_service import RemitoService
from app.dependencies.auth import (
    get_current_active_user, require_permission,
    require_operador_or_admin
)
from app.models.user import User

router = APIRouter()

@router.post("/remitos/", response_model=RemitoResponse, status_code=status.HTTP_201_CREATED)
async def crear_remito(
    remito: RemitoCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("create_remito"))
):
    """Crear un nuevo remito"""
    # Verificar que el usuario puede crear remitos para este CUIT
    if not current_user.can_access_remito(remito.emisor_cuit):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear remitos para este CUIT"
        )
    
    service = RemitoService(db)
    return service.crear_remito(remito)

@router.get("/remitos/", response_model=List[RemitoResponse])
async def listar_remitos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("read_remito"))
):
    """Listar remitos (filtrados por permisos del usuario)"""
    service = RemitoService(db)
    
    if current_user.has_permission("read_all_remitos"):
        # Admin puede ver todos los remitos
        return service.obtener_remitos(skip=skip, limit=limit)
    else:
        # Usuarios normales solo ven remitos de su empresa
        return service.obtener_remitos_por_cuit(
            cuit=current_user.cuit_empresa, 
            skip=skip, 
            limit=limit
        )

@router.get("/remitos/{remito_id}", response_model=RemitoResponse)
async def obtener_remito(
    remito_id: int,
    db: Session = Depends(get_database_session)
):
    """Obtener un remito por ID"""
    service = RemitoService(db)
    remito = service.obtener_remito_por_id(remito_id)
    if not remito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remito no encontrado"
        )
    return remito

@router.put("/remitos/{remito_id}", response_model=RemitoResponse)
async def actualizar_remito(
    remito_id: int,
    remito_update: RemitoUpdate,
    db: Session = Depends(get_database_session)
):
    """Actualizar un remito"""
    service = RemitoService(db)
    remito = service.actualizar_remito(remito_id, remito_update)
    if not remito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remito no encontrado"
        )
    return remito

@router.delete("/remitos/{remito_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_remito(
    remito_id: int,
    db: Session = Depends(get_database_session)
):
    """Eliminar un remito"""
    service = RemitoService(db)
    success = service.eliminar_remito(remito_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remito no encontrado"
        )
    return None

@router.post("/remitos/{remito_id}/enviar-afip")
async def enviar_remito_afip(
    remito_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_permission("send_afip"))
):
    """Enviar remito a AFIP para autorización"""
    service = RemitoService(db)
    
    # Verificar que el remito existe y el usuario tiene acceso
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
    
    resultado = service.enviar_remito_afip(remito_id)
    
    if not resultado.get("success"):
        # Determinar código de error HTTP apropiado
        codigo_error = resultado.get("codigo", "UNKNOWN_ERROR")
        if codigo_error == "REMITO_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif codigo_error == "INVALID_STATE":
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        raise HTTPException(
            status_code=status_code,
            detail=resultado.get("error", "Error desconocido")
        )
    
    return {
        "message": resultado.get("mensaje"),
        "cae": resultado.get("cae"),
        "fecha_vencimiento": resultado.get("fecha_vencimiento"),
        "remito_id": remito_id
    }

@router.get("/remitos/{remito_id}/estado-afip")
async def consultar_estado_afip(
    remito_id: int,
    db: Session = Depends(get_database_session)
):
    """Consultar estado del remito en AFIP"""
    service = RemitoService(db)
    resultado = service.consultar_estado_afip(remito_id)
    
    if not resultado.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.get("error", "Error consultando estado en AFIP")
        )
    
    return resultado

@router.get("/afip/status")
async def obtener_status_afip(
    db: Session = Depends(get_database_session)
):
    """Obtener status del servicio AFIP"""
    service = RemitoService(db)
    return service.obtener_status_afip()