#!/bin/bash
set -e

# Nginx Production Entrypoint Script
# PyLadies Seoul Project

echo "Starting Nginx production setup..."

# Create necessary directories
mkdir -p /var/log/nginx
mkdir -p /var/cache/nginx
mkdir -p /etc/nginx/ssl

# Set permissions
chown -R nginx:nginx /var/log/nginx
chown -R nginx:nginx /var/cache/nginx

# Generate DH parameters if they don't exist
if [ ! -f /etc/nginx/ssl/dhparam.pem ]; then
    echo "Generating Diffie-Hellman parameters (this may take a while)..."
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
    chown nginx:nginx /etc/nginx/ssl/dhparam.pem
    chmod 644 /etc/nginx/ssl/dhparam.pem
fi

# Replace environment variables in configuration files
envsubst '${DOMAIN_NAME} ${WWW_DOMAIN_NAME}' < /etc/nginx/conf.d/production.conf > /etc/nginx/conf.d/production.conf.tmp
mv /etc/nginx/conf.d/production.conf.tmp /etc/nginx/conf.d/production.conf

# Test nginx configuration
echo "Testing Nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    echo "Nginx configuration test failed!"
    exit 1
fi

echo "Nginx configuration is valid"

# If SSL certificates don't exist, create self-signed ones for initial startup
if [ ! -f "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}/fullchain.pem" ]; then
    echo "SSL certificates not found, creating self-signed certificates for initial startup..."
    
    mkdir -p "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}"
    
    openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
        -keyout "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}/privkey.pem" \
        -out "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}/fullchain.pem" \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=PyLadies Seoul/OU=IT Department/CN=${DOMAIN_NAME:-pyladiesseoul.org}"
    
    # Create chain.pem (same as fullchain.pem for self-signed)
    cp "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}/fullchain.pem" \
       "/etc/letsencrypt/live/${DOMAIN_NAME:-pyladiesseoul.org}/chain.pem"
    
    echo "Self-signed certificates created. Remember to replace with Let's Encrypt certificates!"
fi

# Wait for Django application to be ready
echo "Waiting for Django application to be ready..."
timeout=60
count=0

while [ $count -lt $timeout ]; do
    if curl -f http://web:8000/health/ > /dev/null 2>&1; then
        echo "Django application is ready!"
        break
    fi
    
    echo "Waiting for Django application... ($count/$timeout)"
    sleep 2
    count=$((count + 2))
done

if [ $count -ge $timeout ]; then
    echo "Warning: Django application is not responding, but starting Nginx anyway"
fi

echo "Starting Nginx..."

# Execute the main command
exec "$@"