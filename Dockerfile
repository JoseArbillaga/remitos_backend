# Dockerfile optimizado para Azure Container Apps
FROM python:3.11-slim

# Variables de entorno para Azure
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements para Azure (prioridad)
COPY azure-requirements.txt requirements.txt ./

# Instalar dependencias Python (usar azure-requirements.txt si existe)
RUN pip install --no-cache-dir -r azure-requirements.txt 2>/dev/null || pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para uploads
RUN mkdir -p uploads certificates logs

# Exponer puerto 80 para Azure Container Apps
EXPOSE 80

# Comando optimizado para Azure
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]