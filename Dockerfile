# Multi-stage build for production optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    # For image processing
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    # For Node.js/SCSS compilation
    nodejs \
    npm \
    # Security and monitoring
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Install uv for faster Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create app user for security (base layer)
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Development stage
FROM base as development

# Create virtual environment as root
RUN uv venv .venv

# Copy dependency files, LICENSE, and README (required for build)
COPY pyproject.toml uv.lock* LICENSE README.md ./

# Install Python dependencies (including dev dependencies)
RUN uv sync --dev --frozen

# Copy project files
COPY . .

# Create directories for media and static files
RUN mkdir -p /app/media /app/static

# Set ownership of all app files to appuser (user already created in base)
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command for development
CMD ["/app/.venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production builder stage
FROM base as prod-builder

# Create virtual environment as root (temporary)
RUN uv venv .venv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* LICENSE README.md ./

# Install only production dependencies
RUN uv sync --frozen --no-dev

# Copy Node.js dependencies for frontend build
COPY package*.json ./
RUN npm ci --only=production --no-audit

# Copy source code
COPY . .

# Build frontend assets
RUN npm run build || echo "No build script found"

# Collect static files with production settings
RUN python manage.py collectstatic --noinput --settings=config.settings.production || echo "Static collection will be done at runtime"

# Production stage
FROM python:3.11-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    # Image processing runtime libraries
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Create app user and directories
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser && \
    mkdir -p /app/media /app/static /app/logs /app/backups && \
    chown -R appuser:appuser /app

# Set work directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=prod-builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code from builder
COPY --from=prod-builder --chown=appuser:appuser /app /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Create entrypoint script for initialization
COPY --chown=appuser:appuser <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! python -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files if not done during build
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "Static collection failed, continuing..."

# Create superuser if specified
if [ "\$DJANGO_SUPERUSER_EMAIL" ] && [ "\$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='\$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('\$DJANGO_SUPERUSER_EMAIL', '\$DJANGO_SUPERUSER_EMAIL', '\$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
" || echo "Superuser creation failed, continuing..."
fi

# Execute the main command
exec "\$@"
EOF

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Production command with optimal settings
CMD ["gunicorn", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "3", \
    "--worker-class", "gevent", \
    "--worker-connections", "1000", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "100", \
    "--timeout", "30", \
    "--keep-alive", "5", \
    "--log-level", "info", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--capture-output", \
    "config.wsgi:application"]