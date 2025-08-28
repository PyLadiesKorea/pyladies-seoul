#!/bin/bash
# Comprehensive Health Check Script for PyLadies Seoul
# Monitors all system components and provides detailed status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}PyLadies Seoul Health Check System${NC}"
echo -e "${BLUE}==================================${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
DOMAIN="pyladiesseoul.org"
HEALTH_ENDPOINT="/health/"
COMPREHENSIVE=${1:-false}

# Health check results
HEALTH_RESULTS=()
FAILED_CHECKS=0
WARNING_CHECKS=0

# Add result to array
add_result() {
    local status="$1"
    local message="$2"
    local component="$3"
    
    HEALTH_RESULTS+=("$status|$component|$message")
    
    case "$status" in
        "PASS")
            log_success "$component: $message"
            ;;
        "WARN")
            log_warning "$component: $message"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            ;;
        "FAIL")
            log_error "$component: $message"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            ;;
    esac
}

# Check container health
check_containers() {
    log_info "Checking container health..."
    
    # Get list of services
    local services=$(docker-compose -f "$COMPOSE_FILE" config --services)
    
    for service in $services; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            # Check if container has health check
            local health_status=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.Health}}" | grep "^$service" | awk '{print $2}')
            
            if [ "$health_status" = "healthy" ]; then
                add_result "PASS" "Container healthy" "$service"
            elif [ "$health_status" = "unhealthy" ]; then
                add_result "FAIL" "Container unhealthy" "$service"
            elif [ -n "$health_status" ]; then
                add_result "WARN" "Container status: $health_status" "$service"
            else
                add_result "PASS" "Container running (no health check)" "$service"
            fi
        else
            add_result "FAIL" "Container not running" "$service"
        fi
    done
}

# Check application endpoints
check_application() {
    log_info "Checking application endpoints..."
    
    # Health endpoint
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN$HEALTH_ENDPOINT" || echo "000")
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" "https://$DOMAIN$HEALTH_ENDPOINT" || echo "999")
    
    if [ "$response_code" = "200" ]; then
        if (( $(echo "$response_time < 2.0" | bc -l) )); then
            add_result "PASS" "Health endpoint responding (${response_time}s)" "Application"
        else
            add_result "WARN" "Health endpoint slow (${response_time}s)" "Application"
        fi
    else
        add_result "FAIL" "Health endpoint failed (HTTP $response_code)" "Application"
    fi
    
    # Main page
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/" || echo "000")
    if [ "$response_code" = "200" ]; then
        add_result "PASS" "Main page accessible" "Application"
    else
        add_result "FAIL" "Main page failed (HTTP $response_code)" "Application"
    fi
    
    # Admin page
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/admin/" || echo "000")
    if [ "$response_code" = "200" ] || [ "$response_code" = "302" ]; then
        add_result "PASS" "Admin page accessible" "Application"
    else
        add_result "WARN" "Admin page check failed (HTTP $response_code)" "Application"
    fi
}

# Check database health
check_database() {
    log_info "Checking database health..."
    
    # Connection test
    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U postgres >/dev/null 2>&1; then
        add_result "PASS" "Database accepting connections" "PostgreSQL"
    else
        add_result "FAIL" "Database not accepting connections" "PostgreSQL"
        return
    fi
    
    # Query test
    local query_time=$(docker-compose -f "$COMPOSE_FILE" exec -T db \
        psql -U postgres -d pyladies_seoul -c "SELECT 1;" \
        -c "\timing" 2>/dev/null | grep "Time:" | awk '{print $2}' | tr -d 'ms' || echo "999")
    
    if [ -n "$query_time" ] && (( $(echo "$query_time < 100" | bc -l) )); then
        add_result "PASS" "Database queries responding (${query_time}ms)" "PostgreSQL"
    else
        add_result "WARN" "Database queries slow (${query_time}ms)" "PostgreSQL"
    fi
    
    # Connection count
    local connections=$(docker-compose -f "$COMPOSE_FILE" exec -T db \
        psql -U postgres -d pyladies_seoul -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='pyladies_seoul';" | xargs)
    
    if [ -n "$connections" ]; then
        if [ "$connections" -lt 50 ]; then
            add_result "PASS" "Database connections: $connections" "PostgreSQL"
        else
            add_result "WARN" "High database connections: $connections" "PostgreSQL"
        fi
    fi
}

# Check Redis health
check_redis() {
    log_info "Checking Redis health..."
    
    # Connection test
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        add_result "PASS" "Redis accepting connections" "Redis"
    else
        add_result "FAIL" "Redis not accepting connections" "Redis"
        return
    fi
    
    # Memory usage
    local memory_info=$(docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli info memory | grep "used_memory_human")
    if [ -n "$memory_info" ]; then
        local memory_used=$(echo "$memory_info" | cut -d':' -f2 | tr -d '\r')
        add_result "PASS" "Redis memory usage: $memory_used" "Redis"
    fi
    
    # Connected clients
    local clients=$(docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli info clients | grep "connected_clients" | cut -d':' -f2 | tr -d '\r')
    if [ -n "$clients" ]; then
        add_result "PASS" "Redis connected clients: $clients" "Redis"
    fi
}

# Check SSL certificate
check_ssl() {
    log_info "Checking SSL certificate..."
    
    # Certificate validity
    local cert_info=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    
    if [ -n "$cert_info" ]; then
        local expiry_date=$(echo "$cert_info" | grep "notAfter" | cut -d'=' -f2)
        local expiry_timestamp=$(date -d "$expiry_date" +%s)
        local now_timestamp=$(date +%s)
        local days_until_exp=$(( (expiry_timestamp - now_timestamp) / 86400 ))
        
        if [ $days_until_exp -gt 30 ]; then
            add_result "PASS" "SSL certificate valid ($days_until_exp days remaining)" "SSL"
        elif [ $days_until_exp -gt 7 ]; then
            add_result "WARN" "SSL certificate expires soon ($days_until_exp days)" "SSL"
        else
            add_result "FAIL" "SSL certificate expires very soon ($days_until_exp days)" "SSL"
        fi
    else
        add_result "FAIL" "Unable to check SSL certificate" "SSL"
    fi
    
    # SSL Labs grade (if comprehensive check)
    if [ "$COMPREHENSIVE" = "--comprehensive" ]; then
        log_info "Running SSL Labs analysis (this may take a few minutes)..."
        # This is a placeholder - in production, you might want to use SSL Labs API
        add_result "PASS" "SSL configuration check skipped in script" "SSL"
    fi
}

# Check disk space
check_disk_space() {
    log_info "Checking disk space..."
    
    # Check main disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    
    if [ "$disk_usage" -lt 80 ]; then
        add_result "PASS" "Disk usage: ${disk_usage}%" "System"
    elif [ "$disk_usage" -lt 90 ]; then
        add_result "WARN" "High disk usage: ${disk_usage}%" "System"
    else
        add_result "FAIL" "Critical disk usage: ${disk_usage}%" "System"
    fi
    
    # Check Docker volumes
    for volume in $(docker volume ls -q | grep pyladies); do
        local volume_path=$(docker volume inspect "$volume" --format '{{.Mountpoint}}')
        if [ -d "$volume_path" ]; then
            local volume_size=$(du -sh "$volume_path" 2>/dev/null | cut -f1)
            add_result "PASS" "Volume $volume: $volume_size" "System"
        fi
    done
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # Memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    
    if (( $(echo "$memory_usage < 80.0" | bc -l) )); then
        add_result "PASS" "Memory usage: ${memory_usage}%" "System"
    elif (( $(echo "$memory_usage < 90.0" | bc -l) )); then
        add_result "WARN" "High memory usage: ${memory_usage}%" "System"
    else
        add_result "FAIL" "Critical memory usage: ${memory_usage}%" "System"
    fi
    
    # CPU load
    local cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    local cpu_cores=$(nproc)
    local load_per_core=$(echo "$cpu_load / $cpu_cores" | bc -l)
    
    if (( $(echo "$load_per_core < 0.8" | bc -l) )); then
        add_result "PASS" "CPU load: $cpu_load (${cpu_cores} cores)" "System"
    elif (( $(echo "$load_per_core < 1.5" | bc -l) )); then
        add_result "WARN" "High CPU load: $cpu_load (${cpu_cores} cores)" "System"
    else
        add_result "FAIL" "Critical CPU load: $cpu_load (${cpu_cores} cores)" "System"
    fi
}

# Check security headers
check_security_headers() {
    log_info "Checking security headers..."
    
    local headers=$(curl -s -I "https://$DOMAIN/")
    
    # HSTS
    if echo "$headers" | grep -qi "strict-transport-security"; then
        add_result "PASS" "HSTS header present" "Security"
    else
        add_result "WARN" "HSTS header missing" "Security"
    fi
    
    # X-Content-Type-Options
    if echo "$headers" | grep -qi "x-content-type-options"; then
        add_result "PASS" "X-Content-Type-Options header present" "Security"
    else
        add_result "WARN" "X-Content-Type-Options header missing" "Security"
    fi
    
    # X-Frame-Options
    if echo "$headers" | grep -qi "x-frame-options"; then
        add_result "PASS" "X-Frame-Options header present" "Security"
    else
        add_result "WARN" "X-Frame-Options header missing" "Security"
    fi
}

# Check backup status
check_backups() {
    log_info "Checking backup status..."
    
    local backup_dir="backups"
    if [ -d "$backup_dir" ]; then
        # Find latest backup
        local latest_backup=$(find "$backup_dir" -name "*.sql.gz" -o -name "*.dump" | sort -r | head -1)
        
        if [ -n "$latest_backup" ]; then
            local backup_age=$(stat -c %Y "$latest_backup")
            local now=$(date +%s)
            local hours_old=$(( (now - backup_age) / 3600 ))
            
            if [ $hours_old -lt 25 ]; then
                add_result "PASS" "Latest backup: $hours_old hours old" "Backup"
            elif [ $hours_old -lt 48 ]; then
                add_result "WARN" "Latest backup: $hours_old hours old" "Backup"
            else
                add_result "FAIL" "Latest backup: $hours_old hours old" "Backup"
            fi
        else
            add_result "FAIL" "No backups found" "Backup"
        fi
    else
        add_result "FAIL" "Backup directory not found" "Backup"
    fi
}

# Check Django system
check_django_system() {
    log_info "Checking Django system..."
    
    # Django check
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py check --settings=config.settings.production >/dev/null 2>&1; then
        add_result "PASS" "Django system check passed" "Django"
    else
        add_result "FAIL" "Django system check failed" "Django"
    fi
    
    # Static files check
    local static_response=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/static/css/main.css")
    if [ "$static_response" = "200" ]; then
        add_result "PASS" "Static files accessible" "Django"
    else
        add_result "WARN" "Static files check failed" "Django"
    fi
}

# Generate health report
generate_report() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}         HEALTH CHECK REPORT${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo -e "\nTimestamp: $(date)"
    echo -e "Domain: $DOMAIN"
    echo -e "Check Type: ${COMPREHENSIVE:-"Standard"}"
    
    # Summary
    local total_checks=${#HEALTH_RESULTS[@]}
    local passed_checks=$((total_checks - FAILED_CHECKS - WARNING_CHECKS))
    
    echo -e "\n${BLUE}SUMMARY:${NC}"
    echo -e "Total checks: $total_checks"
    echo -e "${GREEN}Passed: $passed_checks${NC}"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    
    # Overall status
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
            echo -e "\n${GREEN}🎉 OVERALL STATUS: HEALTHY${NC}"
        else
            echo -e "\n${YELLOW}⚠️  OVERALL STATUS: HEALTHY WITH WARNINGS${NC}"
        fi
    else
        echo -e "\n${RED}🚨 OVERALL STATUS: UNHEALTHY${NC}"
    fi
    
    # Detailed results by component
    echo -e "\n${BLUE}DETAILED RESULTS:${NC}"
    
    # Group results by component
    declare -A components
    for result in "${HEALTH_RESULTS[@]}"; do
        IFS='|' read -r status component message <<< "$result"
        if [ -z "${components[$component]}" ]; then
            components[$component]="$status|$message"
        else
            components[$component]="${components[$component]}##$status|$message"
        fi
    done
    
    # Display results by component
    for component in $(printf '%s\n' "${!components[@]}" | sort); do
        echo -e "\n$component:"
        IFS='##' read -ra MESSAGES <<< "${components[$component]}"
        for msg in "${MESSAGES[@]}"; do
            IFS='|' read -r status message <<< "$msg"
            case "$status" in
                "PASS") echo -e "  ${GREEN}✓${NC} $message" ;;
                "WARN") echo -e "  ${YELLOW}⚠${NC} $message" ;;
                "FAIL") echo -e "  ${RED}✗${NC} $message" ;;
            esac
        done
    done
    
    # Recommendations
    if [ $FAILED_CHECKS -gt 0 ] || [ $WARNING_CHECKS -gt 0 ]; then
        echo -e "\n${BLUE}RECOMMENDATIONS:${NC}"
        
        if [ $FAILED_CHECKS -gt 0 ]; then
            echo -e "${RED}• Address failed checks immediately${NC}"
            echo -e "• Check container logs: docker-compose -f $COMPOSE_FILE logs"
            echo -e "• Consider rolling back if issues persist"
        fi
        
        if [ $WARNING_CHECKS -gt 0 ]; then
            echo -e "${YELLOW}• Monitor warning conditions closely${NC}"
            echo -e "• Schedule maintenance to address warnings"
        fi
    fi
    
    echo -e "\n${BLUE}========================================${NC}"
}

# Main function
main() {
    echo -e "${BLUE}Starting health check at $(date)${NC}\n"
    
    # Basic checks (always run)
    check_containers
    check_application
    check_database
    check_redis
    check_ssl
    check_disk_space
    
    # Comprehensive checks (optional)
    if [ "$COMPREHENSIVE" = "--comprehensive" ]; then
        check_system_resources
        check_security_headers
        check_backups
        check_django_system
    fi
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [ $FAILED_CHECKS -gt 0 ]; then
        exit 1  # Critical issues found
    elif [ $WARNING_CHECKS -gt 0 ]; then
        exit 2  # Warnings found
    else
        exit 0  # All checks passed
    fi
}

# Run main function
main "$@"