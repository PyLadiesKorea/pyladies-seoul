#!/bin/bash
# Setup Production Secrets for PyLadies Seoul
# This script creates the secrets directory structure and templates

set -e

echo "Setting up production secrets management..."

# Create secrets directory
SECRETS_DIR="secrets"
mkdir -p "$SECRETS_DIR"

# Function to create secret file if it doesn't exist
create_secret_file() {
    local filename=$1
    local description=$2
    local example_value=$3
    
    if [ ! -f "$SECRETS_DIR/$filename" ]; then
        echo "$example_value" > "$SECRETS_DIR/$filename"
        chmod 600 "$SECRETS_DIR/$filename"
        echo "Created $SECRETS_DIR/$filename - $description"
    else
        echo "Secret file $SECRETS_DIR/$filename already exists, skipping..."
    fi
}

# Generate Django secret key
generate_django_secret() {
    python3 -c "
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
" 2>/dev/null || echo "django-insecure-$(openssl rand -hex 25)"
}

# Generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

echo "Creating secret files..."

# Core Django secrets
create_secret_file "django_secret_key.txt" "Django SECRET_KEY" "$(generate_django_secret)"
create_secret_file "django_superuser_password.txt" "Django superuser password" "$(generate_password)"

# Database secrets
create_secret_file "postgres_password.txt" "PostgreSQL password" "$(generate_password)"

# Cache secrets  
create_secret_file "redis_password.txt" "Redis password" "$(generate_password)"

# Email secrets
create_secret_file "email_password.txt" "Email service password" "your-email-service-password-here"

# AWS secrets (optional)
create_secret_file "aws_secret_key.txt" "AWS secret access key" "your-aws-secret-access-key-here"

# Monitoring secrets (optional)
create_secret_file "sentry_dsn.txt" "Sentry DSN" "https://your-sentry-dsn@sentry.io/project-id"
create_secret_file "logfire_token.txt" "Logfire token" "your-logfire-token-here"

# Set proper permissions on secrets directory
chmod 700 "$SECRETS_DIR"
chmod 600 "$SECRETS_DIR"/*

# Create .gitignore for secrets if it doesn't exist
if [ ! -f "$SECRETS_DIR/.gitignore" ]; then
    cat > "$SECRETS_DIR/.gitignore" << 'EOF'
# Ignore all secrets
*
!.gitignore
!README.md
EOF
    echo "Created $SECRETS_DIR/.gitignore"
fi

# Create README for secrets management
if [ ! -f "$SECRETS_DIR/README.md" ]; then
    cat > "$SECRETS_DIR/README.md" << 'EOF'
# Secrets Management

This directory contains production secrets for the PyLadies Seoul application.

## Security Guidelines

1. **NEVER commit secret files to version control**
2. **Always use strong, unique passwords**
3. **Rotate secrets regularly**
4. **Use proper file permissions (600 for files, 700 for directory)**
5. **Keep backups of secrets in a secure location**

## Secret Files

- `django_secret_key.txt` - Django SECRET_KEY setting
- `django_superuser_password.txt` - Admin user password
- `postgres_password.txt` - PostgreSQL database password
- `redis_password.txt` - Redis cache password
- `email_password.txt` - Email service password
- `aws_secret_key.txt` - AWS S3 secret key (optional)
- `sentry_dsn.txt` - Sentry error tracking DSN (optional)
- `logfire_token.txt` - Logfire APM token (optional)

## Usage in Production

These secrets are mounted as Docker secrets in the production compose file:

```yaml
secrets:
  django_secret_key:
    file: ./secrets/django_secret_key.txt
```

## Secret Rotation

To rotate secrets:

1. Generate new secret value
2. Update the secret file
3. Restart the affected services
4. Update any external services if needed

## Backup

Ensure secrets are backed up securely, separate from code repository.
EOF
    echo "Created $SECRETS_DIR/README.md"
fi

echo ""
echo "✅ Secrets setup complete!"
echo ""
echo "⚠️  IMPORTANT: Please update the following secret files with real values:"
echo "   - $SECRETS_DIR/email_password.txt"
echo "   - $SECRETS_DIR/aws_secret_key.txt (if using AWS S3)"
echo "   - $SECRETS_DIR/sentry_dsn.txt (if using Sentry)"
echo "   - $SECRETS_DIR/logfire_token.txt (if using Logfire)"
echo ""
echo "🔒 All secret files have been created with secure permissions (600)"
echo "🚨 NEVER commit the secrets directory to version control!"
echo ""
echo "To verify secrets are properly secured:"
echo "   ls -la $SECRETS_DIR/"