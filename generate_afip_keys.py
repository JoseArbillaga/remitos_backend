#!/usr/bin/env python3
"""
Script para generar claves RSA para AFIP usando cryptography
Certificado: sgpatagon25_23ad6985d1bcb772
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_rsa_key_pair():
    """Genera un par de claves RSA de 2048 bits"""
    
    print("🔐 Generando par de claves RSA de 2048 bits...")
    
    # Generar clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Serializar clave privada en formato PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Obtener clave pública
    public_key = private_key.public_key()
    
    # Serializar clave pública en formato PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

def save_keys():
    """Guarda las claves generadas en archivos"""
    
    # Crear directorio si no existe
    os.makedirs("api_afip", exist_ok=True)
    
    # Generar claves
    private_key, public_key = generate_rsa_key_pair()
    
    # Guardar clave privada
    private_key_path = "api_afip/sgpatagon25_private_key.key"
    with open(private_key_path, "wb") as f:
        f.write(private_key)
    
    print(f"✅ Clave privada guardada en: {private_key_path}")
    
    # Guardar clave pública
    public_key_path = "api_afip/sgpatagon25_public_key.pem"
    with open(public_key_path, "wb") as f:
        f.write(public_key)
    
    print(f"✅ Clave pública guardada en: {public_key_path}")
    
    # Mostrar información de las claves
    print(f"""
📋 INFORMACIÓN DE CLAVES GENERADAS:
===================================
Certificado: sgpatagon25_23ad6985d1bcb772
Clave Privada: {private_key_path}
Clave Pública: {public_key_path}
Algoritmo: RSA 2048 bits
Formato: PEM
===================================
""")
    
    return private_key_path, public_key_path

if __name__ == "__main__":
    print("""
🚀 GENERADOR DE CLAVES AFIP
===========================
Certificado: sgpatagon25_23ad6985d1bcb772
Entorno: Testing
===========================
""")
    
    try:
        private_path, public_path = save_keys()
        
        print("✅ ¡Claves generadas exitosamente!")
        print("\n📝 Próximos pasos:")
        print("1. Configurar config_afip.py con las nuevas rutas")
        print("2. Actualizar certificado AFIP (.crt)")
        print("3. Configurar endpoints para testing")
        
    except Exception as e:
        print(f"❌ Error generando claves: {e}")
        import traceback
        traceback.print_exc()