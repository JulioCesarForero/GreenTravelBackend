# GreenTravelBackend - Microservicios FastAPI

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-MariaDB-orange.svg)](https://mariadb.org/)

**Arquitectura de microservicios** para GreenTravelBackend siguiendo principios **Clean Code** y **The Twelve-Factor App**. Este proyecto proporciona tres microservicios independientes para gestionar liquidaciones, proveedores y facturas.

---

## 🎯 Overview

Este proyecto implementa una arquitectura de microservicios con:

- ✅ **Clean Architecture**: Separación de responsabilidades con capas (routes, services, models, database)
- ✅ **Twelve-Factor App**: Cumplimiento completo con mejores prácticas de aplicaciones modernas
- ✅ **Production-Ready**: Docker, health checks, logging, manejo de errores, testing
- ✅ **Infraestructura Escalable**: MySQL/MariaDB, Nginx API Gateway
- ✅ **Type-Safe**: Modelos Pydantic para validación de request/response
- ✅ **Tested**: Suite de tests con pytest (>80% cobertura objetivo)
- ✅ **Documented**: Documentación OpenAPI/Swagger automática

---

## 📋 Tabla de Contenidos

- [Quick Start](#-quick-start)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Servicios](#-servicios)
- [Configuración](#️-configuración)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Despliegue](#-despliegue)

---

## 🚀 Quick Start

### Prerequisitos

- **Docker** y **Docker Compose** (recomendado)
- **Python 3.12+** (para desarrollo local)
- **Git** (para control de versiones)

### 1. Clonar o Copiar el Proyecto

```powershell
# Navegar al directorio del proyecto
cd GreenTravelBackend
```

### 2. Configurar Variables de Entorno

```powershell
# Copiar plantilla de variables de entorno
# En Windows PowerShell:
Copy-Item ENV_TEMPLATE.txt .env
# O en Linux/Mac:
# cp ENV_TEMPLATE.txt .env

# Editar .env con tu configuración (contraseñas de base de datos, puertos, etc.)
# IMPORTANTE: Cambiar todas las contraseñas y secretos en producción!
```

### 3. Iniciar la Infraestructura

```powershell
# Construir e iniciar todos los servicios
docker-compose up --build

# O ejecutar en modo detached
docker-compose up -d --build
```

### 4. Verificar Servicios

- **API Gateway**: http://localhost (Nginx)
- **Liquidaciones Service API**: http://localhost:8001
- **Provedores Service API**: http://localhost:8002
- **Facturas Service API**: http://localhost:8003
- **API Documentation**: 
  - Liquidaciones: http://localhost:8001/docs
  - Provedores: http://localhost:8002/docs
  - Facturas: http://localhost:8003/docs
- **Health Check**: 
  - Liquidaciones: http://localhost:8001/health
  - Provedores: http://localhost:8002/health
  - Facturas: http://localhost:8003/health
- **MySQL**: localhost:3307

### 5. Probar la API

```powershell
# Health check
curl http://localhost/health

# Crear una liquidación
curl -X POST http://localhost/api/v1/liquidaciones `
  -H "Content-Type: application/json" `
  -d '{"observaciones":"Test","nombre_empresa":"Test Empresa","estado":1}'

# Obtener todas las liquidaciones
curl http://localhost/api/v1/liquidaciones

# Crear un proveedor
curl -X POST http://localhost/api/v1/provedores `
  -H "Content-Type: application/json" `
  -d '{"provedor_nombre":"Test Proveedor","provedor_razonsocial":"Test S.A.","provedor_estado":1}'

# Obtener todos los proveedores
curl http://localhost/api/v1/provedores
```

---

## 📁 Estructura del Proyecto

```
GreenTravelBackend/
│
├── docker-compose.yml              # Orquestación de servicios
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore                     # Reglas de Git
├── nginx.conf                     # Configuración API Gateway
├── README.md                      # Este archivo
│
├── docker-entrypoint-initdb.d/     # Scripts de inicialización MySQL
│   └── 001-init-databases.sql
│
├── liquidaciones-service/          # Microservicio 1
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── facturas-service/                # Microservicio 3
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── conftest.py
│   │
│   ├── app/
│   │   ├── database/               # Capa de base de datos
│   │   │   ├── connection.py
│   │   │   ├── migration.py
│   │   │   └── seed.py
│   │   │
│   │   ├── models/                 # Modelos de datos
│   │   │   └── liquidacion.py
│   │   │
│   │   ├── services/               # Lógica de negocio
│   │   │   └── liquidacion_service.py
│   │   │
│   │   └── routes/                 # Endpoints API
│   │       └── liquidacion.py
│   │
│   └── tests/                      # Suite de tests
│       ├── test_database_connection.py
│       ├── test_liquidacion_routes.py
│       └── test_liquidacion_service.py
│
└── provedores-service/             # Microservicio 2
    ├── Dockerfile
    ├── main.py
    ├── requirements.txt
    ├── pytest.ini
    ├── conftest.py
    │
    ├── app/
    │   ├── database/
    │   │   ├── connection.py
    │   │   ├── migration.py
    │   │   └── seed.py
    │   │
    │   ├── models/
    │   │   └── provedor.py
    │   │
    │   ├── services/
    │   │   └── provedor_service.py
    │   │
    │   └── routes/
    │       └── provedor.py
    │
    └── tests/
        ├── test_database_connection.py
        ├── test_provedor_routes.py
        └── test_provedor_service.py
│
└── facturas-service/               # Microservicio 3
    ├── Dockerfile
    ├── main.py
    ├── requirements.txt
    ├── pytest.ini
    ├── conftest.py
    │
    ├── app/
    │   ├── database/               # Capa de base de datos
    │   │   ├── connection.py
    │   │   ├── migration.py
    │   │   └── seed.py
    │   │
    │   ├── models/                 # Modelos de datos
    │   │   ├── invoice.py
    │   │   └── invoice_item.py
    │   │
    │   ├── services/               # Lógica de negocio
    │   │   ├── invoice_service.py
    │   │   └── invoice_item_service.py
    │   │
    │   └── routes/                 # Endpoints API
    │       ├── invoice.py
    │       └── invoice_item.py
    │
    └── tests/                      # Suite de tests
        ├── test_database_connection.py
        ├── test_invoice_routes.py
        ├── test_invoice_service.py
        ├── test_invoice_item_routes.py
        └── test_invoice_item_service.py
```

---

## 🎯 Servicios

### Liquidaciones Service (Puerto 8001)

Gestiona las liquidaciones del sistema.

**Endpoints:**
- `GET /api/v1/liquidaciones` - Listar liquidaciones (con paginación y filtros)
- `GET /api/v1/liquidaciones/{id}` - Obtener liquidación por ID
- `POST /api/v1/liquidaciones` - Crear nueva liquidación
- `PUT /api/v1/liquidaciones/{id}` - Actualizar liquidación
- `DELETE /api/v1/liquidaciones/{id}` - Eliminar liquidación (soft delete)
- `GET /api/v1/liquidaciones/stats` - Estadísticas

**Tabla:** `colombia_green_travel.liquidaciones`

### Provedores Service (Puerto 8002)

Gestiona los proveedores del sistema.

**Endpoints:**
- `GET /api/v1/provedores` - Listar proveedores (con paginación y filtros)
- `GET /api/v1/provedores/{id}` - Obtener proveedor por ID
- `POST /api/v1/provedores` - Crear nuevo proveedor
- `PUT /api/v1/provedores/{id}` - Actualizar proveedor
- `DELETE /api/v1/provedores/{id}` - Eliminar proveedor (soft delete)
- `GET /api/v1/provedores/stats` - Estadísticas

**Tabla:** `colombia_green_travel.provedores`

### Facturas Service (Puerto 8003)

Gestiona facturas e items de factura del sistema.

**Endpoints de Facturas:**
- `GET /api/v1/invoices` - Listar facturas (con paginación y filtros)
- `GET /api/v1/invoices/{id}` - Obtener factura por ID (con items incluidos)
- `POST /api/v1/invoices` - Crear factura (sin items)
- `POST /api/v1/invoices/with-items` - Crear factura con items anidados
- `PUT /api/v1/invoices/{id}` - Actualizar factura
- `DELETE /api/v1/invoices/{id}` - Eliminar factura (hard delete)
- `GET /api/v1/invoices/stats` - Estadísticas

**Endpoints de Items de Factura:**
- `GET /api/v1/invoices/{invoice_id}/items` - Listar items de una factura
- `GET /api/v1/invoice-items/{id}` - Obtener item por ID
- `POST /api/v1/invoices/{invoice_id}/items` - Crear item para una factura
- `PUT /api/v1/invoice-items/{id}` - Actualizar item
- `DELETE /api/v1/invoice-items/{id}` - Eliminar item

**Características:**
- Cálculo automático de totales (subtotal, tax_amount, total_amount)
- Recálculo automático del total de la factura al crear/actualizar/eliminar items
- Validación de fechas (departure_date >= arrival_date)
- Validación de total_amount vs suma de items
- Relación ForeignKey con CASCADE delete

**Tablas:** `colombia_green_travel.invoices`, `colombia_green_travel.invoice_items`

**Rutas a través del Gateway:**
- Facturas: `/api/v1/facturas/` → `facturas-service`
- Items: `/api/v1/invoice-items/` → `facturas-service`

---

## ⚙️ Configuración

### Variables de Entorno

Toda la configuración se realiza mediante variables de entorno. Ver `.env.example` para todas las opciones.

#### Configuración Clave:

**Base de Datos** (MySQL/MariaDB):
```bash
MYSQL_HOST=mysql-db
MYSQL_PORT=3307
MYSQL_DATABASE=colombia_green_travel
MYSQL_USER=appuser
MYSQL_PASSWORD=AppPass123!
```

**Servicios:**
```bash
LIQUIDACIONES_SERVICE_PORT=8001
PROVEDORES_SERVICE_PORT=8002
FACTURAS_SERVICE_PORT=8003
```

### Puertos de Servicios

- **Nginx Gateway**: 80
- **Liquidaciones Service**: 8001
- **Provedores Service**: 8002
- **Facturas Service**: 8003
- **MySQL**: 3307 (externo), 3306 (interno Docker)

---

## 💻 Desarrollo

### Desarrollo Local (Sin Docker)

```powershell
# Navegar al servicio
cd liquidaciones-service  # o provedores-service

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp ..\.env.example .env
# Editar .env para desarrollo local

# Ejecutar servicio
python main.py

# O con uvicorn directamente
uvicorn main:app --reload --port 8001  # o 8002
```

### Hot Reload Development

El setup de docker-compose soporta hot reload mediante montaje de volúmenes:

```yaml
volumes:
  - ./liquidaciones-service:/app
```

Los cambios en el código se recargan automáticamente.

---

## 🧪 Testing

### Ejecutar Tests

```powershell
# Usando Docker
docker-compose run liquidaciones-service pytest
docker-compose run provedores-service pytest
docker-compose run facturas-service pytest

# O localmente
cd liquidaciones-service  # o provedores-service o facturas-service
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=html

# Ejecutar archivo de test específico
pytest tests/test_liquidacion_routes.py

# Ejecutar con marcadores
pytest -m unit          # Solo tests unitarios
pytest -m integration   # Solo tests de integración
```

### Estructura de Tests

- **Unit Tests**: Prueban funciones/clases individuales en aislamiento
- **Integration Tests**: Prueban endpoints API con base de datos
- **Fixtures**: Datos de prueba reutilizables en `conftest.py`
- **Coverage**: Objetivo >80% de cobertura

---

## 🚢 Despliegue

### Checklist de Producción

- [ ] Cambiar todas las contraseñas y secretos en `.env`
- [ ] Establecer `ENVIRONMENT=production`
- [ ] Establecer `DEBUG=false`
- [ ] Configurar `ALLOWED_ORIGINS` para CORS
- [ ] Usar `JWT_SECRET_KEY` fuerte (32+ caracteres aleatorios)
- [ ] Configurar límites de recursos en `docker-compose.yml`
- [ ] Configurar monitoreo y agregación de logs
- [ ] Configurar estrategia de backup para MySQL
- [ ] Usar gestión de secretos (Docker Secrets, Vault, AWS Secrets Manager)

### Despliegue Docker

```powershell
# Build de producción
docker-compose -f docker-compose.yml build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Escalar servicios
docker-compose up -d --scale liquidaciones-service=3
```

---

## 📚 Documentación de API

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: 
  - Liquidaciones: http://localhost:8001/docs
  - Provedores: http://localhost:8002/docs
  - Facturas: http://localhost:8003/docs
- **ReDoc**: 
  - Liquidaciones: http://localhost:8001/redoc
  - Provedores: http://localhost:8002/redoc
  - Facturas: http://localhost:8003/redoc
- **OpenAPI JSON**: 
  - Liquidaciones: http://localhost:8001/openapi.json
  - Provedores: http://localhost:8002/openapi.json
  - Facturas: http://localhost:8003/openapi.json

---

## 🏗️ Arquitectura

### Arquitectura de Capas

Cada microservicio sigue una **arquitectura limpia en capas**:

```
HTTP Layer (main.py)
    ↓
Routes Layer (app/routes/)
    ↓
Services Layer (app/services/)
    ↓
Models Layer (app/models/)
    ↓
Database Layer (app/database/)
```

### Stack Tecnológico

- **Framework**: FastAPI 0.115+ (async, type-safe)
- **ORM**: SQLAlchemy 2.0+ (soporte async moderno)
- **Validación**: Pydantic 2.9+ (validación de tipos)
- **Base de Datos**: MySQL/MariaDB 10.6 (RDBMS de grado producción)
- **Gateway**: Nginx (load balancing, rate limiting)
- **Servidor**: Uvicorn con uvloop (alto rendimiento)
- **Testing**: Pytest con cobertura (>80% objetivo)
- **Contenedor**: Docker con multi-stage builds

---

## 🔧 Mejores Prácticas

### Organización de Código

1. **Arquitectura en Capas**:
   - **Routes**: Manejo HTTP request/response, validación
   - **Services**: Lógica de negocio, transacciones
   - **Models**: Estructuras de datos, esquema de base de datos
   - **Database**: Gestión de conexión, sesión

2. **Inyección de Dependencias**:
   ```python
   @router.get("/items")
   def get_items(db: Session = Depends(get_db)):
       service = ItemService(db)
       return service.get_all()
   ```

3. **Manejo de Errores**:
   ```python
   try:
       result = service.create(data)
       return result
   except ValueError as e:
       raise HTTPException(status_code=409, detail=str(e))
   ```

### Seguridad

1. **Variables de Entorno**: Nunca commitear archivos `.env`
2. **SQL Injection**: Usar SQLAlchemy ORM (protección automática)
3. **CORS**: Configurar `ALLOWED_ORIGINS` apropiadamente
4. **Rate Limiting**: Configurado en nginx.conf

---

## 📝 Licencia

Este proyecto es proporcionado tal cual para uso educativo y profesional. Modificar según sea necesario para tus proyectos.

---

## 🙏 Agradecimientos

Este proyecto sigue principios de:
- [The Twelve-Factor App](https://12factor.net/)
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) por Robert C. Martin
- [FastAPI](https://fastapi.tiangolo.com/) documentación
- [SQLAlchemy](https://www.sqlalchemy.org/) mejores prácticas

---

**¡Feliz Coding! 🚀**

Construye microservicios escalables, mantenibles y profesionales con esta arquitectura.

