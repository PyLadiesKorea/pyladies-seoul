#!/bin/bash
# SSL Certificate Setup Script for PyLadies Seoul
# Automated Let's Encrypt certificate management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN_NAME=${DOMAIN_NAME:-"pyladiesseoul.org"}
WWW_DOMAIN_NAME=${WWW_DOMAIN_NAME:-"www.pyladiesseoul.org"}
CERTBOT_EMAIL=${CERTBOT_EMAIL:-"admin@pyladiesseoul.org"}
WEBROOT_PATH="/var/www/certbot"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN_NAME}"
NGINX_CONTAINER="pyladies_seoul_nginx_prod"
STAGING=${STAGING:-false}

echo -e "${BLUE}PyLadies Seoul SSL Certificate Setup${NC}"
echo -e "${BLUE}===================================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show help
show_help() {
    echo "SSL Certificate Setup Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  init      Initialize SSL certificates (first time setup)"
    echo "  renew     Renew existing certificates"
    echo "  revoke    Revoke certificates"
    echo "  status    Show certificate status"
    echo "  test      Test SSL configuration"
    echo ""
    echo "Options:"
    echo "  --staging         Use Let's Encrypt staging environment"
    echo "  --force-renewal   Force certificate renewal"
    echo "  --dry-run         Test renewal without actually renewing"
    echo "  --help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DOMAIN_NAME       Primary domain (default: pyladiesseoul.org)"
    echo "  WWW_DOMAIN_NAME   WWW domain (default: www.pyladiesseoul.org)"
    echo "  CERTBOT_EMAIL     Email for Let's Encrypt (default: admin@pyladiesseoul.org)"
    echo "  STAGING           Use staging environment (default: false)"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if Nginx container is running
    if ! docker ps | grep -q "$NGINX_CONTAINER"; then
        log_warning "Nginx container is not running. Starting it..."
        docker-compose -f docker-compose.prod.yml up -d nginx
        sleep 10
    fi
    
    # Create webroot directory
    docker exec "$NGINX_CONTAINER" mkdir -p "$WEBROOT_PATH"
    
    log_success "Prerequisites checked"
}

# Test domain accessibility
test_domain_accessibility() {
    local domain="$1"
    
    log_info "Testing domain accessibility: $domain"
    
    # Test HTTP access
    if curl -f -s -o /dev/null "http://$domain/.well-known/acme-challenge/test" 2>/dev/null; then
        log_success "Domain $domain is accessible via HTTP"
    else
        # Create test file
        docker exec "$NGINX_CONTAINER" sh -c "echo 'test' > $WEBROOT_PATH/test"
        
        if curl -f -s "http://$domain/.well-known/acme-challenge/test" >/dev/null 2>&1; then
            log_success "Domain $domain is accessible via HTTP"
        else
            log_error "Domain $domain is not accessible. Check DNS and firewall settings."
            return 1
        fi
        
        # Clean up test file
        docker exec "$NGINX_CONTAINER" rm -f "$WEBROOT_PATH/test"
    fi
}

# Initialize SSL certificates
init_certificates() {
    log_info "Initializing SSL certificates..."
    
    # Test domain accessibility
    test_domain_accessibility "$DOMAIN_NAME"
    test_domain_accessibility "$WWW_DOMAIN_NAME"
    
    # Prepare certbot command
    local certbot_cmd="certbot certonly --webroot"
    local staging_flag=""
    
    if [ "$STAGING" = "true" ]; then
        staging_flag="--staging"
        log_warning "Using Let's Encrypt staging environment"
    fi
    
    # Create certificates
    docker run --rm \
        -v "$(pwd)/data/certbot/conf:/etc/letsencrypt" \
        -v "$(pwd)/data/certbot/www:/var/www/certbot" \
        certbot/certbot \
        $certbot_cmd \
        $staging_flag \
        --webroot-path=/var/www/certbot \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --no-eff-email \
        --expand \
        -d "$DOMAIN_NAME" \
        -d "$WWW_DOMAIN_NAME"
    
    if [ $? -eq 0 ]; then
        log_success "SSL certificates created successfully"
        
        # Reload Nginx to use new certificates
        docker exec "$NGINX_CONTAINER" nginx -s reload
        
        log_success "Nginx reloaded with new certificates"
    else
        log_error "Failed to create SSL certificates"
        exit 1
    fi
}

# Renew certificates
renew_certificates() {
    local force_renewal="$1"
    local dry_run="$2"
    
    log_info "Renewing SSL certificates..."
    
    local renew_args=""
    if [ "$force_renewal" = "true" ]; then
        renew_args="$renew_args --force-renewal"
        log_warning "Forcing certificate renewal"
    fi
    
    if [ "$dry_run" = "true" ]; then
        renew_args="$renew_args --dry-run"
        log_info "Running dry-run renewal test"
    fi
    
    # Renew certificates
    docker run --rm \
        -v "$(pwd)/data/certbot/conf:/etc/letsencrypt" \
        -v "$(pwd)/data/certbot/www:/var/www/certbot" \
        certbot/certbot \
        renew \
        $renew_args \
        --webroot \
        --webroot-path=/var/www/certbot
    
    if [ $? -eq 0 ]; then
        if [ "$dry_run" != "true" ]; then
            log_success "Certificates renewed successfully"
            
            # Reload Nginx
            docker exec "$NGINX_CONTAINER" nginx -s reload
            log_success "Nginx reloaded"
        else
            log_success "Dry-run renewal test passed"
        fi
    else
        log_error "Certificate renewal failed"
        exit 1
    fi
}

# Revoke certificates
revoke_certificates() {
    log_warning "Revoking SSL certificates..."
    
    echo -e "${RED}This will revoke your SSL certificates!${NC}"
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Certificate revocation cancelled"
        exit 0
    fi
    
    # Revoke certificates
    docker run --rm \
        -v "$(pwd)/data/certbot/conf:/etc/letsencrypt" \
        -v "$(pwd)/data/certbot/www:/var/www/certbot" \
        certbot/certbot \
        revoke \
        --cert-path "/etc/letsencrypt/live/${DOMAIN_NAME}/cert.pem" \
        --reason superseded
    
    if [ $? -eq 0 ]; then
        log_success "Certificates revoked successfully"
    else
        log_error "Certificate revocation failed"
        exit 1
    fi
}

# Show certificate status
show_certificate_status() {
    log_info "Certificate status for $DOMAIN_NAME:"
    
    local cert_file="$(pwd)/data/certbot/conf/live/${DOMAIN_NAME}/cert.pem"
    
    if [ -f "$cert_file" ]; then
        echo -e "\n${GREEN}Certificate found:${NC}"
        
        # Show certificate details
        openssl x509 -in "$cert_file" -noout -dates -subject -issuer
        
        # Check expiration
        local exp_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
        local exp_timestamp=$(date -d "$exp_date" +%s)
        local now_timestamp=$(date +%s)
        local days_until_exp=$(( (exp_timestamp - now_timestamp) / 86400 ))
        
        echo -e "\n${BLUE}Expiration Status:${NC}"
        if [ $days_until_exp -gt 30 ]; then
            echo -e "${GREEN}Certificate expires in $days_until_exp days${NC}"
        elif [ $days_until_exp -gt 7 ]; then
            echo -e "${YELLOW}Certificate expires in $days_until_exp days - consider renewal${NC}"
        else
            echo -e "${RED}Certificate expires in $days_until_exp days - URGENT renewal needed${NC}"
        fi
        
        # Show domains covered
        echo -e "\n${BLUE}Domains covered:${NC}"
        openssl x509 -in "$cert_file" -noout -text | grep -A1 "Subject Alternative Name" | tail -1 | sed 's/DNS://g' | tr ',' '\n' | sed 's/^[ \t]*//' | sort
        
    else
        echo -e "\n${RED}No certificate found${NC}"
        echo "Run '$0 init' to create initial certificates"
    fi
}

# Test SSL configuration
test_ssl_configuration() {
    log_info "Testing SSL configuration..."
    
    # Test certificate validity
    if openssl s_client -connect "${DOMAIN_NAME}:443" -servername "$DOMAIN_NAME" </dev/null 2>/dev/null | openssl x509 -noout -dates; then
        log_success "SSL certificate is valid"
    else
        log_error "SSL certificate test failed"
        return 1
    fi
    
    # Test SSL Labs API (if available)
    log_info "Running SSL Labs test (this may take a few minutes)..."
    
    # Use SSL Labs API to test the domain
    local api_url="https://api.ssllabs.com/api/v3/analyze?host=${DOMAIN_NAME}&publish=off&startNew=on&all=done"
    
    # This is a simplified test - in production you might want to use a more comprehensive tool
    if curl -s -f "https://$DOMAIN_NAME" >/dev/null; then
        log_success "HTTPS connection successful"
    else
        log_error "HTTPS connection failed"
        return 1
    fi
    
    # Test HTTP to HTTPS redirect
    local redirect_location=$(curl -s -I "http://$DOMAIN_NAME" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')
    
    if [[ $redirect_location == https://* ]]; then
        log_success "HTTP to HTTPS redirect is working"
    else
        log_warning "HTTP to HTTPS redirect may not be working properly"
    fi
    
    # Test security headers
    log_info "Checking security headers..."
    local headers=$(curl -s -I "https://$DOMAIN_NAME")
    
    if echo "$headers" | grep -qi "strict-transport-security"; then
        log_success "HSTS header is present"
    else
        log_warning "HSTS header is missing"
    fi
    
    if echo "$headers" | grep -qi "x-content-type-options"; then
        log_success "X-Content-Type-Options header is present"
    else
        log_warning "X-Content-Type-Options header is missing"
    fi
    
    if echo "$headers" | grep -qi "x-frame-options"; then
        log_success "X-Frame-Options header is present"
    else
        log_warning "X-Frame-Options header is missing"
    fi
}

# Create renewal cron job
setup_auto_renewal() {
    log_info "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > "$(pwd)/scripts/renew-certs.sh" << 'EOF'
#!/bin/bash
# Automatic certificate renewal script

cd "$(dirname "$0")/.."

# Renew certificates
./scripts/setup-ssl.sh renew

# Log the renewal attempt
echo "$(date): Certificate renewal attempted" >> /var/log/certbot-renewal.log
EOF
    
    chmod +x "$(pwd)/scripts/renew-certs.sh"
    
    # Add cron job (runs twice daily as recommended by Let's Encrypt)
    local cron_job="0 */12 * * * $(pwd)/scripts/renew-certs.sh >/dev/null 2>&1"
    
    (crontab -l 2>/dev/null | grep -v "renew-certs.sh"; echo "$cron_job") | crontab -
    
    log_success "Automatic renewal cron job added"
    log_info "Certificates will be checked for renewal twice daily"
}

# Main function
main() {
    local command="$1"
    shift
    
    # Parse options
    local force_renewal=false
    local dry_run=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --staging)
                STAGING=true
                shift
                ;;
            --force-renewal)
                force_renewal=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Create necessary directories
    mkdir -p "$(pwd)/data/certbot/conf"
    mkdir -p "$(pwd)/data/certbot/www"
    
    case "$command" in
        "init")
            check_prerequisites
            init_certificates
            setup_auto_renewal
            show_certificate_status
            ;;
        "renew")
            check_prerequisites
            renew_certificates "$force_renewal" "$dry_run"
            ;;
        "revoke")
            revoke_certificates
            ;;
        "status")
            show_certificate_status
            ;;
        "test")
            test_ssl_configuration
            ;;
        *)
            if [ -z "$command" ]; then
                show_help
            else
                log_error "Unknown command: $command"
                show_help
                exit 1
            fi
            ;;
    esac
}

# Run main function
main "$@"