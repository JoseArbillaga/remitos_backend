"""
Punto de entrada principal para la aplicación remitos_backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import remitos
from database import create_tables

app = FastAPI(
    title="Remitos Backend",
    description="API para gestión de remitos de carne",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(remitos.router, prefix="/api/v1", tags=["remitos"])

# Importar y incluir rutas de autenticación
try:
    from app.routes import auth
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
except ImportError:
    print("⚠️ Rutas de autenticación no disponibles")

# Importar y incluir rutas asíncronas
try:
    from app.routes import async_operations
    app.include_router(async_operations.router, prefix="/api/v1", tags=["async"])
except ImportError:
    print("⚠️ Rutas asíncronas no disponibles")

# Importar y incluir rutas de AFIP
try:
    from app.routes import afip_routes
    app.include_router(afip_routes.router, prefix="/api/v1", tags=["afip"])
    print("✅ Rutas AFIP cargadas correctamente")
except ImportError as e:
    print(f"⚠️ Rutas AFIP no disponibles: {e}")

# Importar y incluir rutas de AFIP Cárnicos
try:
    from app.routes import afip_carnicos_routes
    app.include_router(afip_carnicos_routes.router, prefix="/api/v1", tags=["afip-carnicos"])
    print("✅ Rutas AFIP Cárnicos cargadas correctamente")
except ImportError as e:
    print(f"⚠️ Rutas AFIP Cárnicos no disponibles: {e}")

@app.get("/")
async def root():
    """Endpoint básico de bienvenida"""
    return {
        "message": "Bienvenido a Remitos Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy", "service": "remitos_backend"}

# Importar modelos para asegurar que se crean las tablas
try:
    from app.models import remito, user
except ImportError:
    print("⚠️ Algunos modelos no están disponibles")

# Crear tablas al iniciar
create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)