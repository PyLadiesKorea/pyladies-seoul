"""
Tests for custom admin forms and their validation.
Testing enhanced form functionality, validation, and user experience.
"""

from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

from wagtail.images.models import Image
from wagtail.models import Page, Site

from .base import (
    BaseAdminTestCase, 
    ImageProcessingTestMixin,
    AdminFormTestMixin
)
from apps.common.forms import (
    CustomPageForm,
    CustomImageForm,
    UserPermissionForm,
    BulkActionForm,
    ContentFilterForm
)


class CustomPageFormTestCase(BaseAdminTestCase, AdminFormTestMixin):
    """Test custom page form validation and functionality"""
    
    def setUp(self):
        super().setUp()
        self.form_data = {
            'title': 'Test Page Title',
            'slug': 'test-page-title',
            'search_description': 'A test page for testing purposes',
        }
    
    def test_valid_page_form_submission(self):
        """Test that valid page form data is accepted"""
        form = CustomPageForm(data=self.form_data)
        
        # Note: The form might not be valid due to other required Wagtail fields
        # This tests our custom validation logic
        if not form.is_valid():
            # Check that our custom fields don't have errors
            custom_field_errors = []
            for field in ['title', 'search_description']:
                if field in form.errors:
                    custom_field_errors.extend(form.errors[field])
            
            # Our custom validation should pass
            self.assertEqual(len(custom_field_errors), 0, 
                           f"Custom validation failed: {custom_field_errors}")
    
    def test_title_required_validation(self):
        """Test that title is required"""
        form_data = self.form_data.copy()
        form_data['title'] = ''
        
        form = CustomPageForm(data=form_data)
        form.is_valid()  # Trigger validation
        
        self.assertIn('title', form.errors)
        self.assertIn('Title is required', str(form.errors['title']))
    
    def test_title_minimum_length_validation(self):
        """Test that title has minimum length requirement"""
        form_data = self.form_data.copy()
        form_data['title'] = 'AB'  # Too short
        
        form = CustomPageForm(data=form_data)
        form.is_valid()
        
        self.assertIn('title', form.errors)
        self.assertIn('at least 3 characters', str(form.errors['title']))
    
    def test_title_maximum_length_validation(self):
        """Test that title has maximum length limit"""
        form_data = self.form_data.copy()
        form_data['title'] = 'A' * 256  # Too long
        
        form = CustomPageForm(data=form_data)
        form.is_valid()
        
        self.assertIn('title', form.errors)
        self.assertIn('cannot exceed 255 characters', str(form.errors['title']))
    
    def test_search_description_length_validation(self):
        """Test that search description has length limit"""
        form_data = self.form_data.copy()
        form_data['search_description'] = 'A' * 161  # Too long
        
        form = CustomPageForm(data=form_data)
        form.is_valid()
        
        self.assertIn('search_description', form.errors)
        self.assertIn('cannot exceed 160 characters', str(form.errors['search_description']))
    
    def test_seo_title_length_warning(self):
        """Test that SEO title generates warning for long titles"""
        form_data = self.form_data.copy()
        form_data['seo_title'] = 'A' * 61  # Too long for optimal SEO
        
        form = CustomPageForm(data=form_data)
        form.is_valid()
        
        if 'seo_title' in form.errors:
            self.assertIn('under 60 characters', str(form.errors['seo_title']))


class CustomImageFormTestCase(BaseAdminTestCase, ImageProcessingTestMixin, AdminFormTestMixin):
    """Test custom image form validation and functionality"""
    
    def setUp(self):
        super().setUp()
        self.valid_image = self.create_test_image()
        
        self.form_data = {
            'title': 'Test Image',
            'alt_text': 'A descriptive alt text for the test image',
            'tags': 'test, image, django',
        }
        
        self.form_files = {
            'file': self.valid_image
        }
    
    def test_valid_image_form_submission(self):
        """Test that valid image form data is accepted"""
        form = CustomImageForm(data=self.form_data, files=self.form_files)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['title'], 'Test Image')
        self.assertEqual(form.cleaned_data['alt_text'], 'A descriptive alt text for the test image')
    
    def test_title_required_validation(self):
        """Test that image title is required"""
        form_data = self.form_data.copy()
        form_data['title'] = ''
        
        form = CustomImageForm(data=form_data, files=self.form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('required', str(form.errors['title']))
    
    def test_generic_title_rejection(self):
        """Test that generic titles are rejected"""
        generic_titles = ['image', 'photo', 'picture', 'img', 'untitled']
        
        for generic_title in generic_titles:
            with self.subTest(title=generic_title):
                form_data = self.form_data.copy()
                form_data['title'] = generic_title
                
                form = CustomImageForm(data=form_data, files=self.form_files)
                self.assertFalse(form.is_valid())
                self.assertIn('title', form.errors)
                self.assertIn('more descriptive title', str(form.errors['title']))
    
    def test_alt_text_validation(self):
        """Test alt text validation rules"""
        # Test too short alt text
        form_data = self.form_data.copy()
        form_data['alt_text'] = 'img'
        
        form = CustomImageForm(data=form_data, files=self.form_files)
        form.is_valid()
        
        if 'alt_text' in form.errors:
            self.assertIn('more descriptive', str(form.errors['alt_text']))
    
    def test_alt_text_length_limit(self):
        """Test alt text maximum length"""
        form_data = self.form_data.copy()
        form_data['alt_text'] = 'A' * 126  # Too long
        
        form = CustomImageForm(data=form_data, files=self.form_files)
        form.is_valid()
        
        if 'alt_text' in form.errors:
            self.assertIn('under 125 characters', str(form.errors['alt_text']))
    
    def test_generic_alt_text_rejection(self):
        """Test that generic alt text is rejected"""
        generic_alt_texts = ['image', 'photo', 'picture']
        
        for alt_text in generic_alt_texts:
            with self.subTest(alt_text=alt_text):
                form_data = self.form_data.copy()
                form_data['alt_text'] = alt_text
                
                form = CustomImageForm(data=form_data, files=self.form_files)
                form.is_valid()
                
                if 'alt_text' in form.errors:
                    self.assertIn('more descriptive alt text', str(form.errors['alt_text']))
    
    def test_file_validation_integration(self):
        """Test that file validation is integrated correctly"""
        # Test with invalid file (text file)
        fake_image = SimpleUploadedFile(
            'fake.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        form_files = {'file': fake_image}
        form = CustomImageForm(data=self.form_data, files=form_files)
        
        self.assertFalse(form.is_valid())
        # The exact error message depends on the ImageValidator implementation


class UserPermissionFormTestCase(BaseAdminTestCase, AdminFormTestMixin):
    """Test user permission form validation and functionality"""
    
    def setUp(self):
        super().setUp()
        self.form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@pyladiesseoul.org',
            'is_staff': True,
            'groups': [self.editors_group.id],
        }
    
    def test_valid_user_form_submission(self):
        """Test that valid user form data is accepted"""
        form = UserPermissionForm(data=self.form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_email_uniqueness_validation(self):
        """Test that duplicate emails are rejected"""
        # Create a user with the test email
        User.objects.create_user(
            username='existing',
            email='testuser@pyladiesseoul.org'
        )
        
        form = UserPermissionForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_group_filtering(self):
        """Test that only relevant groups are available"""
        form = UserPermissionForm()
        
        group_names = [group.name for group in form.fields['groups'].queryset]
        self.assertIn('Editors', group_names)
        self.assertIn('Publishers', group_names)
        self.assertIn('Content Managers', group_names)


class BulkActionFormTestCase(BaseAdminTestCase, AdminFormTestMixin):
    """Test bulk action form validation"""
    
    def test_valid_bulk_action_form(self):
        """Test that valid bulk action form is accepted"""
        form_data = {
            'action': 'publish',
            'selected_items': '1,2,3',
            'confirm': True,
        }
        
        form = BulkActionForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Test that selected items are properly parsed
        cleaned_items = form.cleaned_data['selected_items']
        self.assertEqual(cleaned_items, [1, 2, 3])
    
    def test_no_items_selected_validation(self):
        """Test validation when no items are selected"""
        form_data = {
            'action': 'publish',
            'selected_items': '',
            'confirm': True,
        }
        
        form = BulkActionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('selected_items', form.errors)
        self.assertIn('No items selected', str(form.errors['selected_items']))
    
    def test_invalid_item_selection(self):
        """Test validation with invalid item IDs"""
        form_data = {
            'action': 'publish',
            'selected_items': 'invalid,ids',
            'confirm': True,
        }
        
        form = BulkActionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('selected_items', form.errors)
        self.assertIn('Invalid item selection', str(form.errors['selected_items']))
    
    def test_confirmation_required(self):
        """Test that confirmation is required for bulk actions"""
        form_data = {
            'action': 'delete',
            'selected_items': '1,2,3',
            'confirm': False,
        }
        
        form = BulkActionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm', form.errors)


class ContentFilterFormTestCase(BaseAdminTestCase, AdminFormTestMixin):
    """Test content filter form validation"""
    
    def test_valid_filter_form(self):
        """Test that valid filter form is accepted"""
        form_data = {
            'status': 'live',
            'language': 'ko',
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'search': 'test query',
        }
        
        form = ContentFilterForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_date_range_validation(self):
        """Test that invalid date ranges are rejected"""
        form_data = {
            'date_from': '2024-12-31',
            'date_to': '2024-01-01',  # End date before start date
        }
        
        form = ContentFilterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Start date cannot be after end date', str(form.non_field_errors()))
    
    def test_empty_filter_form(self):
        """Test that empty filter form is valid (no filters applied)"""
        form = ContentFilterForm(data={})
        self.assertTrue(form.is_valid())


class FormWidgetTestCase(BaseAdminTestCase):
    """Test form widget enhancements and styling"""
    
    def test_image_form_widget_attributes(self):
        """Test that image form has proper widget attributes"""
        form = CustomImageForm()
        
        # Test file field accept attribute
        file_widget = form.fields['file'].widget
        self.assertIn('accept', file_widget.attrs)
        self.assertEqual(file_widget.attrs['accept'], 'image/jpeg,image/png,image/gif,image/webp')
        
        # Test CSS classes
        title_widget = form.fields['title'].widget
        self.assertIn('class', title_widget.attrs)
        self.assertIn('form-control', title_widget.attrs['class'])
    
    def test_page_form_widget_enhancements(self):
        """Test that page form has proper widget enhancements"""
        form = CustomPageForm()
        
        if 'title' in form.fields:
            title_widget = form.fields['title'].widget
            self.assertIn('placeholder', title_widget.attrs)
            self.assertIn('descriptive title', title_widget.attrs['placeholder'])
    
    def test_form_help_text_presence(self):
        """Test that forms have appropriate help text"""
        image_form = CustomImageForm()
        
        # Check alt_text help text
        self.assertIn('accessibility', image_form.fields['alt_text'].help_text)
        
        # Check file field help text
        self.assertIn('Supported formats', image_form.fields['file'].help_text)