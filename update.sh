#!/bin/bash

# ============================================
# Script de Actualización Rápida
# ============================================
# Actualiza el código y reinicia los servicios
# Uso: ./update.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

info "Actualizando GreenTravelBackend..."

# Actualizar código
info "Descargando cambios desde Git..."
git pull origin main

# Reiniciar servicios
info "Reiniciando servicios..."
docker compose restart

# Esperar un momento
sleep 5

# Verificar estado
info "Estado de los servicios:"
docker compose ps

info "Actualización completada!"

