"""
Dependencias para autenticación y autorización
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_database_session
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

# Configuración del esquema de seguridad
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_database_session)) -> AuthService:
    """Inyección de dependencia para AuthService"""
    return AuthService(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Obtener usuario actual del token"""
    token = credentials.credentials
    token_data = auth_service.verify_token(token)
    
    user = auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtener usuario activo actual"""
    return current_user

def require_permission(permission: str):
    """Decorador para requerir permisos específicos"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Requiere: {permission}"
            )
        return current_user
    return permission_checker

def require_role(required_role: UserRole):
    """Decorador para requerir rol específico"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol insuficiente. Requiere: {required_role.value}"
            )
        return current_user
    return role_checker

def require_admin():
    """Requerir rol de administrador"""
    return require_role(UserRole.ADMIN)

def require_operador_or_admin():
    """Requerir rol de operador o administrador"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in [UserRole.OPERADOR, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requiere rol de operador o administrador"
            )
        return current_user
    return role_checker

def can_access_remito(remito_cuit: str):
    """Verificar acceso a remito específico por CUIT"""
    def access_checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.can_access_remito(remito_cuit):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este remito"
            )
        return current_user
    return access_checker