#!/usr/bin/env python3
"""
Script de prueba completa de la API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8003"

def test_api():
    """Prueba completa de endpoints de la API"""
    
    print("🚀 Iniciando pruebas de la API REST...")
    
    # 1. Test de salud básica
    print("\n1️⃣ Probando endpoint de salud...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ GET / - Status: {response.status_code}")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ GET / - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")
        return False
    
    # 2. Test de registro de usuario
    print("\n2️⃣ Probando registro de usuario...")
    user_data = {
        "email": "admin@test.com",
        "password": "admin123",
        "nombre": "Admin",
        "apellido": "Test",
        "role": "ADMIN"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            print(f"✅ POST /auth/register - Status: {response.status_code}")
        else:
            print(f"⚠️  POST /auth/register - Status: {response.status_code} (puede ser usuario existente)")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en registro: {e}")
    
    # 3. Test de login
    print("\n3️⃣ Probando login...")
    login_data = {
        "username": "admin@test.com",  # FastAPI OAuth2 usa 'username'
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ POST /auth/login - Status: {response.status_code}")
            print(f"   Token obtenido: {access_token[:20]}...")
            
            # Usar token para requests autenticados
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 4. Test de perfil de usuario
            print("\n4️⃣ Probando perfil de usuario...")
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                print(f"✅ GET /auth/me - Status: {response.status_code}")
                print(f"   Usuario: {response.json()}")
            else:
                print(f"❌ GET /auth/me - Status: {response.status_code}")
            
            # 5. Test de listado de remitos
            print("\n5️⃣ Probando listado de remitos...")
            response = requests.get(f"{BASE_URL}/remitos", headers=headers)
            if response.status_code == 200:
                remitos = response.json()
                print(f"✅ GET /remitos - Status: {response.status_code}")
                print(f"   Remitos encontrados: {len(remitos)}")
            else:
                print(f"❌ GET /remitos - Status: {response.status_code}")
            
            # 6. Test de creación de remito
            print("\n6️⃣ Probando creación de remito...")
            remito_data = {
                "numero": f"R-{datetime.now().strftime('%Y%m%d')}",
                "fecha_emision": datetime.now().isoformat(),
                "cuit_emisor": "20123456786",
                "razon_social_emisor": "Empresa Test SRL",
                "cuit_receptor": "20987654321",
                "razon_social_receptor": "Cliente Test SA",
                "productos": [
                    {
                        "descripcion": "Carne vacuna",
                        "cantidad": 100.5,
                        "unidad": "kg",
                        "precio_unitario": 1500.0
                    }
                ],
                "total": 150750.0,
                "observaciones": "Remito de prueba"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/remitos", json=remito_data, headers=headers)
                if response.status_code in [200, 201]:
                    remito_creado = response.json()
                    print(f"✅ POST /remitos - Status: {response.status_code}")
                    print(f"   Remito creado ID: {remito_creado.get('id')}")
                    
                    # 7. Test de obtener remito específico
                    remito_id = remito_creado.get('id')
                    if remito_id:
                        print(f"\n7️⃣ Probando obtener remito ID {remito_id}...")
                        response = requests.get(f"{BASE_URL}/remitos/{remito_id}", headers=headers)
                        if response.status_code == 200:
                            print(f"✅ GET /remitos/{remito_id} - Status: {response.status_code}")
                        else:
                            print(f"❌ GET /remitos/{remito_id} - Status: {response.status_code}")
                    
                else:
                    print(f"❌ POST /remitos - Status: {response.status_code}")
                    print(f"   Error: {response.text}")
            except Exception as e:
                print(f"❌ Error creando remito: {e}")
            
        else:
            print(f"❌ POST /auth/login - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en login: {e}")
    
    # 8. Test de documentación
    print("\n8️⃣ Probando documentación...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"✅ GET /docs - Status: {response.status_code} (Documentación disponible)")
        else:
            print(f"❌ GET /docs - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo a docs: {e}")
    
    print(f"\n🎉 ¡Pruebas de API completadas!")
    print(f"📱 Documentación interactiva: {BASE_URL}/docs")
    print(f"📚 Documentación alternativa: {BASE_URL}/redoc")

if __name__ == "__main__":
    test_api()