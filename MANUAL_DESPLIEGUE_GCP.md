# Manual de Despliegue - GreenTravelBackend en GCP VMI

## 📋 Tabla de Contenidos
1. [Prerequisitos](#prerequisitos)
2. [Configuración Inicial](#configuración-inicial)
3. [Primer Despliegue](#primer-despliegue)
4. [Actualización del Proyecto](#actualización-del-proyecto)
5. [Verificación y Pruebas](#verificación-y-pruebas)
6. [Comandos Útiles](#comandos-útiles)
7. [Solución de Problemas](#solución-de-problemas)

---

## ✅ Prerequisitos

Asegúrate de tener configurado:
- ✅ Docker instalado y funcionando (`docker --version`)
- ✅ Docker Compose instalado (`docker compose version`)
- ✅ Usuario agregado al grupo docker (`sudo usermod -aG docker ${USER}`)
- ✅ GitHub CLI autenticado (`gh auth status`)
- ✅ Repositorio clonado en la VMI

---

## 🔧 Configuración Inicial

### Paso 1: Navegar al Directorio del Proyecto

```bash
cd ~/GreenTravelBackend
```

### Paso 2: Crear Archivo de Variables de Entorno

```bash
# Copiar la plantilla
cp ENV_TEMPLATE.txt .env

# Editar el archivo .env con tus configuraciones
nano .env
```

**⚠️ IMPORTANTE:** Configura las siguientes variables según tu entorno:

```bash
# Para producción, cambiar estos valores:
ENVIRONMENT=production
DEBUG=false

# Cambiar contraseñas por valores seguros:
MYSQL_ROOT_PASSWORD=TuPasswordSeguro123!
MYSQL_PASSWORD=TuPasswordSeguro123!

# Si necesitas cambiar puertos (por defecto están bien):
NGINX_PORT=80
MYSQL_PORT=3307
LIQUIDACIONES_SERVICE_PORT=8001
PROVEDORES_SERVICE_PORT=8002
FACTURAS_SERVICE_PORT=8003
```

**Guardar y salir:** `Ctrl+X`, luego `Y`, luego `Enter`

### Paso 3: Verificar que el archivo .env existe

```bash
ls -la .env
# Debe mostrar el archivo .env
```

---

## 🚀 Primer Despliegue

### Paso 1: Detener Contenedores Existentes (si hay)

```bash
cd ~/GreenTravelBackend
docker compose down
```

### Paso 2: Limpiar Imágenes y Volúmenes Antiguos (Opcional)

```bash
# Solo si quieres empezar completamente desde cero
docker compose down -v
docker system prune -f
```

### Paso 3: Construir e Iniciar los Servicios

```bash
# Construir todas las imágenes y levantar los servicios
docker compose up --build -d

# El flag -d ejecuta en modo detached (en segundo plano)
# El flag --build fuerza la reconstrucción de las imágenes
```

### Paso 4: Verificar el Estado de los Contenedores

```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f liquidaciones-service
docker compose logs -f provedores-service
docker compose logs -f facturas-service
docker compose logs -f mysql-db
docker compose logs -f nginx-gateway
```

**Espera 30-60 segundos** para que todos los servicios inicien correctamente.

### Paso 5: Verificar Health Checks

```bash
# Verificar estado de salud de los contenedores
docker compose ps

# Todos deben mostrar "healthy" o "running" después de unos momentos
```

---

## 🔄 Actualización del Proyecto

### Método 1: Actualización Completa (Recomendado)

```bash
# 1. Navegar al directorio
cd ~/GreenTravelBackend

# 2. Detener servicios actuales
docker compose down

# 3. Actualizar código desde GitHub
git pull origin main
# O si estás en otra rama:
# git pull origin <nombre-rama>

# 4. Reconstruir e iniciar servicios
docker compose up --build -d

# 5. Verificar logs
docker compose logs -f
```

### Método 2: Actualización Rápida (Solo Código, Sin Rebuild)

```bash
# 1. Navegar al directorio
cd ~/GreenTravelBackend

# 2. Actualizar código
git pull origin main

# 3. Reiniciar servicios (recargará código si hay volúmenes montados)
docker compose restart

# Nota: Este método solo funciona si los volúmenes están montados correctamente
# Para cambios en requirements.txt o Dockerfile, usar Método 1
```

### Método 3: Actualización de Variables de Entorno

```bash
# 1. Editar .env
nano .env

# 2. Reiniciar servicios para aplicar cambios
docker compose down
docker compose up -d

# O solo reiniciar servicios específicos afectados
docker compose restart liquidaciones-service
```

---

## ✅ Verificación y Pruebas

### Paso 1: Verificar Contenedores en Ejecución

```bash
docker compose ps
```

**Salida esperada:**
```
NAME                      STATUS          PORTS
facturas-service          Up (healthy)    0.0.0.0:8003->8003/tcp
liquidaciones-service     Up (healthy)    0.0.0.0:8001->8001/tcp
mysql-db                  Up (healthy)    0.0.0.0:3307->3306/tcp
nginx-gateway             Up (healthy)    0.0.0.0:80->80/tcp
provedores-service        Up (healthy)    0.0.0.0:8002->8002/tcp
```

### Paso 2: Probar Health Checks

```bash
# Health check del API Gateway
curl http://localhost/health

# Health checks individuales de servicios
curl http://localhost:8001/health  # Liquidaciones
curl http://localhost:8002/health  # Provedores
curl http://localhost:8003/health  # Facturas
```

**Respuesta esperada:**
```json
{"status":"healthy","service":"liquidaciones-service","version":"1.0.0"}
```

### Paso 3: Probar Endpoints del API Gateway

```bash
# Verificar que el gateway responde
curl http://localhost/

# Debe retornar:
# {"status":"ok","message":"GreenTravelBackend API Gateway is running",...}

# Probar endpoint de liquidaciones (debe estar vacío inicialmente)
curl http://localhost/api/v1/liquidaciones

# Probar endpoint de proveedores
curl http://localhost/api/v1/provedores

# Probar endpoint de facturas
curl http://localhost/api/v1/facturas/invoices
```

### Paso 4: Verificar Documentación Swagger

Abre en tu navegador (si tienes acceso desde fuera):
- `http://TU_IP_VMI:8001/docs` - Liquidaciones API Docs
- `http://TU_IP_VMI:8002/docs` - Provedores API Docs
- `http://TU_IP_VMI:8003/docs` - Facturas API Docs

### Paso 5: Verificar Conexión a Base de Datos

```bash
# Conectarse a MySQL desde el host
docker compose exec mysql-db mysql -u appuser -p${MYSQL_PASSWORD} colombia_green_travel

# O usando el contenedor directamente
docker exec -it mysql-db mysql -u appuser -p colombia_green_travel
# (te pedirá la contraseña)

# Ver tablas creadas
SHOW TABLES;

# Salir de MySQL
exit;
```

---

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar servicios
docker compose up -d

# Detener servicios
docker compose down

# Detener y eliminar volúmenes (⚠️ CUIDADO: elimina datos)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart liquidaciones-service

# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f liquidaciones-service

# Ver últimas 100 líneas de logs
docker compose logs --tail=100
```

### Gestión de Imágenes

```bash
# Ver imágenes construidas
docker images | grep greentravel

# Eliminar imágenes no utilizadas
docker image prune -a

# Reconstruir una imagen específica
docker compose build liquidaciones-service
```

### Gestión de Base de Datos

```bash
# Backup de la base de datos
docker compose exec mysql-db mysqldump -u appuser -p${MYSQL_PASSWORD} colombia_green_travel > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker compose exec -T mysql-db mysql -u appuser -p${MYSQL_PASSWORD} colombia_green_travel < backup_20240101_120000.sql

# Ver tamaño de volúmenes
docker volume ls
docker volume inspect greentravelbackend_mysql_data
```

### Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver procesos dentro de un contenedor
docker compose exec liquidaciones-service ps aux

# Ver variables de entorno de un contenedor
docker compose exec liquidaciones-service env
```

---

## 🔍 Solución de Problemas

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker compose logs

# Verificar archivo .env
cat .env

# Verificar que no hay puertos en uso
sudo netstat -tulpn | grep -E ':(80|8001|8002|8003|3307)'

# Verificar espacio en disco
df -h
```

### Problema: Error de conexión a base de datos

```bash
# Verificar que MySQL está corriendo
docker compose ps mysql-db

# Ver logs de MySQL
docker compose logs mysql-db

# Verificar variables de entorno de conexión
docker compose exec liquidaciones-service env | grep MYSQL
```

### Problema: Servicios no responden

```bash
# Verificar health checks
docker compose ps

# Ver logs del servicio específico
docker compose logs liquidaciones-service

# Reiniciar el servicio
docker compose restart liquidaciones-service

# Verificar conectividad interna
docker compose exec liquidaciones-service curl http://mysql-db:3306
```

### Problema: Error al construir imágenes

```bash
# Limpiar cache de Docker
docker builder prune

# Reconstruir sin cache
docker compose build --no-cache

# Verificar espacio en disco
df -h
```

### Problema: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :80
sudo lsof -i :8001

# Detener proceso o cambiar puerto en .env
```

### Problema: Permisos de Docker

```bash
# Verificar grupo docker
groups

# Si no estás en el grupo docker:
sudo usermod -aG docker ${USER}
newgrp docker

# Verificar permisos
docker ps
```

---

## 📝 Checklist de Despliegue

Antes de considerar el despliegue completo:

- [ ] Archivo `.env` configurado correctamente
- [ ] Todos los contenedores en estado "Up" o "healthy"
- [ ] Health checks responden correctamente
- [ ] API Gateway responde en `/`
- [ ] Endpoints de servicios responden correctamente
- [ ] Base de datos accesible y tablas creadas
- [ ] Logs sin errores críticos
- [ ] Puertos expuestos correctamente
- [ ] Firewall de GCP configurado (si es necesario)

---

## 🔐 Seguridad en Producción

### Configuración de Firewall GCP

```bash
# Permitir tráfico HTTP (puerto 80)
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic"

# Permitir tráfico HTTPS (puerto 443) si usas SSL
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic"

# Permitir acceso SSH (ya debería estar configurado)
gcloud compute firewall-rules create allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow SSH"
```

### Recomendaciones de Seguridad

1. **Cambiar contraseñas por defecto** en `.env`
2. **Configurar `ALLOWED_ORIGINS`** en `.env` para CORS
3. **Usar HTTPS** con certificado SSL (Let's Encrypt)
4. **Configurar backup automático** de base de datos
5. **Monitorear logs** regularmente
6. **Mantener imágenes actualizadas** (`docker compose pull`)

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs -f`
2. Verifica el estado: `docker compose ps`
3. Consulta este manual en la sección de solución de problemas
4. Verifica la documentación del proyecto en `README.md`

---

**Última actualización:** $(date)
**Versión del manual:** 1.0

