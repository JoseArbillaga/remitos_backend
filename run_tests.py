#!/usr/bin/env python3
"""
Script para ejecutar tests del proyecto
"""
import subprocess
import sys
import os

def run_tests():
    """Ejecutar suite de tests"""
    print("🧪 EJECUTANDO SUITE DE TESTS")
    print("=" * 50)
    
    # Asegurar que estamos en el directorio correcto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Comando para ejecutar pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ TODOS LOS TESTS PASARON!")
            print("📊 Reporte de cobertura generado en htmlcov/index.html")
        else:
            print("\n❌ ALGUNOS TESTS FALLARON!")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False
    
    return result.returncode == 0

def run_specific_tests(test_type):
    """Ejecutar tests específicos"""
    test_files = {
        "auth": "tests/test_auth.py",
        "validators": "tests/test_validators.py", 
        "remitos": "tests/test_remitos.py"
    }
    
    if test_type not in test_files:
        print(f"❌ Tipo de test inválido: {test_type}")
        print(f"Tipos disponibles: {', '.join(test_files.keys())}")
        return False
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_files[test_type],
        "-v"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        success = run_specific_tests(test_type)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)