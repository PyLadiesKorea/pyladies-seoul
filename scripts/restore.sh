#!/bin/bash
# Database Restore Script for PyLadies Seoul
# Supports restoration from various backup formats

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
BACKUP_FILE="$1"

echo -e "${BLUE}PyLadies Seoul Database Restore System${NC}"
echo -e "${BLUE}=====================================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show help
show_help() {
    echo "PyLadies Seoul Database Restore Script"
    echo ""
    echo "Usage: $0 <backup_file> [options]"
    echo ""
    echo "Options:"
    echo "  --force              Force restore without confirmation"
    echo "  --create-db          Create database if it doesn't exist"
    echo "  --clean              Clean existing data before restore"
    echo "  --help               Show this help message"
    echo ""
    echo "Supported backup formats:"
    echo "  - Plain SQL files (.sql, .sql.gz)"
    echo "  - Custom format files (.dump)"
    echo "  - Directory format backups"
    echo ""
    echo "Examples:"
    echo "  $0 /backups/full/full_backup_20231201_120000.sql.gz"
    echo "  $0 /backups/full/custom_backup_20231201_120000.dump --clean"
    echo "  $0 latest  # Restore from latest backup"
}

# Check if backup file exists and is valid
validate_backup_file() {
    local file="$1"
    
    if [ "$file" = "latest" ]; then
        # Find latest backup
        local latest_sql=$(find "$BACKUP_DIR/full" -name "*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        local latest_dump=$(find "$BACKUP_DIR/full" -name "*.dump" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        
        if [ -n "$latest_dump" ] && [ -n "$latest_sql" ]; then
            # Compare timestamps and choose newer
            if [ "$latest_dump" -nt "$latest_sql" ]; then
                file="$latest_dump"
            else
                file="$latest_sql"
            fi
        elif [ -n "$latest_dump" ]; then
            file="$latest_dump"
        elif [ -n "$latest_sql" ]; then
            file="$latest_sql"
        else
            log_error "No backup files found in $BACKUP_DIR/full"
            exit 1
        fi
        
        log_info "Using latest backup: $file"
    fi
    
    if [ ! -f "$file" ]; then
        log_error "Backup file not found: $file"
        exit 1
    fi
    
    # Verify checksum if available
    if [ -f "${file}.sha256" ]; then
        log_info "Verifying backup checksum..."
        if sha256sum -c "${file}.sha256" >/dev/null 2>&1; then
            log_success "Checksum verification passed"
        else
            log_error "Checksum verification failed"
            exit 1
        fi
    fi
    
    echo "$file"
}

# Detect backup format
detect_backup_format() {
    local file="$1"
    
    if [[ "$file" == *.sql.gz ]]; then
        echo "sql_gz"
    elif [[ "$file" == *.sql ]]; then
        echo "sql"
    elif [[ "$file" == *.dump ]]; then
        echo "custom"
    elif [ -d "$file" ]; then
        echo "directory"
    else
        log_error "Unknown backup format: $file"
        exit 1
    fi
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    if ! PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; then
        log_error "Cannot connect to PostgreSQL server"
        exit 1
    fi
    
    log_success "Database server is accessible"
}

# Check if database exists
database_exists() {
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"
}

# Create database if it doesn't exist
create_database() {
    log_info "Creating database: $POSTGRES_DB"
    
    PGPASSWORD="$POSTGRES_PASSWORD" createdb \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -O "$POSTGRES_USER" \
        "$POSTGRES_DB"
    
    log_success "Database created: $POSTGRES_DB"
}

# Create pre-restore backup
create_pre_restore_backup() {
    if database_exists; then
        log_info "Creating pre-restore backup..."
        
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="$BACKUP_DIR/full/pre_restore_${timestamp}.sql.gz"
        
        mkdir -p "$BACKUP_DIR/full"
        
        PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
            -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            --verbose \
            --no-password | gzip > "$backup_file"
        
        if [ $? -eq 0 ]; then
            log_success "Pre-restore backup created: $backup_file"
            echo "$backup_file"
        else
            log_error "Failed to create pre-restore backup"
            exit 1
        fi
    else
        log_info "Database doesn't exist, skipping pre-restore backup"
    fi
}

# Clean existing data
clean_database() {
    log_info "Cleaning existing database data..."
    
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO $POSTGRES_USER; GRANT ALL ON SCHEMA public TO public;"
    
    log_success "Database cleaned"
}

# Restore from SQL file
restore_sql() {
    local file="$1"
    local is_compressed="$2"
    
    log_info "Restoring from SQL file: $file"
    
    if [ "$is_compressed" = "true" ]; then
        gunzip -c "$file" | PGPASSWORD="$POSTGRES_PASSWORD" psql \
            -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            -v ON_ERROR_STOP=1
    else
        PGPASSWORD="$POSTGRES_PASSWORD" psql \
            -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            -v ON_ERROR_STOP=1 \
            -f "$file"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "SQL restore completed"
    else
        log_error "SQL restore failed"
        exit 1
    fi
}

# Restore from custom format
restore_custom() {
    local file="$1"
    
    log_info "Restoring from custom format file: $file"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --clean \
        --if-exists \
        "$file"
    
    if [ $? -eq 0 ]; then
        log_success "Custom format restore completed"
    else
        log_error "Custom format restore failed"
        exit 1
    fi
}

# Restore from directory format
restore_directory() {
    local dir="$1"
    
    log_info "Restoring from directory format: $dir"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-password \
        --clean \
        --if-exists \
        "$dir"
    
    if [ $? -eq 0 ]; then
        log_success "Directory format restore completed"
    else
        log_error "Directory format restore failed"
        exit 1
    fi
}

# Verify restore
verify_restore() {
    log_info "Verifying restore..."
    
    # Check if database has tables
    local table_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    
    table_count=$(echo $table_count | xargs)
    
    if [ "$table_count" -gt 0 ]; then
        log_success "Database contains $table_count tables"
    else
        log_error "No tables found in restored database"
        exit 1
    fi
    
    # Test basic connectivity
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -c "SELECT 1;" >/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Database connectivity verified"
    else
        log_error "Database connectivity test failed"
        exit 1
    fi
}

# Show backup info
show_backup_info() {
    local file="$1"
    
    echo -e "\n${BLUE}Backup Information:${NC}"
    echo "- File: $file"
    echo "- Size: $(du -h "$file" | cut -f1)"
    echo "- Modified: $(stat -c %y "$file")"
    
    # Show metadata if available
    if [ -f "${file}.metadata" ]; then
        echo -e "\n${BLUE}Backup Metadata:${NC}"
        cat "${file}.metadata" | python3 -m json.tool 2>/dev/null || cat "${file}.metadata"
    fi
}

# Main function
main() {
    # Parse command line arguments
    FORCE=false
    CREATE_DB=false
    CLEAN=false
    
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE=true
                shift
                ;;
            --create-db)
                CREATE_DB=true
                shift
                ;;
            --clean)
                CLEAN=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                if [ -z "$BACKUP_FILE" ]; then
                    BACKUP_FILE="$1"
                else
                    log_error "Unknown option: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$BACKUP_FILE" ]; then
        log_error "No backup file specified"
        show_help
        exit 1
    fi
    
    echo -e "${BLUE}Starting restore process at $(date)${NC}"
    
    # Validate inputs
    BACKUP_FILE=$(validate_backup_file "$BACKUP_FILE")
    BACKUP_FORMAT=$(detect_backup_format "$BACKUP_FILE")
    
    # Show backup info
    show_backup_info "$BACKUP_FILE"
    
    # Pre-flight checks
    check_database
    
    # Handle database creation
    if ! database_exists; then
        if [ "$CREATE_DB" = "true" ]; then
            create_database
        else
            log_error "Database '$POSTGRES_DB' does not exist. Use --create-db to create it."
            exit 1
        fi
    fi
    
    # Confirmation prompt
    if [ "$FORCE" = "false" ]; then
        echo -e "\n${YELLOW}WARNING: This will restore data to database '$POSTGRES_DB'.${NC}"
        if [ "$CLEAN" = "true" ]; then
            echo -e "${RED}All existing data will be DELETED!${NC}"
        fi
        read -p "Continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Restore cancelled by user"
            exit 0
        fi
    fi
    
    # Create pre-restore backup
    local pre_restore_backup=""
    if [ "$CLEAN" = "true" ] || [ "$FORCE" = "false" ]; then
        pre_restore_backup=$(create_pre_restore_backup)
    fi
    
    # Clean database if requested
    if [ "$CLEAN" = "true" ]; then
        clean_database
    fi
    
    # Perform restore based on format
    case "$BACKUP_FORMAT" in
        "sql_gz")
            restore_sql "$BACKUP_FILE" true
            ;;
        "sql")
            restore_sql "$BACKUP_FILE" false
            ;;
        "custom")
            restore_custom "$BACKUP_FILE"
            ;;
        "directory")
            restore_directory "$BACKUP_FILE"
            ;;
        *)
            log_error "Unsupported backup format: $BACKUP_FORMAT"
            exit 1
            ;;
    esac
    
    # Verify restore
    verify_restore
    
    echo -e "\n${GREEN}Restore Summary:${NC}"
    echo "- Backup file: $BACKUP_FILE"
    echo "- Backup format: $BACKUP_FORMAT"
    echo "- Database: $POSTGRES_DB"
    echo "- Pre-restore backup: ${pre_restore_backup:-"None"}"
    echo "- Status: SUCCESS"
    
    log_success "Restore process completed at $(date)"
}

# Run main function
main "$@"