"""
Security middleware for Django REST Framework backend.
Provides comprehensive security enhancements including rate limiting,
request validation, and security headers.
"""

import time
import logging
import hashlib
import hmac
import re
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_bytes
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security headers to all HTTP responses.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"
        )
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        # Remove server information
        response['Server'] = 'Server'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limit settings
        self.requests_per_minute = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 100)
        self.requests_per_hour = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_HOUR', 1000)
        self.requests_per_day = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_DAY', 10000)
        
    def process_request(self, request):
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check rate limits
        if not self.check_rate_limit(client_ip):
            return HttpResponseForbidden(
                'Rate limit exceeded. Please try again later.',
                content_type='application/json'
            )
        
        return None
    
    def get_client_ip(self, request):
        """
        Get the real client IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_rate_limit(self, client_ip):
        """
        Check if the client has exceeded rate limits.
        """
        now = time.time()
        
        # Check minute rate limit
        minute_key = f'rate_limit:minute:{client_ip}'
        minute_count = cache.get(minute_key, 0)
        if minute_count >= self.requests_per_minute:
            return False
        
        # Check hour rate limit
        hour_key = f'rate_limit:hour:{client_ip}'
        hour_count = cache.get(hour_key, 0)
        if hour_count >= self.requests_per_hour:
            return False
        
        # Check day rate limit
        day_key = f'rate_limit:day:{client_ip}'
        day_count = cache.get(day_key, 0)
        if day_count >= self.requests_per_day:
            return False
        
        # Increment counters
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        cache.set(day_key, day_count + 1, 86400)
        
        return True


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validates incoming requests for security issues.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Validation settings
        self.max_request_size = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)  # 10MB
        self.blocked_user_agents = getattr(settings, 'BLOCKED_USER_AGENTS', [])
        self.allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        
    def process_request(self, request):
        # Check request size
        if hasattr(request, 'body') and len(request.body) > self.max_request_size:
            return HttpResponseBadRequest(
                'Request too large.',
                content_type='application/json'
            )
        
        # Check user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if self.blocked_user_agents:
            for blocked_agent in self.blocked_user_agents:
                if re.search(blocked_agent, user_agent, re.IGNORECASE):
                    return HttpResponseForbidden(
                        'Access denied.',
                        content_type='application/json'
                    )
        
        # Check host
        if self.allowed_hosts and not url_has_allowed_host_and_scheme(request.get_host(), self.allowed_hosts):
            return HttpResponseForbidden(
                'Access denied.',
                content_type='application/json'
            )
        
        # Validate request path
        if self.is_suspicious_path(request.path):
            logger.warning(f'Suspicious request path detected: {request.path} from {self.get_client_ip(request)}')
            return HttpResponseForbidden(
                'Access denied.',
                content_type='application/json'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_suspicious_path(self, path):
        """
        Check if the request path is suspicious.
        """
        suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'\.\.\\',  # Windows path traversal
            r'admin',  # Admin paths
            r'wp-',   # WordPress paths
            r'php',   # PHP files
            r'asp',   # ASP files
            r'jsp',   # JSP files
            r'cgi',   # CGI scripts
            r'bin',   # Binary files
            r'etc',   # System files
            r'var',   # Variable files
            r'tmp',   # Temp files
            r'proc',  # Process files
            r'sys',   # System files
            r'root',  # Root directory
        ]
        
        return any(re.search(pattern, path, re.IGNORECASE) for pattern in suspicious_patterns)


class HoneypotMiddleware(MiddlewareMixin):
    """
    Honeypot middleware to detect and block automated attacks.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.honeypot_paths = getattr(settings, 'HONEYPOT_PATHS', [
            '/wp-admin/',
            '/admin/',
            '/wp-login.php',
            '/xmlrpc.php',
            '/.env',
            '/config.php',
            '/database/',
            '/backup/',
            '/test/',
            '/debug/',
            '/trace',
            '/profile',
            '/phpinfo',
            '/shell',
            '/cmd',
            '/exec',
        ])
        
    def process_request(self, request):
        # Check if request is to honeypot
        if request.path in self.honeypot_paths:
            logger.warning(f'Honeypot triggered: {request.path} from {self.get_client_ip(request)}')
            # Block the IP for a longer period
            self.block_ip(self.get_client_ip(request))
            return HttpResponseForbidden(
                'Access denied.',
                content_type='application/json'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def block_ip(self, ip):
        """Block an IP address for a specified duration."""
        block_duration = getattr(settings, 'HONEYPOT_BLOCK_DURATION', 3600)  # 1 hour
        cache.set(f'blocked_ip:{ip}', True, block_duration)


class APIKeyMiddleware(MiddlewareMixin):
    """
    API key authentication middleware for API endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key_header = getattr(settings, 'API_KEY_HEADER', 'X-API-Key')
        self.api_keys = getattr(settings, 'API_KEYS', [])
        self.bypass_paths = getattr(settings, 'API_KEY_BYPASS_PATHS', [
            '/health/',
            '/status/',
            '/metrics/',
            '/docs/',
            '/redoc/',
        ])
        
    def process_request(self, request):
        # Bypass authentication for certain paths
        if request.path in self.bypass_paths:
            return None
        
        # Check for API key in headers
        api_key = request.META.get(f'HTTP_{self.api_key_header.replace("-", "_").upper()}')
        
        if not api_key:
            return HttpResponse(
                {'error': 'API key required'},
                status=status.HTTP_401_UNAUTHORIZED,
                content_type='application/json'
            )
        
        # Validate API key
        if not self.validate_api_key(api_key):
            logger.warning(f'Invalid API key used: {api_key[:10]}... from {self.get_client_ip(request)}')
            return HttpResponse(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED,
                content_type='application/json'
            )
        
        # Add API key to request for later use
        request.api_key = api_key
        return None
    
    def validate_api_key(self, api_key):
        """Validate the provided API key."""
        return api_key in self.api_keys
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Logs security events and suspicious activities.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def process_request(self, request):
        # Log request details
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        method = request.method
        path = request.path
        
        # Log suspicious activities
        if self.is_suspicious_request(request):
            logger.warning(
                f'Suspicious request: {method} {path} from {client_ip} - {user_agent}'
            )
        
        # Log API requests
        if path.startswith('/api/'):
            logger.info(
                f'API request: {method} {path} from {client_ip} - {user_agent}'
            )
        
        return None
    
    def process_response(self, request, response):
        # Log response details for errors
        if response.status_code >= 400:
            logger.error(
                f'Error response: {response.status_code} for {request.method} {request.path} '
                f'from {self.get_client_ip(request)} - {request.META.get("HTTP_USER_AGENT", "")}'
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_suspicious_request(self, request):
        """
        Check if the request is suspicious.
        """
        suspicious_indicators = [
            request.path.count('/') > 5,  # Too many path segments
            len(request.path) > 200,  # Very long path
            'sql' in request.path.lower(),  # SQL injection attempt
            'script' in request.path.lower(),  # XSS attempt
            'union' in request.path.lower(),  # SQL injection attempt
            'select' in request.path.lower(),  # SQL injection attempt
            'drop' in request.path.lower(),  # SQL injection attempt
            'insert' in request.path.lower(),  # SQL injection attempt
            'update' in request.path.lower(),  # SQL injection attempt
            'delete' in request.path.lower(),  # SQL injection attempt
            'exec' in request.path.lower(),  # Command injection attempt
            'system' in request.path.lower(),  # Command injection attempt
            'eval' in request.path.lower(),  # Code injection attempt
            'base64' in request.path.lower(),  # Encoding attempt
        ]
        
        return any(indicator for indicator in suspicious_indicators)


class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    CSRF protection middleware for API endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.csrf_exempt_methods = getattr(settings, 'CSRF_EXEMPT_METHODS', ['GET', 'HEAD', 'OPTIONS'])
        self.csrf_header = getattr(settings, 'CSRF_HEADER', 'X-CSRFToken')
        self.csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')
        
    def process_request(self, request):
        # Exempt safe methods
        if request.method in self.csrf_exempt_methods:
            return None
        
        # Check for CSRF token
        csrf_token = request.META.get(f'HTTP_{self.csrf_header.replace("-", "_").upper()}')
        cookie_token = request.COOKIES.get(self.csrf_cookie_name)
        
        if not csrf_token and not cookie_token:
            return HttpResponse(
                {'error': 'CSRF token required'},
                status=status.HTTP_403_FORBIDDEN,
                content_type='application/json'
            )
        
        # Validate CSRF token
        if csrf_token and cookie_token and csrf_token != cookie_token:
            logger.warning(f'CSRF token mismatch from {self.get_client_ip(request)}')
            return HttpResponse(
                {'error': 'CSRF token mismatch'},
                status=status.HTTP_403_FORBIDDEN,
                content_type='application/json'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContentSecurityMiddleware(MiddlewareMixin):
    """
    Content security middleware to validate request content.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_content_length = getattr(settings, 'MAX_CONTENT_LENGTH', 10 * 1024 * 1024)  # 10MB
        
    def process_request(self, request):
        # Check content length
        if hasattr(request, 'body') and len(request.body) > self.max_content_length:
            return HttpResponseBadRequest(
                'Request content too large.',
                content_type='application/json'
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.content_type
            if content_type and not self.is_valid_content_type(content_type):
                logger.warning(
                    f'Invalid content type: {content_type} from {self.get_client_ip(request)}'
                )
                return HttpResponseBadRequest(
                    'Invalid content type.',
                    content_type='application/json'
                )
        
        return None
    
    def is_valid_content_type(self, content_type):
        """Check if the content type is allowed."""
        allowed_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data',
            'text/plain',
        ]
        
        return any(content_type.startswith(allowed_type) for allowed_type in allowed_types)
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    IP whitelist middleware for enhanced security.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        self.whitelist_enabled = getattr(settings, 'IP_WHITELIST_ENABLED', False)
        self.bypass_paths = getattr(settings, 'IP_WHITELIST_BYPASS_PATHS', [
            '/health/',
            '/status/',
            '/metrics/',
        ])
        
    def process_request(self, request):
        # Bypass whitelist if disabled
        if not self.whitelist_enabled:
            return None
        
        # Bypass certain paths
        if request.path in self.bypass_paths:
            return None
        
        # Check if IP is allowed
        client_ip = self.get_client_ip(request)
        
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(f'Blocked IP {client_ip} attempting to access {request.path}')
            return HttpResponseForbidden(
                'Access denied.',
                content_type='application/json'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestIDMiddleware(MiddlewareMixin):
    """
    Adds unique request ID to each request for tracking.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def process_request(self, request):
        # Generate unique request ID
        request_id = self.generate_request_id()
        request.request_id = request_id
        
        # Add request ID to response headers
        request.request_id_header = request_id
        
        return None
    
    def generate_request_id(self):
        """Generate a unique request ID."""
        timestamp = str(int(time.time()))
        random_str = hashlib.md5(force_bytes(f"{timestamp}{id(self)}")).hexdigest()[:8]
        return f"req_{timestamp}_{random_str}"
    
    def id(self):
        """Return a unique identifier."""
        return str(id(self))


class SecurityMiddleware:
    """
    Combined security middleware that includes all security features.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.middlewares = [
            SecurityHeadersMiddleware(get_response),
            RequestIDMiddleware(get_response),
            SecurityLoggingMiddleware(get_response),
            RequestValidationMiddleware(get_response),
            RateLimitMiddleware(get_response),
            HoneypotMiddleware(get_response),
            ContentSecurityMiddleware(get_response),
            CSRFProtectionMiddleware(get_response),
            IPWhitelistMiddleware(get_response),
        ]
        
        # Add API key middleware if configured
        if getattr(settings, 'API_KEYS', None):
            self.middlewares.append(APIKeyMiddleware(get_response))
    
    def __call__(self, request):
        # Process request through all middlewares
        for middleware in self.middlewares:
            response = middleware.process_request(request)
            if response:
                return response
        
        # Get response
        response = self.get_response(request)
        
        # Process response through middlewares that have process_response
        for middleware in self.middlewares:
            if hasattr(middleware, 'process_response'):
                response = middleware.process_response(request, response)
        
        return response
