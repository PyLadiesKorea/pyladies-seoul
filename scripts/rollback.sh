#!/bin/bash
# Rollback Script for PyLadies Seoul
# Provides comprehensive rollback capabilities for production deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}PyLadies Seoul Rollback System${NC}"
echo -e "${BLUE}==============================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="backups"
ROLLBACK_TYPE="$1"
TARGET_VERSION="$2"

# Show help
show_help() {
    echo "PyLadies Seoul Rollback Script"
    echo ""
    echo "Usage: $0 [rollback_type] [options]"
    echo ""
    echo "Rollback Types:"
    echo "  --to-previous       Rollback to previous deployment"
    echo "  --to-version=VER    Rollback to specific version"
    echo "  --to-backup=FILE    Rollback to specific backup file"
    echo "  --containers-only   Rollback containers only (no database)"
    echo ""
    echo "Options:"
    echo "  --force             Skip confirmation prompts"
    echo "  --skip-backup       Skip creating rollback backup"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --to-previous"
    echo "  $0 --to-version=v1.0.0"
    echo "  $0 --to-backup=/backups/pre_deployment_20231201_120000.sql.gz"
}

# Enable maintenance mode
enable_maintenance_mode() {
    log_info "Enabling maintenance mode..."
    
    if docker-compose -f "$COMPOSE_FILE" ps nginx | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" exec -T nginx \
            cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf 2>/dev/null || \
        docker-compose -f "$COMPOSE_FILE" exec -T nginx \
            sh -c 'echo "server { listen 80; return 503 \"Service temporarily unavailable for maintenance\"; }" > /etc/nginx/conf.d/default.conf'
        
        docker-compose -f "$COMPOSE_FILE" exec -T nginx nginx -s reload
        log_success "Maintenance mode enabled"
    else
        log_warning "Nginx container not running, skipping maintenance mode"
    fi
}

# Disable maintenance mode
disable_maintenance_mode() {
    log_info "Disabling maintenance mode..."
    
    if docker-compose -f "$COMPOSE_FILE" ps nginx | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" exec -T nginx \
            cp /etc/nginx/conf.d/production.conf /etc/nginx/conf.d/default.conf
        
        docker-compose -f "$COMPOSE_FILE" exec -T nginx nginx -s reload
        log_success "Maintenance mode disabled"
    else
        log_warning "Nginx container not running, skipping maintenance mode disable"
    fi
}

# Create rollback backup
create_rollback_backup() {
    log_info "Creating rollback backup..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/rollback_backup_${timestamp}.sql.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" exec -T db \
            pg_dump -U postgres pyladies_seoul | gzip > "$backup_file"
        
        if [ $? -eq 0 ]; then
            log_success "Rollback backup created: $backup_file"
            echo "$backup_file"
        else
            log_error "Failed to create rollback backup"
            exit 1
        fi
    else
        log_warning "Database container not running, skipping backup"
    fi
}

# Get previous deployment info
get_previous_deployment() {
    log_info "Identifying previous deployment..."
    
    # Look for previous Docker images
    local current_image=$(docker-compose -f "$COMPOSE_FILE" config | grep "image:" | head -1 | awk '{print $2}')
    local previous_images=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep pyladies-seoul | grep -v latest | head -5)
    
    echo "Current image: $current_image"
    echo "Available images for rollback:"
    echo "$previous_images"
    
    # Get the previous image (second in the list, first is current)
    local previous_image=$(echo "$previous_images" | sed -n '2p')
    
    if [ -n "$previous_image" ]; then
        echo "$previous_image"
    else
        log_error "No previous image found for rollback"
        exit 1
    fi
}

# Rollback to previous deployment
rollback_to_previous() {
    log_info "Rolling back to previous deployment..."
    
    local previous_image=$(get_previous_deployment)
    log_info "Rolling back to image: $previous_image"
    
    # Update docker-compose file to use previous image
    sed -i.bak "s|image: .*|image: $previous_image|g" "$COMPOSE_FILE"
    
    # Restart containers
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Rollback to previous deployment completed"
}

# Rollback to specific version
rollback_to_version() {
    local version="$1"
    log_info "Rolling back to version: $version"
    
    # Check if image exists locally or pull it
    local image_name="ghcr.io/pyladies-seoul/production:$version"
    
    if ! docker image inspect "$image_name" >/dev/null 2>&1; then
        log_info "Pulling image: $image_name"
        if ! docker pull "$image_name"; then
            log_error "Failed to pull image: $image_name"
            exit 1
        fi
    fi
    
    # Update docker-compose file
    sed -i.bak "s|image: .*|image: $image_name|g" "$COMPOSE_FILE"
    
    # Restart containers
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Rollback to version $version completed"
}

# Rollback to specific backup
rollback_to_backup() {
    local backup_file="$1"
    log_info "Rolling back to backup: $backup_file"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    # Stop application containers
    docker-compose -f "$COMPOSE_FILE" stop web
    
    # Restore database
    if [[ "$backup_file" == *.gz ]]; then
        log_info "Restoring compressed backup..."
        gunzip -c "$backup_file" | docker-compose -f "$COMPOSE_FILE" exec -T db \
            psql -U postgres -d pyladies_seoul
    else
        log_info "Restoring uncompressed backup..."
        docker-compose -f "$COMPOSE_FILE" exec -T db \
            psql -U postgres -d pyladies_seoul < "$backup_file"
    fi
    
    # Start application containers
    docker-compose -f "$COMPOSE_FILE" start web
    
    log_success "Rollback to backup completed"
}

# Rollback containers only
rollback_containers_only() {
    log_info "Rolling back containers only (preserving database)..."
    
    case "$ROLLBACK_TYPE" in
        "--to-previous")
            rollback_to_previous
            ;;
        "--to-version="*)
            local version="${ROLLBACK_TYPE#--to-version=}"
            rollback_to_version "$version"
            ;;
        *)
            log_error "Invalid rollback type for containers-only rollback"
            exit 1
            ;;
    esac
}

# Verify rollback
verify_rollback() {
    log_info "Verifying rollback..."
    
    # Wait for containers to be ready
    local timeout=120
    local count=0
    
    while [ $count -lt $timeout ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T web curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
            log_success "Application is responding"
            break
        fi
        
        echo "Waiting for application to respond... ($count/$timeout)"
        sleep 2
        count=$((count + 2))
    done
    
    if [ $count -ge $timeout ]; then
        log_error "Application failed to respond after rollback"
        return 1
    fi
    
    # Test database connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py check --settings=config.settings.production >/dev/null 2>&1; then
        log_success "Database connectivity verified"
    else
        log_error "Database connectivity check failed"
        return 1
    fi
    
    # Test external access (if not in maintenance mode)
    if curl -f -s https://pyladiesseoul.org/health/ >/dev/null 2>&1; then
        log_success "External access verified"
    else
        log_warning "External access check failed (may be in maintenance mode)"
    fi
    
    log_success "Rollback verification completed"
}

# Main rollback function
perform_rollback() {
    local rollback_type="$1"
    local force="$2"
    local skip_backup="$3"
    local containers_only="$4"
    
    # Confirmation prompt
    if [ "$force" != "true" ]; then
        echo -e "${YELLOW}WARNING: This will rollback your production deployment!${NC}"
        echo "Rollback type: $rollback_type"
        read -p "Are you sure you want to continue? [y/N] " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Rollback cancelled by user"
            exit 0
        fi
    fi
    
    # Enable maintenance mode
    enable_maintenance_mode
    
    # Create rollback backup unless skipped
    local rollback_backup=""
    if [ "$skip_backup" != "true" ]; then
        rollback_backup=$(create_rollback_backup)
    fi
    
    # Perform rollback based on type
    if [ "$containers_only" = "true" ]; then
        rollback_containers_only
    else
        case "$rollback_type" in
            "--to-previous")
                rollback_to_previous
                ;;
            "--to-version="*)
                local version="${rollback_type#--to-version=}"
                rollback_to_version "$version"
                ;;
            "--to-backup="*)
                local backup_file="${rollback_type#--to-backup=}"
                rollback_to_backup "$backup_file"
                ;;
            *)
                log_error "Unknown rollback type: $rollback_type"
                exit 1
                ;;
        esac
    fi
    
    # Verify rollback
    if verify_rollback; then
        # Disable maintenance mode
        disable_maintenance_mode
        
        echo -e "\n${GREEN}Rollback Summary:${NC}"
        echo "- Rollback type: $rollback_type"
        echo "- Rollback backup: ${rollback_backup:-"None"}"
        echo "- Status: SUCCESS"
        echo "- Completed at: $(date)"
        
        log_success "Rollback completed successfully!"
    else
        log_error "Rollback verification failed!"
        log_warning "System is in maintenance mode. Manual intervention required."
        exit 1
    fi
}

# Main function
main() {
    # Parse command line arguments
    local force=false
    local skip_backup=false
    local containers_only=false
    local rollback_type=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --to-previous|--to-version=*|--to-backup=*)
                rollback_type="$1"
                shift
                ;;
            --containers-only)
                containers_only=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [ -z "$rollback_type" ]; then
        log_error "No rollback type specified"
        show_help
        exit 1
    fi
    
    echo -e "${BLUE}Starting rollback process at $(date)${NC}"
    
    # Perform rollback
    perform_rollback "$rollback_type" "$force" "$skip_backup" "$containers_only"
}

# Trap for cleanup
trap 'log_error "Rollback process interrupted"; exit 130' INT TERM

# Run main function
main "$@"