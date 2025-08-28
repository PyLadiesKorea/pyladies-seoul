"""
Context processors for PyLadies Seoul website.
"""

from django.utils import timezone
from typing import Dict, Any


def navigation_categories(request):
    """
    Provide navigation categories for all templates.
    """
    try:
        from apps.content.models import CategoryPage
        
        # Get all live category pages ordered by order field, then title
        categories = CategoryPage.objects.live().filter(
            show_in_navigation=True
        ).order_by('order', 'title')
        
        return {
            'navigation_categories': categories
        }
    except Exception:
        # Return empty list if there's any error
        return {
            'navigation_categories': []
        }


def content_helpers(request):
    """
    Provide helper variables for content templates.
    """
    return {
        'current_date': timezone.now(),
        'is_events_page': request.path.startswith('/events/'),
        'is_members_page': request.path.startswith('/members/'),
        'is_about_page': request.path.startswith('/about/'),
        'is_contact_page': request.path.startswith('/contact/'),
    }