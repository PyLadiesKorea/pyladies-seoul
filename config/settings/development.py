"""
Django development settings for PyLadies Seoul project.

This file is used for local development.
"""

from .base import *  # noqa

# Configure Logfire APM
try:
    from config.logfire_config import configure_logfire
    configure_logfire()
except ImportError:
    print("⚠️  Logfire not available, skipping APM configuration")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development specific allowed hosts
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "pyladies-seoul-web-1",  # Docker container name
]

# Database
# Use SQLite for development by default
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Override with PostgreSQL if DATABASE_URL is set
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.config(default=DATABASE_URL)

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable caching in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Enable Redis cache if REDIS_URL is provided
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# Disable compression in development
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# SASS settings for development
SASS_OUTPUT_STYLE = "expanded"

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Django Extensions
if "django_extensions" in INSTALLED_APPS:
    # Shell Plus configuration
    SHELL_PLUS = "ipython"
    SHELL_PLUS_PRINT_SQL = True
    
    # Runserver Plus configuration
    RUNSERVER_PLUS_EXTRA_FILES = [
        BASE_DIR / "static",
    ]

# Debug Toolbar settings
if DEBUG and "debug_toolbar" in INSTALLED_APPS:
    # Only add if not already present
    debug_middleware = "debug_toolbar.middleware.DebugToolbarMiddleware"
    if debug_middleware not in MIDDLEWARE:
        MIDDLEWARE = [debug_middleware] + MIDDLEWARE
    
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]
    
    # Docker support
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
        "SHOW_COLLAPSED": True,
    }

# Logging configuration for development
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["apps"]["level"] = "DEBUG"

# Add SQL query logging for development
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG" if os.environ.get("DEBUG_SQL") else "INFO",
    "propagate": False,
}

# Wagtail settings for development
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Allow all origins for development CORS (if needed)
CORS_ALLOW_ALL_ORIGINS = True if DEBUG else False

# Development specific file handling
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Enable all error reporting in development
ADMINS = [
    ("Developer", "dev@pyladiesseoul.org"),
]

MANAGERS = ADMINS

# Development-specific middleware additions
MIDDLEWARE += [
    # Add any development-specific middleware here
]

# Webpack Dev Server support (if using frontend build tools)
if os.environ.get("USE_WEBPACK_DEV_SERVER"):
    WEBPACK_DEV_SERVER_URL = "http://localhost:3000"

# Allow Content-Type: application/json for API testing
ALLOWED_JSON_CONTENT_TYPES = [
    "application/json",
    "application/vnd.api+json",
]