"""
Modelo base para remitos
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from database import Base

class Remito(Base):
    """Modelo para la tabla de remitos"""
    __tablename__ = "remitos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_remito = Column(String(50), unique=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_emision = Column(DateTime(timezone=True))
    
    # Datos del emisor
    emisor_cuit = Column(String(11), nullable=False)
    emisor_razon_social = Column(String(200), nullable=False)
    emisor_domicilio = Column(Text)
    
    # Datos del receptor
    receptor_cuit = Column(String(11), nullable=False)
    receptor_razon_social = Column(String(200), nullable=False)
    receptor_domicilio = Column(Text)
    
    # Datos del transporte
    transporte_cuit = Column(String(11))
    transporte_razon_social = Column(String(200))
    patente_vehiculo = Column(String(20))
    
    # Estado del remito
    estado = Column(String(20), default="borrador")  # borrador, enviado, autorizado, rechazado
    cae = Column(String(14))  # Código de Autorización Electrónico
    fecha_vencimiento_cae = Column(DateTime(timezone=True))
    
    # Totales
    peso_total = Column(Float)
    cantidad_total = Column(Float)
    
    # Observaciones
    observaciones = Column(Text)
    
    def __repr__(self):
        return f"<Remito(numero={self.numero_remito}, estado={self.estado})>"