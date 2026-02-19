"""
API Rate Limiting Utility for Django REST Framework.
Provides comprehensive rate limiting with different strategies and configurations.
"""

import time
import json
import logging
from typing import Dict, Optional, Tuple, Any, Union
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import status
from django.conf import settings
from datetime import datetime, timedelta
import hashlib
import ipaddress

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class RateLimitStrategy:
    """Base class for rate limiting strategies."""
    
    def __init__(self, key_prefix: str = "rate_limit"):
        self.key_prefix = key_prefix
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the request is allowed based on rate limit.
        
        Args:
            key: Unique identifier for the client (IP, user ID, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        raise NotImplementedError
    
    def get_cache_key(self, key: str, window: int) -> str:
        """Generate cache key for rate limiting."""
        return f"{self.key_prefix}:{key}:{window}"


class TokenBucketStrategy(RateLimitStrategy):
    """Token bucket rate limiting strategy."""
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Token bucket algorithm implementation.
        
        Args:
            key: Unique identifier for the client
            limit: Maximum number of tokens (requests)
            window: Time window for token refill
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        cache_key = self.get_cache_key(key, window)
        current_time = int(time.time())
        
        # Get current bucket state
        bucket_data = cache.get(cache_key, {
            'tokens': limit,
            'last_refill': current_time,
            'requests': []
        })
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket_data['last_refill']
        tokens_to_add = (time_elapsed / window) * limit
        
        # Refill tokens but don't exceed the limit
        bucket_data['tokens'] = min(limit, bucket_data['tokens'] + tokens_to_add)
        bucket_data['last_refill'] = current_time
        
        # Check if request is allowed
        if bucket_data['tokens'] >= 1:
            bucket_data['tokens'] -= 1
            bucket_data['requests'].append(current_time)
            
            # Clean old requests (keep only recent ones for analytics)
            bucket_data['requests'] = [
                req_time for req_time in bucket_data['requests']
                if current_time - req_time <= window
            ]
            
            # Save updated bucket state
            cache.set(cache_key, bucket_data, window + 1)
            
            return True, {
                'tokens_remaining': bucket_data['tokens'],
                'tokens_limit': limit,
                'refill_rate': limit / window,
                'requests_in_window': len(bucket_data['requests']),
                'reset_time': current_time + window
            }
        else:
            # Calculate when the next token will be available
            tokens_needed = 1 - bucket_data['tokens']
            time_until_reset = (tokens_needed / limit) * window
            
            return False, {
                'tokens_remaining': 0,
                'tokens_limit': limit,
                'refill_rate': limit / window,
                'requests_in_window': len(bucket_data['requests']),
                'reset_time': current_time + time_until_reset,
                'retry_after': int(time_until_reset)
            }


class SlidingWindowStrategy(RateLimitStrategy):
    """Sliding window rate limiting strategy."""
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Sliding window algorithm implementation.
        
        Args:
            key: Unique identifier for the client
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        cache_key = self.get_cache_key(key, window)
        current_time = int(time.time())
        
        # Get existing requests
        requests = cache.get(cache_key, [])
        
        # Remove requests outside the current window
        requests = [req_time for req_time in requests if current_time - req_time < window]
        
        # Check if under limit
        if len(requests) < limit:
            requests.append(current_time)
            cache.set(cache_key, requests, window)
            
            return True, {
                'requests_in_window': len(requests),
                'requests_limit': limit,
                'window_size': window,
                'reset_time': current_time + window
            }
        else:
            # Calculate when the oldest request will expire
            oldest_request = min(requests)
            retry_after = window - (current_time - oldest_request)
            
            return False, {
                'requests_in_window': len(requests),
                'requests_limit': limit,
                'window_size': window,
                'reset_time': oldest_request + window,
                'retry_after': int(retry_after)
            }


class FixedWindowStrategy(RateLimitStrategy):
    """Fixed window rate limiting strategy."""
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Fixed window algorithm implementation.
        
        Args:
            key: Unique identifier for the client
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        cache_key = self.get_cache_key(key, window)
        current_time = int(time.time())
        
        # Calculate current window start time
        window_start = (current_time // window) * window
        window_end = window_start + window
        
        # Get current window data
        window_data = cache.get(cache_key, {'count': 0, 'window_start': window_start})
        
        # Reset if we're in a new window
        if window_data['window_start'] != window_start:
            window_data = {'count': 0, 'window_start': window_start}
        
        # Check if under limit
        if window_data['count'] < limit:
            window_data['count'] += 1
            cache.set(cache_key, window_data, window)
            
            return True, {
                'requests_in_window': window_data['count'],
                'requests_limit': limit,
                'window_start': window_start,
                'window_end': window_end,
                'reset_time': window_end
            }
        else:
            return False, {
                'requests_in_window': window_data['count'],
                'requests_limit': limit,
                'window_start': window_start,
                'window_end': window_end,
                'reset_time': window_end,
                'retry_after': int(window_end - current_time)
            }


class RateLimiter:
    """
    Main rate limiter class that manages different strategies and configurations.
    """
    
    def __init__(self, strategy: RateLimitStrategy = None):
        self.strategy = strategy or TokenBucketStrategy()
        self.default_limits = getattr(settings, 'RATE_LIMIT_DEFAULTS', {
            'anonymous': {
                'requests': 100,
                'window': 3600  # 1 hour
            },
            'authenticated': {
                'requests': 1000,
                'window': 3600  # 1 hour
            },
            'premium': {
                'requests': 5000,
                'window': 3600  # 1 hour
            }
        })
        self.ip_whitelist = getattr(settings, 'RATE_LIMIT_IP_WHITELIST', [])
        self.blocked_ips = getattr(settings, 'RATE_LIMIT_BLOCKED_IPS', [])
        
    def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        user_type: str = 'anonymous'
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed based on rate limiting rules.
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            limit: Override limit (optional)
            window: Override window (optional)
            user_type: User type for default limits
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        # Check IP whitelist
        if key in self.ip_whitelist:
            return True, {
                'whitelisted': True,
                'message': 'IP is whitelisted'
            }
        
        # Check blocked IPs
        if key in self.blocked_ips:
            return False, {
                'blocked': True,
                'message': 'IP is blocked'
            }
        
        # Get limits
        if limit is None or window is None:
            default_config = self.default_limits.get(user_type, self.default_limits['anonymous'])
            limit = limit or default_config['requests']
            window = window or default_config['window']
        
        # Check rate limit
        return self.strategy.is_allowed(key, limit, window)
    
    def get_rate_limit_headers(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate rate limit headers for HTTP responses.
        
        Args:
            metadata: Rate limit metadata
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = {}
        
        if 'requests_limit' in metadata:
            headers['X-RateLimit-Limit'] = str(metadata['requests_limit'])
        
        if 'requests_in_window' in metadata:
            headers['X-RateLimit-Remaining'] = str(
                max(0, metadata['requests_limit'] - metadata['requests_in_window'])
            )
        
        if 'reset_time' in metadata:
            headers['X-RateLimit-Reset'] = str(int(metadata['reset_time']))
        
        if 'retry_after' in metadata:
            headers['Retry-After'] = str(metadata['retry_after'])
        
        return headers
    
    def create_rate_limit_response(self, metadata: Dict[str, Any]) -> HttpResponse:
        """
        Create an HTTP response for rate limit exceeded.
        
        Args:
            metadata: Rate limit metadata
            
        Returns:
            HTTP response with appropriate headers
        """
        response = HttpResponse(status=status.HTTP_429_TOO_MANY_REQUESTS,
            content=json.dumps({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': metadata.get('retry_after'),
                'reset_time': metadata.get('reset_time')
            }),
            content_type='application/json'
        )
        
        # Add rate limit headers
        for header, value in self.get_rate_limit_headers(metadata).items():
            response[header] = value
        
        return response
    
    def get_client_ip(self, request) -> str:
        """
        Extract client IP from request.
        
        Args:
            request: Django request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP headers
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP in the chain
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        return ip
    
    def get_user_key(self, request) -> str:
        """
        Get unique key for rate limiting based on user.
        
        Args:
            request: Django request object
            
        Returns:
            Unique key for rate limiting
        """
        # Use user ID if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Use IP address for anonymous users
        return f"ip:{self.get_client_ip(request)}"
    
    def get_user_type(self, request) -> str:
        """
        Determine user type for rate limiting.
        
        Args:
            request: Django request object
            
        Returns:
            User type string
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if user has premium status (customize based on your user model)
            if hasattr(request.user, 'is_premium') and request.user.is_premium:
                return 'premium'
            return 'authenticated'
        
        return 'anonymous'
    
    def check_rate_limit(
        self,
        request,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        key: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit for a request.
        
        Args:
            request: Django request object
            limit: Override limit (optional)
            window: Override window (optional)
            key: Override key (optional)
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        if key is None:
            key = self.get_user_key(request)
        
        user_type = self.get_user_type(request)
        
        return self.is_allowed(key, limit, window, user_type)
    
    def log_rate_limit_event(
        self,
        request,
        metadata: Dict[str, Any],
        exceeded: bool = False
    ):
        """
        Log rate limiting events for monitoring.
        
        Args:
            request: Django request object
            metadata: Rate limit metadata
            exceeded: Whether the limit was exceeded
        """
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        path = request.get_full_path()
        method = request.method
        
        log_data = {
            'ip': ip,
            'user_agent': user_agent,
            'path': path,
            'method': method,
            'exceeded': exceeded,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if exceeded:
            logger.warning(f"Rate limit exceeded: {json.dumps(log_data)}")
        else:
            logger.info(f"Rate limit check: {json.dumps(log_data)}")
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """
        Get rate limiting statistics.
        
        Returns:
            Dictionary with rate limiting statistics
        """
        # This would typically be stored in a database or cache
        # For now, return basic info
        return {
            'strategy': self.strategy.__class__.__name__,
            'default_limits': self.default_limits,
            'whitelisted_ips': len(self.ip_whitelist),
            'blocked_ips': len(self.blocked_ips)
        }
    
    def add_to_whitelist(self, ip: str):
        """Add IP to whitelist."""
        if ip not in self.ip_whitelist:
            self.ip_whitelist.append(ip)
            logger.info(f"Added IP {ip} to rate limit whitelist")
    
    def remove_from_whitelist(self, ip: str):
        """Remove IP from whitelist."""
        if ip in self.ip_whitelist:
            self.ip_whitelist.remove(ip)
            logger.info(f"Removed IP {ip} from rate limit whitelist")
    
    def block_ip(self, ip: str):
        """Block an IP address."""
        if ip not in self.blocked_ips:
            self.blocked_ips.append(ip)
            logger.info(f"Blocked IP {ip} from rate limiting")
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"Unblocked IP {ip} from rate limiting")
    
    def clear_cache(self, key: Optional[str] = None):
        """
        Clear rate limit cache.
        
        Args:
            key: Specific key to clear (optional), clears all if None
        """
        if key:
            # Clear specific key for all windows
            for window in [60, 300, 3600, 86400]:  # Common window sizes
                cache_key = self.strategy.get_cache_key(key, window)
                cache.delete(cache_key)
        else:
            # Clear all rate limit cache (this might be expensive)
            logger.warning("Clearing all rate limit cache")
            # Implementation depends on your cache backend


class RateLimitMiddleware:
    """
    Django middleware for rate limiting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = RateLimiter()
        
        # Configure rate limiting paths
        self.rate_limit_paths = getattr(settings, 'RATE_LIMIT_PATHS', [
            r'^/api/',
            r'^/v1/',
            r'^/v2/',
        ])
        
        # Configure exempt paths
        self.exempt_paths = getattr(settings, 'RATE_LIMIT_EXEMPT_PATHS', [
            r'^/health/',
            r'^/status/',
            r'^/metrics/',
            r'^/admin/',
        ])
        
        # Configure path-specific limits
        self.path_limits = getattr(settings, 'RATE_LIMIT_PATH_LIMITS', {})
    
    def __call__(self, request):
        # Check if path should be rate limited
        if not self.should_rate_limit(request):
            return self.get_response(request)
        
        # Check rate limit
        is_allowed, metadata = self.rate_limiter.check_rate_limit(request)
        
        # Log the event
        self.rate_limiter.log_rate_limit_event(request, metadata, not is_allowed)
        
        if not is_allowed:
            return self.rate_limiter.create_rate_limit_response(metadata)
        
        # Get response and add headers
        response = self.get_response(request)
        
        # Add rate limit headers to successful responses
        for header, value in self.rate_limiter.get_rate_limit_headers(metadata).items():
            response[header] = value
        
        return response
    
    def should_rate_limit(self, request) -> bool:
        """
        Determine if the request should be rate limited.
        
        Args:
            request: Django request object
            
        Returns:
            True if request should be rate limited
        """
        path = request.get_full_path()
        
        # Check exempt paths first
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return False
        
        # Check rate limit paths
        for limit_path in self.rate_limit_paths:
            if path.startswith(limit_path):
                return True
        
        return False
    
    def get_path_limit(self, request) -> Optional[Tuple[int, int]]:
        """
        Get path-specific rate limit configuration.
        
        Args:
            request: Django request object
            
        Returns:
            Tuple of (limit, window) or None
        """
        path = request.get_full_path()
        
        for pattern, config in self.path_limits.items():
            if path.startswith(pattern):
                return config.get('limit'), config.get('window')
        
        return None


# Global rate limiter instance
rate_limiter = RateLimiter()
