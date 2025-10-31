# Configuración para Azure App Service
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Variables de entorno para Azure
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./remitos.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
AZURE_ENVIRONMENT = os.getenv("AZURE_ENVIRONMENT", "production")

# CORS para Azure
ALLOWED_ORIGINS = [
    "https://*.azurewebsites.net",
    "https://your-domain.com",
    "http://localhost:3000",  # Para desarrollo
]

def create_azure_app():
    """Crear aplicación FastAPI configurada para Azure"""
    
    app = FastAPI(
        title="Remitos Backend - Azure",
        description="API para gestión de remitos de carne en Azure",
        version="1.0.0",
        docs_url="/docs" if AZURE_ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if AZURE_ENVIRONMENT != "production" else None
    )
    
    # CORS configurado para Azure
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    return app