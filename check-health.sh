#!/bin/bash

# ============================================
# Script de Verificación de Health Checks
# ============================================
# Verifica el estado de salud de todos los servicios
# Uso: ./check-health.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo "=========================================="
echo "Verificación de Health Checks"
echo "=========================================="
echo ""

# Verificar contenedores
echo "1. Verificando contenedores..."
if docker compose ps | grep -q "Up (healthy)"; then
    info "Contenedores en ejecución"
    docker compose ps
else
    error "Algunos contenedores no están saludables"
    docker compose ps
fi

echo ""
echo "2. Verificando endpoints..."

# Health check del gateway
echo -n "  Gateway (http://localhost/health): "
if curl -s -f http://localhost/health > /dev/null 2>&1; then
    info "OK"
    curl -s http://localhost/health | head -c 100
    echo ""
else
    error "FAIL"
fi

# Health check de liquidaciones
echo -n "  Liquidaciones (http://localhost:8001/health): "
if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    info "OK"
    curl -s http://localhost:8001/health | head -c 100
    echo ""
else
    error "FAIL"
fi

# Health check de provedores
echo -n "  Provedores (http://localhost:8002/health): "
if curl -s -f http://localhost:8002/health > /dev/null 2>&1; then
    info "OK"
    curl -s http://localhost:8002/health | head -c 100
    echo ""
else
    error "FAIL"
fi

# Health check de facturas
echo -n "  Facturas (http://localhost:8003/health): "
if curl -s -f http://localhost:8003/health > /dev/null 2>&1; then
    info "OK"
    curl -s http://localhost:8003/health | head -c 100
    echo ""
else
    error "FAIL"
fi

echo ""
echo "3. Verificando API Gateway..."
echo -n "  Root endpoint (http://localhost/): "
if curl -s -f http://localhost/ > /dev/null 2>&1; then
    info "OK"
    curl -s http://localhost/ | head -c 150
    echo ""
else
    error "FAIL"
fi

echo ""
echo "=========================================="
echo "Verificación completada"
echo "=========================================="

