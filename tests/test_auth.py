"""
Tests para autenticación y autorización
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

class TestAuthService:
    """Tests para el servicio de autenticación"""
    
    def test_create_user_success(self, auth_service: AuthService):
        """Test crear usuario exitoso"""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name="New User",
            role=UserRole.OPERADOR
        )
        
        user = auth_service.create_user(user_data)
        
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.role == UserRole.OPERADOR
        assert user.is_active == True
        assert user.hashed_password != "password123"  # Debe estar hasheada
    
    def test_create_user_duplicate_username(self, auth_service: AuthService, test_user: User):
        """Test crear usuario con username duplicado"""
        user_data = UserCreate(
            username=test_user.username,  # Username ya existe
            email="different@example.com",
            password="password123",
            role=UserRole.CONSULTA
        )
        
        with pytest.raises(Exception):  # Debe lanzar HTTPException
            auth_service.create_user(user_data)
    
    def test_authenticate_user_success(self, auth_service: AuthService, test_user: User):
        """Test autenticación exitosa"""
        user = auth_service.authenticate_user(test_user.username, "testpassword123")
        
        assert user is not None
        assert user.id == test_user.id
    
    def test_authenticate_user_wrong_password(self, auth_service: AuthService, test_user: User):
        """Test autenticación con contraseña incorrecta"""
        user = auth_service.authenticate_user(test_user.username, "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_not_exists(self, auth_service: AuthService):
        """Test autenticación con usuario inexistente"""
        user = auth_service.authenticate_user("nonexistent", "password")
        
        assert user is None
    
    def test_create_access_token(self, auth_service: AuthService):
        """Test creación de token de acceso"""
        token = auth_service.create_access_token({"sub": "123", "username": "testuser"})
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self, auth_service: AuthService):
        """Test verificación de token válido"""
        token = auth_service.create_access_token({"sub": "123", "username": "testuser"})
        token_data = auth_service.verify_token(token)
        
        assert token_data.user_id == 123
        assert token_data.username == "testuser"

class TestUserModel:
    """Tests para el modelo de Usuario"""
    
    def test_user_has_permission_admin(self, admin_user: User):
        """Test permisos de administrador"""
        assert admin_user.has_permission("create_remito") == True
        assert admin_user.has_permission("manage_users") == True
        assert admin_user.has_permission("read_all_remitos") == True
    
    def test_user_has_permission_operador(self, test_user: User):
        """Test permisos de operador"""
        assert test_user.has_permission("create_remito") == True
        assert test_user.has_permission("send_afip") == True
        assert test_user.has_permission("manage_users") == False
    
    def test_user_can_access_remito_same_cuit(self, test_user: User):
        """Test acceso a remito del mismo CUIT"""
        assert test_user.can_access_remito(test_user.cuit_empresa) == True
    
    def test_user_cannot_access_remito_different_cuit(self, test_user: User):
        """Test no acceso a remito de diferente CUIT"""
        assert test_user.can_access_remito("20999999999") == False
    
    def test_admin_can_access_any_remito(self, admin_user: User):
        """Test admin puede acceder a cualquier remito"""
        assert admin_user.can_access_remito("20123456789") == True
        assert admin_user.can_access_remito("20999999999") == True

class TestAuthEndpoints:
    """Tests para endpoints de autenticación"""
    
    def test_register_success(self, client: TestClient):
        """Test registro exitoso"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "cuit_empresa": "20111222333",
            "role": "operador"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test login exitoso"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == test_user.id
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login con credenciales inválidas"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "invalid",
                "password": "invalid"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_success(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test obtener usuario actual exitoso"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["id"] == test_user.id
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test obtener usuario sin autenticación"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No Bearer token
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test obtener usuario con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_change_password_success(self, client: TestClient, auth_headers: dict):
        """Test cambio de contraseña exitoso"""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        response = client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """Test cambio de contraseña con contraseña actual incorrecta"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400

class TestAdminEndpoints:
    """Tests para endpoints administrativos"""
    
    def test_list_users_admin_success(self, client: TestClient, admin_headers: dict):
        """Test listar usuarios como admin"""
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_users_non_admin_forbidden(self, client: TestClient, auth_headers: dict):
        """Test listar usuarios como no-admin debe fallar"""
        response = client.get("/api/v1/admin/users", headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_update_user_admin_success(self, client: TestClient, admin_headers: dict, test_user: User):
        """Test actualizar usuario como admin"""
        update_data = {
            "full_name": "Updated Name",
            "role": "admin"
        }
        
        response = client.put(
            f"/api/v1/admin/users/{test_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"