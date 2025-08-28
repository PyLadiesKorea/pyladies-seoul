"""
API URL configuration for PyLadies Seoul project.
"""

from django.urls import include, path
from rest_framework import routers

# Create API router
router = routers.DefaultRouter()

# Register API viewsets here when they are created
# router.register(r'events', EventViewSet)
# router.register(r'interviews', InterviewViewSet)

urlpatterns = [
    # API root
    path("", include(router.urls)),
    
    # Wagtail API (if needed)
    # path("pages/", include(wagtailapi_urls)),
    
    # Authentication endpoints
    path("auth/", include("rest_framework.urls")),
]