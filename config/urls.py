"""
URL configuration for PyLadies Seoul project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.i18n import set_language
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

def index_view(request):
    """Simple index view for URL resolver"""
    return HttpResponse("PyLadies Seoul")

# Non-translatable URLs (no language prefix)
urlpatterns = [
    # Django Admin (keep for user management)
    path("django-admin/", admin.site.urls),
    
    # Wagtail Admin
    path("admin/", include(wagtailadmin_urls)),
    
    # Wagtail Documents
    path("documents/", include(wagtaildocs_urls)),
    
    # Health check endpoint
    path("health/", TemplateView.as_view(
        template_name="health_check.html",
        extra_context={"status": "healthy"}
    ), name="health_check"),
    
    # Language switching
    path("i18n/setlang/", set_language, name="set_language"),
    
    # API endpoints (future use)
    path("api/v1/", include("config.api_urls")),
]

# Translatable URLs (with language prefix)
urlpatterns += i18n_patterns(
    # All functionality now in content app
    path("", include("apps.content.urls")),  # Everything: search, contact, content, etc.
    
    # Add index pattern before Wagtail pages
    path("index/", index_view, name="index"),  # Add named index pattern
    
    # Wagtail pages - this should be last
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
)

# Add debug toolbar URLs in development
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# Serve media files in development
if settings.DEBUG:
    from django.urls import re_path
    import os
    import mimetypes
    from django.http import HttpResponse, Http404, HttpResponseNotModified
    from django.utils.http import http_date, parse_http_date_safe
    from django.utils._os import safe_join
    # Complete custom media serving to avoid FileResponse issues
    def custom_media_serve(request, path):
        """Custom media serving view that bypasses Django's FileResponse"""
        # Only allow GET and HEAD requests
        if request.method not in ['GET', 'HEAD']:
            from django.http import HttpResponseNotAllowed
            return HttpResponseNotAllowed(['GET', 'HEAD'])
        
        document_root = settings.MEDIA_ROOT
        
        # Safely join the path
        fullpath = safe_join(document_root, path)
        if not fullpath or not os.path.exists(fullpath):
            raise Http404(f'Media file "{path}" not found')
        
        if os.path.isdir(fullpath):
            raise Http404('Directory listings not allowed')
        
        # Get file stats
        statobj = os.stat(fullpath)
        
        # Determine content type
        content_type, encoding = mimetypes.guess_type(fullpath)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Handle If-Modified-Since header
        if_modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
        if if_modified_since is not None:
            if_modified_since = parse_http_date_safe(if_modified_since)
            if if_modified_since is not None and int(statobj.st_mtime) <= if_modified_since:
                return HttpResponseNotModified()
        
        # Read and serve the file
        try:
            with open(fullpath, 'rb') as f:
                file_content = f.read()
                
            response = HttpResponse(file_content, content_type=content_type)
            response['Last-Modified'] = http_date(statobj.st_mtime)
            response['Content-Length'] = len(file_content)
            
            # Add encoding if detected
            if encoding:
                response['Content-Encoding'] = encoding
            
            # Add caching headers for images
            if content_type.startswith('image/'):
                response['Cache-Control'] = 'public, max-age=3600'
                response['Expires'] = http_date(statobj.st_mtime + 3600)
            
            return response
            
        except (IOError, OSError):
            raise Http404(f'Error reading media file "{path}"')
    
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', custom_media_serve),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

