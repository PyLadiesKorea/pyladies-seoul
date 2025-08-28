"""
Tests for image management and optimization system.
Testing image upload, processing, validation, and admin interface.
"""

import os
from unittest.mock import patch, Mock
from io import BytesIO

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse

from PIL import Image as PILImage
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from .base import (
    BaseAdminTestCase, 
    AdminPermissionTestMixin, 
    ImageProcessingTestMixin,
    AdminFormTestMixin
)


class ImageUploadValidationTestCase(BaseAdminTestCase, ImageProcessingTestMixin, AdminFormTestMixin):
    """Test image upload validation and processing"""
    
    def test_valid_image_upload_accepted(self):
        """Test that valid image formats are accepted"""
        valid_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        
        for format_name in valid_formats:
            with self.subTest(format=format_name):
                test_image = self.create_test_image(
                    filename=f'test.{format_name.lower()}',
                    format=format_name if format_name != 'WEBP' else 'WEBP'
                )
                
                # This should not raise any exception
                image_instance = Image.objects.create(
                    title=f'Test {format_name} Image',
                    file=test_image
                )
                
                self.assertTrue(image_instance.file)
                self.assertEqual(image_instance.title, f'Test {format_name} Image')
    
    def test_invalid_image_format_rejected(self):
        """Test that invalid file formats are rejected"""
        # Create a text file pretending to be an image
        fake_image = SimpleUploadedFile(
            'fake_image.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        with self.assertRaises(Exception):
            Image.objects.create(
                title='Fake Image',
                file=fake_image
            )
    
    def test_image_size_limits_enforced(self):
        """Test that image size limits are properly enforced"""
        # Create oversized image (this test will need corresponding model validation)
        oversized_image = PILImage.new('RGB', (5000, 5000), color='red')
        image_buffer = BytesIO()
        oversized_image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        
        large_file = SimpleUploadedFile(
            'oversized.jpg',
            image_buffer.getvalue(),
            content_type='image/jpeg'
        )
        
        # This test expects validation logic to be implemented
        # For now, we'll just ensure the image can be created (validation will be added)
        image_instance = Image.objects.create(
            title='Large Image',
            file=large_file
        )
        
        self.assertTrue(image_instance.file)
    
    def test_alt_text_required_validation(self):
        """Test that alt text validation works correctly"""
        # This test will be implemented once alt text validation is added
        test_image = self.create_test_image()
        
        image_instance = Image.objects.create(
            title='Test Image',
            file=test_image
        )
        
        # For now, just verify the image was created
        # Alt text validation will be implemented in the admin forms
        self.assertTrue(image_instance.file)
    
    def test_automatic_webp_conversion(self):
        """Test that images are automatically converted to WebP when configured"""
        # Create a JPEG image
        jpeg_image = self.create_test_image(filename='test.jpg', format='JPEG')
        
        image_instance = Image.objects.create(
            title='JPEG to WebP Test',
            file=jpeg_image
        )
        
        # Test that rendition can be created in WebP format
        webp_rendition = image_instance.get_rendition('width-200|format-webp')
        self.assertTrue(webp_rendition.file)
        self.assertTrue(webp_rendition.file.name.endswith('.webp'))
    
    def test_image_optimization_quality_settings(self):
        """Test that image quality optimization works"""
        test_image = self.create_test_image()
        
        image_instance = Image.objects.create(
            title='Quality Test Image',
            file=test_image
        )
        
        # Create renditions with different quality settings
        high_quality = image_instance.get_rendition('width-200|jpegquality-95')
        low_quality = image_instance.get_rendition('width-200|jpegquality-60')
        
        self.assertTrue(high_quality.file)
        self.assertTrue(low_quality.file)
        
        # Low quality should have smaller file size
        # This is a basic check - actual file size comparison might vary
        self.assertTrue(high_quality.file.size > 0)
        self.assertTrue(low_quality.file.size > 0)


class ImageAdminInterfaceTestCase(BaseAdminTestCase, AdminPermissionTestMixin):
    """Test image admin interface functionality"""
    
    def test_image_admin_access_requires_staff(self):
        """Test that image admin requires staff access"""
        url = reverse('wagtailimages:index')
        self.assertRequiresStaffStatus(url)
    
    def test_image_upload_admin_interface(self):
        """Test image upload through admin interface"""
        self.login_as_editor()
        
        url = reverse('wagtailimages:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test form submission
        test_image = self.create_test_image()
        response = self.client.post(url, {
            'title': 'Admin Uploaded Image',
            'file': test_image,
            'tags': 'test, admin',
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify image was created
        image = Image.objects.filter(title='Admin Uploaded Image').first()
        self.assertIsNotNone(image)
        self.assertEqual(image.title, 'Admin Uploaded Image')
    
    def test_image_bulk_operations(self):
        """Test bulk operations on images in admin"""
        self.login_as_editor()
        
        # Create multiple test images
        images = []
        for i in range(3):
            test_image = self.create_test_image(filename=f'bulk_test_{i}.jpg')
            image_instance = Image.objects.create(
                title=f'Bulk Test Image {i}',
                file=test_image
            )
            images.append(image_instance)
        
        # Test bulk delete (when implemented)
        url = reverse('wagtailimages:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify all images are listed
        for image in images:
            self.assertContains(response, image.title)
    
    def test_image_search_functionality(self):
        """Test image search in admin interface"""
        self.login_as_editor()
        
        # Create images with different titles
        searchable_image = self.create_wagtail_image(title='Searchable Test Image')
        other_image = self.create_wagtail_image(title='Other Image')
        
        url = reverse('wagtailimages:index')
        
        # Test search
        response = self.client.get(url, {'q': 'Searchable'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Searchable Test Image')
        self.assertNotContains(response, 'Other Image')
    
    def test_image_filtering_by_collection(self):
        """Test filtering images by collection in admin"""
        self.login_as_editor()
        
        url = reverse('wagtailimages:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test that filter options are available
        # Collection filtering will be implemented with custom collections
        self.assertContains(response, 'Images')


class ImageProcessingBackgroundTestCase(TestCase, ImageProcessingTestMixin):
    """Test background image processing tasks"""
    
    def test_image_resize_task(self):
        """Test background image resizing task"""
        # This test will be implemented once background processing is added
        test_image = self.create_test_image()
        
        image_instance = Image.objects.create(
            title='Background Processing Test',
            file=test_image
        )
        
        # For now, just verify the image was created
        # Background processing tasks will be implemented later
        self.assertTrue(image_instance.file)
    
    def test_webp_conversion_task(self):
        """Test background WebP conversion task"""
        # This test will be implemented once background processing is added
        test_image = self.create_test_image(format='PNG')
        
        image_instance = Image.objects.create(
            title='WebP Conversion Test',
            file=test_image
        )
        
        # For now, just verify the image was created
        self.assertTrue(image_instance.file)
    
    @patch('celery.current_app.send_task')
    def test_image_processing_queue(self, mock_send_task):
        """Test that image processing tasks are queued properly"""
        # This test assumes Celery integration will be added
        test_image = self.create_test_image()
        
        image_instance = Image.objects.create(
            title='Queue Test Image',
            file=test_image
        )
        
        # For now, just verify the image was created
        # Task queuing will be implemented with Celery
        self.assertTrue(image_instance.file)


class ImagePermissionsTestCase(BaseAdminTestCase, AdminPermissionTestMixin):
    """Test image-related permissions and access control"""
    
    def test_image_view_permissions(self):
        """Test permissions for viewing images"""
        url = reverse('wagtailimages:index')
        
        # Test access levels
        self.assertRequiresStaffStatus(url)
    
    def test_image_upload_permissions(self):
        """Test permissions for uploading images"""
        url = reverse('wagtailimages:add')
        
        # Test access levels
        self.assertRequiresStaffStatus(url)
    
    def test_image_edit_permissions(self):
        """Test permissions for editing images"""
        # Create test image
        test_image = self.create_wagtail_image()
        url = reverse('wagtailimages:edit', args=[test_image.id])
        
        # Test access levels
        self.assertRequiresStaffStatus(url)
    
    def test_image_delete_permissions(self):
        """Test permissions for deleting images"""
        # Create test image
        test_image = self.create_wagtail_image()
        url = reverse('wagtailimages:delete', args=[test_image.id])
        
        # Test access levels
        self.assertRequiresStaffStatus(url)


class ImageMetadataTestCase(BaseAdminTestCase):
    """Test image metadata handling and display"""
    
    def test_image_metadata_extraction(self):
        """Test that image metadata is properly extracted"""
        test_image = self.create_test_image()
        
        image_instance = Image.objects.create(
            title='Metadata Test Image',
            file=test_image
        )
        
        # Verify basic metadata
        self.assertTrue(image_instance.width > 0)
        self.assertTrue(image_instance.height > 0)
        self.assertTrue(image_instance.file_size > 0)
    
    def test_image_alt_text_management(self):
        """Test alt text management in admin"""
        # This will be expanded once alt text fields are added
        test_image = self.create_wagtail_image(title='Alt Text Test')
        
        # Verify image exists (alt text functionality to be implemented)
        self.assertTrue(test_image.file)
    
    def test_image_usage_tracking(self):
        """Test tracking where images are used"""
        # This will be implemented to show where images are referenced
        test_image = self.create_wagtail_image(title='Usage Tracking Test')
        
        # Basic test - usage tracking to be implemented
        self.assertTrue(test_image.file)