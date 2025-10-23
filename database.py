"""
Configuración y conexión a la base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Crear el motor de la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def get_database_session():
    """
    Generador de sesiones de base de datos para inyección de dependencias
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Crear todas las tablas en la base de datos
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Eliminar todas las tablas de la base de datos (usar con cuidado)
    """
    Base.metadata.drop_all(bind=engine)

def init_db():
    """
    Inicializar la base de datos creando todas las tablas
    """
    # Importar modelos para que sean registrados
    from app.models import user, remito
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)