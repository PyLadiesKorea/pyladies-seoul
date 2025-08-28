"""
Django production settings for PyLadies Seoul project.

This file contains production-specific configuration.
All sensitive values MUST be provided via environment variables.
"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Production allowed hosts - MUST be set via environment variable
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise ValueError("ALLOWED_HOSTS environment variable must be set for production")

# Database - MUST be set via environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for production")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cache configuration - Redis required for production
REDIS_URL = os.environ.get("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable must be set for production")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "pyladies_seoul_prod",
        "VERSION": 1,
        "TIMEOUT": 300,  # 5 minutes default timeout
    }
}

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF configuration
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Additional security headers
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Email configuration for production
EMAIL_BACKEND = "django_anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.environ.get("MAILGUN_SENDER_DOMAIN"),
}

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@pyladiesseoul.org")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Static and media files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Media files in production (consider using cloud storage)
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Consider using cloud storage for media files
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "ap-northeast-2")

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# Compression settings
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.rCSSMinFilter",
]
COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.rJSMinFilter",
]

# SASS settings
SASS_OUTPUT_STYLE = "compressed"

# Logging configuration for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Admin and manager emails
ADMINS = [
    ("PyLadies Seoul Tech", os.environ.get("ADMIN_EMAIL", "tech@pyladiesseoul.org")),
]
MANAGERS = ADMINS

# Wagtail settings for production
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILADMIN_BASE_URL = os.environ.get("BASE_URL", "https://pyladiesseoul.org")

# Error reporting with Sentry (optional)
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
    )

# Database connection pooling (if using pgbouncer)
if os.environ.get("USE_PGBOUNCER"):
    DATABASES["default"]["OPTIONS"] = {
        "MAX_CONNS": 20,
        "OPTIONS": {
            "CONN_MAX_AGE": 0,
        },
    }

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Consider removing this and using nonces
    "https://cdnjs.cloudflare.com",
    "https://cdn.jsdelivr.net",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Consider removing this and using nonces
    "https://fonts.googleapis.com",
    "https://cdnjs.cloudflare.com",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https:",
)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# Remove debug toolbar and other dev apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ["debug_toolbar"]]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware]

# Performance optimizations
CONN_MAX_AGE = 600

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Cache middleware for anonymous pages
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
] + MIDDLEWARE + [
    "django.middleware.cache.FetchFromCacheMiddleware",
]

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = "pyladies_seoul"

# Rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"