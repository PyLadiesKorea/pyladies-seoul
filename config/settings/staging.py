"""
Django staging settings for PyLadies Seoul project.

This file contains staging-specific configuration.
All sensitive values MUST be provided via environment variables.
"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Staging allowed hosts - MUST be set via environment variable
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise ValueError("ALLOWED_HOSTS environment variable must be set for staging")

# Database - Use SQLite for staging
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "db_staging.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Cache configuration - Use dummy cache for staging
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = False  # Allow HTTP for staging
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF configuration
CSRF_COOKIE_SECURE = False  # Allow HTTP for staging
CSRF_COOKIE_HTTPONLY = True

# Security settings (relaxed for staging)
SECURE_SSL_REDIRECT = False  # Allow HTTP for staging
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True



# Static and media files
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Media files in staging
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Disable compression for staging
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# SASS settings
SASS_OUTPUT_STYLE = "expanded"

# Check if we can write to the logs directory
can_write_logs = False

try:
    # Try to create the logs directory
    os.makedirs("/app/logs", exist_ok=True)
    
    # Try to write a test file
    test_file = "/app/logs/test_write.tmp"
    with open(test_file, 'w') as f:
        f.write('test')
    os.unlink(test_file)  # Remove test file
    
    can_write_logs = True
except (OSError, PermissionError):
    can_write_logs = False
    print("Warning: Cannot write to logs directory, using console logging only")

# Logging configuration for staging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
}

# Add file handler only if we can write to logs
if can_write_logs:
    LOGGING["handlers"]["file"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "/app/logs/django_staging.log",
        "maxBytes": 1024 * 1024 * 15,  # 15MB
        "backupCount": 5,
        "formatter": "verbose",
    }

# Add root and loggers configuration
LOGGING["root"] = {
    "handlers": ["console"],
}

LOGGING["loggers"] = {
    "django": {
        "handlers": ["console"] + (["file"] if can_write_logs else []),
        "level": "INFO",
        "propagate": False,
    },
    "django.security": {
        "handlers": ["console"] + (["file"] if can_write_logs else []),
        "level": "INFO",
        "propagate": False,
    },
    "wagtail": {
        "handlers": ["console"] + (["file"] if can_write_logs else []),
        "level": "INFO",
        "propagate": False,
    },
    "apps": {
        "handlers": ["console"] + (["file"] if can_write_logs else []),
        "level": "INFO",
        "propagate": False,
    },
}

# Admin and manager emails
ADMINS = [
    ("PyLadies Seoul Tech", os.environ.get("ADMIN_EMAIL", "tech@pyladiesseoul.org")),
]
MANAGERS = ADMINS

# Wagtail settings for staging
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILADMIN_BASE_URL = os.environ.get("BASE_URL", "http://staging.pyladiesseoul.org")



# Remove debug toolbar and other dev apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ["debug_toolbar"]]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware]

# Performance optimizations
CONN_MAX_AGE = 600

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Disable cache middleware for staging
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "cache" not in middleware]

# Rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"
