"""
Configuración general de la aplicación
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./remitos.db"
    DATABASE_HOST: Optional[str] = None
    DATABASE_PORT: Optional[int] = None
    DATABASE_USER: Optional[str] = None
    DATABASE_PASSWORD: Optional[str] = None
    DATABASE_NAME: Optional[str] = None
    
    # Configuración de la aplicación
    APP_NAME: str = "Remitos Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuración de seguridad JWT
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here"
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración AFIP
    AFIP_CUIT: str = "20123456786"
    AFIP_CERT_PATH: str = "./certificates/certificado.crt"
    AFIP_KEY_PATH: str = "./certificates/clave_privada.key"
    AFIP_PASSPHRASE: Optional[str] = None
    
    # Configuración Celery/Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Crear directorio de uploads si no existe
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)