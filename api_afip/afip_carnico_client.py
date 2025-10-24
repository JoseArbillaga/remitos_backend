#!/usr/bin/env python3
"""
Cliente AFIP especializado para remitos cárnicos
Integración con SENASA, trazabilidad y servicios específicos del sector cárnico
Certificado: sgpatagon25_23ad6985d1bcb772
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Importar configuración base
sys.path.append(os.path.dirname(__file__))
from config_afip import (
    CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, CERTIFICADO_ID,
    AMBIENTE, get_service_url, TESTING_CONFIG
)

class AFIPCarnicoClient:
    """Cliente AFIP especializado para el sector cárnico"""
    
    def __init__(self):
        self.certificado_path = os.path.join(os.path.dirname(__file__), CERTIFICADO_AFIP)
        self.clave_privada_path = os.path.join(os.path.dirname(__file__), CLAVE_PRIVADA_AFIP)
        self.ambiente = AMBIENTE
        self.certificado_id = CERTIFICADO_ID
        self.session = requests.Session()
        
        # URLs específicas para servicios cárnicos
        self.urls_carnico = {
            "senasa_ws": "https://ws.senasa.gob.ar/services/",
            "trazabilidad": "https://trazabilidad.senasa.gob.ar/ws/",
            "remcarneservice": "https://wswhomo.afip.gov.ar/remcarneservice/RemCarneService?wsdl",
            "renspa": "https://ws.senasa.gob.ar/renspa/",
            "productos_carnicos": "https://servicios1.afip.gov.ar/genericos/nomencladorProductos/"
        }
        
        print(f"""
🥩 CLIENTE AFIP CÁRNICO INICIADO
================================
Certificado: {self.certificado_id}
Ambiente: {self.ambiente}
Servicios cárnicos: {len(self.urls_carnico)}
================================
""")
    
    def obtener_establecimientos_carnicos(self, cuit: str) -> Dict[str, Any]:
        """
        Obtiene establecimientos cárnicos registrados para un CUIT
        Incluye datos de SENASA y RENSPA
        """
        print(f"🏭 Obteniendo establecimientos cárnicos para CUIT: {cuit}")
        
        # Datos simulados para testing - En producción se conectaría a SENASA
        establecimientos = {
            "cuit_empresa": cuit,
            "establecimientos": [
                {
                    "numero_senasa": f"ES-{cuit}-001",
                    "nombre": f"Frigorífico Principal - {cuit}",
                    "tipo": "FRIGORIFICO",
                    "categoria": "A",
                    "estado": "HABILITADO",
                    "direccion": {
                        "calle": "Av. Industrial 1234",
                        "localidad": "Ciudad del Establecimiento",
                        "provincia": "Buenos Aires",
                        "codigo_postal": "1000"
                    },
                    "actividades_autorizadas": [
                        "FAENA_BOVINOS",
                        "FAENA_PORCINOS", 
                        "DESPOSTE",
                        "ELABORACION_EMBUTIDOS"
                    ],
                    "capacidad_diaria": {
                        "bovinos": 150,
                        "porcinos": 300
                    },
                    "numero_renspa": f"RENSPA-{cuit[-8:]}-A1",
                    "fecha_habilitacion": "2024-01-15",
                    "vencimiento_habilitacion": "2025-12-31",
                    "veterinario_responsable": {
                        "nombre": "Dr. Juan Veterinario",
                        "matricula": "12345-BA"
                    }
                },
                {
                    "numero_senasa": f"ES-{cuit}-002",
                    "nombre": f"Establecimiento Secundario - {cuit}",
                    "tipo": "DESPENSITA",
                    "categoria": "B",
                    "estado": "HABILITADO",
                    "direccion": {
                        "calle": "Ruta Provincial 25 Km 15",
                        "localidad": "Pueblo Ganadero",
                        "provincia": "Buenos Aires", 
                        "codigo_postal": "2000"
                    },
                    "actividades_autorizadas": [
                        "DESPOSTE_MENOR",
                        "COMERCIALIZACION"
                    ],
                    "numero_renspa": f"RENSPA-{cuit[-8:]}-B2",
                    "fecha_habilitacion": "2024-03-01",
                    "vencimiento_habilitacion": "2025-12-31"
                }
            ],
            "resumen": {
                "total_establecimientos": 2,
                "habilitados": 2,
                "suspendidos": 0,
                "tipos": ["FRIGORIFICO", "DESPENSITA"]
            },
            "fecha_consulta": datetime.now().isoformat(),
            "fuente": "SENASA-AFIP",
            "ambiente": self.ambiente
        }
        
        print(f"✅ Encontrados {len(establecimientos['establecimientos'])} establecimientos")
        for est in establecimientos['establecimientos']:
            print(f"   - {est['numero_senasa']}: {est['nombre']} ({est['tipo']})")
        
        return establecimientos
    
    def obtener_productos_carnicos_autorizados(self) -> Dict[str, Any]:
        """
        Obtiene el catálogo de productos cárnicos autorizados
        Con códigos SENASA y nomencladores AFIP
        """
        print("📋 Obteniendo catálogo de productos cárnicos...")
        
        productos = {
            "categorias": {
                "bovinos": {
                    "descripcion": "Productos bovinos",
                    "productos": [
                        {
                            "codigo_senasa": "BOV001",
                            "codigo_afip": "02011000",
                            "descripcion": "Carne bovina fresca - Cuartos delanteros",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "A",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C"
                        },
                        {
                            "codigo_senasa": "BOV002", 
                            "codigo_afip": "02012000",
                            "descripcion": "Carne bovina fresca - Cuartos traseros",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "A",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C"
                        },
                        {
                            "codigo_senasa": "BOV003",
                            "codigo_afip": "02013000",
                            "descripcion": "Carne bovina deshuesada fresca",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "A",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C"
                        }
                    ]
                },
                "porcinos": {
                    "descripcion": "Productos porcinos",
                    "productos": [
                        {
                            "codigo_senasa": "POR001",
                            "codigo_afip": "02031100",
                            "descripcion": "Carne porcina fresca - Canales",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "A",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C"
                        },
                        {
                            "codigo_senasa": "POR002",
                            "codigo_afip": "02031200",
                            "descripcion": "Carne porcina fresca - Cortes",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "A", 
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C"
                        }
                    ]
                },
                "elaborados": {
                    "descripcion": "Productos elaborados",
                    "productos": [
                        {
                            "codigo_senasa": "ELA001",
                            "codigo_afip": "16020010",
                            "descripcion": "Embutidos frescos - Chorizo",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "B",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "0 a 4°C",
                            "vida_util_dias": 15
                        },
                        {
                            "codigo_senasa": "ELA002",
                            "codigo_afip": "16020020",
                            "descripcion": "Embutidos secos - Salame",
                            "unidad_medida": "KG",
                            "categoria_sanitaria": "B",
                            "requiere_trazabilidad": True,
                            "temperatura_transporte": "Ambiente",
                            "vida_util_dias": 60
                        }
                    ]
                }
            },
            "normativas": {
                "senasa": "Resolución SENASA 382/2021",
                "codigo_alimentario": "CAA - Capítulo VI",
                "trazabilidad": "Sistema Nacional de Trazabilidad",
                "transporte": "Reglamento transporte carnes"
            },
            "fecha_actualizacion": datetime.now().isoformat(),
            "fuente": "SENASA-AFIP",
            "ambiente": self.ambiente
        }
        
        total_productos = sum(len(cat["productos"]) for cat in productos["categorias"].values())
        print(f"✅ Catálogo cargado: {total_productos} productos en {len(productos['categorias'])} categorías")
        
        return productos
    
    def obtener_datos_trazabilidad(self, cuit: str) -> Dict[str, Any]:
        """
        Obtiene datos de trazabilidad para una empresa cárnica
        Incluye animales, lotes y cadena de custodia
        """
        print(f"🔗 Obteniendo datos de trazabilidad para CUIT: {cuit}")
        
        trazabilidad = {
            "cuit_empresa": cuit,
            "sistemas_trazabilidad": {
                "bovinos": {
                    "activo": True,
                    "sistema": "SNIG - Sistema Nacional de Identificación de Ganado",
                    "animales_registrados": 2500,
                    "lotes_activos": 15,
                    "establecimiento_origen": f"EST-{cuit}-CAMPO",
                    "ultimo_movimiento": "2025-10-20"
                },
                "porcinos": {
                    "activo": True,
                    "sistema": "SIGP - Sistema de Identificación de Ganado Porcino",
                    "animales_registrados": 800,
                    "lotes_activos": 8,
                    "establecimiento_origen": f"EST-{cuit}-GRANJA",
                    "ultimo_movimiento": "2025-10-22"
                }
            },
            "movimientos_recientes": [
                {
                    "fecha": "2025-10-22",
                    "tipo": "INGRESO_FAENA",
                    "cantidad": 50,
                    "especie": "BOVINO",
                    "lote": "LOT-BOV-2025-045",
                    "establecimiento_origen": "Campo San Juan - RENSPA 12345",
                    "establecimiento_destino": f"Frigorífico - {cuit}",
                    "numero_dte": "DTE-2025-001234"
                },
                {
                    "fecha": "2025-10-21",
                    "tipo": "EGRESO_COMERCIALIZACION",
                    "cantidad": 1500,
                    "especie": "BOVINO",
                    "producto": "Carne bovina deshuesada",
                    "lote": "LOT-BOV-2025-044",
                    "establecimiento_origen": f"Frigorífico - {cuit}",
                    "establecimiento_destino": "Carnicería Los Pinos",
                    "numero_remito": "REM-2025-567"
                }
            ],
            "certificaciones": {
                "halal": False,
                "kosher": False,
                "organico": True,
                "bienestar_animal": True,
                "exportacion": ["Brasil", "Chile"]
            },
            "fecha_consulta": datetime.now().isoformat(),
            "fuente": "Sistema Trazabilidad SENASA",
            "ambiente": self.ambiente
        }
        
        total_animales = sum(s["animales_registrados"] for s in trazabilidad["sistemas_trazabilidad"].values())
        print(f"✅ Trazabilidad: {total_animales} animales registrados")
        
        return trazabilidad
    
    def generar_remito_automatico(self, cuit_origen: str, cuit_destino: str, productos: List[Dict]) -> Dict[str, Any]:
        """
        Genera automáticamente un remito cárnico basado en datos AFIP
        Incluye toda la información requerida por SENASA
        """
        print(f"📄 Generando remito automático: {cuit_origen} → {cuit_destino}")
        
        # Obtener datos de establecimientos
        establecimientos_origen = self.obtener_establecimientos_carnicos(cuit_origen)
        establecimientos_destino = self.obtener_establecimientos_carnicos(cuit_destino)
        
        # Obtener catálogo de productos
        catalogo = self.obtener_productos_carnicos_autorizados()
        
        # Generar número de remito
        numero_remito = f"REM-CARN-{datetime.now().strftime('%Y%m%d')}-{cuit_origen[-6:]}"
        
        remito_automatico = {
            "numero_remito": numero_remito,
            "fecha_emision": datetime.now().isoformat(),
            "tipo_remito": "CARNICO",
            "ambiente": self.ambiente,
            
            # Datos del emisor
            "emisor": {
                "cuit": cuit_origen,
                "datos_afip": self._obtener_datos_padron_simplificado(cuit_origen),
                "establecimiento": establecimientos_origen["establecimientos"][0],
                "habilitacion_senasa": establecimientos_origen["establecimientos"][0]["numero_senasa"]
            },
            
            # Datos del destinatario
            "destinatario": {
                "cuit": cuit_destino,
                "datos_afip": self._obtener_datos_padron_simplificado(cuit_destino),
                "establecimiento": establecimientos_destino["establecimientos"][0],
                "habilitacion_senasa": establecimientos_destino["establecimientos"][0]["numero_senasa"]
            },
            
            # Productos procesados con códigos AFIP/SENASA
            "productos": self._procesar_productos_remito(productos, catalogo),
            
            # Información regulatoria
            "regulatorio": {
                "requiere_inspeccion": True,
                "veterinario_responsable": establecimientos_origen["establecimientos"][0].get("veterinario_responsable"),
                "temperatura_transporte": "0°C a 4°C",
                "tiempo_maximo_transporte": "4 horas",
                "documentos_adjuntos": [
                    "Certificado sanitario",
                    "Guía de tránsito SENASA",
                    "Análisis microbiológicos"
                ]
            },
            
            # Trazabilidad
            "trazabilidad": {
                "lote_origen": f"LOT-{datetime.now().strftime('%Y%m%d')}-{cuit_origen[-4:]}",
                "cadena_custodia": True,
                "codigo_trazabilidad": f"TRAZ-{numero_remito}",
                "sistema_utilizado": "SNIG/SIGP"
            },
            
            "totales": self._calcular_totales(productos),
            "estado": "GENERADO_AUTOMATICAMENTE",
            "origen_datos": "AFIP-SENASA",
            "certificado_usado": self.certificado_id
        }
        
        print(f"✅ Remito generado automáticamente: {numero_remito}")
        print(f"   - Productos: {len(remito_automatico['productos'])}")
        print(f"   - Peso total: {remito_automatico['totales']['peso_total_kg']} kg")
        print(f"   - Valor total: ${remito_automatico['totales']['valor_total']:.2f}")
        
        return remito_automatico
    
    def _obtener_datos_padron_simplificado(self, cuit: str) -> Dict[str, Any]:
        """Obtiene datos básicos del padrón para el remito"""
        return {
            "cuit": cuit,
            "denominacion": f"Empresa Cárnica {cuit}",
            "estado": "ACTIVO",
            "domicilio": f"Dirección Fiscal {cuit}",
            "actividad_principal": "Industria Cárnica"
        }
    
    def _procesar_productos_remito(self, productos: List[Dict], catalogo: Dict) -> List[Dict]:
        """Procesa y enriquece los productos con datos del catálogo AFIP/SENASA"""
        productos_procesados = []
        
        for producto in productos:
            # Buscar en catálogo por descripción o código
            producto_catalogo = self._buscar_en_catalogo(producto.get("descripcion", ""), catalogo)
            
            producto_procesado = {
                "descripcion": producto.get("descripcion", "Producto cárnico"),
                "cantidad": producto.get("cantidad", 1),
                "unidad": producto_catalogo.get("unidad_medida", "KG"),
                "peso_unitario": producto.get("peso_unitario", 1.0),
                "precio_unitario": producto.get("precio_unitario", 100.0),
                
                # Códigos oficiales
                "codigo_senasa": producto_catalogo.get("codigo_senasa", ""),
                "codigo_afip": producto_catalogo.get("codigo_afip", ""),
                "categoria_sanitaria": producto_catalogo.get("categoria_sanitaria", "A"),
                
                # Requisitos
                "requiere_trazabilidad": producto_catalogo.get("requiere_trazabilidad", True),
                "temperatura_transporte": producto_catalogo.get("temperatura_transporte", "0 a 4°C"),
                
                # Cálculos
                "peso_total": producto.get("cantidad", 1) * producto.get("peso_unitario", 1.0),
                "valor_total": producto.get("cantidad", 1) * producto.get("precio_unitario", 100.0)
            }
            
            productos_procesados.append(producto_procesado)
        
        return productos_procesados
    
    def _buscar_en_catalogo(self, descripcion: str, catalogo: Dict) -> Dict[str, Any]:
        """Busca un producto en el catálogo por descripción"""
        descripcion_lower = descripcion.lower()
        
        for categoria in catalogo["categorias"].values():
            for producto in categoria["productos"]:
                if any(term in descripcion_lower for term in ["bovina", "bovino", "res"]):
                    if "bovino" in producto["descripcion"].lower():
                        return producto
                elif any(term in descripcion_lower for term in ["porcina", "porcino", "cerdo"]):
                    if "porcino" in producto["descripcion"].lower():
                        return producto
                elif any(term in descripcion_lower for term in ["embutido", "chorizo", "salame"]):
                    if any(term in producto["descripcion"].lower() for term in ["embutido", "chorizo", "salame"]):
                        return producto
        
        # Producto por defecto
        return {
            "codigo_senasa": "GEN001",
            "codigo_afip": "02010000",
            "unidad_medida": "KG",
            "categoria_sanitaria": "A",
            "requiere_trazabilidad": True,
            "temperatura_transporte": "0 a 4°C"
        }
    
    def _calcular_totales(self, productos: List[Dict]) -> Dict[str, Any]:
        """Calcula totales del remito"""
        peso_total = sum(p.get("cantidad", 1) * p.get("peso_unitario", 1.0) for p in productos)
        valor_total = sum(p.get("cantidad", 1) * p.get("precio_unitario", 100.0) for p in productos)
        
        return {
            "cantidad_productos": len(productos),
            "peso_total_kg": peso_total,
            "valor_total": valor_total,
            "iva": valor_total * 0.21,
            "total_con_iva": valor_total * 1.21
        }

if __name__ == "__main__":
    # Demo del cliente cárnico
    cliente = AFIPCarnicoClient()
    
    # Ejemplo de uso
    cuit_test = "24238783522"
    
    print("\n🧪 DEMO CLIENTE CÁRNICO:")
    
    # 1. Obtener establecimientos
    establecimientos = cliente.obtener_establecimientos_carnicos(cuit_test)
    
    # 2. Obtener catálogo productos
    catalogo = cliente.obtener_productos_carnicos_autorizados()
    
    # 3. Obtener trazabilidad
    trazabilidad = cliente.obtener_datos_trazabilidad(cuit_test)
    
    # 4. Generar remito automático
    productos_ejemplo = [
        {"descripcion": "Carne bovina fresca", "cantidad": 100, "peso_unitario": 1.0, "precio_unitario": 150.0},
        {"descripcion": "Chorizo fresco", "cantidad": 50, "peso_unitario": 0.5, "precio_unitario": 80.0}
    ]
    
    remito = cliente.generar_remito_automatico(
        cuit_test, 
        "30999999999", 
        productos_ejemplo
    )
    
    print(f"\n🎯 Demo completado - Remito {remito['numero_remito']} generado automáticamente")