"""
Servicio para integración con AFIP - Remitos Cárnicos
"""
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Agregar el directorio api_afip al path
current_dir = Path(__file__).parent.parent.parent
afip_dir = current_dir / "api_afip"
sys.path.append(str(afip_dir))

# Importar cliente AFIP con manejo de errores
try:
    from afip_client import AFIPServiceClient
    from config_afip import CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, AMBIENTE
except ImportError:
    # Fallback para desarrollo
    AFIPServiceClient = None
    CERTIFICADO_AFIP = "certificado_afip.crt"
    CLAVE_PRIVADA_AFIP = "clave_privada_afip.key"
    AMBIENTE = "testing"

class AFIPRemitoService:
    """Servicio para gestionar remitos cárnicos con AFIP"""
    
    def __init__(self):
        """Inicializar el servicio AFIP"""
        self.ambiente = AMBIENTE
        self.certificado_path = os.path.join(str(afip_dir), CERTIFICADO_AFIP)
        self.clave_privada_path = os.path.join(str(afip_dir), CLAVE_PRIVADA_AFIP)
        
        # Verificar si AFIP está disponible
        if AFIPServiceClient is None:
            print("⚠️  AFIP Client no disponible - funcionando en modo simulación")
            self.afip_disponible = False
            self.cliente_afip = None
        else:
            self.afip_disponible = True
        
        # Solo inicializar cliente si los certificados existen
        self.cliente_afip = None
        self._verificar_certificados()
    
    def _verificar_certificados(self):
        """Verificar que existan los certificados necesarios"""
        if os.path.exists(self.certificado_path) and os.path.exists(self.clave_privada_path):
            try:
                self.cliente_afip = AFIPServiceClient(
                    self.certificado_path, 
                    self.clave_privada_path, 
                    self.ambiente
                )
                print(f"✅ Cliente AFIP inicializado correctamente")
                return True
            except Exception as e:
                print(f"❌ Error inicializando cliente AFIP: {e}")
                return False
        else:
            print(f"⚠️  Certificados AFIP no encontrados:")
            print(f"   Certificado: {self.certificado_path}")
            print(f"   Clave privada: {self.clave_privada_path}")
            return False
    
    def verificar_conectividad(self) -> bool:
        """Verificar conectividad con AFIP"""
        if not self.cliente_afip:
            return False
        
        try:
            return self.cliente_afip.verificar_conectividad_wsaa()
        except Exception as e:
            print(f"Error verificando conectividad: {e}")
            return False
    
    def obtener_ticket_remcarne(self) -> Optional[Dict[str, Any]]:
        """Obtener ticket de acceso para remcarneservice"""
        if not self.cliente_afip:
            return None
        
        try:
            return self.cliente_afip.obtener_ticket_acceso("remcarneservice")
        except Exception as e:
            print(f"Error obteniendo ticket remcarne: {e}")
            return None
    
    def generar_remito_electronico(self, remito_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar remito electrónico en AFIP
        
        Args:
            remito_data: Datos del remito a enviar a AFIP
            
        Returns:
            Dict con respuesta de AFIP (CAE, fecha vencimiento, etc.)
        """
        if not self.cliente_afip:
            return {
                "success": False,
                "error": "Cliente AFIP no disponible - verificar certificados",
                "codigo": "CERT_ERROR"
            }
        
        try:
            # Obtener ticket para remcarneservice
            ticket = self.obtener_ticket_remcarne()
            if not ticket:
                return {
                    "success": False,
                    "error": "No se pudo obtener ticket de acceso",
                    "codigo": "TICKET_ERROR"
                }
            
            # Preparar datos para AFIP según especificación
            datos_afip = self._preparar_datos_afip(remito_data)
            
            # Simular envío a AFIP (aquí iría la llamada real al servicio)
            # Por ahora retornamos un resultado simulado
            return self._simular_respuesta_afip(remito_data)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error procesando remito: {str(e)}",
                "codigo": "PROCESS_ERROR"
            }
    
    def _preparar_datos_afip(self, remito_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar datos según especificación de AFIP"""
        return {
            "numero_remito": remito_data.get("numero_remito"),
            "fecha_emision": remito_data.get("fecha_emision"),
            "cuit_emisor": remito_data.get("emisor_cuit"),
            "cuit_receptor": remito_data.get("receptor_cuit"),
            "cuit_transporte": remito_data.get("transporte_cuit"),
            "patente": remito_data.get("patente_vehiculo"),
            "peso_total": remito_data.get("peso_total"),
            "observaciones": remito_data.get("observaciones")
        }
    
    def _simular_respuesta_afip(self, remito_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simular respuesta de AFIP para testing"""
        import random
        import string
        
        # Generar CAE simulado (14 dígitos)
        cae = ''.join([str(random.randint(0, 9)) for _ in range(14)])
        
        # Fecha de vencimiento (10 días desde hoy)
        from datetime import datetime, timedelta
        fecha_vencimiento = datetime.now() + timedelta(days=10)
        
        return {
            "success": True,
            "cae": cae,
            "fecha_vencimiento_cae": fecha_vencimiento.isoformat(),
            "numero_comprobante": remito_data.get("numero_remito"),
            "fecha_proceso": datetime.now().isoformat(),
            "mensaje": "Remito autorizado correctamente (SIMULADO)",
            "ambiente": self.ambiente
        }
    
    def consultar_estado_remito(self, numero_remito: str, cae: str) -> Dict[str, Any]:
        """Consultar estado de un remito en AFIP"""
        if not self.cliente_afip:
            return {
                "success": False,
                "error": "Cliente AFIP no disponible"
            }
        
        # Implementar consulta real a AFIP
        return {
            "success": True,
            "estado": "autorizado",
            "numero_remito": numero_remito,
            "cae": cae,
            "mensaje": "Consulta simulada - remito válido"
        }
    
    def obtener_status_servicio(self) -> Dict[str, Any]:
        """Obtener status del servicio AFIP"""
        return {
            "certificados_disponibles": self.cliente_afip is not None,
            "ambiente": self.ambiente,
            "certificado_path": self.certificado_path,
            "clave_privada_path": self.clave_privada_path,
            "conectividad": self.verificar_conectividad() if self.cliente_afip else False
        }