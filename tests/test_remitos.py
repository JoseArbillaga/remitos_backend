"""
Tests para endpoints de remitos
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

class TestRemitosEndpoints:
    """Tests para endpoints de remitos"""
    
    def test_create_remito_success(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test crear remito exitoso"""
        response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["numero_remito"] == sample_remito_data["numero_remito"]
        assert data["estado"] == "borrador"
    
    def test_create_remito_unauthorized(self, client: TestClient, sample_remito_data: dict):
        """Test crear remito sin autenticación"""
        response = client.post("/api/v1/remitos/", json=sample_remito_data)
        
        assert response.status_code == 403
    
    def test_create_remito_invalid_cuit(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test crear remito con CUIT inválido"""
        sample_remito_data["emisor_cuit"] = "20999999999"  # CUIT diferente al usuario
        
        response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_create_remito_validation_error(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test crear remito con error de validación"""
        sample_remito_data["emisor_cuit"] = "INVALID_CUIT"
        
        response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_list_remitos_success(self, client: TestClient, auth_headers: dict):
        """Test listar remitos exitoso"""
        response = client.get("/api/v1/remitos/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_remitos_unauthorized(self, client: TestClient):
        """Test listar remitos sin autenticación"""
        response = client.get("/api/v1/remitos/")
        
        assert response.status_code == 403
    
    def test_get_remito_success(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test obtener remito por ID exitoso"""
        # Primero crear un remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        remito_id = create_response.json()["id"]
        
        # Luego obtenerlo
        response = client.get(f"/api/v1/remitos/{remito_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == remito_id
    
    def test_get_remito_not_found(self, client: TestClient, auth_headers: dict):
        """Test obtener remito inexistente"""
        response = client.get("/api/v1/remitos/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_remito_success(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test actualizar remito exitoso"""
        # Crear remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Actualizar
        update_data = {"observaciones": "Observaciones actualizadas"}
        response = client.put(
            f"/api/v1/remitos/{remito_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["observaciones"] == "Observaciones actualizadas"
    
    def test_delete_remito_success(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test eliminar remito exitoso"""
        # Crear remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Eliminar
        response = client.delete(f"/api/v1/remitos/{remito_id}", headers=auth_headers)
        
        assert response.status_code == 204

class TestAFIPEndpoints:
    """Tests para endpoints de AFIP"""
    
    def test_afip_status(self, client: TestClient, auth_headers: dict):
        """Test obtener status de AFIP"""
        response = client.get("/api/v1/afip/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "certificados_disponibles" in data
        assert "ambiente" in data
    
    def test_send_remito_afip_success(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test enviar remito a AFIP exitoso"""
        # Crear remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Enviar a AFIP
        response = client.post(
            f"/api/v1/remitos/{remito_id}/enviar-afip",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "cae" in data
        assert "message" in data
    
    def test_send_remito_afip_not_found(self, client: TestClient, auth_headers: dict):
        """Test enviar remito inexistente a AFIP"""
        response = client.post(
            "/api/v1/remitos/99999/enviar-afip",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_send_remito_afip_wrong_state(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test enviar remito en estado incorrecto a AFIP"""
        # Crear y enviar remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Enviar primera vez (debería funcionar)
        first_send = client.post(
            f"/api/v1/remitos/{remito_id}/enviar-afip",
            headers=auth_headers
        )
        assert first_send.status_code == 200
        
        # Enviar segunda vez (debería fallar por estado)
        second_send = client.post(
            f"/api/v1/remitos/{remito_id}/enviar-afip",
            headers=auth_headers
        )
        assert second_send.status_code == 400
    
    def test_check_remito_afip_status(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test consultar estado de remito en AFIP"""
        # Crear y enviar remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Enviar a AFIP
        client.post(
            f"/api/v1/remitos/{remito_id}/enviar-afip",
            headers=auth_headers
        )
        
        # Consultar estado
        response = client.get(
            f"/api/v1/remitos/{remito_id}/estado-afip",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

class TestAsyncEndpoints:
    """Tests para endpoints asíncronos"""
    
    def test_async_send_remito_afip(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test envío asíncrono de remito a AFIP"""
        # Crear remito
        create_response = client.post(
            "/api/v1/remitos/",
            json=sample_remito_data,
            headers=auth_headers
        )
        remito_id = create_response.json()["id"]
        
        # Enviar de forma asíncrona
        response = client.post(
            f"/api/v1/async/remitos/{remito_id}/enviar-afip",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "message" in data
    
    def test_async_batch_send_remitos(self, client: TestClient, auth_headers: dict, sample_remito_data: dict):
        """Test envío asíncrono de lote de remitos"""
        # Crear varios remitos
        remitos_ids = []
        for i in range(3):
            sample_remito_data["numero_remito"] = f"R-0000000{i}"
            create_response = client.post(
                "/api/v1/remitos/",
                json=sample_remito_data,
                headers=auth_headers
            )
            remitos_ids.append(create_response.json()["id"])
        
        # Enviar lote
        response = client.post(
            "/api/v1/async/remitos/lote/enviar-afip",
            json={"remitos_ids": remitos_ids},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["total_remitos"] == 3
    
    def test_get_task_status(self, client: TestClient, auth_headers: dict):
        """Test obtener estado de tarea"""
        # Nota: Este test es básico ya que requiere Celery ejecutándose
        response = client.get(
            "/api/v1/async/tasks/fake-task-id/status",
            headers=auth_headers
        )
        
        # Puede ser 404 (tarea no encontrada) o 200 dependiendo del estado de Celery
        assert response.status_code in [200, 404]