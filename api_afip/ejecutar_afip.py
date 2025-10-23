#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema AFIP - Ejecutable Principal
Obtiene tickets de acceso para servicios AFIP específicos

Servicios soportados:
- wslsp: Web Service de Liquidación Sector Pecuario
- mtxca: Factura Electrónica Web Service
- remcarneservice: Webservice Remitos Electrónicos Cárnicos
"""

import sys
import argparse
from afip_client import AFIPServiceClient
from config_afip import *

def verificar_conectividad(ambiente="testing"):
    """
    Verifica conectividad con servicios AFIP
    
    Args:
        ambiente (str): testing o production
    """
    try:
        print(f"\n🌐 VERIFICANDO CONECTIVIDAD AFIP")
        print("=" * 50)
        
        # Crear cliente para verificación
        cliente = AFIPServiceClient(CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, ambiente)
        
        # Verificar WSAA
        if cliente.verificar_conectividad_wsaa():
            print(f"✅ Conectividad con WSAA: OK")
            return True
        else:
            print(f"❌ Sin conectividad con WSAA")
            return False
        
    except Exception as e:
        print(f"❌ Error verificando conectividad: {e}")
        return False

def obtener_ticket_servicio(servicio, ambiente="testing"):
    """
    Obtiene ticket para un servicio específico
    
    Args:
        servicio (str): Código del servicio
        ambiente (str): testing o production
    """
    try:
        print(f"\n🎫 OBTENIENDO TICKET PARA: {servicio.upper()}")
        print("=" * 50)
        
        # Crear cliente
        cliente = AFIPServiceClient(CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, ambiente)
        
        # Obtener ticket
        ticket = cliente.obtener_ticket_acceso(servicio)
        
        print(f"\n✅ TICKET OBTENIDO EXITOSAMENTE")
        print(f"🎫 Servicio: {ticket['service']}")
        print(f"📝 Nombre: {ticket['service_name']}")
        print(f"⏰ Válido hasta: {ticket['expiration']}")
        print(f"💾 Guardado en: ticket_{servicio}_{ambiente}.json")
        
        return ticket
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def obtener_todos_tickets(ambiente="testing"):
    """Obtiene tickets para todos los servicios configurados"""
    
    print(f"\n🚀 OBTENIENDO TICKETS PARA TODOS LOS SERVICIOS")
    print(f"🌐 Ambiente: {ambiente}")
    print("=" * 60)
    
    try:
        cliente = AFIPServiceClient(CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP, ambiente)
        tickets = cliente.obtener_tickets_todos_servicios()
        
        # Resumen
        exitosos = sum(1 for t in tickets.values() if t is not None)
        total = len(tickets)
        
        print(f"\n📊 RESUMEN: {exitosos}/{total} tickets obtenidos exitosamente")
        
        return tickets
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def mostrar_servicios():
    """Muestra información de servicios disponibles"""
    
    try:
        # Solo crear cliente para mostrar info (sin validar certificados)
        from afip_client import AFIPServiceClient
        cliente = AFIPServiceClient.__new__(AFIPServiceClient)
        cliente.SERVICIOS = AFIPServiceClient.SERVICIOS
        cliente.mostrar_servicios_disponibles()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_configuracion():
    """Verifica que la configuración esté correcta"""
    
    print("\n🔍 VERIFICANDO CONFIGURACIÓN")
    print("=" * 40)
    
    import os
    
    # Verificar archivos
    archivos = [CERTIFICADO_AFIP, CLAVE_PRIVADA_AFIP]
    todo_ok = True
    
    for archivo in archivos:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"✅ {archivo} ({size} bytes)")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            todo_ok = False
    
    # Verificar OpenSSL
    try:
        import subprocess
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSSL: {result.stdout.strip()}")
        else:
            print("❌ OpenSSL: Error al ejecutar")
            todo_ok = False
    except FileNotFoundError:
        print("❌ OpenSSL: No encontrado en PATH")
        todo_ok = False
    
    # Verificar configuración
    print(f"\n📋 CONFIGURACIÓN ACTUAL:")
    print(f"   🌐 Ambiente: {AMBIENTE}")
    print(f"   ⏰ Validez tickets: {HORAS_VALIDEZ_TICKET} horas")
    print(f"   📋 Servicios activos: {', '.join(SERVICIOS_ACTIVOS)}")
    
    if todo_ok:
        print(f"\n🎉 ¡Configuración correcta!")
    else:
        print(f"\n❌ Configuración incompleta")
        print(f"\n📋 INSTRUCCIONES:")
        print(f"1. Coloca tu certificado AFIP como '{CERTIFICADO_AFIP}'")
        print(f"2. Coloca tu clave privada como '{CLAVE_PRIVADA_AFIP}'")
        print(f"3. Instala OpenSSL si no está disponible")
    
    return todo_ok

def main():
    """Función principal"""
    
    parser = argparse.ArgumentParser(
        description='Cliente AFIP - Obtener tickets de acceso',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos de uso:
  python ejecutar_afip.py --verificar          # Verificar configuración
  python ejecutar_afip.py --conectividad       # Verificar conectividad WSAA
  python ejecutar_afip.py --servicios          # Mostrar servicios disponibles  
  python ejecutar_afip.py --servicio wslsp     # Obtener ticket para wslsp
  python ejecutar_afip.py --todos              # Obtener todos los tickets
  python ejecutar_afip.py --servicio mtxca --produccion  # Usar ambiente producción
        '''
    )
    
    parser.add_argument('--verificar', action='store_true',
                       help='Verificar configuración del sistema')
    
    parser.add_argument('--conectividad', action='store_true',
                       help='Verificar conectividad con servicios AFIP')
    
    parser.add_argument('--servicios', action='store_true',
                       help='Mostrar servicios AFIP disponibles')
    
    parser.add_argument('--servicio', type=str,
                       choices=['wslsp', 'mtxca', 'remcarneservice'],
                       help='Obtener ticket para servicio específico')
    
    parser.add_argument('--todos', action='store_true',
                       help='Obtener tickets para todos los servicios')
    
    parser.add_argument('--produccion', action='store_true',
                       help='Usar ambiente de producción (default: testing)')
    
    args = parser.parse_args()
    
    # Determinar ambiente
    ambiente = "production" if args.produccion else "testing"
    
    print("🇦🇷 SISTEMA AFIP - CLIENTE DEFINITIVO")
    print("=" * 50)
    
    # Ejecutar acción solicitada
    if args.verificar:
        verificar_configuracion()
        
    elif args.conectividad:
        verificar_conectividad(ambiente)
        
    elif args.servicios:
        mostrar_servicios()
        
    elif args.servicio:
        obtener_ticket_servicio(args.servicio, ambiente)
        
    elif args.todos:
        obtener_todos_tickets(ambiente)
        
    else:
        # Sin argumentos, mostrar ayuda
        parser.print_help()
        print(f"\n💡 Sugerencia: Comienza con --verificar para validar tu configuración")

if __name__ == "__main__":
    main()