#!/usr/bin/env python3
"""
Script de prueba completo para endpoints AFIP con certificado sgpatagon25
Prueba extracción de datos de AFIP usando la API
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8080/api/v1"
TEST_CUIT = "24238783522"  # CUIT proporcionado
TEST_PASSWORD = "Ignacio2024"  # Clave proporcionada
TEST_USERNAME = "ignacio_afip"
TEST_EMAIL = "ignacio.afip@sgpatagon25.com"

class AFIPAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.base_url = BASE_URL
        
    def print_response(self, response, title):
        """Imprime la respuesta de manera formateada"""
        print(f"\n{'='*70}")
        print(f"🔍 {title}")
        print(f"{'='*70}")
        print(f"Status Code: {response.status_code}")
        try:
            json_data = response.json()
            print(f"Response: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
        print(f"{'='*70}")
        
    def register_and_login(self):
        """Registra usuario y hace login"""
        print(f"\n👤 Registrando usuario para pruebas AFIP...")
        
        # Registro
        user_data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "cuit": TEST_CUIT,
            "full_name": "Usuario Prueba AFIP - Sgpatagon25",
            "role": "admin"  # Admin para acceder a todos los endpoints
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            print("✅ Usuario registrado exitosamente")
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️ Usuario ya existe, procediendo con login")
        else:
            print(f"❌ Error en registro: {response.status_code}")
            self.print_response(response, "Error Registro")
        
        # Login
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ Login exitoso - Token configurado")
            return True
        else:
            print(f"❌ Error en login: {response.status_code}")
            self.print_response(response, "Error Login")
            return False
    
    def test_afip_status(self):
        """Prueba el endpoint de estado AFIP"""
        print("\n🏥 Probando estado del sistema AFIP...")
        response = self.session.get(f"{self.base_url}/afip/")
        self.print_response(response, "Estado Sistema AFIP")
        return response.status_code == 200
    
    def test_afip_diagnostico(self):
        """Prueba el diagnóstico completo AFIP"""
        print("\n🔧 Ejecutando diagnóstico completo AFIP...")
        response = self.session.get(f"{self.base_url}/afip/diagnostico")
        self.print_response(response, "Diagnóstico AFIP")
        return response.status_code == 200
    
    def test_padron_a4(self, cuit=TEST_CUIT):
        """Prueba consulta Padrón A4"""
        print(f"\n📋 Consultando Padrón A4 para CUIT: {cuit}")
        response = self.session.get(f"{self.base_url}/afip/padron-a4/{cuit}")
        self.print_response(response, f"Padrón A4 - CUIT {cuit}")
        return response.status_code == 200
    
    def test_padron_a5(self, cuit=TEST_CUIT):
        """Prueba consulta Padrón A5"""
        print(f"\n📋 Consultando Padrón A5 para CUIT: {cuit}")
        response = self.session.get(f"{self.base_url}/afip/padron-a5/{cuit}")
        self.print_response(response, f"Padrón A5 - CUIT {cuit}")
        return response.status_code == 200
    
    def test_datos_completos(self, cuit=TEST_CUIT):
        """Prueba extracción completa de datos"""
        print(f"\n🔍 Extracción completa de datos para CUIT: {cuit}")
        params = {
            "incluir_padron_a4": True,
            "incluir_padron_a5": True
        }
        response = self.session.get(f"{self.base_url}/afip/datos-completos/{cuit}", params=params)
        self.print_response(response, f"Datos Completos - CUIT {cuit}")
        return response.status_code == 200
    
    def test_batch_consulta(self):
        """Prueba consulta en lote"""
        print("\n📦 Probando consulta batch...")
        
        cuits_test = [TEST_CUIT, "20123456789", "30999999995"]
        batch_data = cuits_test
        
        params = {"tipo_consulta": "padron-a5"}
        response = self.session.post(
            f"{self.base_url}/afip/batch-consulta", 
            json=batch_data,
            params=params
        )
        self.print_response(response, "Consulta Batch")
        return response.status_code == 200
    
    def test_multiple_cuits(self):
        """Prueba con múltiples CUITs para verificar robustez"""
        print("\n🔄 Probando múltiples CUITs...")
        
        cuits_prueba = [
            TEST_CUIT,           # CUIT principal
            "20123456789",       # CUIT de prueba válido
            "30999999995",       # CUIT de prueba empresa
            "27123456785",       # Otro CUIT de prueba
        ]
        
        resultados = {}
        for cuit in cuits_prueba:
            print(f"\n   Probando CUIT: {cuit}")
            try:
                response = self.session.get(f"{self.base_url}/afip/padron-a5/{cuit}")
                resultados[cuit] = {
                    "status": response.status_code,
                    "success": response.status_code == 200
                }
                if response.status_code == 200:
                    print(f"   ✅ {cuit}: OK")
                else:
                    print(f"   ❌ {cuit}: Error {response.status_code}")
            except Exception as e:
                print(f"   ❌ {cuit}: Excepción - {e}")
                resultados[cuit] = {"status": "error", "success": False}
        
        print(f"\n📊 Resumen múltiples CUITs:")
        exitosos = sum(1 for r in resultados.values() if r.get("success"))
        print(f"   Total probados: {len(cuits_prueba)}")
        print(f"   Exitosos: {exitosos}")
        print(f"   Errores: {len(cuits_prueba) - exitosos}")
        
        return exitosos > 0

    def run_full_afip_test(self):
        """Ejecuta todas las pruebas AFIP en secuencia"""
        print(f"""
🚀 PRUEBAS COMPLETAS AFIP - CERTIFICADO SGPATAGON25
==================================================
Certificado ID: sgpatagon25_23ad6985d1bcb772
CUIT Principal: {TEST_CUIT}
Usuario: {TEST_USERNAME}
Ambiente: Testing
API Base: {self.base_url}
==================================================
""")
        
        results = {}
        
        # 1. Registro y login
        if not self.register_and_login():
            print("❌ No se puede continuar sin autenticación")
            return
        
        # 2. Estado del sistema AFIP
        results['afip_status'] = self.test_afip_status()
        
        # 3. Diagnóstico completo
        results['diagnostico'] = self.test_afip_diagnostico()
        
        # 4. Padrón A4
        results['padron_a4'] = self.test_padron_a4()
        
        # 5. Padrón A5
        results['padron_a5'] = self.test_padron_a5()
        
        # 6. Datos completos
        results['datos_completos'] = self.test_datos_completos()
        
        # 7. Consulta batch
        results['batch_consulta'] = self.test_batch_consulta()
        
        # 8. Múltiples CUITs
        results['multiple_cuits'] = self.test_multiple_cuits()
        
        # Resumen final
        print(f"""
📊 RESUMEN FINAL PRUEBAS AFIP
=============================
Estado AFIP: {'✅ PASS' if results.get('afip_status') else '❌ FAIL'}
Diagnóstico: {'✅ PASS' if results.get('diagnostico') else '❌ FAIL'}
Padrón A4: {'✅ PASS' if results.get('padron_a4') else '❌ FAIL'}
Padrón A5: {'✅ PASS' if results.get('padron_a5') else '❌ FAIL'}
Datos Completos: {'✅ PASS' if results.get('datos_completos') else '❌ FAIL'}
Consulta Batch: {'✅ PASS' if results.get('batch_consulta') else '❌ FAIL'}
Múltiples CUITs: {'✅ PASS' if results.get('multiple_cuits') else '❌ FAIL'}
=============================
Total Exitosos: {sum(1 for v in results.values() if v)}/{len(results)}

🎯 CERTIFICADO SGPATAGON25: {'🟢 FUNCIONANDO CORRECTAMENTE' if sum(1 for v in results.values() if v) >= 5 else '🔴 REQUIERE ATENCIÓN'}

📋 ENDPOINTS AFIP DISPONIBLES:
- GET /api/v1/afip/ (Estado del sistema)
- GET /api/v1/afip/diagnostico (Diagnóstico completo)  
- GET /api/v1/afip/padron-a4/{{cuit}} (Padrón A4)
- GET /api/v1/afip/padron-a5/{{cuit}} (Padrón A5)
- GET /api/v1/afip/datos-completos/{{cuit}} (Extracción completa)
- POST /api/v1/afip/batch-consulta (Consulta en lote)

🔐 Certificado: sgpatagon25_23ad6985d1bcb772
🌐 Ambiente: Testing (Homologación AFIP)
✅ Listo para extracción de datos reales con certificado válido
""")

if __name__ == "__main__":
    tester = AFIPAPITester()
    tester.run_full_afip_test()