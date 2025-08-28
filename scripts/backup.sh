#!/bin/bash
# Database Backup Script for PyLadies Seoul
# Supports full backups, incremental backups, and automated retention

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
POSTGRES_DB=${POSTGRES_DB:-"pyladies_seoul"}
POSTGRES_USER=${POSTGRES_USER:-"postgres"}
POSTGRES_HOST=${POSTGRES_HOST:-"db"}
POSTGRES_PORT=${POSTGRES_PORT:-"5432"}
BACKUP_DIR=${BACKUP_DIR:-"/backups"}
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_ONLY=$(date +"%Y%m%d")

# Backup types
BACKUP_TYPE=${1:-"full"}  # full, incremental, wal

echo -e "${BLUE}PyLadies Seoul Database Backup System${NC}"
echo -e "${BLUE}=====================================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create backup directories
setup_directories() {
    log_info "Setting up backup directories..."
    
    mkdir -p "$BACKUP_DIR/full"
    mkdir -p "$BACKUP_DIR/incremental"
    mkdir -p "$BACKUP_DIR/wal"
    mkdir -p "$BACKUP_DIR/logs"
    
    log_success "Backup directories created"
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    if ! PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; then
        log_error "Cannot connect to database"
        exit 1
    fi
    
    log_success "Database is accessible"
}

# Get database size
get_database_size() {
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -t -c "SELECT pg_size_pretty(pg_database_size('$POSTGRES_DB'));" | xargs
}

# Full database backup
full_backup() {
    log_info "Starting full database backup..."
    
    local backup_file="$BACKUP_DIR/full/full_backup_${TIMESTAMP}.sql"
    local backup_file_compressed="${backup_file}.gz"
    
    # Create SQL dump
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --format=plain \
        --no-owner \
        --no-privileges \
        > "$backup_file" 2>"$BACKUP_DIR/logs/full_backup_${TIMESTAMP}.log"
    
    if [ $? -eq 0 ]; then
        # Compress the backup
        gzip "$backup_file"
        
        # Calculate backup size
        local backup_size=$(du -h "$backup_file_compressed" | cut -f1)
        local db_size=$(get_database_size)
        
        log_success "Full backup completed"
        log_info "Database size: $db_size"
        log_info "Backup size: $backup_size"
        log_info "Backup file: $backup_file_compressed"
        
        # Create checksum
        sha256sum "$backup_file_compressed" > "${backup_file_compressed}.sha256"
        log_success "Checksum created"
        
        echo "$backup_file_compressed"
    else
        log_error "Full backup failed"
        exit 1
    fi
}

# Custom format backup (for faster restore)
custom_backup() {
    log_info "Starting custom format backup..."
    
    local backup_file="$BACKUP_DIR/full/custom_backup_${TIMESTAMP}.dump"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$backup_file" 2>"$BACKUP_DIR/logs/custom_backup_${TIMESTAMP}.log"
    
    if [ $? -eq 0 ]; then
        local backup_size=$(du -h "$backup_file" | cut -f1)
        local db_size=$(get_database_size)
        
        log_success "Custom backup completed"
        log_info "Database size: $db_size"
        log_info "Backup size: $backup_size"
        log_info "Backup file: $backup_file"
        
        # Create checksum
        sha256sum "$backup_file" > "${backup_file}.sha256"
        log_success "Checksum created"
        
        echo "$backup_file"
    else
        log_error "Custom backup failed"
        exit 1
    fi
}

# WAL archive backup
wal_backup() {
    log_info "Starting WAL archive backup..."
    
    local wal_backup_dir="$BACKUP_DIR/wal/${DATE_ONLY}"
    mkdir -p "$wal_backup_dir"
    
    # Copy WAL files if they exist
    if [ -d "/var/lib/postgresql/data/pg_wal" ]; then
        find /var/lib/postgresql/data/pg_wal -name "*.wal" -mtime -1 | while read wal_file; do
            if [ -f "$wal_file" ]; then
                cp "$wal_file" "$wal_backup_dir/"
                log_info "Copied WAL file: $(basename "$wal_file")"
            fi
        done
        
        log_success "WAL backup completed"
        echo "$wal_backup_dir"
    else
        log_warning "WAL directory not found, skipping WAL backup"
    fi
}

# Schema-only backup
schema_backup() {
    log_info "Starting schema-only backup..."
    
    local schema_file="$BACKUP_DIR/full/schema_${TIMESTAMP}.sql"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --schema-only \
        --format=plain \
        > "$schema_file" 2>"$BACKUP_DIR/logs/schema_backup_${TIMESTAMP}.log"
    
    if [ $? -eq 0 ]; then
        gzip "$schema_file"
        log_success "Schema backup completed: ${schema_file}.gz"
        echo "${schema_file}.gz"
    else
        log_error "Schema backup failed"
        exit 1
    fi
}

# Data-only backup
data_backup() {
    log_info "Starting data-only backup..."
    
    local data_file="$BACKUP_DIR/full/data_${TIMESTAMP}.sql"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --data-only \
        --format=plain \
        > "$data_file" 2>"$BACKUP_DIR/logs/data_backup_${TIMESTAMP}.log"
    
    if [ $? -eq 0 ]; then
        gzip "$data_file"
        log_success "Data backup completed: ${data_file}.gz"
        echo "${data_file}.gz"
    else
        log_error "Data backup failed"
        exit 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Full backups
    find "$BACKUP_DIR/full" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/full" -name "*.dump" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/full" -name "*.sha256" -mtime +$RETENTION_DAYS -delete
    
    # WAL backups
    find "$BACKUP_DIR/wal" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    # Log files
    find "$BACKUP_DIR/logs" -name "*.log" -mtime +$RETENTION_DAYS -delete
    
    log_success "Cleanup completed"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Verifying backup integrity..."
    
    # Check checksum if available
    if [ -f "${backup_file}.sha256" ]; then
        if sha256sum -c "${backup_file}.sha256" >/dev/null 2>&1; then
            log_success "Checksum verification passed"
        else
            log_error "Checksum verification failed"
            return 1
        fi
    fi
    
    # Test if file can be read
    if [[ "$backup_file" == *.gz ]]; then
        if gzip -t "$backup_file" 2>/dev/null; then
            log_success "Gzip integrity check passed"
        else
            log_error "Gzip integrity check failed"
            return 1
        fi
    elif [[ "$backup_file" == *.dump ]]; then
        if PGPASSWORD="$POSTGRES_PASSWORD" pg_restore --list "$backup_file" >/dev/null 2>&1; then
            log_success "Custom format integrity check passed"
        else
            log_error "Custom format integrity check failed"
            return 1
        fi
    fi
    
    log_success "Backup integrity verified"
}

# Create backup metadata
create_metadata() {
    local backup_file="$1"
    local metadata_file="${backup_file}.metadata"
    
    cat > "$metadata_file" << EOF
{
    "backup_timestamp": "$TIMESTAMP",
    "backup_type": "$BACKUP_TYPE",
    "database_name": "$POSTGRES_DB",
    "database_size": "$(get_database_size)",
    "backup_size": "$(du -h "$backup_file" | cut -f1)",
    "postgres_version": "$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT version();" | head -1 | xargs)",
    "server_hostname": "$(hostname)",
    "backup_command": "$0 $*"
}
EOF
    
    log_success "Metadata created: $metadata_file"
}

# Main function
main() {
    echo -e "${BLUE}Starting backup process at $(date)${NC}"
    
    # Setup
    setup_directories
    check_database
    
    local backup_file=""
    
    # Perform backup based on type
    case "$BACKUP_TYPE" in
        "full")
            backup_file=$(full_backup)
            ;;
        "custom")
            backup_file=$(custom_backup)
            ;;
        "schema")
            backup_file=$(schema_backup)
            ;;
        "data")
            backup_file=$(data_backup)
            ;;
        "wal")
            backup_file=$(wal_backup)
            ;;
        *)
            log_error "Unknown backup type: $BACKUP_TYPE"
            echo "Usage: $0 [full|custom|schema|data|wal]"
            exit 1
            ;;
    esac
    
    # Post-backup tasks
    if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
        verify_backup "$backup_file"
        create_metadata "$backup_file"
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    echo -e "\n${GREEN}Backup Summary:${NC}"
    echo "- Backup type: $BACKUP_TYPE"
    echo "- Backup file: $backup_file"
    echo "- Database: $POSTGRES_DB"
    echo "- Retention: $RETENTION_DAYS days"
    echo "- Status: SUCCESS"
    
    log_success "Backup process completed at $(date)"
}

# Help function
show_help() {
    echo "PyLadies Seoul Database Backup Script"
    echo ""
    echo "Usage: $0 [BACKUP_TYPE]"
    echo ""
    echo "Backup Types:"
    echo "  full     - Complete database backup (default)"
    echo "  custom   - Custom format backup (faster restore)"
    echo "  schema   - Schema-only backup"
    echo "  data     - Data-only backup"
    echo "  wal      - WAL archive backup"
    echo ""
    echo "Environment Variables:"
    echo "  POSTGRES_DB            - Database name (default: pyladies_seoul)"
    echo "  POSTGRES_USER          - Database user (default: postgres)"
    echo "  POSTGRES_PASSWORD      - Database password"
    echo "  POSTGRES_HOST          - Database host (default: db)"
    echo "  POSTGRES_PORT          - Database port (default: 5432)"
    echo "  BACKUP_DIR             - Backup directory (default: /backups)"
    echo "  BACKUP_RETENTION_DAYS  - Retention in days (default: 7)"
}

# Check for help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# Run main function
main "$@"