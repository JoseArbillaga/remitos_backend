# 📊 Arquitectura Azure para Remitos Globales (2 usuarios)

## 🎯 **URLs de la aplicación:**
- **Producción**: `https://remitosglobales.azurewebsites.net`
- **Documentación**: `https://remitosglobales.azurewebsites.net/docs`
- **Estado**: `https://remitosglobales.azurewebsites.net/health`

## 🏗️ Recursos Necesarios

### 1. 🌐 **Azure App Service (Principal)**
```bash
# Tier recomendado: Basic B1
az appservice plan create \
  --name remitos-plan \
  --resource-group remitos-rg \
  --sku B1 \
  --is-linux
```

**Especificaciones B1:**
- ✅ **CPU**: 1 vCore compartido
- ✅ **RAM**: 1.75 GB
- ✅ **Storage**: 10 GB SSD
- ✅ **Ancho de banda**: Ilimitado
- ✅ **Uptime**: 99.95% SLA
- 💰 **Costo**: ~$13.14 USD/mes

### 2. 🗄️ **Base de Datos**

#### **Opción A: PostgreSQL Flexible Server (Recomendado para producción)**
```bash
az postgres flexible-server create \
  --resource-group remitos-rg \
  --name remitos-db \
  --admin-user adminuser \
  --admin-password "SecurePass123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32
```

**Especificaciones Standard_B1ms:**
- ✅ **CPU**: 1 vCore burstable
- ✅ **RAM**: 2 GB
- ✅ **Storage**: 32 GB SSD
- ✅ **Backup**: 7 días automático
- 💰 **Costo**: ~$24.82 USD/mes

#### **Opción B: SQLite en App Service (Más económico)**
- ✅ **Incluido** en App Service
- ✅ **Sin costo adicional**
- ⚠️ **Limitación**: Un solo archivo de BD

### 3. 📦 **Azure Container Registry (Opcional)**
```bash
az acr create \
  --resource-group remitos-rg \
  --name remitosregistry \
  --sku Basic
```
- 💰 **Costo**: ~$5 USD/mes (solo si usas Docker)

## 💰 **Costos Totales Mensuales**

### **🥉 Configuración Básica (SQLite)**
- App Service B1: $13.14
- **Total**: **$13.14 USD/mes**

### **🥈 Configuración Recomendada (PostgreSQL)**
- App Service B1: $13.14
- PostgreSQL B1ms: $24.82
- **Total**: **$37.96 USD/mes**

### **🥇 Configuración Premium (con Container Registry)**
- App Service B1: $13.14
- PostgreSQL B1ms: $24.82
- Container Registry: $5.00
- **Total**: **$42.96 USD/mes**

## 🎯 **¿Docker o Código Directo?**

### **Recomendación: Código Directo (más fácil)**
```bash
# Deploy directo desde GitHub
az webapp up \
  --name remitosglobales \
  --resource-group remitos-rg \
  --runtime "PYTHON|3.11"
```

### **Docker (más control)**
```bash
# Si prefieres usar Docker
az webapp create \
  --resource-group remitos-rg \
  --name remitosglobales \
  --name remitos-backend-prod \
  --deployment-container-image-name remitosregistry.azurecr.io/remitos:latest
```

## 🔧 **Comandos Completos de Setup**

### **Script de Creación Automática:**
```bash
#!/bin/bash

# Variables
RESOURCE_GROUP="remitos-rg"
LOCATION="East US"
APP_NAME="remitosglobales"
DB_NAME="remitos-db"
PLAN_NAME="remitos-plan"

# 1. Crear grupo de recursos
az group create \
  --name $RESOURCE_GROUP \
  --location "$LOCATION"

# 2. Crear App Service Plan
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# 3. Crear Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON|3.11"

# 4. Crear PostgreSQL (opcional)
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_NAME \
  --admin-user remitoadmin \
  --admin-password "SecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --public-access 0.0.0.0

# 5. Crear base de datos
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_NAME \
  --database-name remitos

# 6. Configurar variables de entorno
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    DATABASE_URL="postgresql://remitoadmin:SecurePassword123!@$DB_NAME.postgres.database.azure.com/remitos" \
    SECRET_KEY="your-super-secret-key-here" \
    AZURE_ENVIRONMENT="production"

# 7. Deploy desde GitHub
az webapp deployment source config \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --repo-url https://github.com/JoseArbillaga/remitos_backend \
  --branch main \
  --manual-integration

echo "✅ Setup completo!"
echo "🌐 URL: https://$APP_NAME.azurewebsites.net"
echo "📚 Docs: https://$APP_NAME.azurewebsites.net/docs"
```

## 📈 **Escalabilidad para el Futuro**

### **Si creces a 10-50 usuarios:**
- Upgrade a **Standard S1** ($56/mes)
- **2x CPU**, **50GB storage**

### **Si creces a 100+ usuarios:**
- Upgrade a **Premium P1V2** ($146/mes)
- **Load balancing automático**
- **Multiple instancias**

## 🔒 **Seguridad Incluida**
- ✅ **HTTPS automático**
- ✅ **Firewall de aplicaciones**
- ✅ **Backup automático**
- ✅ **Monitoreo 24/7**

## 🎯 **Recomendación Final para 2 personas:**

**Configuración Óptima:**
- ✅ **App Service B1** ($13/mes)
- ✅ **PostgreSQL B1ms** ($25/mes)
- ✅ **Deploy directo** (sin Docker inicialmente)
- 💰 **Total: $38/mes**
- 🕐 **99.95% uptime garantizado**