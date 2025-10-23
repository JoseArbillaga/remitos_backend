"""
Modelo de Usuario para autenticación y autorización
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(enum.Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    OPERADOR = "operador"
    CONSULTA = "consulta"

class User(Base):
    """Modelo para la tabla de usuarios"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    
    # Roles y permisos
    role = Column(Enum(UserRole), default=UserRole.CONSULTA, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # CUIT empresarial (para validar acceso a remitos)
    cuit_empresa = Column(String(11))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
    
    def has_permission(self, permission: str) -> bool:
        """Verificar si el usuario tiene un permiso específico"""
        role_permissions = {
            UserRole.ADMIN: [
                "create_remito", "read_remito", "update_remito", "delete_remito",
                "send_afip", "read_afip", "manage_users", "read_all_remitos"
            ],
            UserRole.OPERADOR: [
                "create_remito", "read_remito", "update_remito",
                "send_afip", "read_afip"
            ],
            UserRole.CONSULTA: [
                "read_remito", "read_afip"
            ]
        }
        return permission in role_permissions.get(self.role, [])
    
    def can_access_remito(self, remito_cuit: str) -> bool:
        """Verificar si puede acceder a remitos de un CUIT específico"""
        if self.role == UserRole.ADMIN:
            return True
        return self.cuit_empresa == remito_cuit