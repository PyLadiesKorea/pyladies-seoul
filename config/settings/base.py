"""
Django base settings for PyLadies Seoul project.

This file contains base configuration that is common to all environments.
Environment-specific settings are in separate files.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Project root directory
PROJECT_DIR = BASE_DIR / "apps"

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this MUST be set via environment variable
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.locales",
    "wagtail.contrib.settings",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.table_block",
]

THIRD_PARTY_APPS = [
    "modelcluster",
    "taggit",
    "rest_framework",
    "django_extensions",
    "compressor",
    "sass_processor",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "modeltranslation",
    "wagtailmarkdown",
]

if DEBUG:
    THIRD_PARTY_APPS.append("debug_toolbar")

LOCAL_APPS = [
    "apps.common",      # Common utilities, middleware, decorators
    "apps.content",     # Main app: homepage, content, contact, search, etc.
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.common.middleware.SimplePerformanceMiddleware",
    "config.logfire_config.LogfireMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "wagtail.contrib.settings.context_processors.settings",
                "apps.common.context_processors.navigation_categories",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=600,
    )
}

# Cache configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 20,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "pyladies_seoul",
        "VERSION": 1,
    }
}

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF configuration
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "ko"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# Supported languages
LANGUAGES = [
    ("ko", "한국어"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
    "sass_processor.finders.CssFinder",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Site ID
SITE_ID = 1

# Wagtail settings
WAGTAIL_SITE_NAME = "PyLadies Seoul"
WAGTAIL_ENABLE_UPDATE_CHECK = False

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# Search configuration
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Wagtail admin configuration
WAGTAILADMIN_BASE_URL = BASE_URL

# Image formats
WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    "bmp": "jpeg",
    "webp": "webp",  # Keep WebP format
}

# Image optimization settings
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB max upload
WAGTAILIMAGES_RENDITION_FORMATS = [
    "webp", "jpeg", "png"
]

# Performance optimization settings
PERFORMANCE_OPTIMIZATION = {
    'ENABLE_QUERY_MONITORING': True,
    'ENABLE_CACHE_WARMING': True,
    'MAX_QUERIES_PER_PAGE': 15,
    'CACHE_TIMEOUT_MULTIPLIERS': {
        'page_content': 1.0,
        'navigation': 4.0,
        'static_content': 24.0,
    }
}

# Document configuration
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HTTPS settings (will be overridden in production)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Email configuration
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@pyladiesseoul.org")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Django Compressor settings
COMPRESS_ENABLED = not DEBUG
COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.rCSSMinFilter",
]
COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.rJSMinFilter",
]

# SASS settings
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = BASE_DIR / "static" 
SASS_PROCESSOR_INCLUDE_DIRS = [
    BASE_DIR / "static/scss",
]
SASS_OUTPUT_STYLE = "compressed" if not DEBUG else "expanded"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
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
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# Debug Toolbar configuration
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
    }

# Model Translation
MODELTRANSLATION_DEFAULT_LANGUAGE = "ko"
MODELTRANSLATION_LANGUAGES = ("ko", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("ko", "en")

# Wagtail Markdown configuration
WAGTAILMARKDOWN = {
    "autodownload_fontawesome": True,
    "allowed_tags": [
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "br", "strong", "em", "del", "s", "ins", "u",
        "blockquote", "code", "pre",
        "ul", "ol", "li",
        "a", "img",
        "table", "thead", "tbody", "tr", "th", "td",
        "hr",
    ],
    "allowed_attributes": {
        "a": ["href", "title", "rel"],
        "img": ["src", "alt", "title"],
        "code": ["class"],
        "pre": ["class"],
    },
    "extensions": [
        "markdown.extensions.extra",
        "markdown.extensions.codehilite",
        "markdown.extensions.toc",
        "pymdownx.superfences",
        "pymdownx.highlight",
        "pymdownx.inlinehilite",
        "pymdownx.tabbed",
        "pymdownx.tasklist",
    ],
    "extension_configs": {
        "markdown.extensions.codehilite": {
            "css_class": "highlight",
        },
        "pymdownx.superfences": {
            "css_class": "highlight",
        },
    },
}