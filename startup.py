# Archivo de inicio para Azure App Service
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from main import app

# Configuración para Gunicorn en Azure
if __name__ == "__main__":
    import uvicorn
    
    # Puerto que Azure App Service usa
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True
    )