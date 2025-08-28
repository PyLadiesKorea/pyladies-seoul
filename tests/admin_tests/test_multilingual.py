"""
Tests for multilingual content management in admin interface.
Testing language switching, translation management, and content synchronization.
"""

from django.test import TestCase, RequestFactory
from django.utils.translation import activate, get_language
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .base import BaseAdminTestCase, MultilingualTestMixin
from apps.common.multilingual import (
    MultilingualAdminMixin,
    LanguageSwitchMixin,
    TranslationSyncMixin,
    ContentCompletenessIndicator,
    MultilingualPageMixin,
    MultilingualFormMixin,
    LanguageWorkflowMixin
)


class TestMultilingualModel:
    """Mock model for testing multilingual functionality"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self):
        pass


class TestMultilingualAdmin(MultilingualAdminMixin):
    """Test admin class with multilingual mixin"""
    
    def get_required_fields_for_language(self, language_code):
        return ['title', 'description']


class MultilingualAdminMixinTestCase(BaseAdminTestCase, MultilingualTestMixin):
    """Test multilingual admin mixin functionality"""
    
    def setUp(self):
        super().setUp()
        self.admin = TestMultilingualAdmin()
        self.test_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='English Title',
            description_ko='한국어 설명',
            description_en='',  # Missing English description
        )
    
    def test_supported_languages(self):
        """Test getting supported languages"""
        supported = self.admin.supported_languages
        self.assertIn('ko', supported)
        self.assertIn('en', supported)
        self.assertEqual(len(supported), 2)
    
    def test_language_tabs_generation(self):
        """Test generation of language tabs"""
        tabs = self.admin.get_language_tabs()
        self.assertEqual(len(tabs), 2)  # Korean and English
        
        # Check that tabs have correct headings
        headings = [tab.heading for tab in tabs]
        self.assertIn('한국어', headings)
        self.assertIn('English', headings)
    
    def test_content_completeness_calculation(self):
        """Test content completeness calculation"""
        completeness = self.admin.get_content_completeness(self.test_instance)
        
        # Korean should be 100% complete
        self.assertEqual(completeness['ko']['completed'], 2)
        self.assertEqual(completeness['ko']['total'], 2)
        self.assertEqual(completeness['ko']['percentage'], 100)
        
        # English should be 50% complete (missing description)
        self.assertEqual(completeness['en']['completed'], 1)
        self.assertEqual(completeness['en']['total'], 2)
        self.assertEqual(completeness['en']['percentage'], 50)
    
    def test_has_language_content(self):
        """Test checking if instance has content in specific language"""
        self.assertTrue(self.admin.has_language_content(self.test_instance, 'ko'))
        self.assertTrue(self.admin.has_language_content(self.test_instance, 'en'))
        
        # Test with empty instance
        empty_instance = TestMultilingualModel()
        self.assertFalse(self.admin.has_language_content(empty_instance, 'ko'))
        self.assertFalse(self.admin.has_language_content(empty_instance, 'en'))
    
    def test_multilingual_content_validation(self):
        """Test multilingual content validation"""
        # Valid instance with content in both languages
        valid_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='English Title',
            description_ko='한국어 설명',
            description_en='English Description',
        )
        
        errors = self.admin.validate_multilingual_content(valid_instance)
        self.assertEqual(len(errors), 0)
        
        # Invalid instance with no content
        empty_instance = TestMultilingualModel()
        errors = self.admin.validate_multilingual_content(empty_instance)
        self.assertIn('__all__', errors)
        
        # Instance with incomplete content
        errors = self.admin.validate_multilingual_content(self.test_instance)
        self.assertIn('language_en', errors)
    
    def test_language_content_validation(self):
        """Test validation of content for specific language"""
        # Valid language content
        errors = self.admin.validate_language_content(self.test_instance, 'ko')
        self.assertEqual(len(errors), 0)
        
        # Invalid language content (missing description)
        errors = self.admin.validate_language_content(self.test_instance, 'en')
        self.assertEqual(len(errors), 1)
        self.assertIn('description', errors[0])


class LanguageSwitchMixinTestCase(BaseAdminTestCase):
    """Test language switching functionality"""
    
    def setUp(self):
        super().setUp()
        self.language_switch = LanguageSwitchMixin()
        self.factory = RequestFactory()
    
    def test_language_switch_context(self):
        """Test language switch context generation"""
        request = self.factory.get('/admin/')
        activate('ko')  # Set current language to Korean
        
        context = self.language_switch.get_language_switch_context(request)
        
        self.assertEqual(context['current_language'], 'ko')
        self.assertEqual(len(context['available_languages']), 2)
        
        # Check that Korean is marked as active
        ko_lang = next(
            lang for lang in context['available_languages'] 
            if lang['code'] == 'ko'
        )
        self.assertTrue(ko_lang['active'])
        
        # Check that English is not active
        en_lang = next(
            lang for lang in context['available_languages'] 
            if lang['code'] == 'en'
        )
        self.assertFalse(en_lang['active'])
    
    def test_language_switching(self):
        """Test language switching functionality"""
        request = self.factory.get('/admin/')
        request.session = {}
        
        # Switch to English
        result = self.language_switch.switch_language(request, 'en')
        self.assertTrue(result)
        self.assertEqual(request.session['django_language'], 'en')
        
        # Try invalid language
        result = self.language_switch.switch_language(request, 'fr')
        self.assertFalse(result)
    
    def test_language_switch_url_generation(self):
        """Test language switch URL generation"""
        request = self.factory.get('/admin/pages/')
        
        url = self.language_switch.get_language_switch_url(request, 'en')
        self.assertIn('lang=en', url)
        self.assertIn('/admin/pages/', url)


class TranslationSyncMixinTestCase(BaseAdminTestCase):
    """Test translation synchronization functionality"""
    
    def setUp(self):
        super().setUp()
        self.sync_mixin = TranslationSyncMixin()
        self.test_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='',  # Empty English title
            description_ko='한국어 설명',
            description_en='',  # Empty English description
        )
    
    def test_get_syncable_fields(self):
        """Test getting syncable fields"""
        # Base implementation returns empty list
        fields = self.sync_mixin.get_syncable_fields()
        self.assertEqual(fields, [])
    
    def test_sync_translations(self):
        """Test syncing translations between languages"""
        # Mock syncable fields
        self.sync_mixin.get_syncable_fields = lambda: ['title']
        
        activate('ko')  # Set source language
        self.sync_mixin.sync_translations(self.test_instance, 'en')
        
        # English title should now have Korean content
        self.assertEqual(self.test_instance.title_en, '한국어 제목')
    
    def test_sync_translations_no_overwrite(self):
        """Test that sync doesn't overwrite existing content"""
        # Set existing English content
        self.test_instance.title_en = 'Existing English Title'
        
        self.sync_mixin.get_syncable_fields = lambda: ['title']
        activate('ko')
        
        self.sync_mixin.sync_translations(self.test_instance, 'en')
        
        # English title should remain unchanged
        self.assertEqual(self.test_instance.title_en, 'Existing English Title')


class ContentCompletenessIndicatorTestCase(BaseAdminTestCase):
    """Test content completeness indicator"""
    
    def setUp(self):
        super().setUp()
        self.test_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='English Title',
            description_ko='한국어 설명',
            description_en='',  # Missing English description
        )
        self.indicator = ContentCompletenessIndicator(
            self.test_instance,
            ['title', 'description']
        )
    
    def test_completeness_data_calculation(self):
        """Test completeness data calculation"""
        data = self.indicator.get_completeness_data()
        
        # Korean should be complete
        self.assertEqual(data['ko']['completed'], 2)
        self.assertEqual(data['ko']['total'], 2)
        self.assertEqual(data['ko']['percentage'], 100)
        self.assertEqual(data['ko']['status'], 'complete')
        
        # English should be partial
        self.assertEqual(data['en']['completed'], 1)
        self.assertEqual(data['en']['total'], 2)
        self.assertEqual(data['en']['percentage'], 50)
        self.assertEqual(data['en']['status'], 'partial')
    
    def test_completeness_status_determination(self):
        """Test completeness status determination"""
        self.assertEqual(self.indicator.get_completeness_status(100), 'complete')
        self.assertEqual(self.indicator.get_completeness_status(85), 'mostly-complete')
        self.assertEqual(self.indicator.get_completeness_status(60), 'partial')
        self.assertEqual(self.indicator.get_completeness_status(30), 'minimal')
    
    def test_render_indicator(self):
        """Test HTML indicator rendering"""
        html = self.indicator.render_indicator()
        
        self.assertIn('language-completeness', html)
        self.assertIn('한국어', html)  # Korean language name
        self.assertIn('English', html)  # English language name
        self.assertIn('100%', html)  # Korean completeness
        self.assertIn('50%', html)   # English completeness


class MultilingualFormMixinTestCase(BaseAdminTestCase):
    """Test multilingual form mixin"""
    
    class TestMultilingualForm(MultilingualFormMixin):
        """Test form with multilingual mixin"""
        
        def __init__(self, *args, **kwargs):
            self.fields = {
                'title_ko': type('Field', (), {'label': 'Title', 'widget': type('Widget', (), {'attrs': {}})()})(),
                'title_en': type('Field', (), {'label': 'Title', 'widget': type('Widget', (), {'attrs': {}})()})(),
            }
            super().__init__(*args, **kwargs)
        
        def get_multilingual_fields(self):
            return ['title']
        
        def clean(self):
            return {}  # Mock clean method
    
    def test_form_field_styling(self):
        """Test that multilingual fields get proper styling"""
        form = self.TestMultilingualForm()
        
        # Check Korean field
        ko_attrs = form.fields['title_ko'].widget.attrs
        self.assertIn('language-field', ko_attrs['class'])
        self.assertIn('language-ko', ko_attrs['class'])
        self.assertEqual(ko_attrs['data-language'], 'ko')
        
        # Check English field
        en_attrs = form.fields['title_en'].widget.attrs
        self.assertIn('language-field', en_attrs['class'])
        self.assertIn('language-en', en_attrs['class'])
        self.assertEqual(en_attrs['data-language'], 'en')
    
    def test_multilingual_form_validation(self):
        """Test multilingual form validation"""
        # This would need a proper form implementation with cleaned_data
        # For now, we test the basic structure
        form = self.TestMultilingualForm()
        self.assertIsNotNone(form)


class LanguageWorkflowMixinTestCase(BaseAdminTestCase):
    """Test language-specific workflow management"""
    
    class TestWorkflowMixin(LanguageWorkflowMixin):
        def get_multilingual_fields(self):
            return ['title', 'description']
    
    def setUp(self):
        super().setUp()
        self.workflow = self.TestWorkflowMixin()
        self.complete_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='English Title',
            description_ko='한국어 설명',
            description_en='English Description',
        )
        self.incomplete_instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='',  # Missing English title
            description_ko='한국어 설명',
            description_en='',  # Missing English description
        )
    
    def test_can_publish_language_complete_content(self):
        """Test publishing permission for complete content"""
        # Complete content should be publishable
        can_publish = self.workflow.can_publish_language(
            self.superuser, self.complete_instance, 'ko'
        )
        self.assertTrue(can_publish)
        
        can_publish = self.workflow.can_publish_language(
            self.superuser, self.complete_instance, 'en'
        )
        self.assertTrue(can_publish)
    
    def test_can_publish_language_incomplete_content(self):
        """Test publishing permission for incomplete content"""
        # Incomplete content should not be publishable
        can_publish = self.workflow.can_publish_language(
            self.superuser, self.incomplete_instance, 'en'
        )
        self.assertFalse(can_publish)  # 0% complete, below 80% threshold
    
    def test_get_publishable_languages(self):
        """Test getting publishable languages"""
        publishable = self.workflow.get_publishable_languages(
            self.superuser, self.complete_instance
        )
        
        lang_codes = [lang[0] for lang in publishable]
        self.assertIn('ko', lang_codes)
        self.assertIn('en', lang_codes)
        
        # Test with incomplete instance
        publishable = self.workflow.get_publishable_languages(
            self.superuser, self.incomplete_instance
        )
        
        lang_codes = [lang[0] for lang in publishable]
        self.assertIn('ko', lang_codes)  # Korean is complete
        self.assertNotIn('en', lang_codes)  # English is incomplete


class MultilingualIntegrationTestCase(BaseAdminTestCase):
    """Test multilingual functionality integration"""
    
    def test_language_settings_integration(self):
        """Test that language settings are properly configured"""
        self.assertIn('ko', [lang[0] for lang in settings.LANGUAGES])
        self.assertIn('en', [lang[0] for lang in settings.LANGUAGES])
        self.assertEqual(len(settings.LANGUAGES), 2)
    
    def test_multilingual_admin_workflow(self):
        """Test complete multilingual admin workflow"""
        # Create multilingual content
        admin = TestMultilingualAdmin()
        instance = TestMultilingualModel(
            title_ko='한국어 제목',
            title_en='English Title',
            description_ko='한국어 설명',
            description_en='English Description',
        )
        
        # Check content completeness
        completeness = admin.get_content_completeness(instance)
        self.assertEqual(completeness['ko']['percentage'], 100)
        self.assertEqual(completeness['en']['percentage'], 100)
        
        # Validate content
        errors = admin.validate_multilingual_content(instance)
        self.assertEqual(len(errors), 0)
        
        # Test workflow permissions
        workflow = LanguageWorkflowMixinTestCase.TestWorkflowMixin()
        publishable = workflow.get_publishable_languages(self.superuser, instance)
        self.assertEqual(len(publishable), 2)  # Both languages publishable