"""
Esquemas Pydantic para validación de remitos con validaciones AFIP
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from app.utils.afip_validators import (
    validar_cuit, validar_formato_remito, validar_patente_argentina,
    validar_peso_carnico, validar_razon_social, validar_observaciones_afip
)

class RemitoBase(BaseModel):
    """Esquema base para remito con validaciones AFIP"""
    numero_remito: str = Field(..., min_length=1, max_length=50)
    fecha_emision: datetime
    
    # Datos del emisor
    emisor_cuit: str = Field(..., min_length=11, max_length=11)
    emisor_razon_social: str = Field(..., min_length=1, max_length=200)
    emisor_domicilio: Optional[str] = None
    
    # Datos del receptor
    receptor_cuit: str = Field(..., min_length=11, max_length=11)
    receptor_razon_social: str = Field(..., min_length=1, max_length=200)
    receptor_domicilio: Optional[str] = None
    
    # Datos del transporte
    transporte_cuit: Optional[str] = Field(None, min_length=11, max_length=11)
    transporte_razon_social: Optional[str] = Field(None, max_length=200)
    patente_vehiculo: Optional[str] = Field(None, max_length=20)
    
    # Totales
    peso_total: Optional[float] = Field(None, ge=0.1, le=50000)
    cantidad_total: Optional[float] = Field(None, ge=0)
    
    # Observaciones
    observaciones: Optional[str] = Field(None, max_length=1000)
    
    @validator('emisor_cuit')
    def validar_emisor_cuit(cls, v):
        if not validar_cuit(v):
            raise ValueError('CUIT del emisor inválido')
        return v
    
    @validator('receptor_cuit')
    def validar_receptor_cuit(cls, v):
        if not validar_cuit(v):
            raise ValueError('CUIT del receptor inválido')
        return v
    
    @validator('transporte_cuit')
    def validar_transporte_cuit(cls, v):
        if v and not validar_cuit(v):
            raise ValueError('CUIT del transporte inválido')
        return v
    
    @validator('numero_remito')
    def validar_numero_remito(cls, v):
        if not validar_formato_remito(v):
            raise ValueError('Formato de número de remito inválido (debe ser R-XXXXXXXX)')
        return v
    
    @validator('patente_vehiculo')
    def validar_patente(cls, v):
        if v and not validar_patente_argentina(v):
            raise ValueError('Formato de patente inválido')
        return v.upper() if v else v
    
    @validator('peso_total')
    def validar_peso(cls, v):
        if v is not None and not validar_peso_carnico(v):
            raise ValueError('Peso inválido (debe ser entre 0.1 y 50000 kg)')
        return v
    
    @validator('emisor_razon_social')
    def validar_emisor_razon_social(cls, v):
        if not validar_razon_social(v):
            raise ValueError('Razón social del emisor inválida')
        return v.strip().title()
    
    @validator('receptor_razon_social')
    def validar_receptor_razon_social(cls, v):
        if not validar_razon_social(v):
            raise ValueError('Razón social del receptor inválida')
        return v.strip().title()
    
    @validator('observaciones')
    def validar_observaciones(cls, v):
        if v and not validar_observaciones_afip(v):
            raise ValueError('Observaciones inválidas (máximo 1000 caracteres, sin caracteres especiales)')
        return v

class RemitoCreate(RemitoBase):
    """Esquema para crear un remito"""
    pass

class RemitoUpdate(BaseModel):
    """Esquema para actualizar un remito"""
    numero_remito: Optional[str] = Field(None, min_length=1, max_length=50)
    fecha_emision: Optional[datetime] = None
    emisor_cuit: Optional[str] = Field(None, min_length=11, max_length=11)
    emisor_razon_social: Optional[str] = Field(None, min_length=1, max_length=200)
    emisor_domicilio: Optional[str] = None
    receptor_cuit: Optional[str] = Field(None, min_length=11, max_length=11)
    receptor_razon_social: Optional[str] = Field(None, min_length=1, max_length=200)
    receptor_domicilio: Optional[str] = None
    transporte_cuit: Optional[str] = Field(None, min_length=11, max_length=11)
    transporte_razon_social: Optional[str] = Field(None, max_length=200)
    patente_vehiculo: Optional[str] = Field(None, max_length=20)
    peso_total: Optional[float] = Field(None, ge=0)
    cantidad_total: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = None

class RemitoResponse(RemitoBase):
    """Esquema para respuesta de remito"""
    id: int
    fecha_creacion: datetime
    estado: str
    cae: Optional[str] = None
    fecha_vencimiento_cae: Optional[datetime] = None
    
    class Config:
        from_attributes = True