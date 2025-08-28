"""
Wagtail hooks for unified content management system using ModelViewSet
"""

from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets import ViewSetGroup

from .models import Member, SocialMediaPlatform, SocialLink, PageView


class MemberViewSet(ModelViewSet):
    model = Member
    menu_label = 'Members'
    icon = 'user'
    menu_order = 200
    add_to_admin_menu = True
    list_display = ['name', 'member_type', 'role', 'is_active', 'is_featured']
    list_filter = ['member_type', 'is_active', 'is_featured']
    search_fields = ['name', 'role']
    ordering = ['member_type', 'order', 'name']
    form_fields = ['name', 'member_type', 'role', 'bio', 'photo', 'email', 'tags', 'is_active', 'is_featured', 'show_in_member_list', 'order', 'joined_date']


class SocialMediaPlatformViewSet(ModelViewSet):
    model = SocialMediaPlatform
    menu_label = 'Social Platforms'
    icon = 'site'
    menu_order = 201
    add_to_admin_menu = True
    add_to_settings_menu = True
    list_display = ['name', 'slug', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    ordering = ['order', 'name']
    form_fields = ['name', 'slug', 'url_pattern', 'icon_class', 'color', 'is_active', 'order']


class SocialLinkViewSet(ModelViewSet):
    model = SocialLink
    menu_label = 'Social Links'
    icon = 'link'
    menu_order = 202
    add_to_admin_menu = True
    list_display = ['member', 'platform', 'is_active', 'order']
    list_filter = ['platform', 'is_active']
    search_fields = ['member__name', 'platform__name', 'url', 'username']
    ordering = ['member', 'order']
    form_fields = ['member', 'platform', 'url', 'username', 'display_name', 'is_active', 'order']


class PageViewViewSet(ModelViewSet):
    model = PageView
    menu_label = 'Page Analytics'
    icon = 'view'
    menu_order = 300
    add_to_admin_menu = True
    add_to_settings_menu = True
    list_display = ['page', 'viewed_at', 'session_key']
    list_filter = ['viewed_at']
    search_fields = ['page__title']
    ordering = ['-viewed_at']
    form_fields = ['page', 'ip_address', 'user_agent', 'referrer']


# Register ViewSets
@hooks.register('register_admin_viewset')
def register_member_viewset():
    return MemberViewSet('members')


@hooks.register('register_admin_viewset')
def register_social_platform_viewset():
    return SocialMediaPlatformViewSet('social_platforms')


@hooks.register('register_admin_viewset')
def register_social_link_viewset():
    return SocialLinkViewSet('social_links')


@hooks.register('register_admin_viewset')
def register_page_view_viewset():
    return PageViewViewSet('page_analytics')


# Alternative: Register ViewSet Group instead of individual viewsets
# @hooks.register('register_admin_viewset')
# def register_content_management_group():
#     return ContentManagementGroup()