"""
Logfire APM configuration for PyLadies Seoul project.
"""

import os
from django.conf import settings

try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    print("⚠️  Logfire package not installed. Install with: pip install logfire")


def configure_logfire():
    """
    Configure Logfire APM for the Django application.
    This should be called early in the application startup.
    """
    if not LOGFIRE_AVAILABLE:
        return
    
    logfire_token = os.environ.get('LOGFIRE_TOKEN')
    
    if logfire_token:
        try:
            logfire.configure(
                service_name='pyladies-seoul-website',
                service_version=os.environ.get('APP_VERSION', '1.0.0'),
                token=logfire_token,
                environment=os.environ.get('ENVIRONMENT', 'development'),
            )
            
            # Instrument Django automatically
            logfire.instrument_django()
            
            # Instrument other libraries
            try:
                logfire.instrument_requests()
            except Exception:
                pass  # requests might not be used
            
            try:
                logfire.instrument_psycopg()
            except Exception:
                pass  # psycopg might not be used
            
            try:
                logfire.instrument_redis()
            except Exception:
                pass  # redis might not be used
            
            print("✅ Logfire APM configured successfully")
        except Exception as e:
            print(f"⚠️  Failed to configure Logfire: {e}")
    else:
        print("ℹ️  LOGFIRE_TOKEN not set. To enable Logfire monitoring:")
        print("    1. Sign up at https://logfire.pydantic.dev/")
        print("    2. Create a new project and get your token")
        print("    3. Add to .env file: LOGFIRE_TOKEN=your-token-here")


class LogfireMiddleware:
    """
    Django middleware for Logfire request/response monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = LOGFIRE_AVAILABLE and os.environ.get('LOGFIRE_TOKEN')

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        # Create a span for the entire request
        with logfire.span(
            'http_request',
            method=request.method,
            url=request.get_full_path(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ) as span:
            
            # Add request metadata
            span.set_attribute('http.request.method', request.method)
            span.set_attribute('http.url', request.build_absolute_uri())
            span.set_attribute('http.scheme', request.scheme)
            span.set_attribute('http.host', request.get_host())
            
            if request.user.is_authenticated:
                span.set_attribute('user.id', str(request.user.id))
                span.set_attribute('user.username', request.user.username)
            
            # Process the request
            response = self.get_response(request)
            
            # Add response metadata
            span.set_attribute('http.status_code', response.status_code)
            span.set_attribute('http.response.size', len(response.content))
            
            # Set span status based on response
            if response.status_code >= 400:
                span.set_attribute('error', True)
                if response.status_code >= 500:
                    span.set_attribute('error.type', 'server_error')
                else:
                    span.set_attribute('error.type', 'client_error')
            
            return response

    def process_exception(self, request, exception):
        """Log exceptions to Logfire"""
        if not self.enabled:
            return None
        
        logfire.error(
            'Unhandled exception in Django view',
            exception=exception,
            request_method=request.method,
            request_url=request.get_full_path(),
        )
        return None


def log_user_action(action, user, **kwargs):
    """
    Log user actions to Logfire for analytics and debugging.
    
    Args:
        action (str): The action being performed
        user: The Django user object
        **kwargs: Additional context
    """
    if not LOGFIRE_AVAILABLE or not os.environ.get('LOGFIRE_TOKEN'):
        return
    
    with logfire.span(f'user_action.{action}') as span:
        span.set_attribute('user.id', str(user.id))
        span.set_attribute('user.username', user.username)
        span.set_attribute('action', action)
        
        for key, value in kwargs.items():
            span.set_attribute(f'context.{key}', str(value))


def log_page_view(page, request):
    """
    Log Wagtail page views for analytics.
    
    Args:
        page: The Wagtail page object
        request: The Django request object
    """
    if not LOGFIRE_AVAILABLE or not os.environ.get('LOGFIRE_TOKEN'):
        return
    
    with logfire.span('page_view') as span:
        span.set_attribute('page.id', page.id)
        span.set_attribute('page.title', page.title)
        span.set_attribute('page.slug', page.slug)
        span.set_attribute('page.content_type', page.content_type.name)
        
        if request.user.is_authenticated:
            span.set_attribute('user.id', str(request.user.id))
        
        span.set_attribute('request.path', request.path)
        span.set_attribute('request.method', request.method)


# Performance monitoring decorators
def monitor_performance(operation_name):
    """
    Decorator to monitor performance of functions.
    
    Usage:
        @monitor_performance('user_registration')
        def register_user(data):
            # ... implementation
    """
    def decorator(func):
        if not LOGFIRE_AVAILABLE or not os.environ.get('LOGFIRE_TOKEN'):
            return func  # Return original function if Logfire is not available
        
        def wrapper(*args, **kwargs):
            with logfire.span(f'operation.{operation_name}') as span:
                span.set_attribute('operation', operation_name)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute('success', True)
                    return result
                except Exception as e:
                    span.set_attribute('success', False)
                    span.set_attribute('error.message', str(e))
                    span.set_attribute('error.type', type(e).__name__)
                    raise
        
        return wrapper
    return decorator


def log_database_query_performance():
    """
    Log slow database queries for optimization.
    This can be integrated with Django's database logging.
    """
    # This would typically be integrated with Django's logging system
    # or database query monitoring
    pass