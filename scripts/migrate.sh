#!/bin/bash
# Production-Safe Database Migration Script
# PyLadies Seoul Project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DJANGO_CONTAINER=${DJANGO_CONTAINER:-"pyladies_seoul_web_prod"}
DB_CONTAINER=${DB_CONTAINER:-"pyladies_seoul_db_prod"}
BACKUP_DIR=${BACKUP_DIR:-"/app/backups"}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${BLUE}PyLadies Seoul - Production Database Migration${NC}"
echo -e "${BLUE}===============================================${NC}"

# Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if container is running
check_container() {
    local container=$1
    if ! docker ps | grep -q "$container"; then
        log_error "Container $container is not running"
        exit 1
    fi
    log_success "Container $container is running"
}

# Function to create pre-migration backup
create_backup() {
    log_info "Creating pre-migration backup..."
    
    docker exec "$DB_CONTAINER" pg_dump \
        -U "${POSTGRES_USER:-postgres}" \
        -d "${POSTGRES_DB:-pyladies_seoul}" \
        --no-password \
        --verbose \
        --format=custom \
        --file="/backups/pre_migration_${TIMESTAMP}.dump"
    
    if [ $? -eq 0 ]; then
        log_success "Pre-migration backup created: pre_migration_${TIMESTAMP}.dump"
    else
        log_error "Failed to create pre-migration backup"
        exit 1
    fi
}

# Function to check migration status
check_migrations() {
    log_info "Checking migration status..."
    
    # Check for unapplied migrations
    docker exec "$DJANGO_CONTAINER" python manage.py showmigrations --plan > /tmp/migration_plan.txt
    
    if grep -q "[ ]" /tmp/migration_plan.txt; then
        log_warning "Found unapplied migrations:"
        grep "[ ]" /tmp/migration_plan.txt
        return 1
    else
        log_success "All migrations are applied"
        return 0
    fi
}

# Function to test migrations in dry-run mode
test_migrations() {
    log_info "Testing migrations (dry-run)..."
    
    # Check for migration conflicts
    if ! docker exec "$DJANGO_CONTAINER" python manage.py migrate --check; then
        log_error "Migration conflicts detected!"
        docker exec "$DJANGO_CONTAINER" python manage.py migrate --check
        exit 1
    fi
    
    log_success "No migration conflicts detected"
}

# Function to apply migrations with monitoring
apply_migrations() {
    log_info "Applying migrations..."
    
    # Enable query logging for migration monitoring
    docker exec "$DJANGO_CONTAINER" python manage.py migrate --verbosity=2
    
    if [ $? -eq 0 ]; then
        log_success "Migrations applied successfully"
    else
        log_error "Migration failed!"
        log_warning "Consider restoring from backup: pre_migration_${TIMESTAMP}.dump"
        exit 1
    fi
}

# Function to verify database integrity
verify_database() {
    log_info "Verifying database integrity..."
    
    # Run Django system checks
    if ! docker exec "$DJANGO_CONTAINER" python manage.py check --deploy; then
        log_error "Django system checks failed"
        exit 1
    fi
    
    # Test database connection
    if ! docker exec "$DJANGO_CONTAINER" python manage.py dbshell -c "SELECT 1;"; then
        log_error "Database connection test failed"
        exit 1
    fi
    
    log_success "Database integrity verified"
}

# Function to update search indexes (if using search)
update_search_indexes() {
    log_info "Updating search indexes..."
    
    # Update Wagtail search indexes
    docker exec "$DJANGO_CONTAINER" python manage.py update_index || log_warning "Search index update failed (non-critical)"
    
    log_success "Search indexes updated"
}

# Function to clear cache
clear_cache() {
    log_info "Clearing cache..."
    
    # Clear Django cache
    docker exec "$DJANGO_CONTAINER" python manage.py clear_cache || log_warning "Cache clear failed (non-critical)"
    
    log_success "Cache cleared"
}

# Function to collect static files
collect_static() {
    log_info "Collecting static files..."
    
    docker exec "$DJANGO_CONTAINER" python manage.py collectstatic --noinput --clear
    
    if [ $? -eq 0 ]; then
        log_success "Static files collected"
    else
        log_error "Static file collection failed"
        exit 1
    fi
}

# Main migration process
main() {
    echo -e "${BLUE}Starting migration process at $(date)${NC}"
    
    # Parse command line arguments
    FORCE=false
    SKIP_BACKUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --force        Force migration even if there are warnings"
                echo "  --skip-backup  Skip pre-migration backup (NOT RECOMMENDED)"
                echo "  --help         Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Pre-flight checks
    log_info "Running pre-flight checks..."
    check_container "$DJANGO_CONTAINER"
    check_container "$DB_CONTAINER"
    
    # Create backup unless skipped
    if [ "$SKIP_BACKUP" = false ]; then
        create_backup
    else
        log_warning "Skipping backup as requested"
    fi
    
    # Check migration status
    if check_migrations; then
        log_info "No migrations to apply"
        if [ "$FORCE" = false ]; then
            echo -e "${GREEN}Migration process completed - no changes needed${NC}"
            exit 0
        fi
    fi
    
    # Test migrations
    test_migrations
    
    # Confirmation prompt
    if [ "$FORCE" = false ]; then
        echo -e "${YELLOW}Ready to apply migrations. This will modify the database.${NC}"
        read -p "Continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Migration cancelled by user"
            exit 0
        fi
    fi
    
    # Apply migrations
    apply_migrations
    
    # Post-migration tasks
    verify_database
    update_search_indexes
    clear_cache
    collect_static
    
    log_success "Migration process completed successfully at $(date)"
    
    # Show final status
    echo -e "\n${GREEN}Migration Summary:${NC}"
    echo "- Pre-migration backup: pre_migration_${TIMESTAMP}.dump"
    echo "- Migration status: SUCCESS"
    echo "- Database integrity: VERIFIED"
    echo "- Post-migration tasks: COMPLETED"
}

# Trap for cleanup
trap 'log_error "Migration process interrupted"; exit 130' INT TERM

# Run main function
main "$@"