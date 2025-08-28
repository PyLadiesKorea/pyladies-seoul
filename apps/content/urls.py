"""
URL patterns for the complete PyLadies Seoul website
Everything in one place: content, search, contact, member lists, etc.
"""

from django.urls import path, include
from . import views

app_name = 'content'

# API URLs for AJAX endpoints
api_urlpatterns = [
    # Content APIs
    path('track-view/', views.track_page_view, name='track_page_view'),
    path('popular-content/', views.get_popular_content, name='popular_content'),
    path('content-stats/', views.content_stats, name='content_stats'),
    
    # Search APIs
    path('search/', views.search_view, name='search_api'),
    path('search/analytics/', views.search_analytics, name='search_analytics'),
]

# Main URL patterns
urlpatterns = [
    # Member/Organizer pages
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('member/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # About
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Connect
    path('connect/', views.ConnectView.as_view(), name='connect'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
]

# Note: CategoryPage and ContentPage URLs are handled by Wagtail's routing system
# They will be available at their respective slugs (e.g., /events/, /members/, etc.)
# Individual content pages will be at /category-slug/content-slug/