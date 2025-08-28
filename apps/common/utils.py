"""
Common utility functions
"""

from django.core.cache import cache
from django.conf import settings


def get_client_ip(request):
    """Get the client's real IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cache_key(prefix, *args):
    """Generate a consistent cache key"""
    key_parts = [str(arg) for arg in args if arg is not None]
    return f"{prefix}:{':'.join(key_parts)}"


def get_or_set_cache(key, callable_func, timeout=None):
    """Get from cache or set if not exists"""
    result = cache.get(key)
    if result is None:
        result = callable_func()
        cache.set(key, result, timeout or 3600)  # Default 1 hour
    return result