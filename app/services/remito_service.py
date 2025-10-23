"""
Servicio para lógica de negocio de remitos
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.remito import Remito
from app.schemas.remito import RemitoCreate, RemitoUpdate
from app.services.afip_service import AFIPRemitoService

class RemitoService:
    """Servicio para gestión de remitos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.afip_service = AFIPRemitoService()
    
    def crear_remito(self, remito_data: RemitoCreate) -> Remito:
        """Crear un nuevo remito"""
        remito = Remito(**remito_data.model_dump())
        self.db.add(remito)
        self.db.commit()
        self.db.refresh(remito)
        return remito
    
    def obtener_remitos(self, skip: int = 0, limit: int = 100) -> List[Remito]:
        """Obtener lista de remitos con paginación"""
        return self.db.query(Remito).offset(skip).limit(limit).all()
    
    def obtener_remito_por_id(self, remito_id: int) -> Optional[Remito]:
        """Obtener un remito por su ID"""
        return self.db.query(Remito).filter(Remito.id == remito_id).first()
    
    def obtener_remito_por_numero(self, numero_remito: str) -> Optional[Remito]:
        """Obtener un remito por su número"""
        return self.db.query(Remito).filter(Remito.numero_remito == numero_remito).first()
    
    def actualizar_remito(self, remito_id: int, remito_data: RemitoUpdate) -> Optional[Remito]:
        """Actualizar un remito existente"""
        remito = self.obtener_remito_por_id(remito_id)
        if not remito:
            return None
        
        update_data = remito_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(remito, field, value)
        
        self.db.commit()
        self.db.refresh(remito)
        return remito
    
    def eliminar_remito(self, remito_id: int) -> bool:
        """Eliminar un remito"""
        remito = self.obtener_remito_por_id(remito_id)
        if not remito:
            return False
        
        self.db.delete(remito)
        self.db.commit()
        return True
    
    def obtener_remitos_por_estado(self, estado: str) -> List[Remito]:
        """Obtener remitos filtrados por estado"""
        return self.db.query(Remito).filter(Remito.estado == estado).all()
    
    def obtener_remitos_por_cuit(self, cuit: str, skip: int = 0, limit: int = 100) -> List[Remito]:
        """Obtener remitos filtrados por CUIT del emisor"""
        return self.db.query(Remito).filter(
            Remito.emisor_cuit == cuit
        ).offset(skip).limit(limit).all()
    
    def enviar_remito_afip(self, remito_id: int) -> Dict[str, Any]:
        """Enviar remito a AFIP para autorización"""
        # Obtener el remito
        remito = self.obtener_remito_por_id(remito_id)
        if not remito:
            return {
                "success": False,
                "error": "Remito no encontrado",
                "codigo": "REMITO_NOT_FOUND"
            }
        
        # Verificar que esté en estado borrador
        if remito.estado != "borrador":
            return {
                "success": False,
                "error": f"El remito debe estar en estado borrador (actual: {remito.estado})",
                "codigo": "INVALID_STATE"
            }
        
        # Preparar datos para AFIP
        remito_data = {
            "numero_remito": remito.numero_remito,
            "fecha_emision": remito.fecha_emision.isoformat() if remito.fecha_emision else None,
            "emisor_cuit": remito.emisor_cuit,
            "emisor_razon_social": remito.emisor_razon_social,
            "receptor_cuit": remito.receptor_cuit,
            "receptor_razon_social": remito.receptor_razon_social,
            "transporte_cuit": remito.transporte_cuit,
            "patente_vehiculo": remito.patente_vehiculo,
            "peso_total": remito.peso_total,
            "observaciones": remito.observaciones
        }
        
        # Enviar a AFIP
        resultado_afip = self.afip_service.generar_remito_electronico(remito_data)
        
        if resultado_afip.get("success"):
            # Actualizar remito con datos de AFIP
            remito.estado = "autorizado"
            remito.cae = resultado_afip.get("cae")
            if resultado_afip.get("fecha_vencimiento_cae"):
                from datetime import datetime
                remito.fecha_vencimiento_cae = datetime.fromisoformat(
                    resultado_afip["fecha_vencimiento_cae"].replace('Z', '+00:00')
                )
            
            self.db.commit()
            self.db.refresh(remito)
            
            return {
                "success": True,
                "remito": remito,
                "cae": resultado_afip.get("cae"),
                "fecha_vencimiento": resultado_afip.get("fecha_vencimiento_cae"),
                "mensaje": "Remito enviado y autorizado por AFIP correctamente"
            }
        else:
            # Marcar como rechazado si AFIP rechazó
            remito.estado = "rechazado"
            self.db.commit()
            
            return resultado_afip
    
    def consultar_estado_afip(self, remito_id: int) -> Dict[str, Any]:
        """Consultar estado del remito en AFIP"""
        remito = self.obtener_remito_por_id(remito_id)
        if not remito:
            return {
                "success": False,
                "error": "Remito no encontrado"
            }
        
        if not remito.cae:
            return {
                "success": False,
                "error": "El remito no tiene CAE asignado"
            }
        
        return self.afip_service.consultar_estado_remito(
            remito.numero_remito, 
            remito.cae
        )
    
    def obtener_status_afip(self) -> Dict[str, Any]:
        """Obtener status del servicio AFIP"""
        return self.afip_service.obtener_status_servicio()