"""
Enhanced security middleware for BlueDive Django Backend.
Provides comprehensive security features including rate limiting, IP filtering,
request validation, and security headers.
"""

import time
import logging
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
import re

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Enhanced security middleware with multiple protection layers:
    - Rate limiting (IP-based and user-based)
    - IP whitelisting/blacklisting
    - Request size validation
    - SQL injection protection
    - XSS protection
    - Security headers
    - Request logging and monitoring
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Configuration
        self.rate_limit_config = getattr(settings, 'RATE_LIMIT_CONFIG', {
            'default': {'requests': 100, 'window': 3600},  # 100 requests per hour
            'api': {'requests': 1000, 'window': 3600},     # 1000 requests per hour for API
            'auth': {'requests': 10, 'window': 900},        # 10 requests per 15 minutes for auth
        })
        
        self.max_request_size = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)  # 10MB
        self.blocked_ips = getattr(settings, 'BLOCKED_IPS', [])
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        self.enable_security_headers = getattr(settings, 'ENABLE_SECURITY_HEADERS', True)
        self.enable_request_logging = getattr(settings, 'ENABLE_REQUEST_LOGGING', True)
        
        # Security patterns
        self.sql_injection_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
            r'(--|#|\/\*|\*\/|;|\'|\"|\\)',
            r'(\bOR\b.*=.*\bOR\b|\bAND\b.*=.*\bAND\b)',
            r'(\bUNION\b.*\bSELECT\b)',
            r'(\bEXEC\b.*\(|\bXP_\w+\b)',
        ]
        
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'eval\s*\(',
            r'alert\s*\(',
            r'document\.cookie',
        ]

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process incoming request for security checks."""
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Log request start
            if self.enable_request_logging:
                self._log_request_start(request, client_ip)
            
            # IP filtering
            ip_check_result = self._check_ip_filtering(client_ip)
            if ip_check_result:
                return ip_check_result
            
            # Rate limiting
            rate_limit_result = self._check_rate_limit(request, client_ip)
            if rate_limit_result:
                return rate_limit_result
            
            # Request size validation
            size_check_result = self._check_request_size(request)
            if size_check_result:
                return size_check_result
            
            # SQL injection protection
            injection_check_result = self._check_sql_injection(request)
            if injection_check_result:
                return injection_check_result
            
            # XSS protection
            xss_check_result = self._check_xss(request)
            if xss_check_result:
                return xss_check_result
            
            # Add security context to request
            request.security_context = {
                'client_ip': client_ip,
                'request_id': self._generate_request_id(),
                'start_time': time.time(),
            }
            
            return None
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JsonResponse({
                'error': 'Security check failed',
                'code': 'SECURITY_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process outgoing response for security headers and logging."""
        try:
            # Add security headers
            if self.enable_security_headers:
                self._add_security_headers(response)
            
            # Log request completion
            if self.enable_request_logging and hasattr(request, 'security_context'):
                self._log_request_completion(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Security response processing error: {e}")
            return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

    def _check_ip_filtering(self, client_ip: str) -> Optional[JsonResponse]:
        """Check if IP is blocked or not in allowed list."""
        # Check blocked IPs
        if self.blocked_ips and client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JsonResponse({
                'error': 'Access denied',
                'code': 'IP_BLOCKED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check allowed IPs (if configured)
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(f"Non-allowed IP attempted access: {client_ip}")
            return JsonResponse({
                'error': 'Access denied',
                'code': 'IP_NOT_ALLOWED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return None

    def _check_rate_limit(self, request: HttpRequest, client_ip: str) -> Optional[JsonResponse]:
        """Check rate limiting based on IP and endpoint."""
        try:
            # Determine rate limit key and config
            rate_limit_key, config = self._get_rate_limit_config(request, client_ip)
            
            if not rate_limit_key or not config:
                return None
            
            # Check current request count
            current_count = cache.get(rate_limit_key, 0)
            
            if current_count >= config['requests']:
                logger.warning(f"Rate limit exceeded for {rate_limit_key}: {current_count}/{config['requests']}")
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': config['window']
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Increment counter
            cache.set(rate_limit_key, current_count + 1, config['window'])
            
            return None
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return None

    def _get_rate_limit_config(self, request: HttpRequest, client_ip: str) -> Tuple[str, Dict[str, int]]:
        """Get rate limit configuration based on request path and user."""
        path = request.path.strip('/')
        
        # Determine rate limit type based on path
        if path.startswith('api/auth'):
            rate_type = 'auth'
            key = f"rate_limit:auth:{client_ip}"
        elif path.startswith('api/'):
            rate_type = 'api'
            key = f"rate_limit:api:{client_ip}"
        else:
            rate_type = 'default'
            key = f"rate_limit:default:{client_ip}"
        
        # Add user-specific rate limiting if authenticated
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            key += f":user_{request.user.id}"
        
        config = self.rate_limit_config.get(rate_type, self.rate_limit_config['default'])
        
        return key, config

    def _check_request_size(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check if request size exceeds limit."""
        try:
            content_length = int(request.META.get('CONTENT_LENGTH', 0))
            
            if content_length > self.max_request_size:
                logger.warning(f"Request size exceeded: {content_length} bytes (limit: {self.max_request_size})")
                return JsonResponse({
                    'error': 'Request too large',
                    'code': 'REQUEST_TOO_LARGE',
                    'max_size': self.max_request_size
                }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            return None
            
        except (ValueError, TypeError):
            return None

    def _check_sql_injection(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check for SQL injection patterns in request data."""
        try:
            # Check GET parameters
            for param, value in request.GET.items():
                if self._contains_sql_injection(str(value)):
                    logger.warning(f"SQL injection attempt in GET parameter '{param}': {value}")
                    return JsonResponse({
                        'error': 'Invalid request parameters',
                        'code': 'SQL_INJECTION_DETECTED'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check POST data
            if request.content_type and 'application/json' in request.content_type:
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    if self._check_data_for_sql_injection(body):
                        return JsonResponse({
                            'error': 'Invalid request data',
                            'code': 'SQL_INJECTION_DETECTED'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            else:
                # Check form data
                for param, value in request.POST.items():
                    if self._contains_sql_injection(str(value)):
                        logger.warning(f"SQL injection attempt in POST parameter '{param}': {value}")
                        return JsonResponse({
                            'error': 'Invalid request data',
                            'code': 'SQL_INJECTION_DETECTED'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            return None
            
        except Exception as e:
            logger.error(f"SQL injection check error: {e}")
            return None

    def _check_xss(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check for XSS patterns in request data."""
        try:
            # Check GET parameters
            for param, value in request.GET.items():
                if self._contains_xss(str(value)):
                    logger.warning(f"XSS attempt in GET parameter '{param}': {value}")
                    return JsonResponse({
                        'error': 'Invalid request parameters',
                        'code': 'XSS_DETECTED'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check POST data
            if request.content_type and 'application/json' in request.content_type:
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    if self._check_data_for_xss(body):
                        return JsonResponse({
                            'error': 'Invalid request data',
                            'code': 'XSS_DETECTED'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            else:
                # Check form data
                for param, value in request.POST.items():
                    if self._contains_xss(str(value)):
                        logger.warning(f"XSS attempt in POST parameter '{param}': {value}")
                        return JsonResponse({
                            'error': 'Invalid request data',
                            'code': 'XSS_DETECTED'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            return None
            
        except Exception as e:
            logger.error(f"XSS check error: {e}")
            return None

    def _contains_sql_injection(self, value: str) -> bool:
        """Check if value contains SQL injection patterns."""
        value_upper = value.upper()
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False

    def _contains_xss(self, value: str) -> bool:
        """Check if value contains XSS patterns."""
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def _check_data_for_sql_injection(self, data: Any, path: str = '') -> bool:
        """Recursively check data structure for SQL injection."""
        if isinstance(data, dict):
            for key, value in data.items():
                if self._check_data_for_sql_injection(value, f"{path}.{key}" if path else key):
                    return True
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if self._check_data_for_sql_injection(item, f"{path}[{i}]" if path else f"[{i}]"):
                    return True
        elif isinstance(data, str):
            if self._contains_sql_injection(data):
                logger.warning(f"SQL injection detected at path: {path}")
                return True
        return False

    def _check_data_for_xss(self, data: Any, path: str = '') -> bool:
        """Recursively check data structure for XSS."""
        if isinstance(data, dict):
            for key, value in data.items():
                if self._check_data_for_xss(value, f"{path}.{key}" if path else key):
                    return True
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if self._check_data_for_xss(item, f"{path}[{i}]" if path else f"[{i}]"):
                    return True
        elif isinstance(data, str):
            if self._contains_xss(data):
                logger.warning(f"XSS detected at path: {path}")
                return True
        return False

    def _add_security_headers(self, response: HttpResponse) -> None:
        """Add security headers to response."""
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response['Content-Security-Policy'] = csp
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # Remove server information
        response['Server'] = 'BlueDive-Secure'

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        timestamp = str(int(time.time()))
        random_str = hashlib.md5(f"{timestamp}{time.time_ns()}".encode()).hexdigest()[:8]
        return f"req_{timestamp}_{random_str}"

    def _log_request_start(self, request: HttpRequest, client_ip: str) -> None:
        """Log request start for monitoring."""
        logger.info(f"Request started: {request.method} {request.path} from {client_ip}")

    def _log_request_completion(self, request: HttpRequest, response: HttpResponse) -> None:
        """Log request completion for monitoring."""
        try:
            security_context = getattr(request, 'security_context', {})
            start_time = security_context.get('start_time', time.time())
            duration = time.time() - start_time
            
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"from {security_context.get('client_ip', 'unknown')} "
                f"status={response.status_code} duration={duration:.3f}s"
            )
            
            # Log slow requests
            if duration > 5.0:  # 5 seconds threshold
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )
                
        except Exception as e:
            logger.error(f"Request logging error: {e}")


class HoneypotMiddleware(MiddlewareMixin):
    """
    Honeypot middleware to trap bots and malicious requests.
    Creates fake endpoints that look attractive to automated scanners.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        self.honeypot_urls = getattr(settings, 'HONEYPOT_URLS', [
            '/admin/login',
            '/wp-admin/',
            '/phpmyadmin/',
            '/.env',
            '/config.php',
            '/backup.sql',
            '/robots.txt'
        ])

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check if request is targeting a honeypot URL."""
        if request.path in self.honeypot_urls:
            client_ip = self._get_client_ip(request)
            logger.warning(f"Honeypot triggered: {client_ip} accessed {request.path}")
            
            # Block the IP for a period
            self._block_ip_temporarily(client_ip)
            
            return JsonResponse({
                'error': 'Access denied',
                'code': 'HONEYPOT_TRIGGERED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return None

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def _block_ip_temporarily(self, client_ip: str) -> None:
        """Temporarily block an IP that triggered the honeypot."""
        cache.set(f"honeypot_block:{client_ip}", True, timeout=3600)  # Block for 1 hour


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Request validation middleware for additional security checks.
    Validates request headers, user agents, and other request attributes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Suspicious user agent patterns
        self.suspicious_ua_patterns = [
            r'sqlmap',
            r'nikto',
            r'nmap',
            r'masscan',
            r'python-requests',
            r'curl',
            r'wget',
            r'bot',
            r'scanner',
            r'crawler'
        ]

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Validate request for suspicious patterns."""
        try:
            # Check user agent
            ua_check_result = self._check_user_agent(request)
            if ua_check_result:
                return ua_check_result
            
            # Check for suspicious headers
            header_check_result = self._check_suspicious_headers(request)
            if header_check_result:
                return header_check_result
            
            return None
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return None

    def _check_user_agent(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check user agent for suspicious patterns."""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        for pattern in self.suspicious_ua_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                logger.warning(f"Suspicious user agent detected: {user_agent}")
                return JsonResponse({
                    'error': 'Access denied',
                    'code': 'SUSPICIOUS_USER_AGENT'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return None

    def _check_suspicious_headers(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check for suspicious request headers."""
        suspicious_headers = [
            'HTTP_X_FORWARDED_HOST',
            'HTTP_X_REAL_IP',
            'HTTP_X_ORIGINATING_IP',
            'HTTP_X_FORWARDED_SERVER'
        ]
        
        for header in suspicious_headers:
            if header in request.META:
                logger.warning(f"Suspicious header detected: {header}")
                return JsonResponse({
                    'error': 'Access denied',
                    'code': 'SUSPICIOUS_HEADERS'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return None
