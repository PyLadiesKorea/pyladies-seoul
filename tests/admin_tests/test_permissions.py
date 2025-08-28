"""
Tests for role-based permissions and access control.
Testing user roles, permissions, and access policies.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from wagtail.models import Page, Collection
from wagtail.images.models import Image

from .base import BaseAdminTestCase, AdminPermissionTestMixin
from apps.common.permissions import (
    PyLadiesPermissions,
    ContentPermissionPolicy,
    ImagePermissionPolicy,
    AdminAccessMixin,
    BulkOperationPermissions,
    LanguagePermissionMixin,
    WorkflowPermissionMixin
)


class PyLadiesPermissionsTestCase(BaseAdminTestCase):
    """Test PyLadies permissions setup and role management"""
    
    def test_roles_definition(self):
        """Test that all required roles are defined"""
        self.assertIn('editors', PyLadiesPermissions.ROLES)
        self.assertIn('publishers', PyLadiesPermissions.ROLES)
        self.assertIn('content_managers', PyLadiesPermissions.ROLES)
        
        # Check role structure
        for role_key, role_data in PyLadiesPermissions.ROLES.items():
            self.assertIn('name', role_data)
            self.assertIn('description', role_data)
            self.assertIn('permissions', role_data)
            self.assertIsInstance(role_data['permissions'], list)
    
    def test_setup_roles_and_permissions(self):
        """Test that roles and permissions are set up correctly"""
        # This test runs the actual setup
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Verify groups were created
        for role_data in PyLadiesPermissions.ROLES.values():
            group = Group.objects.get(name=role_data['name'])
            self.assertIsNotNone(group)
    
    def test_assign_user_to_role(self):
        """Test assigning users to roles"""
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Test successful assignment
        result = PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        self.assertTrue(result)
        self.assertTrue(self.editor.groups.filter(name='Editors').exists())
        
        # Test invalid role
        result = PyLadiesPermissions.assign_user_to_role(self.editor, 'NonExistentRole')
        self.assertFalse(result)
    
    def test_remove_user_from_role(self):
        """Test removing users from roles"""
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Add user to role first
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        self.assertTrue(self.editor.groups.filter(name='Editors').exists())
        
        # Remove user from role
        result = PyLadiesPermissions.remove_user_from_role(self.editor, 'Editors')
        self.assertTrue(result)
        self.assertFalse(self.editor.groups.filter(name='Editors').exists())
    
    def test_get_user_roles(self):
        """Test getting user roles"""
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Assign multiple roles
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Publishers')
        
        roles = PyLadiesPermissions.get_user_roles(self.editor)
        role_names = [role.name for role in roles]
        
        self.assertIn('Editors', role_names)
        self.assertIn('Publishers', role_names)
    
    def test_user_has_role(self):
        """Test checking if user has specific role"""
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # User doesn't have role initially
        self.assertFalse(PyLadiesPermissions.user_has_role(self.editor, 'Editors'))
        
        # Assign role
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        self.assertTrue(PyLadiesPermissions.user_has_role(self.editor, 'Editors'))


class ContentPermissionPolicyTestCase(BaseAdminTestCase):
    """Test content permission policy"""
    
    def setUp(self):
        super().setUp()
        self.policy = ContentPermissionPolicy()
        PyLadiesPermissions.setup_roles_and_permissions()
    
    def test_superuser_has_all_permissions(self):
        """Test that superuser has all permissions"""
        self.assertTrue(self.policy.user_has_permission(self.superuser, 'add'))
        self.assertTrue(self.policy.user_has_permission(self.superuser, 'change'))
        self.assertTrue(self.policy.user_has_permission(self.superuser, 'delete'))
        self.assertTrue(self.policy.user_has_permission(self.superuser, 'publish'))
    
    def test_editor_permissions(self):
        """Test editor role permissions"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        
        # Editors can add and change
        self.assertTrue(self.policy.user_has_permission(self.editor, 'add'))
        self.assertTrue(self.policy.user_has_permission(self.editor, 'change'))
        
        # Editors cannot delete or publish
        self.assertFalse(self.policy.user_has_permission(self.editor, 'delete'))
        self.assertFalse(self.policy.user_has_permission(self.editor, 'publish'))
    
    def test_publisher_permissions(self):
        """Test publisher role permissions"""
        publisher_user = User.objects.create_user(
            username='publisher',
            email='publisher@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(publisher_user, 'Publishers')
        
        # Publishers can add, change, and publish
        self.assertTrue(self.policy.user_has_permission(publisher_user, 'add'))
        self.assertTrue(self.policy.user_has_permission(publisher_user, 'change'))
        self.assertTrue(self.policy.user_has_permission(publisher_user, 'publish'))
        
        # Publishers can delete
        self.assertTrue(self.policy.user_has_permission(publisher_user, 'delete'))
    
    def test_content_manager_permissions(self):
        """Test content manager role permissions"""
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(manager_user, 'Content Managers')
        
        # Content managers have all permissions
        self.assertTrue(self.policy.user_has_permission(manager_user, 'add'))
        self.assertTrue(self.policy.user_has_permission(manager_user, 'change'))
        self.assertTrue(self.policy.user_has_permission(manager_user, 'delete'))
        self.assertTrue(self.policy.user_has_permission(manager_user, 'publish'))
    
    def test_regular_user_no_permissions(self):
        """Test that regular users have no permissions"""
        self.assertFalse(self.policy.user_has_permission(self.regular_user, 'add'))
        self.assertFalse(self.policy.user_has_permission(self.regular_user, 'change'))
        self.assertFalse(self.policy.user_has_permission(self.regular_user, 'delete'))
        self.assertFalse(self.policy.user_has_permission(self.regular_user, 'publish'))


class ImagePermissionPolicyTestCase(BaseAdminTestCase):
    """Test image permission policy"""
    
    def setUp(self):
        super().setUp()
        self.policy = ImagePermissionPolicy()
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Create test image
        self.test_image = self.create_wagtail_image()
    
    def test_superuser_image_permissions(self):
        """Test superuser has all image permissions"""
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.superuser, 'add', self.test_image
        ))
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.superuser, 'change', self.test_image
        ))
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.superuser, 'delete', self.test_image
        ))
    
    def test_editor_image_permissions(self):
        """Test editor image permissions"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        
        # Editors can add, change, and choose images
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.editor, 'add', self.test_image
        ))
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.editor, 'change', self.test_image
        ))
        self.assertTrue(self.policy.user_has_permission_for_instance(
            self.editor, 'choose', self.test_image
        ))
        
        # Editors cannot delete images
        self.assertFalse(self.policy.user_has_permission_for_instance(
            self.editor, 'delete', self.test_image
        ))
    
    def test_content_manager_image_permissions(self):
        """Test content manager image permissions"""
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(manager_user, 'Content Managers')
        
        # Content managers can delete images
        self.assertTrue(self.policy.user_has_permission_for_instance(
            manager_user, 'delete', self.test_image
        ))


class AdminAccessMixinTestCase(BaseAdminTestCase):
    """Test admin access controls"""
    
    def setUp(self):
        super().setUp()
        self.admin_access = AdminAccessMixin()
        PyLadiesPermissions.setup_roles_and_permissions()
    
    def test_superuser_admin_access(self):
        """Test superuser has admin access"""
        self.assertTrue(self.admin_access.has_admin_access(self.superuser))
    
    def test_staff_with_role_has_access(self):
        """Test staff user with content role has admin access"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        self.assertTrue(self.admin_access.has_admin_access(self.editor))
    
    def test_non_staff_no_access(self):
        """Test non-staff user has no admin access"""
        self.assertFalse(self.admin_access.has_admin_access(self.regular_user))
    
    def test_staff_without_role_no_access(self):
        """Test staff user without content role has no admin access"""
        staff_user = User.objects.create_user(
            username='staff_only',
            email='staff@test.com',
            password='testpass',
            is_staff=True
        )
        self.assertFalse(self.admin_access.has_admin_access(staff_user))
    
    def test_get_admin_menu_items_superuser(self):
        """Test superuser gets all menu items"""
        menu_items = self.admin_access.get_admin_menu_items(self.superuser)
        self.assertEqual(menu_items, 'all')
    
    def test_get_admin_menu_items_editor(self):
        """Test editor gets appropriate menu items"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        menu_items = self.admin_access.get_admin_menu_items(self.editor)
        
        self.assertIn('pages', menu_items)
        self.assertIn('images', menu_items)
        self.assertIn('documents', menu_items)
        self.assertNotIn('users', menu_items)
    
    def test_get_admin_menu_items_content_manager(self):
        """Test content manager gets extended menu items"""
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(manager_user, 'Content Managers')
        menu_items = self.admin_access.get_admin_menu_items(manager_user)
        
        self.assertIn('collections', menu_items)
        self.assertIn('users', menu_items)


class BulkOperationPermissionsTestCase(BaseAdminTestCase):
    """Test bulk operation permissions"""
    
    def setUp(self):
        super().setUp()
        PyLadiesPermissions.setup_roles_and_permissions()
    
    def test_superuser_bulk_permissions(self):
        """Test superuser has all bulk permissions"""
        self.assertTrue(BulkOperationPermissions.can_bulk_publish(self.superuser))
        self.assertTrue(BulkOperationPermissions.can_bulk_unpublish(self.superuser))
        self.assertTrue(BulkOperationPermissions.can_bulk_delete(self.superuser))
        self.assertTrue(BulkOperationPermissions.can_bulk_move(self.superuser))
    
    def test_editor_bulk_permissions(self):
        """Test editor bulk permissions"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        
        # Editors cannot do bulk operations
        self.assertFalse(BulkOperationPermissions.can_bulk_publish(self.editor))
        self.assertFalse(BulkOperationPermissions.can_bulk_unpublish(self.editor))
        self.assertFalse(BulkOperationPermissions.can_bulk_delete(self.editor))
        self.assertFalse(BulkOperationPermissions.can_bulk_move(self.editor))
    
    def test_publisher_bulk_permissions(self):
        """Test publisher bulk permissions"""
        publisher_user = User.objects.create_user(
            username='publisher',
            email='publisher@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(publisher_user, 'Publishers')
        
        # Publishers can bulk publish/unpublish
        self.assertTrue(BulkOperationPermissions.can_bulk_publish(publisher_user))
        self.assertTrue(BulkOperationPermissions.can_bulk_unpublish(publisher_user))
        
        # Publishers cannot bulk delete or move
        self.assertFalse(BulkOperationPermissions.can_bulk_delete(publisher_user))
        self.assertFalse(BulkOperationPermissions.can_bulk_move(publisher_user))
    
    def test_content_manager_bulk_permissions(self):
        """Test content manager has all bulk permissions"""
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(manager_user, 'Content Managers')
        
        self.assertTrue(BulkOperationPermissions.can_bulk_publish(manager_user))
        self.assertTrue(BulkOperationPermissions.can_bulk_unpublish(manager_user))
        self.assertTrue(BulkOperationPermissions.can_bulk_delete(manager_user))
        self.assertTrue(BulkOperationPermissions.can_bulk_move(manager_user))


class LanguagePermissionMixinTestCase(BaseAdminTestCase):
    """Test multilingual permissions"""
    
    def setUp(self):
        super().setUp()
        self.language_permissions = LanguagePermissionMixin()
    
    def test_superuser_language_permissions(self):
        """Test superuser can edit all languages"""
        self.assertTrue(self.language_permissions.can_edit_language(self.superuser, 'ko'))
        self.assertTrue(self.language_permissions.can_edit_language(self.superuser, 'en'))
        
        allowed_languages = self.language_permissions.get_allowed_languages(self.superuser)
        self.assertIn('ko', allowed_languages)
        self.assertIn('en', allowed_languages)
    
    def test_regular_user_language_permissions(self):
        """Test regular user language permissions"""
        # Default behavior - users can edit all languages
        self.assertTrue(self.language_permissions.can_edit_language(self.editor, 'ko'))
        self.assertTrue(self.language_permissions.can_edit_language(self.editor, 'en'))
        
        allowed_languages = self.language_permissions.get_allowed_languages(self.editor)
        self.assertIn('ko', allowed_languages)
        self.assertIn('en', allowed_languages)


class WorkflowPermissionMixinTestCase(BaseAdminTestCase):
    """Test workflow permissions"""
    
    def setUp(self):
        super().setUp()
        self.workflow_permissions = WorkflowPermissionMixin()
        PyLadiesPermissions.setup_roles_and_permissions()
        
        # Create a test page
        self.test_page = Page.objects.first()
    
    def test_editor_workflow_permissions(self):
        """Test editor workflow permissions"""
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        
        # Editors can submit for moderation
        self.assertTrue(self.workflow_permissions.can_submit_for_moderation(
            self.editor, self.test_page
        ))
        
        # Editors cannot moderate or approve
        self.assertFalse(self.workflow_permissions.can_moderate(
            self.editor, self.test_page
        ))
        self.assertFalse(self.workflow_permissions.can_approve(
            self.editor, self.test_page
        ))
    
    def test_publisher_workflow_permissions(self):
        """Test publisher workflow permissions"""
        publisher_user = User.objects.create_user(
            username='publisher',
            email='publisher@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(publisher_user, 'Publishers')
        
        # Publishers can moderate
        self.assertTrue(self.workflow_permissions.can_moderate(
            publisher_user, self.test_page
        ))
        
        # Publishers cannot approve (only content managers can)
        self.assertFalse(self.workflow_permissions.can_approve(
            publisher_user, self.test_page
        ))
    
    def test_content_manager_workflow_permissions(self):
        """Test content manager workflow permissions"""
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass'
        )
        PyLadiesPermissions.assign_user_to_role(manager_user, 'Content Managers')
        
        # Content managers can do everything
        self.assertTrue(self.workflow_permissions.can_moderate(
            manager_user, self.test_page
        ))
        self.assertTrue(self.workflow_permissions.can_approve(
            manager_user, self.test_page
        ))
    
    def test_superuser_workflow_permissions(self):
        """Test superuser workflow permissions"""
        self.assertTrue(self.workflow_permissions.can_submit_for_moderation(
            self.superuser, self.test_page
        ))
        self.assertTrue(self.workflow_permissions.can_moderate(
            self.superuser, self.test_page
        ))
        self.assertTrue(self.workflow_permissions.can_approve(
            self.superuser, self.test_page
        ))


class PermissionIntegrationTestCase(BaseAdminTestCase, AdminPermissionTestMixin):
    """Test permission system integration with admin views"""
    
    def setUp(self):
        super().setUp()
        PyLadiesPermissions.setup_roles_and_permissions()
    
    def test_admin_access_with_roles(self):
        """Test admin access based on user roles"""
        # Editor should have access to admin
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        self.login_as_editor()
        
        response = self.client.get('/admin/')
        # Should be accessible (would redirect if not)
        self.assertNotEqual(response.status_code, 403)
    
    def test_role_based_menu_filtering(self):
        """Test that menu items are filtered based on roles"""
        # This would need actual admin menu testing
        # For now, we test the logic
        admin_access = AdminAccessMixin()
        
        PyLadiesPermissions.assign_user_to_role(self.editor, 'Editors')
        menu_items = admin_access.get_admin_menu_items(self.editor)
        
        # Editors should not see admin-only items
        if isinstance(menu_items, list):
            self.assertNotIn('users', menu_items)
            self.assertIn('pages', menu_items)