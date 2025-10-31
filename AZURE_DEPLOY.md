# 🚀 Guía de Deployment a Microsoft Azure

## 📋 Prerrequisitos

1. **Cuenta de Azure** (puedes obtener $200 gratis)
2. **Azure CLI** instalado
3. **Git** configurado con tu repositorio

## 🎯 Método 1: Azure App Service (Recomendado)

### **Paso 1: Instalar Azure CLI**
```bash
# Windows (desde PowerShell como administrador)
winget install Microsoft.AzureCLI

# O descargar desde: https://aka.ms/installazurecliwindows
```

### **Paso 2: Login en Azure**
```bash
az login
az account list --output table
```

### **Paso 3: Crear recursos en Azure**
```bash
# Crear grupo de recursos
az group create --name remitos-rg --location "Argentina central"

# Crear App Service Plan (F1 = gratis)
az appservice plan create \
  --name remitos-plan \
  --resource-group remitos-rg \
  --sku F1 \
  --is-linux

# Crear Web App
az webapp create \
  --resource-group remitos-rg \
  --plan remitos-plan \
  --name remitos-backend-unique \
  --runtime "PYTHON|3.11"
```

### **Paso 4: Configurar variables de entorno**
```bash
az webapp config appsettings set \
  --resource-group remitos-rg \
  --name remitos-backend-unique \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    SECRET_KEY="your-super-secret-key-here" \
    AZURE_ENVIRONMENT="production"
```

### **Paso 5: Deploy desde GitHub**
```bash
# Configurar deployment desde GitHub
az webapp deployment source config \
  --resource-group remitos-rg \
  --name remitos-backend-unique \
  --repo-url https://github.com/JoseArbillaga/remitos_backend \
  --branch main \
  --manual-integration
```

## 🐳 Método 2: Azure Container Apps

### **Paso 1: Crear Dockerfile**
Ver archivo `Dockerfile` incluido.

### **Paso 2: Deploy con Container Apps**
```bash
# Instalar extensión
az extension add --name containerapp

# Crear Container App Environment
az containerapp env create \
  --name remitos-env \
  --resource-group remitos-rg \
  --location "East US"

# Deploy desde código
az containerapp up \
  --resource-group remitos-rg \
  --name remitos-container \
  --environment remitos-env \
  --source .
```

## 💾 Configurar Base de Datos

### **Opción 1: PostgreSQL en Azure**
```bash
# Crear PostgreSQL server
az postgres flexible-server create \
  --resource-group remitos-rg \
  --name remitos-db-server \
  --admin-user adminuser \
  --admin-password "YourPassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32

# Crear base de datos
az postgres flexible-server db create \
  --resource-group remitos-rg \
  --server-name remitos-db-server \
  --database-name remitos
```

### **Opción 2: SQLite (para desarrollo)**
La configuración actual con SQLite funcionará automáticamente.

## 🔒 Configurar SSL y Dominio

```bash
# Agregar dominio personalizado (opcional)
az webapp config hostname add \
  --resource-group remitos-rg \
  --webapp-name remitos-backend-unique \
  --hostname yourdomain.com

# SSL automático (gratis)
az webapp config ssl bind \
  --resource-group remitos-rg \
  --name remitos-backend-unique \
  --certificate-thumbprint auto \
  --ssl-type SNI
```

## 📊 Monitoreo y Logs

```bash
# Ver logs en tiempo real
az webapp log tail \
  --resource-group remitos-rg \
  --name remitos-backend-unique

# Configurar Application Insights
az monitor app-insights component create \
  --app remitos-insights \
  --location "East US" \
  --resource-group remitos-rg
```

## 💰 Costos Estimados

### **Tier Gratuito (F1)**
- ✅ **Costo**: $0/mes
- ⚠️ **Limitaciones**: 60 min/día, 1GB storage
- 🎯 **Ideal para**: Desarrollo y demos

### **Tier Básico (B1)**
- 💰 **Costo**: ~$13/mes
- ✅ **Recursos**: 1.75GB RAM, 10GB storage
- 🎯 **Ideal para**: Producción pequeña

### **Tier Estándar (S1)**
- 💰 **Costo**: ~$56/mes
- ✅ **Recursos**: 1.75GB RAM, 50GB storage, SSL
- 🎯 **Ideal para**: Producción empresarial

## 🔧 Variables de Entorno para Producción

```bash
# Variables esenciales
SECRET_KEY="tu-clave-super-secreta-aqui"
DATABASE_URL="postgresql://user:pass@server.postgres.database.azure.com/remitos"
AZURE_ENVIRONMENT="production"
ALLOWED_HOSTS="tu-app.azurewebsites.net,tu-dominio.com"

# Variables AFIP (opcional)
AFIP_CERT_PATH="/home/site/wwwroot/certs/cert.crt"
AFIP_KEY_PATH="/home/site/wwwroot/certs/private.key"
```

## 🚀 URLs finales

- **App**: https://remitos-backend-unique.azurewebsites.net
- **API Docs**: https://remitos-backend-unique.azurewebsites.net/docs
- **Health**: https://remitos-backend-unique.azurewebsites.net/health

## 📞 Soporte

- **Azure Docs**: https://docs.microsoft.com/azure/app-service/
- **FastAPI + Azure**: https://fastapi.tiangolo.com/deployment/azure/