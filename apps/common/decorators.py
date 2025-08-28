"""
Common decorators
"""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from .utils import get_client_ip, cache_key


def cache_per_user(timeout=3600):
    """
    Cache decorator that varies by user
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                key = cache_key('user_cache', request.user.id, request.get_full_path())
            else:
                key = cache_key('anon_cache', get_client_ip(request), request.get_full_path())
            
            result = cache.get(key)
            if result is None:
                result = view_func(request, *args, **kwargs)
                cache.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def ajax_required(view_func):
    """
    Decorator that requires the request to be AJAX
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper


def rate_limit_per_ip(max_requests=60, time_window=3600):
    """
    Simple rate limiting decorator per IP address
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            key = cache_key('rate_limit', ip)
            
            requests = cache.get(key, 0)
            if requests >= max_requests:
                return JsonResponse(
                    {'error': 'Rate limit exceeded'}, 
                    status=429
                )
            
            cache.set(key, requests + 1, time_window)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator