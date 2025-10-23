# Sistema AFIP - Cliente definitivo para servicios WSAA
# Conecta con: wslsp, mtxca, remcarneservice
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import uuid
import base64
import subprocess
import os
import requests
from pathlib import Path

class AFIPServiceClient:
    """Cliente definitivo para servicios AFIP con autenticación WSAA"""
    
    # Servicios AFIP disponibles
    SERVICIOS = {
        'wslsp': {
            'nombre': 'Web Service de Liquidación Sector Pecuario',
            'descripcion': 'Liquidación y facturación sector pecuario',
            'testing_url': 'https://wswhomo.afip.gov.ar/wslsp/LspService',
            'production_url': 'https://serviciosjava.afip.gob.ar/wslsp/LspService'
        },
        'mtxca': {
            'nombre': 'Factura Electrónica Web Service',
            'descripcion': 'Comprobantes electrónicos monotributo',
            'testing_url': 'https://wswhomo.afip.gov.ar/wsmtxca/services/MTXCAService',
            'production_url': 'https://serviciosjava.afip.gob.ar/wsmtxca/services/MTXCAService'
        },
        'remcarneservice': {
            'nombre': 'Webservice Remitos Electrónicos Cárnicos',
            'descripcion': 'Remitos de carnes y subproductos derivados de faena',
            'testing_url': 'https://wswhomo.afip.gov.ar/remcarne/RemCarneService',
            'production_url': 'https://serviciosjava.afip.gob.ar/remcarne/RemCarneService'
        }
    }
    
    def __init__(self, certificado_path, clave_privada_path, ambiente="testing"):
        """
        Inicializar cliente AFIP
        
        Args:
            certificado_path (str): Ruta al certificado AFIP (.crt)
            clave_privada_path (str): Ruta a la clave privada (.key)
            ambiente (str): "testing" o "production"
        """
        self.certificado_path = certificado_path
        self.clave_privada_path = clave_privada_path
        self.ambiente = ambiente
        
        # URLs WSAA para autenticación según especificación oficial AFIP
        self.wsaa_urls = {
            # Entorno de Testing (Homologación)
            "testing": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms",
            # Entorno de Producción  
            "production": "https://wsaa.afip.gov.ar/ws/services/LoginCms"
        }
        
        # URLs WSDL para referencia (no usadas en implementación actual)
        self.wsaa_wsdl_urls = {
            "testing": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl",
            "production": "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
        }
        
        # Validar archivos
        self._validar_certificados()
        
        # Cache de tickets
        self.tickets_cache = {}
    
    def _validar_certificados(self):
        """Valida que existan los archivos de certificado y clave"""
        if not os.path.exists(self.certificado_path):
            raise FileNotFoundError(f"Certificado no encontrado: {self.certificado_path}")
        if not os.path.exists(self.clave_privada_path):
            raise FileNotFoundError(f"Clave privada no encontrada: {self.clave_privada_path}")
        
        print(f"✅ Certificado encontrado: {self.certificado_path}")
        print(f"✅ Clave privada encontrada: {self.clave_privada_path}")
    
    def _extraer_subject_dn(self):
        """
        Extrae el Distinguished Name (DN) del subject del certificado
        
        Returns:
            str: DN del certificado o None si hay error
        """
        try:
            cmd = [
                "openssl", "x509", "-in", self.certificado_path,
                "-subject", "-noout", "-nameopt", "RFC2253"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # El output es "subject=CN=..." -> extraer solo la parte después del =
            if result.stdout.startswith("subject="):
                dn = result.stdout[8:].strip()  # Quitar "subject=" del inicio
                print(f"   📜 DN extraído del certificado: {dn}")
                return dn
            else:
                print(f"   ⚠️  Formato inesperado del subject: {result.stdout}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Error extrayendo DN del certificado: {e.stderr}")
            return None
        except Exception as e:
            print(f"   ⚠️  Error procesando certificado: {e}")
            return None
    
    def _manejar_error_soap(self, error_code, error_description):
        """
        Maneja errores SOAP según especificación AFIP
        Retorna True si se debe reintentar después de 60 segundos
        """
        print(f"❌ ERROR SOAP AFIP: {error_code}")
        print(f"📄 Descripción: {error_description}")
        
        # Errores que NO requieren reintento
        errores_sin_reintento = [
            'coe.notAuthorized',
            'coe.alreadyAuthenticated',
            'cms.cert.expired',
            'cms.cert.invalid',
            'cms.cert.untrusted',
            'xml.source.invalid',
            'xml.destination.invalid',
            'xml.version.notSupported',
            'wsn.notFound'
        ]
        
        if error_code in errores_sin_reintento:
            print("🚫 Este error requiere corrección manual. NO reintentar automáticamente.")
            return False
        
        # Errores que requieren espera de 60 segundos
        errores_con_espera = [
            'cms.bad',
            'cms.bad.base64',
            'cms.cert.notFound',
            'cms.sign.invalid',
            'xml.bad',
            'xml.generationTime.invalid',
            'xml.expirationTime.expired',
            'xml.expirationTime.invalid',
            'wsn.unavailable',
            'wsaa.unavailable',
            'wsaa.internalError'
        ]
        
        if error_code in errores_con_espera:
            print("⏱️ Error temporal. Esperar 60 segundos antes de reintentar.")
            return True
        
        print("⚠️ Código de error no reconocido. Verificar especificación AFIP.")
        return True
    
    def verificar_conectividad_wsaa(self):
        """
        Verifica conectividad con el servicio WSAA
        
        Returns:
            bool: True si hay conectividad, False en caso contrario
        """
        url = self.wsaa_urls[self.ambiente]
        wsdl_url = self.wsaa_wsdl_urls[self.ambiente]
        
        print(f"🌐 Verificando conectividad WSAA - Ambiente: {self.ambiente}")
        print(f"📡 URL: {url}")
        print(f"📄 WSDL: {wsdl_url}")
        
        try:
            # Verificar conectividad básica al WSDL
            response = requests.get(wsdl_url, timeout=10, verify=True)
            
            if response.status_code == 200:
                print(f"✅ Conectividad WSAA: OK")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                # Verificar que sea un WSDL válido
                if 'xml' in response.headers.get('content-type', '').lower():
                    if 'wsdl' in response.text.lower() or 'definitions' in response.text.lower():
                        print(f"✅ WSDL válido detectado")
                        return True
                    else:
                        print(f"⚠️  Respuesta XML pero no parece WSDL")
                else:
                    print(f"⚠️  Respuesta no es XML")
                
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout conectando a WSAA (>10s)")
            return False
        except requests.exceptions.SSLError as e:
            print(f"❌ Error SSL/TLS: {e}")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Error de conexión: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
        
        return True
    
    def _validar_respuesta_wsaa(self, xml_response):
        """
        Valida y procesa la respuesta del WSAA según especificación oficial
        
        Args:
            xml_response (str): XML de respuesta del WSAA
            
        Returns:
            dict: Token y sign extraídos, o None si hay error
        """
        try:
            root = ET.fromstring(xml_response)
            
            # Buscar loginTicketResponse
            ticket_response = root.find('.//loginTicketResponse')
            if ticket_response is None:
                print("❌ Respuesta WSAA: No se encontró loginTicketResponse")
                return None
            
            # Extraer header para validaciones
            header = ticket_response.find('header')
            if header is None:
                print("❌ Respuesta WSAA: Header no encontrado")
                return None
            
            # Extraer campos del header
            source = header.find('source')
            destination = header.find('destination')
            unique_id = header.find('uniqueId')
            generation_time = header.find('generationTime')
            expiration_time = header.find('expirationTime')
            
            if None in [source, destination, unique_id, generation_time, expiration_time]:
                print("❌ Respuesta WSAA: Campos obligatorios del header faltantes")
                return None
            
            # Validar fechas
            try:
                gen_time = datetime.fromisoformat(generation_time.text.replace('T', ' ').replace('-03:00', ''))
                exp_time = datetime.fromisoformat(expiration_time.text.replace('T', ' ').replace('-03:00', ''))
                
                ahora = datetime.now()
                
                if exp_time < ahora:
                    print(f"❌ Ticket EXPIRADO. Expiración: {expiration_time.text}")
                    return None
                
                if gen_time > ahora:
                    print(f"❌ Tiempo de generación futuro: {generation_time.text}")
                    return None
                
                print(f"✅ Ticket válido hasta: {expiration_time.text}")
                
            except Exception as e:
                print(f"❌ Error validando fechas del ticket: {e}")
                return None
            
            # Extraer credentials
            credentials = ticket_response.find('credentials')
            if credentials is None:
                print("❌ Respuesta WSAA: Credentials no encontradas")
                return None
            
            token_elem = credentials.find('token')
            sign_elem = credentials.find('sign')
            
            if token_elem is None or sign_elem is None:
                print("❌ Respuesta WSAA: Token o Sign no encontrados")
                return None
            
            token = token_elem.text
            sign = sign_elem.text
            
            if not token or not sign:
                print("❌ Respuesta WSAA: Token o Sign vacíos")
                return None
            
            print(f"✅ Token extraído: {token[:20]}...")
            print(f"✅ Sign extraído: {sign[:20]}...")
            
            return {
                'token': token,
                'sign': sign,
                'expiration': expiration_time.text,
                'generation': generation_time.text,
                'unique_id': unique_id.text
            }
            
        except ET.ParseError as e:
            print(f"❌ Error parseando XML de respuesta: {e}")
            return None
        except Exception as e:
            print(f"❌ Error procesando respuesta WSAA: {e}")
            return None
    
    def generar_tra(self, servicio, horas_validez=12):
        """
        Genera TRA (LoginTicketRequest.xml) según especificación oficial AFIP
        
        Incluye campos source y destination según documentación oficial:
        - source: DN del certificado (opcional pero recomendado)
        - destination: DN del WSAA según ambiente
        - uniqueId: Entero 32 bits sin signo
        - generationTime: Momento de generación (tolerancia: 24h previas)
        - expirationTime: Momento de expiración (tolerancia: 24h posteriores)
        
        Args:
            servicio (str): Código del servicio (wslsp, mtxca, remcarneservice)
            horas_validez (int): Horas de validez del ticket (máx 24h)
            
        Returns:
            tuple: (xml_string, unique_id)
        """
        if servicio not in self.SERVICIOS:
            raise ValueError(f"Servicio no válido. Disponibles: {list(self.SERVICIOS.keys())}")
        
        # Validar servicio según patrón XSD: [a-z,A-Z][a-z,A-Z,\,_,0-9]* (3-32 chars)
        if not (3 <= len(servicio) <= 32):
            raise ValueError(f"Servicio debe tener entre 3 y 32 caracteres")
        
        # Validar tolerancia de 24 horas según especificación AFIP
        if horas_validez > 24:
            print(f"⚠️  Advertencia: Horas de validez ({horas_validez}) excede tolerancia AFIP (24h)")
            horas_validez = 24
        
        # Generar timestamps según especificación AFIP
        ahora = datetime.now()
        expiracion = ahora + timedelta(hours=horas_validez)
        
        # Formato específico AFIP: YYYY-MM-DDTHH:MM:SS-03:00 (sin microsegundos)
        generation_time = ahora.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        expiration_time = expiracion.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        
        # uniqueId: Entero de 32 bits sin signo (junto con generationTime identifica el requerimiento)
        unique_id = int(datetime.now().timestamp() * 1000) % (2**32)  # 32-bit unsigned int
        
        # DN destination según ambiente (especificación oficial AFIP)
        destination_dn = {
            "production": "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239",
            "testing": "cn=wsaahomo,o=afip,c=ar,serialNumber=CUIT 33693450239"
        }
        
        # Extraer información del certificado para source DN
        source_dn = self._extraer_subject_dn()
        
        print(f"📄 Generando TRA según especificación oficial AFIP:")
        print(f"   🎯 Servicio: {servicio}")
        print(f"   🆔 UniqueId: {unique_id}")
        print(f"   📅 Generación: {generation_time}")
        print(f"   ⏰ Expiración: {expiration_time}")
        print(f"   🔗 Source DN: {source_dn}")
        print(f"   🎯 Destination DN: {destination_dn[self.ambiente]}")
        
        # Crear XML TRA según schema oficial
        root = ET.Element("loginTicketRequest")
        root.set("version", "1.0")
        
        # Header (headerType según XSD)
        header = ET.SubElement(root, "header")
        
        # source: Campo opcional - DN del certificado (recomendado incluirlo)
        if source_dn:
            ET.SubElement(header, "source").text = source_dn
        
        # destination: Campo opcional - DN del WSAA según ambiente
        ET.SubElement(header, "destination").text = destination_dn[self.ambiente]
        
        # uniqueId: Campo requerido (minOccurs="1" maxOccurs="1")
        ET.SubElement(header, "uniqueId").text = str(unique_id)
        
        # generationTime y expirationTime: Campos requeridos (dateTime)
        ET.SubElement(header, "generationTime").text = generation_time
        ET.SubElement(header, "expirationTime").text = expiration_time
        
        # Service: Identificación del WSN (campo requerido)
        ET.SubElement(root, "service").text = servicio
        
        # Convertir a string XML
        xml_string = ET.tostring(root, encoding='unicode')
        
        # Formatear XML manteniendo compatibilidad AFIP
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
        
        # Limpiar XML (remover líneas vacías pero mantener estructura)
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines[1:])  # Quitar declaración XML (se agrega al guardar)
        
        return formatted_xml, unique_id
    
    def firmar_tra(self, tra_xml, servicio):
        """
        Paso 2: Generar CMS que contenga el TRA, su firma electrónica y el certificado X.509
        (LoginTicketRequest.xml.cms)
        
        Args:
            tra_xml (str): XML del TRA
            servicio (str): Código del servicio
            
        Returns:
            bytes: CMS firmado en formato DER
        """
        # Nombres de archivos según convención AFIP
        tra_file = f"LoginTicketRequest.xml"
        cms_file = f"LoginTicketRequest.xml.cms"
        
        # Paso 2.1: Escribir TRA con declaración XML UTF-8
        with open(tra_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(tra_xml)
        
        print(f"📄 Paso 2.1: TRA guardado como {tra_file}")
        
        # Paso 2.2: Generar CMS tipo "SignedData" con SHA1+RSA según especificación AFIP
        cmd = [
            "openssl", "cms", "-sign",
            "-in", tra_file,
            "-out", cms_file,
            "-signer", self.certificado_path,      # Certificado X.509
            "-inkey", self.clave_privada_path,     # Clave privada para firma
            "-outform", "DER",                     # Formato binario DER
            "-nodetach",                           # Incluir contenido original
            "-md", "sha1"                          # Usar SHA1 como especifica AFIP
        ]
        
        try:
            print(f"🔐 Paso 2.2: Generando CMS tipo 'SignedData' con SHA1+RSA...")
            print(f"   📜 Certificado: {self.certificado_path}")
            print(f"   🔑 Clave privada: {self.clave_privada_path}")
            print(f"   🔒 Algoritmo: SHA1+RSA (especificación AFIP)")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Verificar que el CMS se generó
            if not os.path.exists(cms_file):
                raise Exception(f"No se generó el archivo CMS: {cms_file}")
            
            # Leer CMS generado
            with open(cms_file, 'rb') as f:
                cms_data = f.read()
            
            print(f"✅ Paso 2.2: CMS tipo 'SignedData' generado exitosamente")
            print(f"   📦 Archivo: {cms_file}")
            print(f"   📊 Tamaño: {len(cms_data)} bytes")
            print(f"   🧬 Contenido: TRA + Firma SHA1+RSA + Certificado X.509")
            
            # Limpiar archivo TRA temporal (mantener CMS para referencia)
            if os.path.exists(tra_file):
                os.remove(tra_file)
            
            return cms_data
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"❌ Error en OpenSSL: {error_msg}")
            
            # Diagnóstico de errores comunes
            if "unable to load certificate" in error_msg.lower():
                print("💡 Diagnóstico: Problema con el certificado")
                print("   - Verifica que el archivo certificado_afip.crt existe")
                print("   - Verifica que el formato sea válido (PEM)")
            elif "unable to load private key" in error_msg.lower():
                print("💡 Diagnóstico: Problema con la clave privada")
                print("   - Verifica que el archivo clave_privada_afip.key exists")
                print("   - Verifica que la clave corresponda al certificado")
            elif "private key does not match" in error_msg.lower():
                print("💡 Diagnóstico: Clave privada no corresponde al certificado")
                print("   - Asegúrate de usar la clave privada correcta")
            
            raise Exception(f"Error al generar CMS: {error_msg}")
            
        except FileNotFoundError:
            print("❌ OpenSSL no encontrado")
            print("💡 Solución: Instala OpenSSL y agrégalo al PATH")
            print("   Descarga: https://slproweb.com/products/Win32OpenSSL.html")
            raise Exception("OpenSSL no disponible")
    
    def obtener_ticket_acceso(self, servicio):
        """
        FLUJO PRINCIPAL AFIP - 5 Pasos para obtener TA (Ticket de Acceso)
        
        1. Generar el mensaje del TRA (LoginTicketRequest.xml)
        2. Generar un CMS que contenga el TRA, su firma electrónica y el certificado X.509
        3. Codificar en Base64 el CMS (LoginTicketRequest.xml.cms.base64)
        4. Invocar WSAA con el CMS y recibir LoginTicketResponse.xml
        5. Extraer y validar la información de autorización (TA)
        
        Args:
            servicio (str): Código del servicio
            
        Returns:
            dict: {"token": "...", "sign": "...", "expiration": "...", "service": "..."}
        """
        print(f"\n�🇷 FLUJO PRINCIPAL AFIP - OBTENCIÓN DE TA")
        print(f"📋 Servicio: {servicio} - {self.SERVICIOS[servicio]['nombre']}")
        print(f"🌐 Ambiente: {self.ambiente}")
        print("=" * 70)
        
        try:
            # PASO 1: Generar el mensaje del TRA (LoginTicketRequest.xml)
            print("📄 PASO 1: Generar el mensaje del TRA (LoginTicketRequest.xml)")
            print("-" * 60)
            tra_xml, unique_id = self.generar_tra(servicio)
            print(f"   ✅ TRA generado según schema XSD oficial")
            print(f"   🆔 UniqueId: {unique_id}")
            
            # PASO 2: Generar un CMS que contenga el TRA, su firma electrónica y el certificado X.509
            print(f"\n🔐 PASO 2: Generar CMS (LoginTicketRequest.xml.cms)")
            print("-" * 60)
            cms_data = self.firmar_tra(tra_xml, servicio)
            print(f"   ✅ CMS contiene: TRA + Firma + Certificado X.509")
            
            # PASO 3: Codificar en Base64 el CMS (LoginTicketRequest.xml.cms.base64)
            print(f"\n📦 PASO 3: Codificar en Base64 el CMS")
            print("-" * 60)
            cms_b64 = base64.b64encode(cms_data).decode('utf-8')
            print(f"   ✅ Base64 generado: {len(cms_b64)} caracteres")
            
            # Guardar base64 para referencia
            with open("LoginTicketRequest.xml.cms.base64", "w") as f:
                f.write(cms_b64)
            print(f"   💾 Guardado como: LoginTicketRequest.xml.cms.base64")
            
            # PASO 4: Invocar WSAA con el CMS y recibir LoginTicketResponse.xml
            print(f"\n🌐 PASO 4: Invocar WSAA y recibir LoginTicketResponse.xml")
            print("-" * 60)
            ticket_data = self._enviar_wsaa(cms_b64, servicio)
            
            # PASO 5: Extraer y validar la información de autorización (TA)
            print(f"\n🎫 PASO 5: Extraer y validar información de autorización (TA)")
            print("-" * 60)
            self._validar_ticket(ticket_data)
            
            # Guardar ticket en cache
            self.tickets_cache[servicio] = ticket_data
            
            print(f"\n🎉 ¡TICKET DE ACCESO (TA) OBTENIDO EXITOSAMENTE!")
            print(f"   🎫 Token: {ticket_data['token'][:50]}...")
            print(f"   ✍️  Sign: {ticket_data['sign'][:50]}...")
            print(f"   ⏰ Válido hasta: {ticket_data['expiration']}")
            print(f"   💾 Ticket guardado: ticket_{servicio}_{self.ambiente}.json")
            
            return ticket_data
            
        except Exception as e:
            print(f"\n❌ ERROR EN FLUJO AFIP: {e}")
            print(f"🔧 Verifica configuración y certificados")
            raise
    
    def _validar_ticket(self, ticket_data):
        """
        Paso 5: Validar la información de autorización (TA)
        
        Args:
            ticket_data (dict): Datos del ticket obtenido
        """
        print(f"   🔍 Validando estructura del ticket...")
        
        # Validar campos requeridos
        campos_requeridos = ['token', 'sign', 'expiration', 'service']
        for campo in campos_requeridos:
            if campo not in ticket_data or not ticket_data[campo]:
                raise Exception(f"Campo requerido faltante o vacío: {campo}")
        
        # Validar formato de fecha de expiración
        try:
            from datetime import datetime
            expiration = datetime.fromisoformat(ticket_data['expiration'].replace('Z', '+00:00'))
            ahora = datetime.now()
            
            if expiration <= ahora:
                print(f"   ⚠️  ADVERTENCIA: Ticket ya expirado")
            else:
                tiempo_restante = expiration - ahora
                print(f"   ✅ Ticket válido por: {tiempo_restante}")
                
        except Exception as e:
            print(f"   ⚠️  No se pudo validar fecha de expiración: {e}")
        
        # Validar longitud de token y sign
        if len(ticket_data['token']) < 100:
            print(f"   ⚠️  Token parece muy corto: {len(ticket_data['token'])} chars")
        else:
            print(f"   ✅ Token válido: {len(ticket_data['token'])} caracteres")
            
        if len(ticket_data['sign']) < 100:
            print(f"   ⚠️  Sign parece muy corto: {len(ticket_data['sign'])} chars")
        else:
            print(f"   ✅ Sign válido: {len(ticket_data['sign'])} caracteres")
        
        print(f"   ✅ Validación de TA completada")
    
    def _enviar_wsaa(self, cms_b64, servicio):
        """
        Paso 4: Invocar WSAA con el CMS y recibir LoginTicketResponse.xml
        """
        
        url = self.wsaa_urls[self.ambiente]
        print(f"   📡 URL WSAA: {url}")
        
        # SOAP envelope según especificación AFIP
        soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" 
               xmlns:wsaa="http://wsaa.view.sua.dvadac.desein.afip.gov">
    <soap:Header/>
    <soap:Body>
        <wsaa:loginCms>
            <wsaa:in0>{cms_b64}</wsaa:in0>
        </wsaa:loginCms>
    </soap:Body>
</soap:Envelope>'''
        
        # Headers requeridos por AFIP
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'SOAPAction': '',
            'User-Agent': 'AFIP-Client/1.0'
        }
        
        # Guardar request para referencia
        with open("LoginTicketRequest_SOAP.xml", "w", encoding="utf-8") as f:
            f.write(soap_request)
        print(f"   💾 SOAP request guardado: LoginTicketRequest_SOAP.xml")
        
        try:
            print(f"   📤 Enviando CMS a WSAA...")
            response = requests.post(url, data=soap_request, headers=headers, timeout=30)
            
            print(f"   📥 Respuesta recibida:")
            print(f"      Status: {response.status_code}")
            print(f"      Content-Length: {len(response.content)} bytes")
            
            # Guardar respuesta completa
            with open("LoginTicketResponse.xml", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"   � LoginTicketResponse.xml guardado")
            
            # Verificar status HTTP
            response.raise_for_status()
            
            # Procesar respuesta
            return self._procesar_respuesta_wsaa(response.text, servicio)
            
        except requests.exceptions.Timeout:
            raise Exception("Timeout al conectar con WSAA")
        except requests.exceptions.ConnectionError:
            raise Exception("Error de conexión con WSAA")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                # Error 500 puede contener detalles del error SOAP
                print(f"   📄 Respuesta de error: {response.text[:500]}...")
                raise Exception(f"Error SOAP del servidor AFIP: {response.status_code}")
            else:
                raise Exception(f"Error HTTP {response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en request HTTP: {e}")
    
    def _procesar_respuesta_wsaa(self, response_xml, servicio):
        """
        Procesa respuesta XML de WSAA con validación completa según especificación
        """
        
        try:
            root = ET.fromstring(response_xml)
            
            # Verificar si hay errores SOAP
            fault = root.find('.//soap:Fault', {'soap': 'http://www.w3.org/2003/05/soap-envelope'})
            if fault is None:
                fault = root.find('.//faultstring')
            
            if fault is not None:
                fault_code = fault.find('faultcode')
                fault_string = fault.find('faultstring')
                
                error_code = fault_code.text if fault_code is not None else "unknown"
                error_desc = fault_string.text if fault_string is not None else fault.text
                
                # Usar el manejador de errores AFIP
                should_retry = self._manejar_error_soap(error_code, error_desc)
                
                if should_retry:
                    raise Exception(f"Error SOAP temporal: {error_code} - {error_desc}")
                else:
                    raise Exception(f"Error SOAP permanente: {error_code} - {error_desc}")
            
            # Buscar loginCmsReturn
            namespaces = {
                'soap': 'http://www.w3.org/2003/05/soap-envelope',
                'wsaa': 'http://wsaa.view.sua.dvadac.desein.afip.gov'
            }
            
            login_response = root.find('.//wsaa:loginCmsReturn', namespaces)
            if login_response is None:
                login_response = root.find('.//loginCmsReturn')
            
            if login_response is None:
                raise Exception("No se encontró loginCmsReturn en respuesta WSAA")
            
            # Decodificar base64
            response_b64 = login_response.text
            response_decoded = base64.b64decode(response_b64).decode('utf-8')
            
            print(f"   📄 Respuesta decodificada del WSAA")
            
            # Validar respuesta usando el nuevo método
            ticket_data = self._validar_respuesta_wsaa(response_decoded)
            if ticket_data is None:
                raise Exception("Error validando respuesta del WSAA")
            
            # Agregar información de servicio
            ticket_data.update({
                'service': servicio,
                'service_name': self.SERVICIOS[servicio]['nombre'],
                'environment': self.ambiente,
                'generated_at': datetime.now().isoformat()
            })
            
            # Guardar ticket completo
            ticket_file = f"ticket_{servicio}_{self.ambiente}.json"
            
            import json
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Ticket guardado: {ticket_file}")
            
            return ticket_data
            
        except Exception as e:
            print(f"❌ Error procesando respuesta WSAA: {e}")
            print(f"📄 Respuesta: {response_xml[:500]}...")
            raise
    
    def obtener_tickets_todos_servicios(self):
        """Obtiene tickets para todos los servicios disponibles"""
        
        print("\n🚀 OBTENIENDO TICKETS PARA TODOS LOS SERVICIOS")
        print("=" * 60)
        
        tickets = {}
        for servicio in self.SERVICIOS.keys():
            try:
                ticket = self.obtener_ticket_acceso(servicio)
                tickets[servicio] = ticket
                print(f"✅ {servicio}: OK\n")
            except Exception as e:
                print(f"❌ {servicio}: Error - {e}\n")
                tickets[servicio] = None
        
        return tickets
    
    def mostrar_servicios_disponibles(self):
        """Muestra información de los servicios disponibles"""
        
        print("\n📋 SERVICIOS AFIP DISPONIBLES")
        print("=" * 60)
        
        for codigo, info in self.SERVICIOS.items():
            print(f"\n🔹 {codigo.upper()}")
            print(f"   📝 Nombre: {info['nombre']}")
            print(f"   📄 Descripción: {info['descripcion']}")
            print(f"   🧪 Testing: {info['testing_url']}")
            print(f"   🚀 Producción: {info['production_url']}")

def main():
    """Función principal de demostración"""
    
    print("🇦🇷 CLIENTE AFIP - SISTEMA DEFINITIVO")
    print("=" * 60)
    
    # Configuración (AJUSTAR SEGÚN TUS ARCHIVOS)
    certificado = "certificado_afip.crt"  # Tu certificado AFIP
    clave_privada = "clave_privada_afip.key"  # Tu clave privada AFIP
    ambiente = "testing"  # Cambiar a "production" para producción
    
    try:
        # Crear cliente
        cliente = AFIPServiceClient(certificado, clave_privada, ambiente)
        
        # Mostrar servicios disponibles
        cliente.mostrar_servicios_disponibles()
        
        # Obtener tickets para todos los servicios
        tickets = cliente.obtener_tickets_todos_servicios()
        
        print("\n📊 RESUMEN FINAL:")
        print("-" * 40)
        for servicio, ticket in tickets.items():
            if ticket:
                print(f"✅ {servicio}: Token y Sign obtenidos")
            else:
                print(f"❌ {servicio}: Error al obtener ticket")
        
        return tickets
        
    except FileNotFoundError as e:
        print(f"\n❌ Error de archivo: {e}")
        print("\n📋 INSTRUCCIONES:")
        print("1. Coloca tu certificado AFIP como 'certificado_afip.crt'")
        print("2. Coloca tu clave privada como 'clave_privada_afip.key'")
        print("3. Ejecuta nuevamente el script")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()