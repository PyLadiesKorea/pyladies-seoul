# Base image for all stages
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    nodejs \
    npm \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv for faster Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create app user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Development stage
FROM base as development

# Create virtual environment
RUN uv venv .venv

# Copy dependency files
COPY pyproject.toml uv.lock* LICENSE README.md ./

# Install Python dependencies
RUN uv sync --dev --frozen

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Development command
CMD ["/app/.venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production builder stage
FROM base as prod-builder

# Create virtual environment
RUN uv venv .venv

# Copy dependency files
COPY pyproject.toml uv.lock* LICENSE README.md ./

# Install production dependencies only
RUN uv sync --frozen --no-dev --extra production

# Copy Node.js dependencies
COPY package*.json ./
RUN npm ci --only=production --no-audit

# Copy source code
COPY . .

# Build frontend assets
RUN npm run build || echo "No build script found"

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production || echo "Static collection will be done at runtime"

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create app user and directories
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser && \
    mkdir -p /app/media /app/static /app/logs /app/backups /app/db && \
    chown -R appuser:appuser /app

# Set work directory
WORKDIR /app

# Copy virtual environment and application from builder
COPY --from=prod-builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=prod-builder --chown=appuser:appuser /app /app

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Setting up homepage..."
python manage.py setup_homepage || echo "Homepage setup failed, continuing..."

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "Static collection failed, continuing..."

if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
" || echo "Superuser creation failed, continuing..."
fi

exec "$@"
EOF

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Production command
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