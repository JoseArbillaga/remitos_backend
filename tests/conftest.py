"""
Configuración base para tests
"""
import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_database_session, Base
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_remitos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Motor de base de datos para tests"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Sesión de base de datos para cada test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente de prueba de FastAPI"""
    def override_get_database_session():
        yield db_session
    
    app.dependency_overrides[get_database_session] = override_get_database_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
    """Servicio de autenticación para tests"""
    return AuthService(db_session)

@pytest.fixture
def test_user(auth_service: AuthService) -> User:
    """Usuario de prueba"""
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        cuit_empresa="20123456789",
        role=UserRole.OPERADOR
    )
    
    return auth_service.create_user(user_data)

@pytest.fixture
def admin_user(auth_service: AuthService) -> User:
    """Usuario administrador de prueba"""
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        username="admin",
        email="admin@example.com",
        password="adminpassword123",
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    
    return auth_service.create_user(user_data)

@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """Token de autenticación para tests"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Token de administrador para tests"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": admin_user.username,
            "password": "adminpassword123"
        }
    )
    
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Headers con autenticación para requests"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Headers con autenticación de admin para requests"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def sample_remito_data() -> dict:
    """Datos de remito de ejemplo para tests"""
    from datetime import datetime
    
    return {
        "numero_remito": "R-00001234",
        "fecha_emision": datetime.now().isoformat(),
        "emisor_cuit": "20123456789",
        "emisor_razon_social": "Frigorífico Test SA",
        "emisor_domicilio": "Av. Test 1234, CABA",
        "receptor_cuit": "20987654321",
        "receptor_razon_social": "Carnicería Test SRL",
        "receptor_domicilio": "San Martín 567, Buenos Aires",
        "transporte_cuit": "20111222333",
        "transporte_razon_social": "Transportes Test SA",
        "patente_vehiculo": "ABC123",
        "peso_total": 500.5,
        "cantidad_total": 50,
        "observaciones": "Remito de prueba para testing"
    }