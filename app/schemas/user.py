"""
Esquemas Pydantic para autenticación y usuarios
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class UserBase(BaseModel):
    """Esquema base para usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)
    cuit_empresa: Optional[str] = Field(None, min_length=11, max_length=11)
    role: UserRole = UserRole.CONSULTA

class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=6, max_length=50)

class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    cuit_empresa: Optional[str] = Field(None, min_length=11, max_length=11)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Esquema de respuesta para usuario"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Esquema para token de acceso"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    role: UserRole

class TokenData(BaseModel):
    """Datos del token"""
    user_id: Optional[int] = None
    username: Optional[str] = None

class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    username: str
    password: str

class PasswordChange(BaseModel):
    """Esquema para cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=50)

# Alias para compatibilidad
User = UserResponse