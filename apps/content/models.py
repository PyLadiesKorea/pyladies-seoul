"""PyLadies Seoul website models."""

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from apps.common.models import TimeStampedModel


# Base Models

class BasePage(Page):
    """Base page model with common fields for all pages."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Description for search engines (max 160 characters)"
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image for social media sharing"
    )
    
    promote_panels = Page.promote_panels + [
        FieldPanel('meta_description'),
        FieldPanel('social_image'),
    ]
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to add custom logic"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)




# Homepage Models

class HeroBlock(StructBlock):
    """Hero section block for homepage"""
    title = CharBlock(max_length=255, help_text="Hero title")
    subtitle = RichTextBlock(help_text="Hero subtitle")
    cta_text = CharBlock(max_length=100, help_text="Call-to-action button text", required=False)
    cta_url = blocks.URLBlock(help_text="Call-to-action button URL", required=False)
    
    class Meta:
        template = "blocks/hero_block.html"
        icon = "home"
        label = "Hero Section"


class FeaturedEventsBlock(StructBlock):
    """Featured events block"""
    title = CharBlock(max_length=255, default="Upcoming Events")
    show_count = blocks.IntegerBlock(min_value=1, max_value=6, default=3, help_text="Number of events to show")
    
    class Meta:
        template = "blocks/featured_events_block.html"
        icon = "date"
        label = "Featured Events"


class StatisticsBlock(StructBlock):
    """Statistics/numbers block"""
    title = CharBlock(max_length=255, default="PyLadies Seoul in Numbers")
    statistics = blocks.ListBlock(
        StructBlock([
            ('number', CharBlock(max_length=50, help_text="e.g., 500+")),
            ('label', CharBlock(max_length=100, help_text="e.g., Members")),
            ('description', CharBlock(max_length=200, required=False)),
        ])
    )
    
    class Meta:
        template = "blocks/statistics_block.html"
        icon = "snippet"
        label = "Statistics"


class HomePage(BasePage):
    """Homepage model"""
    
    hero_title = models.CharField(max_length=255, default="PyLadies Seoul")
    hero_subtitle = RichTextField(default="Empowering women in Python development")
    hero_cta_text = models.CharField(max_length=100, default="Join Us", blank=True)
    hero_cta_url = models.URLField(blank=True)
    
    body = StreamField([
        ('hero_section', HeroBlock()),
        ('featured_events', FeaturedEventsBlock()),
        ('statistics', StatisticsBlock()),
        ('rich_text', RichTextBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('hero_title'),
        FieldPanel('hero_subtitle'),
        FieldPanel('hero_cta_text'),
        FieldPanel('hero_cta_url'),
        FieldPanel('body'),
    ]
    
    max_count = 1
    subpage_types = ['content.CategoryPage']
    
    class Meta:
        verbose_name = "Homepage"


# Content Blocks


# Custom tag model for ContentPage
class ContentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'ContentPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


# Block definitions (reusing from pages app with some additions)
class ImageBlock(StructBlock):
    """Full-width image block with caption"""
    image = ImageChooserBlock(help_text="Choose an image to display")
    caption = CharBlock(max_length=255, help_text="Image caption", required=False)
    alt_text = CharBlock(max_length=255, help_text="Alternative text for accessibility", required=False)
    
    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        label = "Full Width Image"


class ImageWithTextBlock(StructBlock):
    """Image with text side by side"""
    image = ImageChooserBlock(help_text="Choose an image")
    image_position = blocks.ChoiceBlock(
        choices=[
            ('left', 'Image on Left'),
            ('right', 'Image on Right'),
        ],
        default='left',
        help_text="Position of the image"
    )
    title = CharBlock(max_length=255, help_text="Section title", required=False)
    text = RichTextBlock(help_text="Text content")
    alt_text = CharBlock(max_length=255, help_text="Alternative text for accessibility", required=False)
    
    class Meta:
        template = "blocks/image_with_text_block.html"
        icon = "image"
        label = "Image with Text"


class GalleryBlock(StructBlock):
    """Image gallery block"""
    title = CharBlock(max_length=255, help_text="Gallery title", required=False)
    images = blocks.ListBlock(
        StructBlock([
            ('image', ImageChooserBlock()),
            ('caption', CharBlock(max_length=255, required=False)),
            ('alt_text', CharBlock(max_length=255, required=False)),
        ])
    )
    
    class Meta:
        template = "blocks/gallery_block.html"
        icon = "image"
        label = "Image Gallery"


class QuoteBlock(StructBlock):
    """Quote block for interviews and testimonials"""
    quote = blocks.TextBlock(help_text="Quote text")
    author = CharBlock(max_length=255, help_text="Quote author", required=False)
    author_title = CharBlock(max_length=255, help_text="Author's title or position", required=False)
    
    class Meta:
        template = "blocks/quote_block.html"
        icon = "openquote"
        label = "Quote"


class CodeBlock(StructBlock):
    """Code block with syntax highlighting"""
    language = blocks.ChoiceBlock(
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('html', 'HTML'),
            ('css', 'CSS'),
            ('sql', 'SQL'),
            ('bash', 'Bash'),
        ],
        default='python',
        help_text="Programming language"
    )
    code = blocks.TextBlock(help_text="Code snippet")
    caption = CharBlock(max_length=255, help_text="Code caption", required=False)
    
    class Meta:
        template = "blocks/code_block.html"
        icon = "code"
        label = "Code Block"


class SpeakerBlock(StructBlock):
    """Speaker block for events"""
    name = CharBlock(max_length=255, help_text="Speaker name")
    title = CharBlock(max_length=255, help_text="Speaker title/position", required=False)
    bio = RichTextBlock(help_text="Speaker bio", required=False)
    photo = ImageChooserBlock(help_text="Speaker photo", required=False)
    
    class Meta:
        template = "blocks/speaker_block.html"
        icon = "user"
        label = "Speaker"


class EventRegistrationBlock(StructBlock):
    """Event registration block"""
    registration_url = blocks.URLBlock(help_text="Registration link URL")
    button_text = CharBlock(
        max_length=100, 
        default="Register Now",
        help_text="Button text"
    )
    deadline = blocks.DateTimeBlock(help_text="Registration deadline", required=False)
    
    class Meta:
        template = "blocks/event_registration_block.html"
        icon = "calendar-check"
        label = "Event Registration"


class CategoryPage(BasePage):
    """Category page - each category's landing page"""
    
    # Category information
    category_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="Category banner image"
    )
    intro = RichTextField(
        help_text="Category introduction text"
    )
    
    # Metadata
    show_in_navigation = models.BooleanField(
        default=True,
        help_text="Show in navigation menu"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in navigation"
    )
    
    # Page hierarchy settings  
    parent_page_types = ['content.HomePage']
    subpage_types = ['content.ContentPage']
    
    content_panels = BasePage.content_panels + [
        FieldPanel('category_image'),
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('show_in_navigation'),
            FieldPanel('order'),
        ], heading="Navigation Settings"),
    ]
    
    class Meta:
        verbose_name = "Category Page"
        ordering = ['order', 'title']
    
    def get_context(self, request, *args, **kwargs):
        """Add category-specific context"""
        context = super().get_context(request, *args, **kwargs)
        
        # Get all published content pages in this category
        content_pages = ContentPage.objects.child_of(self).live().public()
        
        # Filter by content type if requested
        content_type = request.GET.get('type')
        if content_type == 'events':
            content_pages = content_pages.filter(event_start_at__isnull=False)
        elif content_type == 'interviews':
            content_pages = content_pages.filter(related_member__isnull=False)
        
        # Order by publication date
        content_pages = content_pages.order_by('-publication_date')
        
        context['content_pages'] = content_pages
        return context


class ContentPage(BasePage):
    """Unified content page - handles all individual pages"""
    
    parent_page_types = ['content.CategoryPage']
    
    # Common metadata
    publication_date = models.DateField(
        default=timezone.now,
        help_text="Publication date"
    )
    
    # Tag system
    tags = ClusterTaggableManager(through=ContentPageTag, blank=True)
    
    # Event-related fields
    event_start_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Event start date and time"
    )
    event_end_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Event end date and time (optional)"
    )
    display_start_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Page display start date and time"
    )
    display_end_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Page display end date and time"
    )
    location = models.CharField(
        max_length=255, blank=True,
        help_text="Event location"
    )
    
    # Member connection (for interviews, speakers, etc.)
    related_member = models.ForeignKey(
        'content.Member',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='content_pages',
        help_text="Related member (interviewee, speaker, etc.)"
    )
    
    # Metadata
    is_featured = models.BooleanField(
        default=False,
        help_text="Show as featured content"
    )
    reading_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated reading time (minutes)"
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Page view count"
    )
    
    # Unified StreamField
    body = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageBlock()),
        ('image_with_text', ImageWithTextBlock()),
        ('gallery', GalleryBlock()),
        ('quote', QuoteBlock()),
        ('code', CodeBlock()),
        ('speaker', SpeakerBlock()),
        ('event_registration', EventRegistrationBlock()),
        ('markdown', MarkdownBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = BasePage.content_panels + [
        FieldPanel('publication_date'),
        FieldPanel('tags'),
        
        # Event-related fields grouped
        MultiFieldPanel([
            FieldPanel('event_start_at'),
            FieldPanel('event_end_at'),
            FieldPanel('location'),
        ], heading="Event Information", classname="collapsible collapsed"),
        
        # Display period settings
        MultiFieldPanel([
            FieldPanel('display_start_at'),
            FieldPanel('display_end_at'),
        ], heading="Display Period", classname="collapsible collapsed"),
        
        # Related member
        FieldPanel('related_member'),
        
        FieldPanel('body'),
    ]
    
    promote_panels = BasePage.promote_panels + [
        FieldPanel('is_featured'),
        FieldPanel('reading_time'),
    ]
    
    def get_related_content(self, limit=3):
        """Return related content based on tags"""
        if not self.tags.exists():
            return ContentPage.objects.none()
        
        # Find other content with the same tags
        tag_names = [tag.name for tag in self.tags.all()]
        related = ContentPage.objects.filter(
            tags__name__in=tag_names
        ).exclude(id=self.id).distinct()
        
        return related[:limit]
    
    def get_category(self):
        """Return the parent category"""
        return self.get_parent().specific
    
    @property
    def is_event(self):
        """Check if this is an event page"""
        return bool(self.event_start_at)
    
    @property
    def is_interview(self):
        """Check if this is an interview page"""
        return bool(self.related_member and self.get_category().slug == 'members')
    
    @property
    def is_upcoming_event(self):
        """Check if this is an upcoming event"""
        if self.event_start_at:
            return self.event_start_at > timezone.now()
        return False
    
    @property
    def is_past_event(self):
        """Check if this is a past event"""
        if self.event_end_at:
            return self.event_end_at < timezone.now()
        elif self.event_start_at:
            return self.event_start_at < timezone.now()
        return False
    
    @property
    def is_displayable(self):
        """Check if the page is currently displayable"""
        now = timezone.now()
        
        # Check display start time
        if self.display_start_at and now < self.display_start_at:
            return False
        
        # Check display end time
        if self.display_end_at and now > self.display_end_at:
            return False
        
        return True
    
    def increment_view_count(self):
        """Increment page view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    @classmethod
    def get_popular_content(cls, days=30, limit=10):
        """Return popular content based on view count"""
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            publication_date__gte=since,
            live=True
        ).order_by('-view_count')[:limit]
    
    class Meta:
        verbose_name = "Content Page"
        verbose_name_plural = "Content Pages"
        ordering = ['-publication_date']


class ContributeMethod(models.Model):
    """Contribution methods for Connect page"""
    
    title = models.CharField(
        max_length=100,
        help_text="제목 (예: 기부, 자원봉사)"
    )
    description = models.TextField(
        help_text="설명 내용"
    )
    icon_class = models.CharField(
        max_length=100,
        help_text="Font Awesome 아이콘 클래스 (예: fas fa-heart)"
    )
    link_url = models.URLField(
        blank=True,
        help_text="자세히 보기 링크 (선택사항)"
    )
    link_text = models.CharField(
        max_length=50,
        default="자세히 보기",
        help_text="링크 텍스트"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="표시 순서"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="활성화 여부"
    )
    
    # 생성/수정 시간
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "기여 방법"
        verbose_name_plural = "기여 방법들"
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    @classmethod
    def setup_initial_data(cls):
        """Create initial contribute methods if they don't exist"""
        initial_methods = [
            {
                'title': '기부',
                'description': 'PyLadies Seoul의 활동을 지원해주세요. 여러분의 후원이 더 많은 여성 개발자들에게 기회를 제공합니다.',
                'icon_class': 'fas fa-heart',
                'link_url': 'mailto:seoul@pyladies.com?subject=기부 문의',
                'link_text': '기부 문의하기',
                'order': 1,
            },
            {
                'title': '자원봉사',
                'description': '이벤트 기획, 운영, 홍보 등 다양한 방법으로 PyLadies Seoul과 함께해주세요.',
                'icon_class': 'fas fa-hands-helping',
                'link_url': 'mailto:seoul@pyladies.com?subject=자원봉사 신청',
                'link_text': '자원봉사 신청',
                'order': 2,
            },
            {
                'title': '연사자 지원',
                'description': '여러분의 경험과 지식을 공유하고 다른 개발자들에게 영감을 주는 연사자가 되어보세요.',
                'icon_class': 'fas fa-microphone',
                'link_url': 'mailto:seoul@pyladies.com?subject=연사자 지원',
                'link_text': '연사자 지원하기',
                'order': 3,
            },
            {
                'title': '스폰서 제안',
                'description': '기업이나 단체에서 PyLadies Seoul의 활동을 후원하고 함께 성장해나가요.',
                'icon_class': 'fas fa-handshake',
                'link_url': 'mailto:seoul@pyladies.com?subject=스폰서 제안',
                'link_text': '스폰서 제안하기',
                'order': 4,
            },
            {
                'title': '협업 제안',
                'description': '다른 커뮤니티나 조직과 함께 더 큰 시너지를 만들어가는 협업을 제안해주세요.',
                'icon_class': 'fas fa-users',
                'link_url': 'mailto:seoul@pyladies.com?subject=협업 제안',
                'link_text': '협업 제안하기',
                'order': 5,
            },
            {
                'title': '피드백',
                'description': '이벤트, 웹사이트, 커뮤니티 운영에 대한 소중한 의견을 들려주세요. 여러분의 피드백이 더 나은 PyLadies Seoul을 만듭니다.',
                'icon_class': 'fas fa-comments',
                'link_url': 'mailto:seoul@pyladies.com?subject=피드백',
                'link_text': '피드백 보내기',
                'order': 6,
            },
        ]
        
        for method_data in initial_methods:
            obj, created = cls.objects.get_or_create(
                title=method_data['title'],
                defaults=method_data
            )
            
            # Update existing objects if link_url is empty
            if not created and not obj.link_url and method_data.get('link_url'):
                obj.link_url = method_data['link_url']
                obj.link_text = method_data.get('link_text', obj.link_text)
                obj.save()


class FAQ(models.Model):
    """FAQ (Frequently Asked Questions) for Connect page"""
    
    question = models.CharField(
        max_length=255,
        help_text="자주 묻는 질문"
    )
    answer = models.TextField(
        help_text="질문에 대한 답변"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="표시 순서"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="활성화 여부"
    )
    
    # 생성/수정 시간
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question
    
    @classmethod
    def setup_initial_data(cls):
        """Create initial FAQ data if they don't exist"""
        initial_faqs = [
            {
                'question': 'PyLadies Seoul은 어떤 활동을 하나요?',
                'answer': 'PyLadies Seoul은 파이썬을 사용하는 여성 개발자들을 위한 커뮤니티입니다. 정기 모임, 워크샵, 세미나, 네트워킹 이벤트 등을 통해 여성 개발자들의 성장과 교류를 지원합니다.',
                'order': 1,
            },
            {
                'question': '참여하려면 어떻게 해야 하나요?',
                'answer': '누구나 자유롭게 참여할 수 있습니다! 이벤트 페이지에서 다가오는 행사를 확인하고 참여 신청을 하거나, 디스코드나 SNS를 통해 커뮤니티에 참여하세요.',
                'order': 2,
            },
            {
                'question': '초보자도 참여할 수 있나요?',
                'answer': '물론입니다! PyLadies Seoul은 모든 레벨의 개발자를 환영합니다. 초보자를 위한 멘토링 프로그램과 기초 워크샵도 정기적으로 진행하고 있습니다.',
                'order': 3,
            },
            {
                'question': '남성도 참여할 수 있나요?',
                'answer': 'PyLadies의 주 목적은 여성 개발자 지원이지만, 우리의 미션을 지지하는 모든 분들의 참여를 환영합니다. 일부 이벤트는 여성 전용이며, 일부는 모든 성별에게 열려있습니다.',
                'order': 4,
            },
            {
                'question': '어떤 프로그래밍 언어를 다루나요?',
                'answer': '주로 Python을 중심으로 활동하지만, 웹 개발, 데이터 사이언스, 머신러닝, DevOps 등 다양한 분야를 다룹니다. Python과 관련된 모든 기술과 도구에 대해 학습하고 공유합니다.',
                'order': 5,
            },
            {
                'question': '정기 모임은 언제 있나요?',
                'answer': '매월 정기 모임을 진행하고 있으며, 추가로 워크샵이나 특별 이벤트도 개최합니다. 구체적인 일정은 이벤트 페이지나 SNS를 통해 공지됩니다.',
                'order': 6,
            },
        ]
        
        for faq_data in initial_faqs:
            cls.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )


class PageView(models.Model):
    """Detailed page view tracking"""
    
    page = models.ForeignKey(
        ContentPage,
        on_delete=models.CASCADE,
        related_name='page_views',
        help_text="Viewed page"
    )
    
    # Viewer information
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="Viewer IP address"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User Agent information"
    )
    referrer = models.URLField(
        blank=True,
        help_text="Referrer URL"
    )
    
    # Session information
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Session key (for duplicate view prevention)"
    )
    
    # Timestamp
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="View timestamp"
    )
    
    class Meta:
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['page', '-viewed_at']),
            models.Index(fields=['session_key', 'page']),
        ]
    
    def __str__(self):
        return f"{self.page.title} - {self.viewed_at}"
    
    @classmethod
    def record_view(cls, page, request):
        """Record a page view"""
        # Get or create session key
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Prevent duplicate views within 24 hours from the same session
        one_day_ago = timezone.now() - timedelta(days=1)
        existing_view = cls.objects.filter(
            page=page,
            session_key=session_key,
            viewed_at__gte=one_day_ago
        ).exists()
        
        if not existing_view:
            # Create view record
            view = cls.objects.create(
                page=page,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', ''),
                session_key=session_key
            )
            
            # Increment page view count
            page.increment_view_count()
            
            return view
        return None
    
    @classmethod
    def get_view_statistics(cls, page, days=30):
        """Get page view statistics"""
        since = timezone.now() - timedelta(days=days)
        views = cls.objects.filter(page=page, viewed_at__gte=since)
        
        return {
            'total_views': views.count(),
            'unique_visitors': views.values('session_key').distinct().count(),
            'daily_views': views.extra(
                select={'day': 'date(viewed_at)'}
            ).values('day').annotate(
                count=models.Count('id')
            ).order_by('day'),
        }




class SocialLink(models.Model):
    """Social media link model"""
    
    member = models.ForeignKey(
        'content.Member',
        on_delete=models.CASCADE,
        related_name='social_links',
        help_text="Social link owner"
    )
    
    platform = models.ForeignKey(
        'content.SocialMediaPlatform',
        on_delete=models.CASCADE,
        help_text="Social media platform"
    )
    
    # URL or username
    url = models.URLField(
        blank=True,
        help_text="Full URL (e.g., https://github.com/username)"
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        help_text="Username or ID (if no URL)"
    )
    
    # Display settings
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Display name (uses platform name if empty)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active status"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
        ordering = ['member', 'order', 'platform']
        unique_together = ['member', 'platform']  # One platform per member
    
    def __str__(self):
        return f"{self.member.name} - {self.platform.name}"
    
    @property
    def full_url(self):
        """Return full URL"""
        if self.url:
            return self.url
        
        # Generate URL from username and platform pattern
        if self.username and self.platform.url_pattern:
            return self.platform.generate_url(self.username)
        
        return ""
    
    @property
    def icon_class(self):
        """Return Font Awesome icon class"""
        return self.platform.icon_class or 'fas fa-link'
    
    @property
    def color(self):
        """Return brand color"""
        return self.platform.color
    
    def get_display_name(self):
        """Return display name"""
        return self.display_name or self.platform.name
    
    def save(self, *args, **kwargs):
        """Validate on save"""
        if not self.url and not self.username:
            raise ValueError("Either URL or username is required.")
        super().save(*args, **kwargs)


# Contact Models

class ContactSubmission(TimeStampedModel):
    """Simple contact form submission"""
    
    name = models.CharField(max_length=100, help_text="Contact name")
    email = models.EmailField(help_text="Contact email")
    subject = models.CharField(max_length=200, help_text="Message subject")
    message = models.TextField(help_text="Message content")
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


# Search Models

class SearchAnalytics(TimeStampedModel):
    """Track search queries and analytics"""
    
    query = models.CharField(max_length=200, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Search Analytics"
        verbose_name_plural = "Search Analytics"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query} ({self.results_count} results)"


class Member(models.Model):
    """Unified member/organizer model"""
    
    MEMBER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('organizer', 'Organizer'),
    ]
    
    # Basic information
    name = models.CharField(
        max_length=255,
        help_text="Name"
    )
    member_type = models.CharField(
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
        default='member',
        help_text="Member type"
    )
    role = models.CharField(
        max_length=255,
        blank=True,
        help_text="Role/position (required for organizers)"
    )
    intro = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short introduction quote (e.g., 'I started my career to change the world!')"
    )
    bio = RichTextField(
        blank=True,
        help_text="Biography"
    )
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Profile photo"
    )
    
    # Contact information
    email = models.EmailField(
        blank=True,
        help_text="Public email address"
    )
    
    # Tag system
    tags = TaggableManager(
        blank=True,
        help_text="Add tags (e.g., python, django, data-science)"
    )
    
    # Status and display settings
    is_active = models.BooleanField(
        default=True,
        help_text="Active status"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show as featured on homepage"
    )
    show_in_member_list = models.BooleanField(
        default=True,
        help_text="Show in member list"
    )
    
    # Order and metadata
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    joined_date = models.DateField(
        null=True, blank=True,
        help_text="Join date"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('member_type'),
        FieldPanel('role'),
        FieldPanel('intro'),
        FieldPanel('bio'),
        FieldPanel('photo'),
        FieldPanel('email'),
        FieldPanel('tags'),
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('is_featured'),
            FieldPanel('show_in_member_list'),
        ], heading="Display Settings"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('joined_date'),
        ], heading="Order & Metadata"),
    ]
    
    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"
        ordering = ['member_type', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_member_type_display()})"
    
    @classmethod
    def setup_official_social_links(cls):
        """Setup PyLadies Seoul official social media platforms and links"""
        # Create or get official member
        official_member, created = cls.objects.get_or_create(
            name='PyLadies Seoul',
            defaults={
                'member_type': 'organizer',
                'role': 'Official Account',
                'bio': 'PyLadies Seoul 공식 계정',
                'is_active': True,
                'show_in_member_list': False,
            }
        )
        
        # Setup social media platforms
        platforms_data = [
            {
                'name': 'GitHub',
                'slug': 'github',
                'url_pattern': 'https://github.com/{username}',
                'icon_class': 'fab fa-github',
                'color': '#333333',
                'order': 1,
            },
            {
                'name': 'LinkedIn',
                'slug': 'linkedin',
                'url_pattern': 'https://linkedin.com/company/{username}',
                'icon_class': 'fab fa-linkedin',
                'color': '#0077b5',
                'order': 2,
            },
            {
                'name': 'X (Twitter)',
                'slug': 'twitter',
                'url_pattern': 'https://x.com/{username}',
                'icon_class': 'fab fa-x-twitter',
                'color': '#000000',
                'order': 3,
            },
            {
                'name': 'Discord',
                'slug': 'discord',
                'url_pattern': 'https://discord.gg/{username}',
                'icon_class': 'fab fa-discord',
                'color': '#5865F2',
                'order': 4,
            },
        ]
        
        for platform_data in platforms_data:
            platform, created = SocialMediaPlatform.objects.get_or_create(
                slug=platform_data['slug'],
                defaults=platform_data
            )
        
        # Setup initial social links for PyLadies Seoul
        links_data = [
            {
                'platform_slug': 'github',
                'url': 'https://github.com/pyladies-seoul',
                'username': 'pyladies-seoul',
                'display_name': 'PyLadies Seoul GitHub',
                'order': 1,
            },
            {
                'platform_slug': 'linkedin',
                'url': 'https://linkedin.com/company/pyladies-seoul',
                'username': 'pyladies-seoul',
                'display_name': 'PyLadies Seoul LinkedIn',
                'order': 2,
            },
            {
                'platform_slug': 'twitter',
                'url': 'https://x.com/pyladies_seoul',
                'username': 'pyladies_seoul',
                'display_name': 'PyLadies Seoul X',
                'order': 3,
            },
        ]
        
        for link_data in links_data:
            try:
                platform = SocialMediaPlatform.objects.get(slug=link_data['platform_slug'])
                SocialLink.objects.get_or_create(
                    member=official_member,
                    platform=platform,
                    defaults={
                        'url': link_data['url'],
                        'username': link_data['username'],
                        'display_name': link_data['display_name'],
                        'order': link_data['order'],
                        'is_active': True,
                    }
                )
            except SocialMediaPlatform.DoesNotExist:
                continue
    
    def get_skill_tags(self):
        """Return only technical skill tags"""
        tech_keywords = ['python', 'django', 'javascript', 'react', 'vue', 'data', 'ml', 'ai']
        return [tag for tag in self.tags.all() if any(keyword in tag.name.lower() for keyword in tech_keywords)]
    
    def get_social_links(self):
        """Return social media links"""
        return self.social_links.filter(is_active=True).order_by('order')
    
    @classmethod
    def get_organizers(cls):
        """Return only organizers"""
        return cls.objects.filter(member_type='organizer', is_active=True).order_by('order', 'name')
    
    @classmethod
    def get_members(cls):
        """Return only regular members"""
        return cls.objects.filter(member_type='member', is_active=True, show_in_member_list=True).order_by('order', 'name')
    
    @classmethod
    def get_featured(cls):
        """Return featured members/organizers"""
        return cls.objects.filter(is_featured=True, is_active=True).order_by('member_type', 'order', 'name')
    
    @classmethod
    def get_members_by_tag(cls, tag_name):
        """Return members with specific tag"""
        return cls.objects.filter(tags__name=tag_name, is_active=True)


class SocialMediaPlatform(models.Model):
    """Social media platform information"""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Platform name (e.g., GitHub, Twitter)"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL slug (e.g., github, twitter)"
    )
    
    # URL pattern
    url_pattern = models.CharField(
        max_length=200,
        blank=True,
        help_text="URL pattern (use {username} placeholder, e.g., https://github.com/{username})"
    )
    
    # Icon information
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class (e.g., fab fa-github)"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Brand color (Hex code, e.g., #333333)"
    )
    
    # Display settings
    is_active = models.BooleanField(
        default=True,
        help_text="Active status"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
        ], heading="Status & Order"),
    ]
    
    class Meta:
        verbose_name = "Social Media Platform"
        verbose_name_plural = "Social Media Platforms"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def generate_url(self, username):
        """Generate URL from username"""
        if self.url_pattern and username:
            return self.url_pattern.format(username=username)
        return ""