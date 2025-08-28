"""
Admin configuration for unified content management system
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList

from .models import (
    Member, SocialMediaPlatform, SocialLink, PageView,
    CategoryPage, ContentPage, ContributeMethod, FAQ
)


# Register Member as a Wagtail snippet
@register_snippet
class MemberSnippet(Member):
    """Proxy model to register Member as a Wagtail snippet"""
    
    class Meta:
        proxy = True
        verbose_name = "Member/Organizer"
        verbose_name_plural = "Members/Organizers"
    
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('member_type'),
            FieldPanel('role'),
            FieldPanel('bio'),
            FieldPanel('photo'),
        ], heading="Basic Information"),
        
        MultiFieldPanel([
            FieldPanel('email'),
        ], heading="Contact Information"),
        
        MultiFieldPanel([
            FieldPanel('tags'),
            FieldPanel('joined_date'),
        ], heading="Additional Information"),
        
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('is_featured'),
            FieldPanel('show_in_member_list'),
            FieldPanel('order'),
        ], heading="Display Settings"),
    ]


# Member admin is defined below with inlines


@register_snippet
class SocialMediaPlatformSnippet(SocialMediaPlatform):
    """Proxy model to register SocialMediaPlatform as a Wagtail snippet"""
    
    class Meta:
        proxy = True
        verbose_name = "Social Media Platform"
        verbose_name_plural = "Social Media Platforms"
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('url_pattern'),
        
        MultiFieldPanel([
            FieldPanel('icon_class'),
            FieldPanel('color'),
        ], heading="Display Settings"),
        
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('order'),
        ], heading="Status"),
    ]


@admin.register(SocialMediaPlatform)
class SocialMediaPlatformAdmin(admin.ModelAdmin):
    """Django admin for SocialMediaPlatform model"""
    
    list_display = [
        'name',
        'slug',
        'icon_preview',
        'color_preview',
        'is_active',
        'order',
    ]
    
    list_filter = [
        'is_active',
    ]
    
    search_fields = [
        'name',
        'slug',
    ]
    
    list_editable = [
        'is_active',
        'order',
    ]
    
    ordering = ['order', 'name']
    
    def icon_preview(self, obj):
        """Preview the icon"""
        if obj.icon_class:
            return format_html(
                '<i class="{}"></i> {}',
                obj.icon_class,
                obj.icon_class
            )
        return "-"
    icon_preview.short_description = "Icon"
    
    def color_preview(self, obj):
        """Preview the color"""
        if obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 2px 10px; color: white;">{}</span>',
                obj.color,
                obj.color
            )
        return "-"
    color_preview.short_description = "Color"


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    """Django admin for SocialLink model"""
    
    list_display = [
        'member',
        'platform',
        'display_link',
        'is_active',
        'order',
    ]
    
    list_filter = [
        'platform',
        'is_active',
        'member__member_type',
    ]
    
    search_fields = [
        'member__name',
        'platform__name',
        'url',
        'username',
    ]
    
    list_editable = [
        'is_active',
        'order',
    ]
    
    ordering = ['member', 'order', 'platform']
    
    autocomplete_fields = ['member', 'platform']
    
    def display_link(self, obj):
        """Display the social link"""
        url = obj.full_url
        if url:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url,
                obj.get_display_name()
            )
        return "-"
    display_link.short_description = "Link"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    """Django admin for PageView model"""
    
    list_display = [
        'page',
        'viewed_at',
        'ip_address',
        'session_key',
        'referrer_preview',
    ]
    
    list_filter = [
        'viewed_at',
        ('page', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'page__title',
        'ip_address',
        'session_key',
        'referrer',
    ]
    
    readonly_fields = [
        'page',
        'ip_address',
        'user_agent',
        'referrer',
        'session_key',
        'viewed_at',
    ]
    
    ordering = ['-viewed_at']
    
    def referrer_preview(self, obj):
        """Preview referrer URL"""
        if obj.referrer:
            # Truncate long URLs
            display_url = obj.referrer[:50]
            if len(obj.referrer) > 50:
                display_url += "..."
            return format_html(
                '<a href="{}" target="_blank" title="{}">{}</a>',
                obj.referrer,
                obj.referrer,
                display_url
            )
        return "-"
    referrer_preview.short_description = "Referrer"
    
    def has_add_permission(self, request):
        """Prevent manual creation of page views"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make page views read-only"""
        return False


# Inline admin for social links within Member admin
class SocialLinkInline(admin.TabularInline):
    """Inline admin for social links"""
    model = SocialLink
    extra = 1
    fields = ['platform', 'url', 'username', 'display_name', 'is_active', 'order']
    ordering = ['order', 'platform']
    autocomplete_fields = ['platform']


# Member admin with inline social links
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Django admin for Member model with inline social links"""
    
    list_display = [
        'name',
        'member_type',
        'role',
        'email',
        'is_active',
        'is_featured',
        'order',
        'view_social_links',
    ]
    
    list_filter = [
        'member_type',
        'is_active',
        'is_featured',
        'show_in_member_list',
        'joined_date',
    ]
    
    search_fields = [
        'name',
        'role',
        'email',
        'bio',
    ]
    
    list_editable = [
        'is_active',
        'is_featured',
        'order',
    ]
    
    ordering = ['member_type', 'order', 'name']
    
    inlines = [SocialLinkInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'member_type', 'role', 'bio', 'photo')
        }),
        ('Contact Information', {
            'fields': ('email',)
        }),
        ('Additional Information', {
            'fields': ('tags', 'joined_date')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'show_in_member_list', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def view_social_links(self, obj):
        """Display social links count with link to inline admin"""
        count = obj.social_links.count()
        if count:
            return format_html(
                '<a href="/admin/content/sociallink/?member__id__exact={}">{} links</a>',
                obj.id,
                count
            )
        return "No links"
    view_social_links.short_description = "Social Links"


@register_snippet
class ContributeMethodSnippet(ContributeMethod):
    """Proxy model to register ContributeMethod as a Wagtail snippet"""
    
    class Meta:
        proxy = True
        verbose_name = "기여 방법"
        verbose_name_plural = "기여 방법들"
    
    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('description'),
            FieldPanel('icon_class'),
        ], heading="기본 정보"),
        
        MultiFieldPanel([
            FieldPanel('link_url'),
            FieldPanel('link_text'),
        ], heading="링크 설정"),
        
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="표시 설정"),
    ]


@admin.register(ContributeMethod)
class ContributeMethodAdmin(admin.ModelAdmin):
    """Django admin for ContributeMethod model"""
    
    list_display = [
        'title',
        'icon_preview',
        'description_preview',
        'link_preview',
        'order',
        'is_active',
        'updated_at',
    ]
    
    list_filter = [
        'is_active',
    ]
    
    search_fields = [
        'title',
        'description',
    ]
    
    list_editable = [
        'order',
        'is_active',
    ]
    
    ordering = ['order', 'title']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'icon_class'),
            'description': '기여 방법의 기본 정보를 입력하세요.'
        }),
        ('링크 설정', {
            'fields': ('link_url', 'link_text'),
            'description': '자세히 보기 버튼이 연결될 URL과 버튼 텍스트를 설정하세요. (예: mailto:, https:// 등)'
        }),
        ('표시 설정', {
            'fields': ('order', 'is_active'),
            'description': '표시 순서와 활성화 여부를 설정하세요.'
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def icon_preview(self, obj):
        """Preview the icon"""
        if obj.icon_class:
            return format_html(
                '<i class="{}"></i> {}',
                obj.icon_class,
                obj.icon_class
            )
        return "-"
    icon_preview.short_description = "아이콘"
    
    def description_preview(self, obj):
        """Preview the description (truncated)"""
        if obj.description:
            preview = obj.description[:50]
            if len(obj.description) > 50:
                preview += "..."
            return preview
        return "-"
    description_preview.short_description = "설명"
    
    def link_preview(self, obj):
        """Preview the link"""
        if obj.link_url:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.link_url,
                obj.link_text or "자세히 보기"
            )
        return "-"
    link_preview.short_description = "링크"


@register_snippet
class FAQSnippet(FAQ):
    """Proxy model to register FAQ as a Wagtail snippet"""
    
    class Meta:
        proxy = True
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    panels = [
        MultiFieldPanel([
            FieldPanel('question'),
            FieldPanel('answer'),
        ], heading="FAQ 내용"),
        
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="표시 설정"),
    ]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Django admin for FAQ model"""
    
    list_display = [
        'question',
        'answer_preview',
        'order',
        'is_active',
        'updated_at',
    ]
    
    list_filter = [
        'is_active',
    ]
    
    search_fields = [
        'question',
        'answer',
    ]
    
    list_editable = [
        'order',
        'is_active',
    ]
    
    ordering = ['order', 'question']
    
    fieldsets = (
        ('FAQ 내용', {
            'fields': ('question', 'answer'),
            'description': '질문과 답변을 입력하세요.'
        }),
        ('표시 설정', {
            'fields': ('order', 'is_active'),
            'description': '표시 순서와 활성화 여부를 설정하세요.'
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def answer_preview(self, obj):
        """Preview the answer (truncated)"""
        if obj.answer:
            preview = obj.answer[:100]
            if len(obj.answer) > 100:
                preview += "..."
            return preview
        return "-"
    answer_preview.short_description = "답변 미리보기"