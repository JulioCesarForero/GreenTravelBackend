#!/bin/bash

# ============================================
# Script de Backup de Base de Datos
# ============================================
# Crea un backup de la base de datos MySQL
# Uso: ./backup-db.sh [nombre-backup]

set -e

GREEN='\033[0;32m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Nombre del backup
if [ -z "$1" ]; then
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).sql"
else
    BACKUP_NAME="$1"
fi

BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"

info "Creando backup de la base de datos..."
info "Nombre: $BACKUP_NAME"

# Crear backup
docker compose exec -T mysql-db mysqldump \
    -u "$MYSQL_USER" \
    -p"$MYSQL_PASSWORD" \
    "$MYSQL_DATABASE" > "$BACKUP_DIR/$BACKUP_NAME"

# Comprimir backup
info "Comprimiendo backup..."
gzip "$BACKUP_DIR/$BACKUP_NAME"

info "Backup creado: $BACKUP_DIR/${BACKUP_NAME}.gz"

# Mostrar tamaño
ls -lh "$BACKUP_DIR/${BACKUP_NAME}.gz"

# Limpiar backups antiguos (mantener últimos 7 días)
info "Limpiando backups antiguos (más de 7 días)..."
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete

info "Backup completado!"

