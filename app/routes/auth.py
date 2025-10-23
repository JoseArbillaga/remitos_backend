"""
Rutas para autenticación y gestión de usuarios
"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_database_session
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, LoginRequest, 
    Token, PasswordChange
)
from app.dependencies.auth import (
    get_current_active_user, require_admin, 
    get_auth_service
)
from app.models.user import User
from config import settings

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Registrar nuevo usuario"""
    return auth_service.create_user(user_data)

@router.post("/auth/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Iniciar sesión"""
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar último login
    auth_service.update_last_login(user.id)
    
    # Crear token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        role=user.role
    )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Obtener información del usuario actual"""
    return current_user

@router.put("/auth/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Actualizar información del usuario actual"""
    # Los usuarios no pueden cambiar su propio rol
    if hasattr(user_data, 'role') and user_data.role is not None:
        user_data.role = None
    
    updated_user = auth_service.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return updated_user

@router.post("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Cambiar contraseña del usuario actual"""
    success = auth_service.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cambiar contraseña"
        )
    
    return {"message": "Contraseña cambiada exitosamente"}

# Rutas administrativas
@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(require_admin())
):
    """Listar todos los usuarios (solo admin)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_admin())
):
    """Obtener usuario por ID (solo admin)"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: int,
    user_data: UserUpdate,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_admin())
):
    """Actualizar usuario por admin"""
    updated_user = auth_service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return updated_user

@router.delete("/admin/users/{user_id}")
async def deactivate_user(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_admin())
):
    """Desactivar usuario (solo admin)"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir desactivar a sí mismo
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivarte a ti mismo"
        )
    
    user.is_active = False
    auth_service.db.commit()
    
    return {"message": f"Usuario {user.username} desactivado exitosamente"}