"""
Tests para validadores AFIP
"""
import pytest
from app.utils.afip_validators import (
    validar_cuit, validar_formato_remito, validar_patente_argentina,
    validar_peso_carnico, validar_razon_social, validar_observaciones_afip,
    validar_remito_completo, generar_numero_remito_automatico,
    AFIPValidationError
)

class TestValidadorCUIT:
    """Tests para validación de CUIT"""
    
    def test_cuit_valido(self):
        """Test con CUIT válido"""
        assert validar_cuit("30123456786") == True  # CUIT válido calculado
        assert validar_cuit("20123456783") == True  # Otro CUIT válido
    
    def test_cuit_invalido_longitud(self):
        """Test con CUIT de longitud incorrecta"""
        assert validar_cuit("2012345678") == False  # 10 dígitos
        assert validar_cuit("201234567890") == False  # 12 dígitos
        assert validar_cuit("") == False
    
    def test_cuit_invalido_caracteres(self):
        """Test con CUIT con caracteres no numéricos"""
        assert validar_cuit("20-12345678-9") == False
        assert validar_cuit("20ABC456789") == False
    
    def test_cuit_invalido_digito_verificador(self):
        """Test con CUIT con dígito verificador incorrecto"""
        assert validar_cuit("20123456788") == False  # Dígito verificador incorrecto
    
    def test_cuit_none(self):
        """Test con CUIT None"""
        assert validar_cuit(None) == False

class TestValidadorRemito:
    """Tests para validación de número de remito"""
    
    def test_formato_remito_valido(self):
        """Test con formato de remito válido"""
        assert validar_formato_remito("R-12345678") == True
        assert validar_formato_remito("R-00000001") == True
    
    def test_formato_remito_invalido(self):
        """Test con formato de remito inválido"""
        assert validar_formato_remito("R12345678") == False  # Sin guión
        assert validar_formato_remito("R-1234567") == False  # 7 dígitos
        assert validar_formato_remito("R-123456789") == False  # 9 dígitos
        assert validar_formato_remito("12345678") == False  # Sin R-
        assert validar_formato_remito("") == False

class TestValidadorPatente:
    """Tests para validación de patente argentina"""
    
    def test_patente_formato_antiguo_valido(self):
        """Test con patente formato antiguo válido"""
        assert validar_patente_argentina("ABC123") == True
        assert validar_patente_argentina("XYZ999") == True
    
    def test_patente_formato_mercosur_valido(self):
        """Test con patente formato Mercosur válido"""
        assert validar_patente_argentina("AB123CD") == True
        assert validar_patente_argentina("XY999ZW") == True
    
    def test_patente_invalida(self):
        """Test con patente inválida"""
        assert validar_patente_argentina("AB12CD") == False  # Muy corta
        assert validar_patente_argentina("ABC1234") == False  # Formato incorrecto
        assert validar_patente_argentina("123ABC") == False  # Orden incorrecto
    
    def test_patente_vacia_opcional(self):
        """Test con patente vacía (debe ser válida porque es opcional)"""
        assert validar_patente_argentina("") == True
        assert validar_patente_argentina(None) == True

class TestValidadorPeso:
    """Tests para validación de peso cárnico"""
    
    def test_peso_valido(self):
        """Test con peso válido"""
        assert validar_peso_carnico(100.5) == True
        assert validar_peso_carnico(0.1) == True
        assert validar_peso_carnico(50000) == True  # Máximo permitido
    
    def test_peso_invalido(self):
        """Test con peso inválido"""
        assert validar_peso_carnico(0) == False  # Cero no válido
        assert validar_peso_carnico(-10) == False  # Negativo
        assert validar_peso_carnico(50001) == False  # Excede máximo
        assert validar_peso_carnico(None) == False

class TestValidadorRazonSocial:
    """Tests para validación de razón social"""
    
    def test_razon_social_valida(self):
        """Test con razón social válida"""
        assert validar_razon_social("Empresa Test SA") == True
        assert validar_razon_social("Mi Empresa SRL") == True
    
    def test_razon_social_invalida(self):
        """Test con razón social inválida"""
        assert validar_razon_social("") == False  # Vacía
        assert validar_razon_social("A") == False  # Muy corta
        assert validar_razon_social("12345") == False  # Solo números
        assert validar_razon_social("A" * 201) == False  # Muy larga

class TestValidadorObservaciones:
    """Tests para validación de observaciones AFIP"""
    
    def test_observaciones_validas(self):
        """Test con observaciones válidas"""
        assert validar_observaciones_afip("Observación normal") == True
        assert validar_observaciones_afip("") == True  # Vacía válida
        assert validar_observaciones_afip(None) == True  # None válida
    
    def test_observaciones_invalidas(self):
        """Test con observaciones inválidas"""
        assert validar_observaciones_afip("A" * 1001) == False  # Muy larga
        assert validar_observaciones_afip("Observación con <script>") == False  # Caracteres prohibidos
        assert validar_observaciones_afip('Observación con "comillas"') == False

class TestValidadorRemitoCompleto:
    """Tests para validación completa de remito"""
    
    def test_remito_completo_valido(self):
        """Test con remito completamente válido"""
        remito_data = {
            "numero_remito": "R-12345678",
            "emisor_cuit": "30123456786",
            "receptor_cuit": "20123456783",
            "emisor_razon_social": "Empresa Emisora SA",
            "receptor_razon_social": "Empresa Receptora SRL",
            "patente_vehiculo": "ABC123",
            "peso_total": 500.0,
            "observaciones": "Observaciones normales"
        }
        
        errores = validar_remito_completo(remito_data)
        assert len(errores) == 0
    
    def test_remito_con_errores_multiples(self):
        """Test con remito que tiene múltiples errores"""
        remito_data = {
            "numero_remito": "REMITO-INVALIDO",
            "emisor_cuit": "20123456788",  # CUIT inválido
            "receptor_cuit": "27123456783",  # CUIT inválido
            "emisor_razon_social": "A",  # Muy corta
            "receptor_razon_social": "12345",  # Solo números
            "peso_total": -100,  # Peso negativo
            "observaciones": "A" * 1001  # Muy larga
        }
        
        errores = validar_remito_completo(remito_data)
        
        assert len(errores) > 0
        assert "numero_remito" in errores
        assert "emisor_cuit" in errores
        assert "receptor_cuit" in errores
        assert "peso_total" in errores
        assert "observaciones" in errores

class TestGeneradorNumeroRemito:
    """Tests para generador automático de número de remito"""
    
    def test_generar_numero_valido(self):
        """Test para generar número de remito válido"""
        numero = generar_numero_remito_automatico("30123456786", 1)
        
        assert numero.startswith("R-")
        assert len(numero) == 10  # R- + 8 dígitos
        assert validar_formato_remito(numero) == True
    
    def test_generar_con_cuit_invalido(self):
        """Test con CUIT inválido debe lanzar excepción"""
        with pytest.raises(AFIPValidationError):
            generar_numero_remito_automatico("CUIT_INVALIDO", 1)
    
    def test_generar_secuencia_correcta(self):
        """Test para verificar secuencia correcta"""
        cuit = "30123456786"
        
        numero1 = generar_numero_remito_automatico(cuit, 1)
        numero2 = generar_numero_remito_automatico(cuit, 99)
        numero3 = generar_numero_remito_automatico(cuit, 1234)
        
        # Verificar formato correcto (últimos 4 dígitos del CUIT: 6786)
        assert numero1 == "R-67860001"
        assert numero2 == "R-67860099"
        assert numero3 == "R-67861234"