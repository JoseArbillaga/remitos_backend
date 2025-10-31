# 🌐 Guía para Cambiar/Agregar Dominios Personalizados

## 📋 **Opciones de Dominio**

### **1. Dominio Azure (.azurewebsites.net)**
- ❌ **NO se puede cambiar** una vez creado
- ✅ **Gratuito** e incluido
- 🔄 **Solución**: Crear nueva app con nombre diferente

### **2. Dominio Personalizado (tu-empresa.com)**
- ✅ **SÍ se puede cambiar** cuando quieras
- 💰 **Requiere** dominio registrado
- 🔒 **SSL gratuito** incluido

## 🚀 **Agregar Dominio Personalizado**

### **Paso 1: Registrar dominio**
Puedes comprar en:
- **Namecheap**: ~$12/año
- **GoDaddy**: ~$15/año
- **Azure Domains**: ~$12/año

### **Paso 2: Configurar DNS**
```bash
# En tu proveedor de DNS, agregar registros:
# Tipo: CNAME
# Nombre: www
# Valor: tu-app.azurewebsites.net

# Tipo: A
# Nombre: @
# Valor: [IP de tu App Service]
```

### **Paso 3: Agregar en Azure**
```bash
# Agregar dominio personalizado
az webapp config hostname add \
  --resource-group remitos-rg \
  --webapp-name remitos-backend-prod \
  --hostname "www.tu-empresa.com"

# Agregar SSL automático (GRATIS)
az webapp config ssl create \
  --resource-group remitos-rg \
  --name remitos-backend-prod \
  --hostname "www.tu-empresa.com"
```

### **Paso 4: Verificar funcionamiento**
```bash
# Probar URLs:
# https://www.tu-empresa.com
# https://tu-empresa.com
# https://tu-app.azurewebsites.net (sigue funcionando)
```

## 🔄 **Cambiar Dominio Personalizado**

### **Ejemplo: De empresa-vieja.com a empresa-nueva.com**

```bash
# 1. Agregar nuevo dominio
az webapp config hostname add \
  --resource-group remitos-rg \
  --webapp-name remitos-backend-prod \
  --hostname "www.empresa-nueva.com"

# 2. Configurar SSL para nuevo dominio
az webapp config ssl create \
  --resource-group remitos-rg \
  --name remitos-backend-prod \
  --hostname "www.empresa-nueva.com"

# 3. Quitar dominio viejo (opcional)
az webapp config hostname delete \
  --resource-group remitos-rg \
  --webapp-name remitos-backend-prod \
  --hostname "www.empresa-vieja.com"
```

## 💡 **Estrategia Recomendada**

### **Fase 1: Desarrollo (Gratis)**
```
URL: remitos-backend-dev.azurewebsites.net
Costo: $0 (usar tier F1)
```

### **Fase 2: Producción sin dominio**
```
URL: remitos-backend-prod.azurewebsites.net
Costo: $38/mes (App Service B1 + PostgreSQL)
```

### **Fase 3: Producción con dominio**
```
URL Principal: www.tu-empresa.com
URL Backup: remitos-backend-prod.azurewebsites.net
Costo: $38/mes + $12/año dominio
```

## 🎯 **Ejemplos de URLs Finales**

### **Opción A: Solo Azure**
```
API: https://remitos-sistema.azurewebsites.net
Docs: https://remitos-sistema.azurewebsites.net/docs
Health: https://remitos-sistema.azurewebsites.net/health
```

### **Opción B: Con dominio personalizado**
```
API: https://api.tu-empresa.com
Docs: https://api.tu-empresa.com/docs
Health: https://api.tu-empresa.com/health
```

### **Opción C: Subdominios específicos**
```
API: https://remitos.tu-empresa.com
Docs: https://remitos.tu-empresa.com/docs
Admin: https://admin.tu-empresa.com
```

## 🔧 **Script para Cambio de Dominio**

```powershell
# Variables
$RESOURCE_GROUP = "remitos-rg"
$APP_NAME = "remitos-backend-prod"
$NEW_DOMAIN = "api.tu-empresa.com"

# Verificar dominio disponible
Write-Host "🔍 Verificando dominio..." -ForegroundColor Yellow
az webapp config hostname add \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $APP_NAME \
  --hostname $NEW_DOMAIN

# Configurar SSL gratuito
Write-Host "🔒 Configurando SSL..." -ForegroundColor Yellow
az webapp config ssl create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --hostname $NEW_DOMAIN

Write-Host "✅ Dominio configurado: https://$NEW_DOMAIN" -ForegroundColor Green
```

## 💰 **Costos de Dominios**

| Proveedor | .com/año | .net/año | .org/año |
|-----------|----------|----------|----------|
| Namecheap | $12.98   | $14.98   | $14.98   |
| GoDaddy   | $14.99   | $16.99   | $16.99   |
| Azure     | $12.00   | $15.00   | $15.00   |

## 🎯 **Recomendación**

### **Para empezar:**
1. ✅ **Usar dominio Azure** gratis: `remitos-backend.azurewebsites.net`
2. ✅ **Nombre bien pensado** (difícil cambiar después)

### **Para producción:**
1. ✅ **Comprar dominio personalizado**: `tu-empresa.com`
2. ✅ **Mantener ambos** funcionando
3. ✅ **SSL gratuito** en ambos

### **Nombres sugeridos para Azure:**
- `remitos-sistema.azurewebsites.net`
- `remitos-api.azurewebsites.net` 
- `gestion-remitos.azurewebsites.net`
- `tu-empresa-remitos.azurewebsites.net`