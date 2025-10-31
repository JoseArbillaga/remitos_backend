# 🚀 Script completo para setup en Azure
# Ejecutar este script después de instalar Azure CLI

# ====== CONFIGURACIÓN ======
$RESOURCE_GROUP = "remitos-rg"
$LOCATION = "East US"
$APP_NAME = "remitosglobales"  # Tu nombre elegido
$DB_NAME = "remitos-db-server"
$PLAN_NAME = "remitos-plan"
$DB_PASSWORD = "SecurePassword123!"  # Cambiar por password seguro

Write-Host "🚀 Iniciando setup de Remitos Backend en Azure..." -ForegroundColor Green

# 1. Login en Azure
Write-Host "📝 Iniciando sesión en Azure..." -ForegroundColor Yellow
az login

# 2. Crear grupo de recursos
Write-Host "📁 Creando grupo de recursos..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Crear App Service Plan
Write-Host "🏗️ Creando App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
  --name $PLAN_NAME `
  --resource-group $RESOURCE_GROUP `
  --sku B1 `
  --is-linux

# 4. Crear Web App
Write-Host "🌐 Creando Web App..." -ForegroundColor Yellow
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $PLAN_NAME `
  --name $APP_NAME `
  --runtime "PYTHON|3.11"

# 5. Crear PostgreSQL (comentar si prefieres SQLite)
Write-Host "🗄️ Creando base de datos PostgreSQL..." -ForegroundColor Yellow
az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_NAME `
  --admin-user remitoadmin `
  --admin-password $DB_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32 `
  --public-access 0.0.0.0

# 6. Crear base de datos
Write-Host "📊 Creando base de datos 'remitos'..." -ForegroundColor Yellow
az postgres flexible-server db create `
  --resource-group $RESOURCE_GROUP `
  --server-name $DB_NAME `
  --database-name remitos

# 7. Configurar variables de entorno
Write-Host "⚙️ Configurando variables de entorno..." -ForegroundColor Yellow
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    DATABASE_URL="postgresql://remitoadmin:$DB_PASSWORD@$DB_NAME.postgres.database.azure.com/remitos" `
    SECRET_KEY="tu-clave-super-secreta-aqui-cambiar" `
    AZURE_ENVIRONMENT="production" `
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# 8. Configurar deployment desde GitHub
Write-Host "🔗 Configurando deployment desde GitHub..." -ForegroundColor Yellow
az webapp deployment source config `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --repo-url https://github.com/JoseArbillaga/remitos_backend `
  --branch main `
  --manual-integration

Write-Host "✅ ¡Setup completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL de tu aplicación: https://$APP_NAME.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📚 Documentación API: https://$APP_NAME.azurewebsites.net/docs" -ForegroundColor Cyan
Write-Host "💚 Health Check: https://$APP_NAME.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "💰 Costo estimado mensual: ~$38 USD" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔑 Credenciales de BD PostgreSQL:" -ForegroundColor Magenta
Write-Host "   Servidor: $DB_NAME.postgres.database.azure.com" -ForegroundColor White
Write-Host "   Usuario: remitoadmin" -ForegroundColor White
Write-Host "   Password: $DB_PASSWORD" -ForegroundColor White
Write-Host "   Base de datos: remitos" -ForegroundColor White