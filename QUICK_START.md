# 🚀 Guía Rápida de Despliegue - GreenTravelBackend

## Despliegue Inicial (Primera Vez)

```bash
# 1. Navegar al directorio
cd ~/GreenTravelBackend

# 2. Crear archivo .env
cp ENV_TEMPLATE.txt .env
nano .env  # Editar y guardar (Ctrl+X, Y, Enter)

# 3. Dar permisos de ejecución a los scripts
chmod +x deploy.sh update.sh check-health.sh backup-db.sh

# 4. Desplegar
./deploy.sh --build --pull

# 5. Verificar
./check-health.sh
```

## Actualización Rápida (Código Nuevo)

```bash
cd ~/GreenTravelBackend
./update.sh
```

## Actualización Completa (Con Rebuild)

```bash
cd ~/GreenTravelBackend
./deploy.sh --build --pull --logs
```

## Comandos Útiles

```bash
# Ver estado de servicios
docker compose ps

# Ver logs
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f liquidaciones-service

# Detener servicios
docker compose down

# Reiniciar servicios
docker compose restart

# Verificar health checks
./check-health.sh

# Crear backup de BD
./backup-db.sh

# Verificar endpoints
curl http://localhost/health
curl http://localhost/api/v1/liquidaciones
```

## Verificación Rápida

```bash
# Health checks
curl http://localhost/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# API Gateway
curl http://localhost/

# Endpoints
curl http://localhost/api/v1/liquidaciones
curl http://localhost/api/v1/provedores
curl http://localhost/api/v1/facturas/invoices
```

## Solución Rápida de Problemas

```bash
# Ver logs de errores
docker compose logs | grep -i error

# Reiniciar todo
docker compose down
docker compose up -d

# Verificar espacio en disco
df -h

# Verificar puertos en uso
sudo netstat -tulpn | grep -E ':(80|8001|8002|8003|3307)'
```

---

**Para más detalles, consulta:** `MANUAL_DESPLIEGUE_GCP.md`

