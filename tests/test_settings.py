"""
Test Django settings configuration.
"""

import os
import django
from django.test import TestCase
from django.conf import settings


class SettingsTestCase(TestCase):
    """Test Django settings are properly configured."""
    
    def test_debug_setting(self):
        """Test DEBUG setting is properly configured."""
        # In testing environment, DEBUG should be False
        self.assertFalse(settings.DEBUG)
    
    def test_installed_apps(self):
        """Test all required apps are installed."""
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'wagtail',
            'wagtail.admin',
            'wagtail.documents',
            'wagtail.snippets',
            'wagtail.users',
            'wagtail.sites',
            'wagtail.images',
            'wagtail.embeds',
            'wagtail.contrib.redirects',
            'wagtail.contrib.forms',
            'apps.core',
            'apps.home',
        ]
        
        for app in required_apps:
            with self.subTest(app=app):
                self.assertIn(app, settings.INSTALLED_APPS)
    
    def test_middleware_configuration(self):
        """Test middleware is properly configured."""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'wagtail.contrib.redirects.middleware.RedirectMiddleware',
        ]
        
        for middleware in required_middleware:
            with self.subTest(middleware=middleware):
                self.assertIn(middleware, settings.MIDDLEWARE)
    
    def test_database_configuration(self):
        """Test database is properly configured."""
        self.assertIn('default', settings.DATABASES)
        self.assertIn('ENGINE', settings.DATABASES['default'])
    
    def test_static_files_configuration(self):
        """Test static files settings."""
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
    
    def test_media_files_configuration(self):
        """Test media files settings."""
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
    
    def test_wagtail_configuration(self):
        """Test Wagtail-specific settings."""
        self.assertTrue(hasattr(settings, 'WAGTAIL_SITE_NAME'))
        self.assertEqual(settings.WAGTAIL_SITE_NAME, 'PyLadies Seoul')
    
    def test_security_settings(self):
        """Test security settings are properly configured."""
        # These should be True in production, but may be False in testing
        self.assertTrue(hasattr(settings, 'SECURE_BROWSER_XSS_FILTER'))
        self.assertTrue(hasattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF'))
        self.assertTrue(hasattr(settings, 'X_FRAME_OPTIONS'))
    
    def test_internationalization_settings(self):
        """Test i18n settings."""
        self.assertTrue(settings.USE_I18N)
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(settings.TIME_ZONE, 'Asia/Seoul')
        self.assertIn(settings.LANGUAGE_CODE, ['ko', 'en'])
    
    def test_cache_configuration(self):
        """Test cache is configured."""
        self.assertIn('default', settings.CACHES)
        # In testing, it should use dummy cache
        self.assertEqual(
            settings.CACHES['default']['BACKEND'],
            'django.core.cache.backends.dummy.DummyCache'
        )