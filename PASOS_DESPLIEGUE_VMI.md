# 📋 Pasos de Despliegue en VMI de GCP

## ✅ Estado Actual
- ✅ Docker instalado y funcionando
- ✅ GitHub CLI autenticado
- ✅ Repositorio clonado en `~/GreenTravelBackend`

---

## 🎯 PASOS A SEGUIR AHORA

### Paso 1: Navegar al Directorio del Proyecto

```bash
cd ~/GreenTravelBackend
```

### Paso 2: Crear Archivo de Variables de Entorno

```bash
# Copiar la plantilla
cp ENV_TEMPLATE.txt .env

# Editar el archivo
nano .env
```

**En el editor nano, modifica al menos estas líneas importantes:**

```bash
# Cambiar a producción si es necesario
ENVIRONMENT=production
DEBUG=false

# ⚠️ CAMBIAR ESTAS CONTRASEÑAS POR VALORES SEGUROS
MYSQL_ROOT_PASSWORD=TuPasswordSeguro123!
MYSQL_PASSWORD=TuPasswordSeguro123!
```

**Para guardar en nano:** `Ctrl+X`, luego `Y`, luego `Enter`

### Paso 3: Dar Permisos de Ejecución a los Scripts

```bash
chmod +x deploy.sh update.sh check-health.sh backup-db.sh
```

### Paso 4: Ejecutar el Despliegue Inicial

```bash
# Opción 1: Usar el script automatizado (RECOMENDADO)
./deploy.sh --build --pull

# Opción 2: Manualmente
docker compose down
docker compose up --build -d
```

**Espera 30-60 segundos** mientras se construyen las imágenes y se inician los servicios.

### Paso 5: Verificar el Despliegue

```bash
# Ver estado de contenedores
docker compose ps

# Verificar health checks con el script
./check-health.sh

# O manualmente
curl http://localhost/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Paso 6: Ver Logs (Opcional)

```bash
# Ver todos los logs
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f liquidaciones-service
```

**Para salir de los logs:** `Ctrl+C`

---

## 🔄 ACTUALIZACIONES FUTURAS

### Cuando haya cambios en el repositorio:

```bash
cd ~/GreenTravelBackend

# Actualización rápida (solo código)
./update.sh

# O actualización completa (con rebuild)
./deploy.sh --build --pull
```

---

## ✅ VERIFICACIÓN FINAL

Ejecuta estos comandos para confirmar que todo funciona:

```bash
# 1. Verificar contenedores
docker compose ps
# Todos deben estar "Up (healthy)"

# 2. Health checks
./check-health.sh

# 3. Probar endpoints
curl http://localhost/
curl http://localhost/api/v1/liquidaciones
curl http://localhost/api/v1/provedores
```

---

## 🆘 SI ALGO FALLA

### Ver logs de errores:
```bash
docker compose logs | grep -i error
```

### Reiniciar todo:
```bash
docker compose down
docker compose up -d
```

### Verificar archivo .env:
```bash
cat .env
```

### Verificar espacio en disco:
```bash
df -h
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **Manual completo:** `MANUAL_DESPLIEGUE_GCP.md`
- **Guía rápida:** `QUICK_START.md`
- **README del proyecto:** `README.md`

---

## 🎉 ¡LISTO!

Si todos los health checks pasan, tu aplicación está desplegada y funcionando.

**Endpoints disponibles:**
- API Gateway: `http://TU_IP_VMI/`
- Liquidaciones: `http://TU_IP_VMI:8001/docs`
- Provedores: `http://TU_IP_VMI:8002/docs`
- Facturas: `http://TU_IP_VMI:8003/docs`

