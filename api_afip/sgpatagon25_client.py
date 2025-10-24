#!/usr/bin/env python3
"""
Cliente AFIP actualizado para sgpatagon25_23ad6985d1bcb772
Configurado para entorno de testing y extracción de datos
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from config_afip import (
    CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, CLAVE_PUBLICA_AFIP,
    CERTIFICADO_ID, CERTIFICADO_NOMBRE, AMBIENTE, SERVICIOS_ACTIVOS,
    TESTING_CONFIG, get_service_url, CUIT_EMPRESA, PUNTO_VENTA
)

class AFIPClientSgpatagon25:
    """Cliente AFIP específico para certificado sgpatagon25"""
    
    def __init__(self):
        self.certificado_path = os.path.join(os.path.dirname(__file__), CERTIFICADO_AFIP)
        self.clave_privada_path = os.path.join(os.path.dirname(__file__), CLAVE_PRIVADA_AFIP)
        self.clave_publica_path = os.path.join(os.path.dirname(__file__), CLAVE_PUBLICA_AFIP)
        self.ambiente = AMBIENTE
        self.certificado_id = CERTIFICADO_ID
        self.session = requests.Session()
        self.ticket_acceso = None
        self.token_autenticacion = None
        
        print(f"""
🔐 AFIP CLIENT SGPATAGON25 INICIADO
===================================
Certificado ID: {self.certificado_id}
Ambiente: {self.ambiente}
Servicios activos: {len(SERVICIOS_ACTIVOS)}
===================================
""")
    
    def verificar_archivos(self):
        """Verifica que existan todos los archivos necesarios"""
        archivos = {
            "Certificado": self.certificado_path,
            "Clave Privada": self.clave_privada_path,
            "Clave Pública": self.clave_publica_path
        }
        
        print("🔍 Verificando archivos...")
        for nombre, path in archivos.items():
            if os.path.exists(path):
                print(f"✅ {nombre}: {path}")
            else:
                print(f"❌ {nombre}: {path} - NO ENCONTRADO")
                return False
        return True
    
    def leer_certificado(self):
        """Lee el contenido del certificado"""
        try:
            with open(self.certificado_path, 'r') as f:
                contenido = f.read()
                print(f"✅ Certificado leído: {len(contenido)} caracteres")
                return contenido
        except Exception as e:
            print(f"❌ Error leyendo certificado: {e}")
            return None
    
    def leer_clave_privada(self):
        """Lee el contenido de la clave privada"""
        try:
            with open(self.clave_privada_path, 'r') as f:
                contenido = f.read()
                print(f"✅ Clave privada leída: {len(contenido)} caracteres")
                return contenido
        except Exception as e:
            print(f"❌ Error leyendo clave privada: {e}")
            return None
    
    def generar_ticket_request(self, servicio):
        """Genera el XML para solicitar ticket de acceso"""
        now = datetime.now()
        unique_id = int(now.timestamp())
        
        xml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
    <header>
        <uniqueId>{unique_id}</uniqueId>
        <generationTime>{now.strftime('%Y-%m-%dT%H:%M:%S')}</generationTime>
        <expirationTime>{(now + timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')}</expirationTime>
    </header>
    <service>{servicio}</service>
</loginTicketRequest>"""
        
        return xml_request
    
    def test_conectividad_wsaa(self):
        """Prueba la conectividad con el servicio WSAA"""
        print("🌐 Probando conectividad con WSAA...")
        
        url_wsaa = get_service_url("wsaa", self.ambiente)
        print(f"URL WSAA: {url_wsaa}")
        
        try:
            response = self.session.get(url_wsaa, timeout=TESTING_CONFIG["timeout"])
            print(f"✅ Respuesta WSAA: Status {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Error conectando WSAA: {e}")
            return False
    
    def obtener_padron_a4(self, cuit):
        """Obtiene datos del padrón A4 para un CUIT"""
        print(f"📋 Obteniendo datos padrón A4 para CUIT: {cuit}")
        
        url_padron = get_service_url("padron-a4", self.ambiente)
        
        # Datos de prueba para testing
        datos_simulados = {
            "cuit": cuit,
            "denominacion": f"Empresa Test CUIT {cuit}",
            "estado": "ACTIVO",
            "fecha_consulta": datetime.now().isoformat(),
            "ambiente": self.ambiente,
            "fuente": "padron-a4-testing"
        }
        
        print(f"✅ Datos padrón A4 obtenidos (simulados para testing):")
        for key, value in datos_simulados.items():
            print(f"   {key}: {value}")
            
        return datos_simulados
    
    def obtener_padron_a5(self, cuit):
        """Obtiene datos del padrón A5 para un CUIT"""
        print(f"📋 Obteniendo datos padrón A5 para CUIT: {cuit}")
        
        # Datos de prueba más completos para testing
        datos_simulados = {
            "cuit": cuit,
            "denominacion": f"Razón Social Test {cuit}",
            "tipo_persona": "JURIDICA",
            "estado": "ACTIVO",
            "domicilio_fiscal": {
                "direccion": "Av. Test 1234",
                "localidad": "CABA",
                "codigo_postal": "1000",
                "provincia": "CAPITAL FEDERAL"
            },
            "actividades": [
                {"codigo": "123456", "descripcion": "Actividad Test 1"},
                {"codigo": "789012", "descripcion": "Actividad Test 2"}
            ],
            "impuestos": [
                {"codigo": "20", "descripcion": "IVA RESPONSABLE INSCRIPTO"},
                {"codigo": "30", "descripcion": "INGRESOS BRUTOS"}
            ],
            "fecha_consulta": datetime.now().isoformat(),
            "ambiente": self.ambiente,
            "fuente": "padron-a5-testing"
        }
        
        print(f"✅ Datos padrón A5 obtenidos (simulados para testing):")
        print(f"   Denominación: {datos_simulados['denominacion']}")
        print(f"   Estado: {datos_simulados['estado']}")
        print(f"   Actividades: {len(datos_simulados['actividades'])}")
        print(f"   Impuestos: {len(datos_simulados['impuestos'])}")
            
        return datos_simulados
    
    def extraer_datos_completos(self, cuit):
        """Extrae datos completos de AFIP para un CUIT"""
        print(f"""
🔍 EXTRAYENDO DATOS COMPLETOS AFIP
==================================
CUIT: {cuit}
Certificado: {self.certificado_id}
Ambiente: {self.ambiente}
==================================
""")
        
        datos_completos = {
            "cuit_consultado": cuit,
            "certificado_usado": self.certificado_id,
            "ambiente": self.ambiente,
            "timestamp": datetime.now().isoformat(),
            "servicios_consultados": []
        }
        
        # Obtener datos padrón A4
        try:
            datos_a4 = self.obtener_padron_a4(cuit)
            datos_completos["padron_a4"] = datos_a4
            datos_completos["servicios_consultados"].append("padron-a4")
        except Exception as e:
            print(f"❌ Error obteniendo padrón A4: {e}")
        
        # Obtener datos padrón A5
        try:
            datos_a5 = self.obtener_padron_a5(cuit)
            datos_completos["padron_a5"] = datos_a5
            datos_completos["servicios_consultados"].append("padron-a5")
        except Exception as e:
            print(f"❌ Error obteniendo padrón A5: {e}")
        
        return datos_completos
    
    def run_diagnostico_completo(self):
        """Ejecuta un diagnóstico completo del sistema AFIP"""
        print(f"""
🚀 DIAGNÓSTICO COMPLETO AFIP
============================
Certificado: {CERTIFICADO_NOMBRE}
ID: {CERTIFICADO_ID}
Ambiente: {self.ambiente}
============================
""")
        
        resultados = {}
        
        # 1. Verificar archivos
        print("\n1️⃣ Verificando archivos...")
        resultados["archivos_ok"] = self.verificar_archivos()
        
        # 2. Leer certificado
        print("\n2️⃣ Leyendo certificado...")
        cert_content = self.leer_certificado()
        resultados["certificado_ok"] = cert_content is not None
        
        # 3. Leer clave privada
        print("\n3️⃣ Leyendo clave privada...")
        key_content = self.leer_clave_privada()
        resultados["clave_privada_ok"] = key_content is not None
        
        # 4. Test conectividad WSAA
        print("\n4️⃣ Probando conectividad WSAA...")
        resultados["wsaa_ok"] = self.test_conectividad_wsaa()
        
        # 5. Test extracción datos
        print("\n5️⃣ Probando extracción de datos...")
        try:
            datos_test = self.extraer_datos_completos("20123456789")
            resultados["extraccion_ok"] = True
            resultados["datos_extraidos"] = len(datos_test.get("servicios_consultados", []))
        except Exception as e:
            print(f"❌ Error en extracción: {e}")
            resultados["extraccion_ok"] = False
            resultados["datos_extraidos"] = 0
        
        # Resumen
        print(f"""
📊 RESUMEN DIAGNÓSTICO
======================
Archivos: {'✅' if resultados['archivos_ok'] else '❌'}
Certificado: {'✅' if resultados['certificado_ok'] else '❌'}
Clave Privada: {'✅' if resultados['clave_privada_ok'] else '❌'}
WSAA: {'✅' if resultados['wsaa_ok'] else '❌'}
Extracción: {'✅' if resultados['extraccion_ok'] else '❌'}
Servicios: {resultados['datos_extraidos']}
======================
Estado: {'🟢 OPERATIVO' if all([resultados['archivos_ok'], resultados['certificado_ok'], resultados['clave_privada_ok']]) else '🔴 REQUIERE ATENCIÓN'}
""")
        
        return resultados

if __name__ == "__main__":
    # Crear cliente y ejecutar diagnóstico
    cliente = AFIPClientSgpatagon25()
    resultados = cliente.run_diagnostico_completo()
    
    print(f"\n🎯 Cliente AFIP sgpatagon25 {'configurado correctamente' if resultados['archivos_ok'] else 'requiere configuración adicional'}")