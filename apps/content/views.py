"""
Views for unified content management system
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django import forms
from django.utils import timezone

from apps.common.decorators import ajax_required, rate_limit_per_ip
from apps.common.utils import get_client_ip
from .models import ContentPage, CategoryPage, Member, PageView, ContactSubmission, SearchAnalytics


class ContentPageDetailView(DetailView):
    """Detail view for content pages with view tracking"""
    
    model = ContentPage
    template_name = 'content/content_page.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        """Filter for published and displayable pages only"""
        return ContentPage.objects.live().public().filter(
            display_start_at__isnull=True
        ).union(
            ContentPage.objects.live().public().filter(
                display_start_at__lte=timezone.now()
            )
        ).filter(
            Q(display_end_at__isnull=True) | Q(display_end_at__gte=timezone.now())
        )
    
    def get_object(self, queryset=None):
        """Get object and record view"""
        obj = super().get_object(queryset)
        
        # Record page view
        PageView.record_view(obj, self.request)
        
        return obj
    
    def get_context_data(self, **kwargs):
        """Add extra context"""
        context = super().get_context_data(**kwargs)
        
        # Add related content
        context['related_content'] = self.object.get_related_content()
        
        # Add category
        context['category'] = self.object.get_category()
        
        return context


class CategoryPageDetailView(DetailView):
    """Detail view for category pages with content listing"""
    
    model = CategoryPage
    context_object_name = 'page'
    
    def get_template_names(self):
        """Use specific template for Events page"""
        if self.object.slug == 'events':
            return ['content/events_page.html']
        return ['content/category_page.html']
    
    def get_context_data(self, **kwargs):
        """Add content pages to context"""
        context = super().get_context_data(**kwargs)
        
        # Get all content pages in this category
        content_pages = ContentPage.objects.child_of(self.object).live().public()
        
        # For events page, add specific context
        if self.object.slug == 'events':
            from django.utils import timezone
            
            # Get upcoming events
            upcoming_events = content_pages.filter(
                event_start_at__isnull=False,
                event_start_at__gte=timezone.now()
            ).order_by('event_start_at')
            
            # Get past events
            past_events = content_pages.filter(
                event_start_at__isnull=False,
                event_start_at__lt=timezone.now()
            )
            
            # Search functionality for past events
            search_query = self.request.GET.get('search')
            if search_query:
                past_events = past_events.filter(
                    Q(title__icontains=search_query) |
                    Q(body__icontains=search_query) |
                    Q(meta_description__icontains=search_query)
                )
            
            # Tag filtering for past events
            tag = self.request.GET.get('tag')
            if tag:
                past_events = past_events.filter(tags__name=tag)
            
            # Order past events by date descending
            past_events = past_events.order_by('-event_start_at')
            
            # Get popular tags from all events in this category
            all_event_tags = content_pages.filter(
                event_start_at__isnull=False
            ).values_list('tags__name', flat=True)
            unique_tags = list(set(filter(None, all_event_tags)))
            
            # Get tag counts for popular tags
            from collections import Counter
            tag_counts = Counter(filter(None, all_event_tags))
            popular_tags = [tag for tag, count in tag_counts.most_common(10)]
            
            context.update({
                'upcoming_events': upcoming_events[:5],  # Show max 5 upcoming
                'past_events': past_events,
                'search_query': search_query,
                'current_tag': tag,
                'all_tags': unique_tags,
                'popular_tags': popular_tags,
            })
            
        else:
            # Default category page logic
            # Filter by content type if requested
            content_type = self.request.GET.get('type')
            if content_type == 'events':
                content_pages = content_pages.filter(event_start_at__isnull=False)
            elif content_type == 'interviews':
                content_pages = content_pages.filter(related_member__isnull=False)
            
            # Search functionality
            search_query = self.request.GET.get('search')
            if search_query:
                content_pages = content_pages.filter(
                    Q(title__icontains=search_query) |
                    Q(body__icontains=search_query) |
                    Q(meta_description__icontains=search_query)
                )
            
            # Tag filtering
            tag = self.request.GET.get('tag')
            if tag:
                content_pages = content_pages.filter(tags__name=tag)
            
            # Order by publication date
            content_pages = content_pages.order_by('-publication_date')
            
            # Pagination
            paginator = Paginator(content_pages, 12)
            page_number = self.request.GET.get('page')
            content_pages = paginator.get_page(page_number)
            
            context['content_pages'] = content_pages
            context['content_type'] = content_type
            context['search_query'] = search_query
            context['current_tag'] = tag
            
            # Get all tags used by content in this category
            all_tags = ContentPage.objects.child_of(self.object).live().public().values_list('tags__name', flat=True)
            context['available_tags'] = list(set(filter(None, all_tags)))
        
        return context


class MemberListView(ListView):
    """List view for members/organizers"""
    
    model = Member
    template_name = 'content/member_list.html'
    context_object_name = 'members'
    paginate_by = 12  # Show 12 members per page for grid layout
    
    def get_queryset(self):
        """Filter active members"""
        queryset = Member.objects.filter(is_active=True, show_in_member_list=True)
        
        # Filter by member type
        member_type = self.request.GET.get('type')
        if member_type in ['member', 'organizer']:
            queryset = queryset.filter(member_type=member_type)
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(bio__icontains=search_query)
            )
        
        return queryset.order_by('member_type', 'order', 'name')
    
    def get_context_data(self, **kwargs):
        """Add extra context"""
        context = super().get_context_data(**kwargs)
        
        # Get featured members (top 3 for rotating display)
        featured_members = Member.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('?')[:3]  # Random 3 featured members
        
        # If no featured members, get random members with photos
        if not featured_members:
            featured_members = Member.objects.filter(
                is_active=True,
                photo__isnull=False
            ).order_by('?')[:3]
        
        context['featured_members'] = featured_members
        
        context['member_type'] = self.request.GET.get('type')
        context['current_tag'] = self.request.GET.get('tag')
        context['search_query'] = self.request.GET.get('search')
        
        # Get available tags
        all_tags = Member.objects.filter(is_active=True).values_list('tags__name', flat=True)
        context['available_tags'] = list(set(filter(None, all_tags)))
        
        # Get counts
        context['organizer_count'] = Member.objects.filter(member_type='organizer', is_active=True).count()
        context['member_count'] = Member.objects.filter(member_type='member', is_active=True).count()
        
        # Check if there are more members to load
        context['has_more'] = context['page_obj'].has_next() if 'page_obj' in context else False
        
        # Handle AJAX requests for "Load More" functionality
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            html = render_to_string('content/member_grid_items.html', {'members': context['members']})
            return JsonResponse({
                'html': html,
                'has_more': context['has_more']
            })
        
        return context


@require_http_methods(["POST"])
@csrf_exempt
@rate_limit_per_ip(max_requests=100, time_window=3600)  # 100 requests per hour
def track_page_view(request):
    """AJAX endpoint to track page views"""
    try:
        page_id = request.POST.get('page_id')
        if not page_id:
            return JsonResponse({'error': 'Page ID required'}, status=400)
        
        page = get_object_or_404(ContentPage, id=page_id)
        view = PageView.record_view(page, request)
        
        return JsonResponse({
            'success': True,
            'view_count': page.view_count,
            'view_recorded': view is not None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_popular_content(request):
    """API endpoint for popular content"""
    try:
        days = int(request.GET.get('days', 30))
        limit = int(request.GET.get('limit', 10))
        
        popular_content = ContentPage.get_popular_content(days=days, limit=limit)
        
        content_data = []
        for page in popular_content:
            content_data.append({
                'id': page.id,
                'title': page.title,
                'url': page.url,
                'view_count': page.view_count,
                'publication_date': page.publication_date.isoformat(),
                'category': page.get_category().title if page.get_category() else None,
                'is_event': page.is_event,
                'is_interview': page.is_interview,
            })
        
        return JsonResponse({
            'success': True,
            'content': content_data,
            'period_days': days
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def content_stats(request):
    """API endpoint for content statistics"""
    try:
        # Overall stats
        total_content = ContentPage.objects.live().count()
        total_events = ContentPage.objects.live().filter(event_start_at__isnull=False).count()
        total_interviews = ContentPage.objects.live().filter(related_member__isnull=False).count()
        total_members = Member.objects.filter(is_active=True).count()
        total_organizers = Member.objects.filter(member_type='organizer', is_active=True).count()
        
        # Recent activity
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_content = ContentPage.objects.filter(
            first_published_at__gte=thirty_days_ago
        ).count()
        
        # Popular tags
        popular_tags = ContentPage.objects.live().values_list('tags__name', flat=True)
        tag_counts = {}
        for tag in popular_tags:
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_content': total_content,
                'total_events': total_events,
                'total_interviews': total_interviews,
                'total_members': total_members,
                'total_organizers': total_organizers,
                'recent_content_30_days': recent_content,
            },
            'top_tags': top_tags
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================================================================
# MEMBER VIEWS
# =============================================================================

class MemberDetailView(DetailView):
    """Detail view for individual members"""
    
    model = Member
    template_name = 'content/member_detail.html'
    context_object_name = 'member'
    
    def get_queryset(self):
        return Member.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related content pages (interviews, etc.)
        context['related_content'] = ContentPage.objects.live().filter(
            related_member=self.object
        ).order_by('-publication_date')
        
        return context


class ConnectView(TemplateView):
    """Connect page view"""
    
    template_name = 'content/connect_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get FAQs (auto-setup initial data if empty)
        from .models import FAQ
        faqs = FAQ.objects.filter(is_active=True)
        
        if not faqs.exists():
            # Setup initial data if none exist
            FAQ.setup_initial_data()
            faqs = FAQ.objects.filter(is_active=True)
        
        faqs = faqs.order_by('order', 'question')
        context['faq_pages'] = faqs  # Keep same variable name for template compatibility
        
        # Get contribute methods (auto-setup initial data if empty)
        from .models import ContributeMethod
        contribute_methods = ContributeMethod.objects.filter(is_active=True)
        
        if not contribute_methods.exists():
            # Setup initial data if none exist
            ContributeMethod.setup_initial_data()
            contribute_methods = ContributeMethod.objects.filter(is_active=True)
        
        contribute_methods = contribute_methods.order_by('order', 'title')
        context['contribute_methods'] = contribute_methods
        
        # Get official social links (from PyLadies Seoul official member)
        from .models import Member, SocialLink
        try:
            # Try to find PyLadies Seoul official member
            official_member = Member.objects.filter(
                name__icontains='PyLadies Seoul'
            ).first()
            
            if not official_member:
                # Setup initial social platforms and official member
                Member.setup_official_social_links()
                official_member = Member.objects.get(name='PyLadies Seoul')
            
            # Get social links for official member
            social_links = SocialLink.objects.filter(
                member=official_member,
                is_active=True
            ).select_related('platform').order_by('order', 'platform__order')
            
            context['social_links'] = social_links
            
        except Exception:
            context['social_links'] = []
        
        return context


# =============================================================================
# SEARCH VIEWS
# =============================================================================

class SearchView(TemplateView):
    """Search functionality"""
    
    template_name = 'content/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get('q', '').strip()
        results = []
        
        if query:
            # Search content pages
            content_results = ContentPage.objects.live().filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(meta_description__icontains=query)
            ).order_by('-publication_date')
            
            # Search members  
            member_results = Member.objects.filter(is_active=True).filter(
                Q(name__icontains=query) |
                Q(role__icontains=query) |
                Q(bio__icontains=query)
            ).order_by('name')
            
            results = list(content_results) + list(member_results)
            
            # Record search analytics
            SearchAnalytics.objects.create(
                query=query,
                results_count=len(results),
                ip_address=get_client_ip(self.request)
            )
        
        context.update({
            'query': query,
            'results': results,
            'results_count': len(results)
        })
        
        return context


@ajax_required
@rate_limit_per_ip(max_requests=60, time_window=3600)  # 60 searches per hour
def search_view(request):
    """API search endpoint"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Query required'}, status=400)
    
    # Search content
    content_results = ContentPage.objects.live().filter(
        Q(title__icontains=query) |
        Q(body__icontains=query)
    )[:10]
    
    # Search members
    member_results = Member.objects.filter(is_active=True).filter(
        Q(name__icontains=query) |
        Q(role__icontains=query)
    )[:10]
    
    results = {
        'content': [{'id': p.id, 'title': p.title, 'url': p.url} for p in content_results],
        'members': [{'id': m.id, 'name': m.name, 'role': m.role} for m in member_results],
        'query': query
    }
    
    return JsonResponse(results)


def search_analytics(request):
    """Search analytics API"""
    recent_searches = SearchAnalytics.objects.order_by('-created_at')[:100]
    
    # Popular queries
    popular = SearchAnalytics.objects.values('query').annotate(
        count=Count('query')
    ).order_by('-count')[:10]
    
    return JsonResponse({
        'recent_searches': [{'query': s.query, 'results': s.results_count} for s in recent_searches],
        'popular_queries': list(popular)
    })


# =============================================================================
# CONTACT VIEWS
# =============================================================================

class ContactForm(forms.Form):
    """Simple contact form"""
    
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


class ContactView(FormView):
    """Contact form view"""
    
    template_name = 'content/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('content:contact_success')
    
    def form_valid(self, form):
        # Save submission
        submission = ContactSubmission.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message'],
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Send email notification (optional)
        try:
            send_mail(
                subject=f"[PyLadies Seoul Contact] {form.cleaned_data['subject']}",
                message=f"From: {form.cleaned_data['name']} ({form.cleaned_data['email']})\n\n{form.cleaned_data['message']}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['contact@pyladiesseoul.org'],
                fail_silently=True
            )
        except:
            pass  # Email sending is optional
        
        messages.success(self.request, 'Thank you! Your message has been sent.')
        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    """Contact success page"""
    
    template_name = 'content/contact_success.html'


class AboutView(TemplateView):
    """About page view"""
    
    template_name = 'content/about_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get About page from ContentPage
        try:
            context['about_page'] = ContentPage.objects.live().filter(title__iexact='About').first()
        except ContentPage.DoesNotExist:
            context['about_page'] = None
        
        # Get CoC page from ContentPage
        try:
            context['coc_page'] = ContentPage.objects.live().filter(title__icontains='Code of Conduct').first()
        except ContentPage.DoesNotExist:
            context['coc_page'] = None
        
        # Get organizers
        context['organizers'] = Member.get_organizers()
        
        # Get social platforms (you can create these in admin or hardcode for now)
        context['social_platforms'] = [
            {'name': 'Email', 'url': 'mailto:seoul@pyladies.com', 'icon_class': 'fas fa-envelope'},
            {'name': 'GitHub', 'url': 'https://github.com/pyladies-seoul', 'icon_class': 'fab fa-github'},
            {'name': 'Twitter', 'url': 'https://twitter.com/pyladiesseoul', 'icon_class': 'fab fa-twitter'},
        ]
        
        return context