#!/bin/bash

# ============================================
# Script de Despliegue - GreenTravelBackend
# ============================================
# Este script automatiza el proceso de despliegue
# Uso: ./deploy.sh [opciones]
#
# Opciones:
#   --build      Reconstruir imágenes
#   --pull       Actualizar código desde Git
#   --restart    Reiniciar servicios
#   --logs       Mostrar logs después del despliegue
#   --help       Mostrar esta ayuda

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Variables
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD=false
PULL=false
RESTART=false
SHOW_LOGS=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --pull)
            PULL=true
            shift
            ;;
        --restart)
            RESTART=true
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        --help)
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --build      Reconstruir imágenes Docker"
            echo "  --pull       Actualizar código desde Git"
            echo "  --restart    Reiniciar servicios"
            echo "  --logs       Mostrar logs después del despliegue"
            echo "  --help       Mostrar esta ayuda"
            exit 0
            ;;
        *)
            error "Opción desconocida: $1"
            echo "Usa --help para ver las opciones disponibles"
            exit 1
            ;;
    esac
done

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

info "Iniciando despliegue de GreenTravelBackend..."
info "Directorio: $PROJECT_DIR"

# Verificar que existe docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    error "No se encontró docker-compose.yml en $PROJECT_DIR"
    exit 1
fi

# Verificar que existe .env
if [ ! -f ".env" ]; then
    warn "No se encontró archivo .env"
    warn "Copiando ENV_TEMPLATE.txt a .env..."
    if [ -f "ENV_TEMPLATE.txt" ]; then
        cp ENV_TEMPLATE.txt .env
        warn "Por favor, edita el archivo .env antes de continuar"
        exit 1
    else
        error "No se encontró ENV_TEMPLATE.txt"
        exit 1
    fi
fi

# Actualizar código desde Git si se solicita
if [ "$PULL" = true ]; then
    info "Actualizando código desde Git..."
    git pull origin main || {
        warn "No se pudo actualizar desde Git. Continuando con código actual..."
    }
fi

# Detener servicios existentes
info "Deteniendo servicios existentes..."
docker compose down

# Construir imágenes si se solicita
if [ "$BUILD" = true ]; then
    info "Construyendo imágenes Docker..."
    docker compose build --no-cache
fi

# Iniciar servicios
if [ "$BUILD" = true ]; then
    info "Iniciando servicios con rebuild..."
    docker compose up --build -d
else
    info "Iniciando servicios..."
    docker compose up -d
fi

# Esperar a que los servicios inicien
info "Esperando a que los servicios inicien (30 segundos)..."
sleep 30

# Verificar estado de los servicios
info "Verificando estado de los servicios..."
docker compose ps

# Verificar health checks
info "Verificando health checks..."
sleep 10

# Mostrar logs si se solicita
if [ "$SHOW_LOGS" = true ]; then
    info "Mostrando logs (Ctrl+C para salir)..."
    docker compose logs -f
else
    info "Para ver logs: docker compose logs -f"
fi

# Mensaje final
echo ""
info "=========================================="
info "Despliegue completado!"
info "=========================================="
info ""
info "Comandos útiles:"
info "  Ver logs:        docker compose logs -f"
info "  Ver estado:      docker compose ps"
info "  Detener:         docker compose down"
info "  Reiniciar:       docker compose restart"
info ""
info "Health checks:"
info "  Gateway:         curl http://localhost/health"
info "  Liquidaciones:   curl http://localhost:8001/health"
info "  Provedores:      curl http://localhost:8002/health"
info "  Facturas:        curl http://localhost:8003/health"
info ""

