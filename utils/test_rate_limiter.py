"""
F2P tests for API rate limiting enhancements.
These tests would fail on the base branch and pass after the fixes.
"""

import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.http import HttpRequest
from rest_framework import status
from django.conf import settings

from utils.rate_limiter import (
    RateLimitExceeded,
    RateLimitStrategy,
    TokenBucketStrategy,
    SlidingWindowStrategy,
    FixedWindowStrategy,
    RateLimiter,
    RateLimitMiddleware
)


class TokenBucketStrategyTest(TestCase):
    """Test token bucket rate limiting strategy."""
    
    def setUp(self):
        self.strategy = TokenBucketStrategy()
        cache.clear()
    
    def test_token_bucket_allows_requests_under_limit(self):
        """Bug: Should allow requests under the limit."""
        key = "test_user"
        limit = 10
        window = 60
        
        # First request should be allowed
        is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
        
        self.assertTrue(is_allowed)
        self.assertEqual(metadata['tokens_remaining'], 9)
        self.assertEqual(metadata['tokens_limit'], limit)
    
    def test_token_bucket_blocks_requests_over_limit(self):
        """Bug: Should block requests over the limit."""
        key = "test_user"
        limit = 2
        window = 60
        
        # Use up all tokens
        self.strategy.is_allowed(key, limit, window)
        self.strategy.is_allowed(key, limit, window)
        
        # Third request should be blocked
        is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
        
        self.assertFalse(is_allowed)
        self.assertEqual(metadata['tokens_remaining'], 0)
        self.assertIn('retry_after', metadata)
    
    def test_token_bucket_refills_tokens_over_time(self):
        """Bug: Should refill tokens over time."""
        key = "test_user"
        limit = 10
        window = 60  # 1 minute
        
        # Use all tokens
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Should be blocked
        is_allowed, _ = self.strategy.is_allowed(key, limit, window)
        self.assertFalse(is_allowed)
        
        # Simulate time passing (half the window)
        with patch('time.time', return_value=time.time() + window // 2):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            
            # Should have some tokens back
            self.assertTrue(is_allowed)
            self.assertGreater(metadata['tokens_remaining'], 0)
    
    def test_token_bucket_handles_multiple_clients(self):
        """Bug: Should handle multiple clients independently."""
        key1 = "user1"
        key2 = "user2"
        limit = 5
        window = 60
        
        # Use all tokens for user1
        for _ in range(limit):
            self.strategy.is_allowed(key1, limit, window)
        
        # User1 should be blocked
        is_allowed1, _ = self.strategy.is_allowed(key1, limit, window)
        self.assertFalse(is_allowed1)
        
        # User2 should still be allowed
        is_allowed2, _ = self.strategy.is_allowed(key2, limit, window)
        self.assertTrue(is_allowed2)
    
    def test_token_bucket_generates_cache_key(self):
        """Bug: Should generate proper cache keys."""
        key = "test_user"
        window = 60
        
        cache_key = self.strategy.get_cache_key(key, window)
        expected_key = f"rate_limit:{key}:{window}"
        
        self.assertEqual(cache_key, expected_key)


class SlidingWindowStrategyTest(TestCase):
    """Test sliding window rate limiting strategy."""
    
    def setUp(self):
        self.strategy = SlidingWindowStrategy()
        cache.clear()
    
    def test_sliding_window_allows_requests_under_limit(self):
        """Bug: Should allow requests under the limit."""
        key = "test_user"
        limit = 5
        window = 60
        
        # Make requests under limit
        for i in range(limit):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['requests_in_window'], i + 1)
    
    def test_sliding_window_blocks_requests_over_limit(self):
        """Bug: Should block requests over the limit."""
        key = "test_user"
        limit = 3
        window = 60
        
        # Use up limit
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Next request should be blocked
        is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
        
        self.assertFalse(is_allowed)
        self.assertEqual(metadata['requests_in_window'], limit)
        self.assertIn('retry_after', metadata)
    
    def test_sliding_window_slides_over_time(self):
        """Bug: Should slide the window over time."""
        key = "test_user"
        limit = 5
        window = 60
        
        # Fill the window
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Should be blocked
        is_allowed, _ = self.strategy.is_allowed(key, limit, window)
        self.assertFalse(is_allowed)
        
        # Simulate time passing (old requests fall out of window)
        with patch('time.time', return_value=time.time() + window + 1):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            
            # Should be allowed again
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['requests_in_window'], 1)
    
    def test_sliding_window_handles_concurrent_requests(self):
        """Bug: Should handle concurrent requests correctly."""
        key = "test_user"
        limit = 10
        window = 60
        
        # Make concurrent requests
        results = []
        for _ in range(limit + 2):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            results.append((is_allowed, metadata))
        
        # First 10 should be allowed
        allowed_count = sum(1 for is_allowed, _ in results if is_allowed)
        self.assertEqual(allowed_count, limit)


class FixedWindowStrategyTest(TestCase):
    """Test fixed window rate limiting strategy."""
    
    def setUp(self):
        self.strategy = FixedWindowStrategy()
        cache.clear()
    
    def test_fixed_window_allows_requests_under_limit(self):
        """Bug: Should allow requests under the limit."""
        key = "test_user"
        limit = 5
        window = 60
        
        # Make requests under limit
        for i in range(limit):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['requests_in_window'], i + 1)
    
    def test_fixed_window_blocks_requests_over_limit(self):
        """Bug: Should block requests over the limit."""
        key = "test_user"
        limit = 3
        window = 60
        
        # Use up limit
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Next request should be blocked
        is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
        
        self.assertFalse(is_allowed)
        self.assertEqual(metadata['requests_in_window'], limit)
    
    def test_fixed_window_resets_at_window_boundary(self):
        """Bug: Should reset counter at window boundary."""
        key = "test_user"
        limit = 5
        window = 60
        
        # Fill the window
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Should be blocked
        is_allowed, _ = self.strategy.is_allowed(key, limit, window)
        self.assertFalse(is_allowed)
        
        # Simulate moving to next window
        with patch('time.time', return_value=time.time() + window + 1):
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            
            # Should be allowed again with fresh counter
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['requests_in_window'], 1)
    
    def test_fixed_window_handles_multiple_windows(self):
        """Bug: Should handle multiple time windows."""
        key = "test_user"
        limit = 3
        window = 30
        
        # Fill first window
        for _ in range(limit):
            self.strategy.is_allowed(key, limit, window)
        
        # Should be blocked in first window
        is_allowed, _ = self.strategy.is_allowed(key, limit, window)
        self.assertFalse(is_allowed)
        
        # Move to next window
        with patch('time.time', return_value=time.time() + window + 1):
            # Should be allowed in new window
            is_allowed, metadata = self.strategy.is_allowed(key, limit, window)
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['requests_in_window'], 1)


class RateLimiterTest(TestCase):
    """Test main rate limiter class."""
    
    def setUp(self):
        self.rate_limiter = RateLimiter()
        cache.clear()
    
    def test_rate_limiter_uses_default_limits(self):
        """Bug: Should use default limits for different user types."""
        # Anonymous user
        is_allowed, metadata = self.rate_limiter.is_allowed("anon_user", user_type='anonymous')
        self.assertTrue(is_allowed)
        self.assertEqual(metadata['requests_limit'], 100)
        
        # Authenticated user
        is_allowed, metadata = self.rate_limiter.is_allowed("auth_user", user_type='authenticated')
        self.assertTrue(is_allowed)
        self.assertEqual(metadata['requests_limit'], 1000)
        
        # Premium user
        is_allowed, metadata = self.rate_limiter.is_allowed("premium_user", user_type='premium')
        self.assertTrue(is_allowed)
        self.assertEqual(metadata['requests_limit'], 5000)
    
    def test_rate_limiter_respects_ip_whitelist(self):
        """Bug: Should allow whitelisted IPs regardless of limits."""
        whitelisted_ip = "192.168.1.100"
        self.rate_limiter.add_to_whitelist(whitelisted_ip)
        
        # Even with zero limit, should be allowed
        is_allowed, metadata = self.rate_limiter.is_allowed(whitelisted_ip, limit=0, window=60)
        self.assertTrue(is_allowed)
        self.assertTrue(metadata['whitelisted'])
    
    def test_rate_limiter_blocks_blacklisted_ips(self):
        """Bug: Should block blacklisted IPs."""
        blocked_ip = "192.168.1.200"
        self.rate_limiter.block_ip(blocked_ip)
        
        # Even with high limit, should be blocked
        is_allowed, metadata = self.rate_limiter.is_allowed(blocked_ip, limit=1000, window=60)
        self.assertFalse(is_allowed)
        self.assertTrue(metadata['blocked'])
    
    def test_rate_limiter_generates_headers(self):
        """Bug: Should generate proper HTTP headers."""
        metadata = {
            'requests_limit': 100,
            'requests_in_window': 25,
            'reset_time': int(time.time()) + 3600
        }
        
        headers = self.rate_limiter.get_rate_limit_headers(metadata)
        
        self.assertEqual(headers['X-RateLimit-Limit'], '100')
        self.assertEqual(headers['X-RateLimit-Remaining'], '75')
        self.assertEqual(headers['X-RateLimit-Reset'], str(metadata['reset_time']))
    
    def test_rate_limiter_creates_too_many_requests_response(self):
        """Bug: Should create proper HTTP 429 response."""
        metadata = {
            'retry_after': 60,
            'reset_time': int(time.time()) + 60
        }
        
        response = self.rate_limiter.create_rate_limit_response(metadata)
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response['Retry-After'], '60')
    
    def test_rate_limiter_extracts_client_ip(self):
        """Bug: Should extract client IP from request."""
        request = HttpRequest()
        
        # Test with X-Forwarded-For header
        request.META = {
            'HTTP_X_FORWARDED_FOR': '203.0.113.1, 192.168.1.1',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        ip = self.rate_limiter.get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')
        
        # Test without X-Forwarded-For header
        request.META = {
            'REMOTE_ADDR': '203.0.113.2'
        }
        
        ip = self.rate_limiter.get_client_ip(request)
        self.assertEqual(ip, '203.0.113.2')
    
    def test_rate_limiter_generates_user_key(self):
        """Bug: Should generate proper user key."""
        # Test with authenticated user
        request = HttpRequest()
        mock_user = Mock()
        mock_user.id = 123
        mock_user.is_authenticated = True
        request.user = mock_user
        
        key = self.rate_limiter.get_user_key(request)
        self.assertEqual(key, 'user:123')
        
        # Test with anonymous user
        mock_user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        key = self.rate_limiter.get_user_key(request)
        self.assertEqual(key, 'ip:192.168.1.1')
    
    def test_rate_limiter_determines_user_type(self):
        """Bug: Should determine user type correctly."""
        request = HttpRequest()
        
        # Anonymous user
        mock_user = Mock()
        mock_user.is_authenticated = False
        request.user = mock_user
        
        user_type = self.rate_limiter.get_user_type(request)
        self.assertEqual(user_type, 'anonymous')
        
        # Authenticated user
        mock_user.is_authenticated = True
        mock_user.is_premium = False
        request.user = mock_user
        
        user_type = self.rate_limiter.get_user_type(request)
        self.assertEqual(user_type, 'authenticated')
        
        # Premium user
        mock_user.is_premium = True
        request.user = mock_user
        
        user_type = self.rate_limiter.get_user_type(request)
        self.assertEqual(user_type, 'premium')
    
    def test_rate_limiter_checks_rate_limit(self):
        """Bug: Should check rate limit for request."""
        request = HttpRequest()
        mock_user = Mock()
        mock_user.id = 123
        mock_user.is_authenticated = True
        mock_user.is_premium = False
        request.user = mock_user
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        is_allowed, metadata = self.rate_limiter.check_rate_limit(request)
        
        self.assertTrue(is_allowed)
        self.assertEqual(metadata['requests_limit'], 1000)  # Authenticated user limit
    
    def test_rate_limiter_logs_events(self):
        """Bug: Should log rate limiting events."""
        request = HttpRequest()
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'TestAgent/1.0'
        }
        request.method = 'GET'
        request.get_full_path = Mock(return_value='/api/test')
        
        metadata = {'requests_limit': 100}
        
        with patch('utils.rate_limiter.logger') as mock_logger:
            self.rate_limiter.log_rate_limit_event(request, metadata, exceeded=False)
            mock_logger.info.assert_called()
            
            self.rate_limiter.log_rate_limit_event(request, metadata, exceeded=True)
            mock_logger.warning.assert_called()
    
    def test_rate_limiter_manages_whitelist(self):
        """Bug: Should manage IP whitelist."""
        ip = "192.168.1.100"
        
        # Add to whitelist
        self.rate_limiter.add_to_whitelist(ip)
        self.assertIn(ip, self.rate_limiter.ip_whitelist)
        
        # Remove from whitelist
        self.rate_limiter.remove_from_whitelist(ip)
        self.assertNotIn(ip, self.rate_limiter.ip_whitelist)
    
    def test_rate_limiter_manages_blocked_ips(self):
        """Bug: Should manage blocked IPs."""
        ip = "192.168.1.200"
        
        # Block IP
        self.rate_limiter.block_ip(ip)
        self.assertIn(ip, self.rate_limiter.blocked_ips)
        
        # Unblock IP
        self.rate_limiter.unblock_ip(ip)
        self.assertNotIn(ip, self.rate_limiter.blocked_ips)
    
    def test_rate_limiter_clears_cache(self):
        """Bug: Should clear rate limit cache."""
        key = "test_user"
        limit = 5
        window = 60
        
        # Add some data to cache
        self.rate_limiter.strategy.is_allowed(key, limit, window)
        
        # Clear specific key
        self.rate_limiter.clear_cache(key)
        
        # Cache should be empty for this key
        cache_key = self.rate_limiter.strategy.get_cache_key(key, window)
        self.assertIsNone(cache.get(cache_key))


class RateLimitMiddlewareTest(TestCase):
    """Test rate limiting middleware."""
    
    def setUp(self):
        self.middleware = RateLimitMiddleware(lambda r: HttpResponse())
        cache.clear()
    
    def test_middleware_allows_exempt_paths(self):
        """Bug: Should allow exempt paths."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/health/')
        request.method = 'GET'
        
        response = self.middleware(request)
        
        # Should pass through without rate limiting
        self.assertIsNotNone(response)
    
    def test_middleware_rate_limits_api_paths(self):
        """Bug: Should rate limit API paths."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/api/users/')
        request.method = 'GET'
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        response = self.middleware(request)
        
        # Should be rate limited
        self.assertIsNotNone(response)
    
    def test_middleware_adds_rate_limit_headers(self):
        """Bug: Should add rate limit headers to responses."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/api/test/')
        request.method = 'GET'
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        response = self.middleware(request)
        
        # Should have rate limit headers
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
    
    def test_middleware_returns_429_when_limit_exceeded(self):
        """Bug: Should return 429 when limit exceeded."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/api/test/')
        request.method = 'GET'
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        # Override rate limiter to always return False
        with patch.object(self.middleware.rate_limiter, 'check_rate_limit', return_value=(False, {'retry_after': 60})):
            response = self.middleware(request)
            
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_middleware_uses_path_specific_limits(self):
        """Bug: Should use path-specific limits when configured."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/api/special/')
        request.method = 'GET'
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        with override_settings(RATE_LIMIT_PATH_LIMITS={'/api/special/': {'limit': 5, 'window': 60}}):
            with patch.object(self.middleware.rate_limiter, 'check_rate_limit') as mock_check:
                self.middleware(request)
                
                # Should call check_rate_limit with path-specific limits
                mock_check.assert_called_once()
                args, kwargs = mock_check.call_args
                self.assertEqual(kwargs.get('limit'), 5)
                self.assertEqual(kwargs.get('window'), 60)
    
    def test_middleware_logs_events(self):
        """Bug: Should log rate limiting events."""
        request = HttpRequest()
        request.get_full_path = Mock(return_value='/api/test/')
        request.method = 'GET'
        request.user = Mock()
        request.user.is_authenticated = False
        request.META = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'TestAgent/1.0'
        }
        
        with patch.object(self.middleware.rate_limiter, 'log_rate_limit_event') as mock_log:
            self.middleware(request)
            
            # Should log the event
            mock_log.assert_called_once()


class RateLimitIntegrationTest(TestCase):
    """Integration tests for rate limiting."""
    
    def setUp(self):
        self.rate_limiter = RateLimiter()
        cache.clear()
    
    def test_end_to_end_rate_limiting_flow(self):
        """Bug: Should handle complete rate limiting flow."""
        key = "integration_test_user"
        limit = 3
        window = 60
        
        # Make requests up to limit
        for i in range(limit):
            is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
            self.assertTrue(is_allowed, f"Request {i+1} should be allowed")
            self.assertEqual(metadata['requests_in_window'], i + 1)
        
        # Next request should be blocked
        is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
        self.assertFalse(is_allowed)
        self.assertEqual(metadata['requests_in_window'], limit)
        
        # Should have retry after information
        self.assertIn('retry_after', metadata)
        self.assertGreaterEqual(metadata['retry_after'], 0)
        self.assertLessEqual(metadata['retry_after'], window)
    
    def test_multiple_strategies_consistency(self):
        """Bug: Different strategies should behave consistently."""
        strategies = [
            TokenBucketStrategy(),
            SlidingWindowStrategy(),
            FixedWindowStrategy()
        ]
        
        key = "consistency_test"
        limit = 5
        window = 60
        
        for strategy in strategies:
            self.rate_limiter.strategy = strategy
            cache.clear()
            
            # All strategies should allow requests under limit
            for i in range(limit):
                is_allowed, _ = self.rate_limiter.is_allowed(key, limit, window)
                self.assertTrue(is_allowed, f"{strategy.__class__.__name__} should allow request {i+1}")
            
            # All strategies should block when over limit
            is_allowed, _ = self.rate_limiter.is_allowed(key, limit, window)
            self.assertFalse(is_allowed, f"{strategy.__class__.__name__} should block over limit")
    
    def test_rate_limiting_with_different_windows(self):
        """Bug: Should handle different time windows correctly."""
        key = "window_test"
        
        windows = [60, 300, 3600]  # 1 minute, 5 minutes, 1 hour
        
        for window in windows:
            cache.clear()
            
            # Should work with different window sizes
            is_allowed, metadata = self.rate_limiter.is_allowed(key, limit=10, window=window)
            self.assertTrue(is_allowed)
            self.assertEqual(metadata['window_size'], window)
    
    def test_rate_limiting_performance(self):
        """Bug: Should handle high volume requests efficiently."""
        key = "performance_test"
        limit = 100
        window = 60
        
        # Make many requests quickly
        start_time = time.time()
        
        for i in range(limit):
            is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
            if i < limit - 1:
                self.assertTrue(is_allowed)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly (under 1 second for 100 requests)
        self.assertLess(duration, 1.0, "Rate limiting should be performant")
    
    def test_rate_limiting_edge_cases(self):
        """Bug: Should handle edge cases gracefully."""
        # Test with zero limit
        is_allowed, metadata = self.rate_limiter.is_allowed("edge_case", limit=0, window=60)
        self.assertFalse(is_allowed)
        
        # Test with very small window
        is_allowed, metadata = self.rate_limiter.is_allowed("edge_case", limit=1, window=1)
        self.assertTrue(is_allowed)
        
        # Test with very large limit
        is_allowed, metadata = self.rate_limiter.is_allowed("edge_case", limit=10000, window=3600)
        self.assertTrue(is_allowed)
        
        # Test with empty key
        is_allowed, metadata = self.rate_limiter.is_allowed("", limit=10, window=60)
        self.assertTrue(is_allowed)
    
    def test_rate_limiting_concurrent_access(self):
        """Bug: Should handle concurrent access safely."""
        import threading
        
        key = "concurrent_test"
        limit = 10
        window = 60
        results = []
        
        def make_request():
            is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
            results.append(is_allowed)
        
        # Create multiple threads making requests
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have exactly 'limit' allowed requests
        allowed_count = sum(results)
        self.assertEqual(allowed_count, limit)
    
    def test_rate_limiting_cache_behavior(self):
        """Bug: Should use cache correctly."""
        key = "cache_test"
        limit = 5
        window = 60
        
        # Make request
        is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
        self.assertTrue(is_allowed)
        
        # Check cache key exists
        cache_key = self.rate_limiter.strategy.get_cache_key(key, window)
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        # Clear cache and verify behavior
        cache.delete(cache_key)
        
        # Should work after cache clear
        is_allowed, metadata = self.rate_limiter.is_allowed(key, limit, window)
        self.assertTrue(is_allowed)
