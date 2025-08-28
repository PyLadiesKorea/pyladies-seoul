"""
Base test classes for admin functionality.
Provides common utilities and setup for all admin tests.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from wagtail.models import Page, Site
from wagtail.images.models import Image


class BaseAdminTestCase(TestCase):
    """Base test case for admin functionality"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all admin tests"""
        # Create test site
        cls.root_page = Page.objects.get(id=1)
        cls.site = Site.objects.get(is_default_site=True)
        
        # Create superuser
        cls.superuser = User.objects.create_user(
            username='admin',
            email='admin@pyladiesseoul.org',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create editor user (staff but not superuser)
        cls.editor = User.objects.create_user(
            username='editor',
            email='editor@pyladiesseoul.org',
            password='testpass123',
            is_staff=True,
            is_superuser=False
        )
        
        # Create regular user (not staff)
        cls.regular_user = User.objects.create_user(
            username='user',
            email='user@pyladiesseoul.org',
            password='testpass123',
            is_staff=False,
            is_superuser=False
        )
        
        # Create user groups for testing permissions
        cls.editors_group, _ = Group.objects.get_or_create(name='Editors')
        cls.publishers_group, _ = Group.objects.get_or_create(name='Publishers')
        cls.content_managers_group, _ = Group.objects.get_or_create(name='Content Managers')
        
    def setUp(self):
        """Set up for each test"""
        self.client = Client()
        
    def login_as_superuser(self):
        """Helper method to log in as superuser"""
        self.client.login(username='admin', password='testpass123')
        
    def login_as_editor(self):
        """Helper method to log in as editor"""
        self.client.login(username='editor', password='testpass123')
        
    def login_as_regular_user(self):
        """Helper method to log in as regular user"""
        self.client.login(username='user', password='testpass123')
        
    def create_test_image(self, filename="test.jpg", format="JPEG"):
        """Create a test image for upload testing"""
        from PIL import Image as PILImage
        from io import BytesIO
        
        # Create a simple test image
        image = PILImage.new('RGB', (100, 100), color='red')
        image_buffer = BytesIO()
        image.save(image_buffer, format=format)
        image_buffer.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_buffer.getvalue(),
            content_type=f'image/{format.lower()}'
        )
        
    def create_wagtail_image(self, title="Test Image", filename="test.jpg"):
        """Create a Wagtail Image instance for testing"""
        test_file = self.create_test_image(filename)
        return Image.objects.create(
            title=title,
            file=test_file
        )
        
    def assign_user_to_group(self, user, group):
        """Helper method to assign user to group"""
        user.groups.add(group)
        
    def give_permission_to_group(self, group, permission_codename, content_type):
        """Helper method to give specific permission to a group"""
        permission = Permission.objects.get(
            codename=permission_codename,
            content_type=content_type
        )
        group.permissions.add(permission)


class AdminPermissionTestMixin:
    """Mixin for testing admin permissions"""
    
    def assertRequiresLogin(self, url):
        """Assert that accessing URL without login redirects to login"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
        
    def assertRequiresSuperuser(self, url):
        """Assert that URL requires superuser access"""
        # Test with regular user
        self.login_as_regular_user()
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])
        
        # Test with editor
        self.login_as_editor()
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])
        
        # Test with superuser should work
        self.login_as_superuser()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def assertRequiresStaffStatus(self, url):
        """Assert that URL requires staff status"""
        # Test with regular user
        self.login_as_regular_user()
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])
        
        # Test with staff user should work
        self.login_as_editor()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AdminFormTestMixin:
    """Mixin for testing admin forms"""
    
    def assertFormHasField(self, form, field_name):
        """Assert that form has specified field"""
        self.assertIn(field_name, form.fields)
        
    def assertFormHasHelpText(self, form, field_name, help_text):
        """Assert that form field has specific help text"""
        self.assertIn(field_name, form.fields)
        self.assertEqual(form.fields[field_name].help_text, help_text)
        
    def assertFormValidationError(self, form, field_name, error_message=None):
        """Assert that form has validation error for specified field"""
        self.assertFalse(form.is_valid())
        self.assertIn(field_name, form.errors)
        if error_message:
            self.assertIn(error_message, form.errors[field_name])


class ImageProcessingTestMixin:
    """Mixin for testing image processing functionality"""
    
    def create_test_images_various_sizes(self):
        """Create test images of various sizes for testing"""
        from PIL import Image as PILImage
        from io import BytesIO
        
        images = {}
        sizes = [
            ('small', 50, 50),
            ('medium', 300, 200),
            ('large', 1920, 1080),
            ('very_large', 3000, 2000)
        ]
        
        for name, width, height in sizes:
            image = PILImage.new('RGB', (width, height), color='blue')
            image_buffer = BytesIO()
            image.save(image_buffer, format='JPEG')
            image_buffer.seek(0)
            
            images[name] = SimpleUploadedFile(
                f'{name}.jpg',
                image_buffer.getvalue(),
                content_type='image/jpeg'
            )
            
        return images
        
    def assertImageProcessed(self, image_instance, expected_formats=None):
        """Assert that image has been processed correctly"""
        self.assertTrue(image_instance.file)
        
        if expected_formats:
            for format_name in expected_formats:
                # Check that rendition can be created
                rendition = image_instance.get_rendition(f'width-200|format-{format_name}')
                self.assertTrue(rendition.file)


class MultilingualTestMixin:
    """Mixin for testing multilingual functionality"""
    
    def assertHasTranslationFields(self, model_class, field_name):
        """Assert that model has translation fields for specified field"""
        # Check for Korean field
        ko_field = f'{field_name}_ko'
        self.assertTrue(hasattr(model_class, ko_field))
        
        # Check for English field
        en_field = f'{field_name}_en'
        self.assertTrue(hasattr(model_class, en_field))
        
    def create_multilingual_content(self, model_instance, field_name, ko_content, en_content):
        """Helper to create multilingual content"""
        setattr(model_instance, f'{field_name}_ko', ko_content)
        setattr(model_instance, f'{field_name}_en', en_content)
        model_instance.save()
        return model_instance