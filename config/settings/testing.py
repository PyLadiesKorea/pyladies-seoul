"""
Django testing settings for PyLadies Seoul project.

This file is used when running tests.
Optimized for fast test execution.
"""

from .base import *  # noqa

# Testing configuration
DEBUG = False
TESTING = True

# Use in-memory SQLite for fast tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use dummy cache backend for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Use in-memory file storage for tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"
MEDIA_ROOT = "/tmp/test_media/"



# Password hashers - use fast hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests (except for errors)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}

# Disable compression for tests
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Disable whitenoise for tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Test-specific middleware (remove unnecessary middleware)
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE 
    if middleware not in [
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
]

# Security settings for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Wagtail settings for tests
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILADMIN_BASE_URL = "http://testserver"

# Search backend for tests
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Disable external services in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Fast test execution settings
SECRET_KEY = "test-secret-key-not-for-production"
ALLOWED_HOSTS = ["*"]

# Disable template caching
TEMPLATES[0]["OPTIONS"]["debug"] = True
if "cached" in TEMPLATES[0]["OPTIONS"].get("loaders", []):
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

# Test database optimization
DATABASE_ENGINE = DATABASES["default"]["ENGINE"]
if "sqlite" in DATABASE_ENGINE:
    DATABASES["default"]["OPTIONS"] = {
        "timeout": 20,
        "check_same_thread": False,
    }

# Disable model translation in tests for simplicity
USE_I18N = False
USE_L10N = False
LANGUAGE_CODE = "en"

# Remove model translation from installed apps if present
if "modeltranslation" in INSTALLED_APPS:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "modeltranslation"]

# Test-specific apps (staticfiles already included in base)

# Factory Boy settings
FACTORY_BOY_SKIP_FACTORY_INITIALIZATION = True

# Override any external service configurations
ANYMAIL = {}
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

# Simplify REST framework settings for tests
REST_FRAMEWORK.update({
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
})

# Test-specific Wagtail settings
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea"
    }
}

# Simplified search for tests
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Performance settings for tests
CONN_MAX_AGE = 0

# Disable any caching middleware
CACHE_MIDDLEWARE_SECONDS = 0