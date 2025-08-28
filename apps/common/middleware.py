"""
Common middleware
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SimplePerformanceMiddleware(MiddlewareMixin):
    """
    Simple performance monitoring middleware
    Logs slow requests for debugging
    """
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (over 2 seconds)
            if duration > 2.0:
                logger.warning(
                    f"Slow request: {request.method} {request.get_full_path()} "
                    f"took {duration:.2f}s"
                )
        
        return response