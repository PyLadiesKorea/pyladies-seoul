#!/bin/bash
# Master Deployment Script for PyLadies Seoul
# Orchestrates the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}PyLadies Seoul Master Deployment Script${NC}"
echo -e "${BLUE}=======================================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
ENVIRONMENT="${1:-production}"
VERSION="${2:-latest}"
FORCE="${3:-false}"

# Show help
show_help() {
    echo "PyLadies Seoul Master Deployment Script"
    echo ""
    echo "Usage: $0 [environment] [version] [force]"
    echo ""
    echo "Environments:"
    echo "  production    Deploy to production (default)"
    echo "  staging       Deploy to staging"
    echo "  development   Deploy to development"
    echo ""
    echo "Options:"
    echo "  version       Version to deploy (default: latest)"
    echo "  force         Force deployment without confirmations (true/false)"
    echo ""
    echo "Examples:"
    echo "  $0 production v1.2.0"
    echo "  $0 staging latest true"
    echo "  $0 development"
}

# Pre-deployment checks
run_pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if required files exist
    local required_files=(
        "docker-compose.yml"
        "docker-compose.prod.yml"
        "docker-compose.staging.yml"
        "Dockerfile"
        ".env.example"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Check if scripts are executable
    local scripts=(
        "scripts/backup.sh"
        "scripts/restore.sh"
        "scripts/migrate.sh"
        "scripts/setup-ssl.sh"
        "scripts/health-check.sh"
        "scripts/rollback.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ ! -x "$script" ]; then
            log_error "Script not executable: $script"
            exit 1
        fi
    done
    
    log_success "Pre-deployment checks passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up $ENVIRONMENT environment..."
    
    case "$ENVIRONMENT" in
        "production")
            COMPOSE_FILE="docker-compose.prod.yml"
            DOMAIN="pyladiesseoul.org"
            ;;
        "staging")
            COMPOSE_FILE="docker-compose.staging.yml"
            DOMAIN="staging.pyladiesseoul.org"
            ;;
        "development")
            COMPOSE_FILE="docker-compose.yml"
            DOMAIN="localhost"
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    log_success "Environment set to $ENVIRONMENT"
    export COMPOSE_FILE DOMAIN
}

# Initialize secrets (for first-time deployment)
initialize_secrets() {
    if [ ! -d "secrets" ]; then
        log_info "Initializing secrets for first-time deployment..."
        ./scripts/setup-secrets.sh
        
        log_warning "IMPORTANT: Please update the secret files with real values before continuing!"
        if [ "$FORCE" != "true" ]; then
            read -p "Have you updated all secret files? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Deployment paused for secret configuration"
                exit 0
            fi
        fi
    fi
}

# Create backup before deployment
create_deployment_backup() {
    log_info "Creating pre-deployment backup..."
    
    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        ./scripts/backup.sh full
        log_success "Pre-deployment backup created"
    else
        log_warning "Database not running, skipping backup"
    fi
}

# Deploy application
deploy_application() {
    log_info "Deploying application ($ENVIRONMENT - $VERSION)..."
    
    # Set build arguments
    export BUILD_DATE=$(date -Iseconds)
    export GIT_COMMIT=$(git rev-parse HEAD)
    export IMAGE_TAG="$VERSION"
    
    case "$ENVIRONMENT" in
        "production")
            deploy_production
            ;;
        "staging")
            deploy_staging
            ;;
        "development")
            deploy_development
            ;;
    esac
}

# Production deployment
deploy_production() {
    log_info "Starting production deployment..."
    
    # Enable maintenance mode if nginx is running
    if docker-compose -f "$COMPOSE_FILE" ps nginx 2>/dev/null | grep -q "Up"; then
        log_info "Enabling maintenance mode..."
        docker-compose -f "$COMPOSE_FILE" exec -T nginx \
            cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true
        docker-compose -f "$COMPOSE_FILE" exec -T nginx nginx -s reload 2>/dev/null || true
    fi
    
    # Build and deploy with zero-downtime
    docker-compose -f "$COMPOSE_FILE" build
    docker-compose -f "$COMPOSE_FILE" up -d --scale web=2
    
    # Wait for new containers to be healthy
    log_info "Waiting for containers to be healthy..."
    sleep 30
    
    # Run migrations
    ./scripts/migrate.sh --force
    
    # Collect static files
    log_info "Collecting static files..."
    docker-compose -f "$COMPOSE_FILE" exec -T web \
        python manage.py collectstatic --noinput --settings=config.settings.production
    
    # Scale back to normal
    docker-compose -f "$COMPOSE_FILE" up -d --scale web=1
    
    # Disable maintenance mode
    if docker-compose -f "$COMPOSE_FILE" ps nginx 2>/dev/null | grep -q "Up"; then
        log_info "Disabling maintenance mode..."
        docker-compose -f "$COMPOSE_FILE" exec -T nginx \
            cp /etc/nginx/conf.d/production.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true
        docker-compose -f "$COMPOSE_FILE" exec -T nginx nginx -s reload 2>/dev/null || true
    fi
    
    log_success "Production deployment completed"
}

# Staging deployment
deploy_staging() {
    log_info "Starting staging deployment..."
    
    # Simple deployment for staging
    docker-compose -f "$COMPOSE_FILE" build
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Run migrations
    ./scripts/migrate.sh --force
    
    # Collect static files
    docker-compose -f "$COMPOSE_FILE" exec -T web \
        python manage.py collectstatic --noinput --settings=config.settings.production
    
    log_success "Staging deployment completed"
}

# Development deployment
deploy_development() {
    log_info "Starting development deployment..."
    
    # Simple development deployment
    docker-compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml up -d
    
    # Run migrations
    docker-compose -f docker-compose.yml exec -T web python manage.py migrate
    
    # Collect static files
    docker-compose -f docker-compose.yml exec -T web python manage.py collectstatic --noinput
    
    log_success "Development deployment completed"
}

# Post-deployment verification
run_post_deployment_checks() {
    log_info "Running post-deployment verification..."
    
    # Wait for application to be ready
    local timeout=120
    local count=0
    
    while [ $count -lt $timeout ]; do
        if curl -f -s "http://localhost:8000/health/" >/dev/null 2>&1 || \
           curl -f -s "https://$DOMAIN/health/" >/dev/null 2>&1; then
            log_success "Application is responding"
            break
        fi
        
        echo "Waiting for application... ($count/$timeout)"
        sleep 5
        count=$((count + 5))
    done
    
    if [ $count -ge $timeout ]; then
        log_error "Application failed to respond after deployment"
        return 1
    fi
    
    # Run health check
    if ./scripts/health-check.sh; then
        log_success "Health check passed"
    else
        local exit_code=$?
        if [ $exit_code -eq 2 ]; then
            log_warning "Health check passed with warnings"
        else
            log_error "Health check failed"
            return 1
        fi
    fi
    
    log_success "Post-deployment verification completed"
}

# Setup SSL certificates (production only)
setup_ssl_certificates() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Setting up SSL certificates..."
        
        if [ ! -f "data/certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
            log_info "Initializing SSL certificates..."
            ./scripts/setup-ssl.sh init
        else
            log_info "SSL certificates already exist, checking renewal..."
            ./scripts/setup-ssl.sh renew --dry-run
        fi
    fi
}

# Send deployment notification
send_notification() {
    local status="$1"
    
    log_info "Sending deployment notification..."
    
    # Create deployment summary
    local summary=""
    summary+="Environment: $ENVIRONMENT\n"
    summary+="Version: $VERSION\n"
    summary+="Status: $status\n"
    summary+="Time: $(date)\n"
    summary+="Domain: https://$DOMAIN\n"
    
    echo -e "\n${BLUE}Deployment Summary:${NC}"
    echo -e "$summary"
    
    # Here you could add actual notification integrations
    # - Slack webhook
    # - Email notification
    # - Teams notification
    # etc.
}

# Main deployment flow
main() {
    local start_time=$(date +%s)
    
    # Parse arguments
    case "$1" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
    esac
    
    echo -e "${BLUE}Starting deployment at $(date)${NC}"
    echo -e "Environment: $ENVIRONMENT"
    echo -e "Version: $VERSION"
    echo -e "Force: $FORCE"
    echo ""
    
    # Confirmation for production
    if [ "$ENVIRONMENT" = "production" ] && [ "$FORCE" != "true" ]; then
        echo -e "${YELLOW}WARNING: You are about to deploy to PRODUCTION!${NC}"
        echo "This will affect the live website."
        read -p "Are you sure you want to continue? [y/N] " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled by user"
            exit 0
        fi
    fi
    
    # Deployment steps
    local deployment_error=false
    
    if ! run_pre_deployment_checks; then
        deployment_error=true
    elif ! setup_environment; then
        deployment_error=true
    elif ! initialize_secrets; then
        deployment_error=true
    elif ! create_deployment_backup; then
        deployment_error=true
    elif ! deploy_application; then
        deployment_error=true
    elif ! run_post_deployment_checks; then
        deployment_error=true
    elif ! setup_ssl_certificates; then
        deployment_error=true
    fi
    
    # Calculate deployment time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Handle deployment result
    if [ "$deployment_error" = "true" ]; then
        log_error "Deployment failed!"
        echo -e "\n${RED}❌ DEPLOYMENT FAILED${NC}"
        echo "Duration: ${duration}s"
        echo ""
        echo "To rollback, run:"
        echo "  ./scripts/rollback.sh --to-previous"
        
        send_notification "FAILED"
        exit 1
    else
        log_success "Deployment completed successfully!"
        echo -e "\n${GREEN}✅ DEPLOYMENT SUCCESSFUL${NC}"
        echo "Duration: ${duration}s"
        echo ""
        echo "Application URL: https://$DOMAIN"
        echo "Health Check: https://$DOMAIN/health/"
        
        send_notification "SUCCESS"
        exit 0
    fi
}

# Trap for cleanup
trap 'log_error "Deployment interrupted"; exit 130' INT TERM

# Run main function
main "$@"