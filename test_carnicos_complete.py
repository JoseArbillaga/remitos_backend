#!/usr/bin/env python3
"""
Script de prueba completo para automatización de remitos cárnicos
Demuestra la extracción automática de datos AFIP para remitos del sector cárnico
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_CUIT = "24238783522"  # CUIT proporcionado
TEST_PASSWORD = "Ignacio2024"  # Clave proporcionada
TEST_USERNAME = "carnico_user"
TEST_EMAIL = "carnico@sgpatagon25.com"

class RemitoCarnicoTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.base_url = BASE_URL
        
    def print_response(self, response, title):
        """Imprime la respuesta de manera formateada"""
        print(f"\n{'='*80}")
        print(f"🔍 {title}")
        print(f"{'='*80}")
        print(f"Status Code: {response.status_code}")
        try:
            json_data = response.json()
            print(f"Response: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
        print(f"{'='*80}")
        
    def setup_user(self):
        """Configura usuario para pruebas cárnicas"""
        print(f"\n👤 Configurando usuario para pruebas cárnicas...")
        
        # Registro
        user_data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "cuit": TEST_CUIT,
            "full_name": "Usuario Remitos Cárnicos - Sgpatagon25",
            "role": "admin"
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            print("✅ Usuario registrado exitosamente")
        elif "already exists" in response.text:
            print("ℹ️ Usuario ya existe")
        
        # Login
        login_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
        response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Login exitoso - Listo para pruebas cárnicas")
            return True
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
    
    def test_estado_sistema_carnico(self):
        """Prueba el estado del sistema cárnico"""
        print("\n🥩 Probando estado del sistema cárnico...")
        response = self.session.get(f"{self.base_url}/afip/carnicos/")
        self.print_response(response, "Estado Sistema Cárnico")
        return response.status_code == 200
    
    def test_establecimientos_carnicos(self, cuit=TEST_CUIT):
        """Prueba obtención de establecimientos cárnicos"""
        print(f"\n🏭 Obteniendo establecimientos cárnicos para CUIT: {cuit}")
        response = self.session.get(f"{self.base_url}/afip/carnicos/establecimientos/{cuit}")
        self.print_response(response, f"Establecimientos Cárnicos - CUIT {cuit}")
        
        if response.status_code == 200:
            data = response.json()
            establecimientos = data.get("establecimientos", {}).get("establecimientos", [])
            print(f"📊 Resumen establecimientos:")
            for est in establecimientos:
                print(f"   • {est['numero_senasa']}: {est['nombre']} ({est['tipo']})")
        
        return response.status_code == 200
    
    def test_catalogo_productos_carnicos(self):
        """Prueba obtención del catálogo de productos cárnicos"""
        print("\n📋 Obteniendo catálogo de productos cárnicos...")
        response = self.session.get(f"{self.base_url}/afip/carnicos/productos")
        self.print_response(response, "Catálogo Productos Cárnicos")
        
        if response.status_code == 200:
            data = response.json()
            categorias = data.get("catalogo", {}).get("categorias", {})
            print(f"📊 Resumen catálogo:")
            for cat_name, cat_data in categorias.items():
                print(f"   • {cat_name}: {len(cat_data['productos'])} productos")
        
        return response.status_code == 200
    
    def test_trazabilidad_carnica(self, cuit=TEST_CUIT):
        """Prueba obtención de trazabilidad cárnica"""
        print(f"\n🔗 Obteniendo trazabilidad cárnica para CUIT: {cuit}")
        response = self.session.get(f"{self.base_url}/afip/carnicos/trazabilidad/{cuit}")
        self.print_response(response, f"Trazabilidad Cárnica - CUIT {cuit}")
        
        if response.status_code == 200:
            data = response.json()
            trazabilidad = data.get("trazabilidad", {})
            sistemas = trazabilidad.get("sistemas_trazabilidad", {})
            print(f"📊 Resumen trazabilidad:")
            for sistema, info in sistemas.items():
                if info.get("activo"):
                    print(f"   • {sistema}: {info['animales_registrados']} animales")
        
        return response.status_code == 200
    
    def test_remito_automatico(self):
        """Prueba generación automática de remito cárnico"""
        print("\n📄 Generando remito cárnico automático...")
        
        remito_data = {
            "cuit_origen": TEST_CUIT,
            "cuit_destino": "30999999995",  # CUIT destino de prueba
            "productos": [
                {
                    "descripcion": "Carne bovina fresca - Cuartos delanteros",
                    "cantidad": 100,
                    "peso_unitario": 25.0,
                    "precio_unitario": 150.0,
                    "tipo_producto": "FRESCO"
                },
                {
                    "descripcion": "Chorizo fresco artesanal",
                    "cantidad": 50,
                    "peso_unitario": 0.5,
                    "precio_unitario": 80.0,
                    "tipo_producto": "ELABORADO"
                },
                {
                    "descripcion": "Carne porcina - Cortes especiales",
                    "cantidad": 75,
                    "peso_unitario": 2.0,
                    "precio_unitario": 120.0,
                    "tipo_producto": "FRESCO"
                }
            ],
            "observaciones": "Remito automático generado desde AFIP - Certificado sgpatagon25",
            "transporte": {
                "empresa": "Transporte Frigorífico SRL",
                "chofer": "Juan Carlos Transportista",
                "vehiculo": "Camión refrigerado - ABC123"
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/afip/carnicos/remito-automatico",
            json=remito_data,
            params={"incluir_trazabilidad": True}
        )
        
        self.print_response(response, "Remito Cárnico Automático")
        
        if response.status_code == 200:
            data = response.json()
            remito = data.get("remito_carnico", {})
            print(f"""
📊 REMITO GENERADO AUTOMÁTICAMENTE:
===================================
Número: {remito.get('numero_remito')}
Origen: {remito.get('emisor', {}).get('cuit')} - {remito.get('emisor', {}).get('datos_afip', {}).get('denominacion')}
Destino: {remito.get('destinatario', {}).get('cuit')} - {remito.get('destinatario', {}).get('datos_afip', {}).get('denominacion')}
Productos: {len(remito.get('productos', []))}
Peso Total: {remito.get('totales', {}).get('peso_total_kg', 0)} kg
Valor Total: ${remito.get('totales', {}).get('valor_total', 0):.2f}
Establecimiento Origen: {remito.get('emisor', {}).get('establecimiento', {}).get('numero_senasa')}
Establecimiento Destino: {remito.get('destinatario', {}).get('establecimiento', {}).get('numero_senasa')}
Trazabilidad: {remito.get('trazabilidad', {}).get('codigo_trazabilidad')}
===================================
""")
        
        return response.status_code == 200
    
    def test_batch_remitos(self):
        """Prueba generación en lote de remitos cárnicos"""
        print("\n📦 Probando generación batch de remitos cárnicos...")
        
        batch_data = [
            {
                "cuit_origen": TEST_CUIT,
                "cuit_destino": "30111111119",
                "productos": [
                    {
                        "descripcion": "Carne bovina deshuesada",
                        "cantidad": 50,
                        "peso_unitario": 1.0,
                        "precio_unitario": 180.0,
                        "tipo_producto": "FRESCO"
                    }
                ]
            },
            {
                "cuit_origen": TEST_CUIT,
                "cuit_destino": "30222222228",
                "productos": [
                    {
                        "descripcion": "Salame artesanal",
                        "cantidad": 30,
                        "peso_unitario": 0.3,
                        "precio_unitario": 200.0,
                        "tipo_producto": "ELABORADO"
                    }
                ]
            }
        ]
        
        response = self.session.post(
            f"{self.base_url}/afip/carnicos/batch-remitos",
            json=batch_data
        )
        
        self.print_response(response, "Batch Remitos Cárnicos")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Batch completado: {data.get('exitosos')}/{data.get('total_solicitados')} remitos generados")
        
        return response.status_code == 200
    
    def test_validacion_establecimiento(self, cuit=TEST_CUIT):
        """Prueba validación de establecimiento cárnico"""
        print(f"\n✅ Validando establecimiento cárnico para CUIT: {cuit}")
        response = self.session.get(f"{self.base_url}/afip/carnicos/validaciones/establecimiento/{cuit}")
        self.print_response(response, f"Validación Establecimiento - CUIT {cuit}")
        
        if response.status_code == 200:
            data = response.json()
            validacion = data.get("validacion", {})
            print(f"""
📊 VALIDACIÓN ESTABLECIMIENTO:
==============================
CUIT: {validacion.get('cuit')}
Total Establecimientos: {validacion.get('total_establecimientos')}
Establecimientos Habilitados: {validacion.get('establecimientos_habilitados')}
Válido: {'✅ SÍ' if validacion.get('valido') else '❌ NO'}
==============================
""")
        
        return response.status_code == 200

    def run_demo_completo_carnicos(self):
        """Ejecuta demostración completa de automatización cárnica"""
        print(f"""
🥩 DEMO COMPLETO: AUTOMATIZACIÓN REMITOS CÁRNICOS
==================================================
Certificado AFIP: sgpatagon25_23ad6985d1bcb772
CUIT Empresa: {TEST_CUIT}
Sistema: Extracción automática AFIP → Remitos cárnicos
Integración: SENASA + Trazabilidad + AFIP
==================================================
""")
        
        results = {}
        
        # 1. Setup usuario
        if not self.setup_user():
            print("❌ No se puede continuar sin autenticación")
            return
        
        # 2. Estado sistema cárnico
        results['sistema_carnico'] = self.test_estado_sistema_carnico()
        
        # 3. Establecimientos cárnicos
        results['establecimientos'] = self.test_establecimientos_carnicos()
        
        # 4. Catálogo productos
        results['catalogo_productos'] = self.test_catalogo_productos_carnicos()
        
        # 5. Trazabilidad
        results['trazabilidad'] = self.test_trazabilidad_carnica()
        
        # 6. Validación establecimiento
        results['validacion_establecimiento'] = self.test_validacion_establecimiento()
        
        # 7. Remito automático
        results['remito_automatico'] = self.test_remito_automatico()
        
        # 8. Batch remitos
        results['batch_remitos'] = self.test_batch_remitos()
        
        # Resumen final
        exitosos = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"""
📊 RESUMEN DEMO AUTOMATIZACIÓN CÁRNICA
=======================================
Sistema Cárnico: {'✅ OK' if results.get('sistema_carnico') else '❌ FAIL'}
Establecimientos: {'✅ OK' if results.get('establecimientos') else '❌ FAIL'}
Catálogo Productos: {'✅ OK' if results.get('catalogo_productos') else '❌ FAIL'}
Trazabilidad: {'✅ OK' if results.get('trazabilidad') else '❌ FAIL'}
Validación Establec.: {'✅ OK' if results.get('validacion_establecimiento') else '❌ FAIL'}
Remito Automático: {'✅ OK' if results.get('remito_automatico') else '❌ FAIL'}
Batch Remitos: {'✅ OK' if results.get('batch_remitos') else '❌ FAIL'}
=======================================
Pruebas exitosas: {exitosos}/{total}

🎯 AUTOMATIZACIÓN CÁRNICA: {'🟢 FUNCIONANDO' if exitosos >= 6 else '🔴 REQUIERE REVISIÓN'}

🔗 ENDPOINTS CÁRNICOS DISPONIBLES:
• GET /api/v1/afip/carnicos/ - Estado sistema
• GET /api/v1/afip/carnicos/establecimientos/{{cuit}} - Establecimientos
• GET /api/v1/afip/carnicos/productos - Catálogo productos
• GET /api/v1/afip/carnicos/trazabilidad/{{cuit}} - Trazabilidad
• POST /api/v1/afip/carnicos/remito-automatico - Remito automático
• POST /api/v1/afip/carnicos/batch-remitos - Remitos en lote
• GET /api/v1/afip/carnicos/validaciones/establecimiento/{{cuit}} - Validaciones

🏭 AUTOMATIZACIÓN COMPLETA:
1. Extraer datos AFIP/SENASA para CUIT empresa
2. Obtener establecimientos cárnicos habilitados
3. Cargar catálogo productos con códigos oficiales
4. Incluir trazabilidad (SNIG/SIGP)
5. Generar remito automáticamente con toda la información regulatoria
6. Validar cumplimiento normativo sector cárnico

✅ Sistema listo para automatizar creación de remitos cárnicos desde datos AFIP!
🥩 Certificado sgpatagon25 operativo para sector cárnico argentino
""")

if __name__ == "__main__":
    tester = RemitoCarnicoTester()
    tester.run_demo_completo_carnicos()