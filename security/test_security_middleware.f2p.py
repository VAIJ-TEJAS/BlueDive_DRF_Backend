"""
F2P tests for security middleware enhancements.
These tests would fail on the base branch and pass after the fixes.
"""

import json
import time
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from security.middleware import SecurityMiddleware, HoneypotMiddleware, RequestValidationMiddleware


class SecurityMiddlewareF2PTests(TestCase):
    """Test security middleware with comprehensive coverage."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.middleware = SecurityMiddleware(lambda req: HttpResponse())
        
        # Clear cache before each test
        cache.clear()

    def test_rate_limiting_default(self):
        """Bug: Should apply default rate limiting."""
        # Create multiple requests to trigger rate limit
        client_ip = '192.168.1.100'
        
        for i in range(105):  # Exceed default limit of 100
            request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
            response = self.middleware.process_request(request)
            
            if i < 100:
                self.assertIsNone(response)
            else:
                self.assertIsNotNone(response)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                self.assertIn('RATE_LIMIT_EXCEEDED', json.loads(response.content)['code'])

    def test_rate_limiting_api_endpoint(self):
        """Bug: Should apply API-specific rate limiting."""
        client_ip = '192.168.1.101'
        
        # API endpoints have higher limits
        for i in range(1005):  # Exceed API limit of 1000
            request = self.factory.get('/api/bookings/', REMOTE_ADDR=client_ip)
            response = self.middleware.process_request(request)
            
            if i < 1000:
                self.assertIsNone(response)
            else:
                self.assertIsNotNone(response)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_rate_limiting_auth_endpoint(self):
        """Bug: Should apply stricter rate limiting to auth endpoints."""
        client_ip = '192.168.1.102'
        
        # Auth endpoints have stricter limits
        for i in range(15):  # Exceed auth limit of 10
            request = self.factory.post('/api/auth/login/', REMOTE_ADDR=client_ip)
            response = self.middleware.process_request(request)
            
            if i < 10:
                self.assertIsNone(response)
            else:
                self.assertIsNotNone(response)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_rate_limiting_with_user(self):
        """Bug: Should apply user-specific rate limiting."""
        client_ip = '192.168.1.103'
        
        # Create requests with different users
        for i in range(105):
            request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
            
            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            request.user = mock_user
            
            response = self.middleware.process_request(request)
            
            if i < 100:
                self.assertIsNone(response)
            else:
                self.assertIsNotNone(response)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_ip_blocking(self):
        """Bug: Should block requests from blocked IPs."""
        blocked_ip = '192.168.1.200'
        
        # Add to blocked IPs
        self.middleware.blocked_ips = [blocked_ip]
        
        request = self.factory.get('/api/test/', REMOTE_ADDR=blocked_ip)
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('IP_BLOCKED', json.loads(response.content)['code'])

    def test_ip_whitelisting(self):
        """Bug: Should only allow requests from whitelisted IPs."""
        allowed_ip = '192.168.1.201'
        blocked_ip = '192.168.1.202'
        
        # Set up whitelist
        self.middleware.allowed_ips = [allowed_ip]
        
        # Test allowed IP
        request = self.factory.get('/api/test/', REMOTE_ADDR=allowed_ip)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        
        # Test non-whitelisted IP
        request = self.factory.get('/api/test/', REMOTE_ADDR=blocked_ip)
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('IP_NOT_ALLOWED', json.loads(response.content)['code'])

    def test_request_size_validation(self):
        """Bug: Should block requests that are too large."""
        large_content = 'x' * (11 * 1024 * 1024)  # 11MB
        
        request = self.factory.post(
            '/api/test/',
            data={'large_data': large_content},
            REMOTE_ADDR='192.168.1.103'
        )
        request.META['CONTENT_LENGTH'] = str(len(large_content))
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertIn('REQUEST_TOO_LARGE', json.loads(response.content)['code'])

    def test_sql_injection_detection_get(self):
        """Bug: Should detect SQL injection in GET parameters."""
        malicious_params = {
            'id': "1' OR "1"="1",
            'search': "'; DROP TABLE users; --"
        }
        
        for param, value in malicious_params.items():
            request = self.factory.get('/api/test/', {param: value}, REMOTE_ADDR='192.168.1.104')
            response = self.middleware.process_request(request)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('SQL_INJECTION_DETECTED', json.loads(response.content)['code'])

    def test_sql_injection_detection_post_json(self):
        """Bug: Should detect SQL injection in JSON POST data."""
        malicious_data = {
            'query': "SELECT * FROM users WHERE '1'='1'",
            'filter': {"id": "1; DELETE FROM users; --"}
        }
        
        request = self.factory.post(
            '/api/test/',
            data=json.dumps(malicious_data),
            content_type='application/json',
            REMOTE_ADDR='192.168.1.105'
        )
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('SQL_INJECTION_DETECTED', json.loads(response.content)['code'])

    def test_sql_injection_detection_post_form(self):
        """Bug: Should detect SQL injection in form POST data."""
        malicious_data = {
            'username': "admin'--",
            'password': "' OR '1'='1"
        }
        
        request = self.factory.post('/api/test/', data=malicious_data, REMOTE_ADDR='192.168.1.106')
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('SQL_INJECTION_DETECTED', json.loads(response.content)['code'])

    def test_xss_detection_get(self):
        """Bug: Should detect XSS in GET parameters."""
        malicious_params = {
            'comment': '<script>alert("xss")</script>',
            'redirect': 'javascript:alert("xss")'
        }
        
        for param, value in malicious_params.items():
            request = self.factory.get('/api/test/', {param: value}, REMOTE_ADDR='192.168.1.107')
            response = self.middleware.process_request(request)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('XSS_DETECTED', json.loads(response.content)['code'])

    def test_xss_detection_post_json(self):
        """Bug: Should detect XSS in JSON POST data."""
        malicious_data = {
            'content': '<img src=x onerror=alert("xss")>',
            'description': '<iframe src="javascript:alert(\'xss\')"></iframe>'
        }
        
        request = self.factory.post(
            '/api/test/',
            data=json.dumps(malicious_data),
            content_type='application/json',
            REMOTE_ADDR='192.168.1.108'
        )
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('XSS_DETECTED', json.loads(response.content)['code'])

    def test_security_headers(self):
        """Bug: Should add security headers to response."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.109')
        
        # Process request (should pass)
        request_response = self.middleware.process_request(request)
        self.assertIsNone(request_response)
        
        # Create mock response
        response = HttpResponse()
        
        # Process response
        processed_response = self.middleware.process_response(request, response)
        
        # Check security headers
        self.assertIn('Content-Security-Policy', processed_response)
        self.assertIn('X-Content-Type-Options', processed_response)
        self.assertIn('X-Frame-Options', processed_response)
        self.assertIn('X-XSS-Protection', processed_response)
        self.assertIn('Referrer-Policy', processed_response)
        self.assertIn('Permissions-Policy', processed_response)

    def test_request_context_addition(self):
        """Bug: Should add security context to request."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.110')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertTrue(hasattr(request, 'security_context'))
        self.assertIn('client_ip', request.security_context)
        self.assertIn('request_id', request.security_context)
        self.assertIn('start_time', request.security_context)

    def test_x_forwarded_for_ip_detection(self):
        """Bug: Should correctly extract IP from X-Forwarded-For header."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.111')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.111'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertEqual(request.security_context['client_ip'], '203.0.113.1')

    def test_nested_data_sql_injection_check(self):
        """Bug: Should detect SQL injection in nested JSON data."""
        malicious_data = {
            'user': {
                'profile': {
                    'bio': "'; DROP TABLE users; --"
                }
            },
            'settings': [
                {'name': 'theme', 'value': "SELECT * FROM users"},
                {'name': 'lang', 'value': 'en'}
            ]
        }
        
        request = self.factory.post(
            '/api/test/',
            data=json.dumps(malicious_data),
            content_type='application/json',
            REMOTE_ADDR='192.168.1.112'
        )
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('SQL_INJECTION_DETECTED', json.loads(response.content)['code'])

    def test_nested_data_xss_check(self):
        """Bug: Should detect XSS in nested JSON data."""
        malicious_data = {
            'post': {
                'content': '<script>alert("xss")</script>',
                'comments': [
                    {'text': '<img src=x onerror=alert(1)>'},
                    {'text': 'Safe comment'}
                ]
            }
        }
        
        request = self.factory.post(
            '/api/test/',
            data=json.dumps(malicious_data),
            content_type='application/json',
            REMOTE_ADDR='192.168.1.113'
        )
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('XSS_DETECTED', json.loads(response.content)['code'])

    def test_concurrent_rate_limiting(self):
        """Bug: Should handle concurrent rate limiting correctly."""
        client_ip = '192.168.1.114'
        
        # Simulate concurrent requests
        responses = []
        for i in range(105):
            request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
            response = self.middleware.process_request(request)
            responses.append(response)
        
        # Should have rate limited responses after 100 requests
        rate_limited_count = sum(1 for r in responses if r is not None)
        self.assertGreater(rate_limited_count, 0)

    def test_rate_limit_window_expiry(self):
        """Bug: Should reset rate limit after window expires."""
        client_ip = '192.168.1.115'
        
        # Exhaust rate limit
        for i in range(100):
            request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
            self.middleware.process_request(request)
        
        # Next request should be rate limited
        request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        
        # Mock cache expiry
        with patch('django.core.cache.cache.get', return_value=0):
            request = self.factory.get('/api/test/', REMOTE_ADDR=client_ip)
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

    def test_error_handling_in_middleware(self):
        """Bug: Should handle errors gracefully without crashing."""
        # Mock cache.get to raise an exception
        with patch('django.core.cache.cache.get', side_effect=Exception('Cache error')):
            request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.116')
            
            # Should not crash and should return None (allow request)
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

    def test_malformed_json_handling(self):
        """Bug: Should handle malformed JSON gracefully."""
        malformed_json = '{"invalid": json}'
        
        request = self.factory.post(
            '/api/test/',
            data=malformed_json,
            content_type='application/json',
            REMOTE_ADDR='192.168.1.117'
        )
        
        # Should not crash and should allow request
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_unicode_handling(self):
        """Bug: Should handle Unicode characters correctly."""
        unicode_data = {
            'name': '测试用户',
            'description': '🎉 Unicode test',
            'comment': 'Café résumé naïve'
        }
        
        request = self.factory.post(
            '/api/test/',
            data=json.dumps(unicode_data),
            content_type='application/json',
            REMOTE_ADDR='192.168.1.118'
        )
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Should allow legitimate Unicode

    def test_empty_request_handling(self):
        """Bug: Should handle empty requests gracefully."""
        request = self.factory.post('/api/test/', REMOTE_ADDR='192.168.1.119')
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_large_request_without_content_length(self):
        """Bug: Should handle requests without Content-Length header."""
        request = self.factory.post('/api/test/', REMOTE_ADDR='192.168.1.120')
        del request.META['CONTENT_LENGTH']
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)


class HoneypotMiddlewareF2PTests(TestCase):
    """Test honeypot middleware functionality."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.middleware = HoneypotMiddleware(lambda req: HttpResponse())

    def test_honeypot_url_blocking(self):
        """Bug: Should block access to honeypot URLs."""
        honeypot_urls = [
            '/admin/login',
            '/wp-admin/',
            '/phpmyadmin/',
            '/.env'
        ]
        
        for url in honeypot_urls:
            request = self.factory.get(url, REMOTE_ADDR='192.168.1.200')
            response = self.middleware.process_request(request)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertIn('HONEYPOT_TRIGGERED', json.loads(response.content)['code'])

    def test_honeypot_ip_blocking(self):
        """Bug: Should temporarily block IP that triggers honeypot."""
        client_ip = '192.168.1.201'
        
        # Trigger honeypot
        request = self.factory.get('/admin/login', REMOTE_ADDR=client_ip)
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        
        # Check if IP is blocked
        blocked = cache.get(f"honeypot_block:{client_ip}")
        self.assertTrue(blocked)

    def test_normal_url_access(self):
        """Bug: Should allow access to normal URLs."""
        normal_urls = [
            '/api/bookings/',
            '/api/packages/',
            '/api/trips/',
            '/home/'
        ]
        
        for url in normal_urls:
            request = self.factory.get(url, REMOTE_ADDR='192.168.1.202')
            response = self.middleware.process_request(request)
            
            self.assertIsNone(response)

    def test_x_forwarded_for_ip_extraction(self):
        """Bug: Should extract IP from X-Forwarded-For for honeypot."""
        request = self.factory.get('/admin/login', REMOTE_ADDR='192.168.1.203')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.203'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        
        # Check if the correct IP was blocked
        blocked = cache.get("honeypot_block:203.0.113.1")
        self.assertTrue(blocked)


class RequestValidationMiddlewareF2PTests(TestCase):
    """Test request validation middleware functionality."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.middleware = RequestValidationMiddleware(lambda req: HttpResponse())

    def test_suspicious_user_agent_blocking(self):
        """Bug: Should block requests with suspicious user agents."""
        suspicious_uas = [
            'sqlmap/1.0',
            'nikto/2.1',
            'python-requests/2.25',
            'curl/7.68',
            'bot/scanner'
        ]
        
        for ua in suspicious_uas:
            request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.210')
            request.META['HTTP_USER_AGENT'] = ua
            
            response = self.middleware.process_request(request)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertIn('SUSPICIOUS_USER_AGENT', json.loads(response.content)['code'])

    def test_legitimate_user_agent_allowance(self):
        """Bug: Should allow requests with legitimate user agents."""
        legitimate_uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        for ua in legitimate_uas:
            request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.211')
            request.META['HTTP_USER_AGENT'] = ua
            
            response = self.middleware.process_request(request)
            
            self.assertIsNone(response)

    def test_suspicious_headers_blocking(self):
        """Bug: Should block requests with suspicious headers."""
        suspicious_headers = [
            'HTTP_X_FORWARDED_HOST',
            'HTTP_X_REAL_IP',
            'HTTP_X_ORIGINATING_IP',
            'HTTP_X_FORWARDED_SERVER'
        ]
        
        for header in suspicious_headers:
            request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.212')
            request.META[header] = 'malicious.com'
            
            response = self.middleware.process_request(request)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertIn('SUSPICIOUS_HEADERS', json.loads(response.content)['code'])

    def test_normal_headers_allowance(self):
        """Bug: Should allow requests with normal headers."""
        normal_headers = {
            'HTTP_ACCEPT': 'application/json',
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer token123',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
        }
        
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.213')
        for header, value in normal_headers.items():
            request.META[header] = value
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_missing_user_agent_handling(self):
        """Bug: Should handle missing User-Agent header gracefully."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.214')
        del request.META['HTTP_USER_AGENT']
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_case_insensitive_user_agent_detection(self):
        """Bug: Should detect suspicious user agents case-insensitively."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.215')
        request.META['HTTP_USER_AGENT'] = 'SQLMAP/1.0'  # Uppercase
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SecurityIntegrationTests(TestCase):
    """Integration tests for security middleware stack."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.security_middleware = SecurityMiddleware(lambda req: HttpResponse())
        self.honeypot_middleware = HoneypotMiddleware(lambda req: HttpResponse())
        self.validation_middleware = RequestValidationMiddleware(lambda req: HttpResponse())

    def test_middleware_stack_integration(self):
        """Bug: Should work correctly when multiple middlewares are stacked."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.220')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (compatible; TestBot/1.0)'
        
        # Apply validation middleware first
        response = self.validation_middleware.process_request(request)
        self.assertIsNone(response)
        
        # Apply security middleware
        response = self.security_middleware.process_request(request)
        self.assertIsNone(response)
        
        # Apply honeypot middleware
        response = self.honeypot_middleware.process_request(request)
        self.assertIsNone(response)

    def test_middleware_priority_order(self):
        """Bug: Should apply middlewares in correct priority order."""
        # Suspicious user agent should be caught first
        request = self.factory.get('/admin/login', REMOTE_ADDR='192.168.1.221')
        request.META['HTTP_USER_AGENT'] = 'sqlmap/1.0'
        
        # Validation middleware should catch this first
        response = self.validation_middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertIn('SUSPICIOUS_USER_AGENT', json.loads(response.content)['code'])

    def test_error_propagation_in_stack(self):
        """Bug: Should handle errors gracefully in middleware stack."""
        request = self.factory.get('/api/test/', REMOTE_ADDR='192.168.1.222')
        
        # Mock an exception in security middleware
        with patch.object(self.security_middleware, '_get_client_ip', side_effect=Exception('Network error')):
            response = self.security_middleware.process_request(request)
            self.assertIsNone(response)  # Should not crash

    def test_performance_under_load(self):
        """Bug: Should maintain performance under high load."""
        import time
        
        start_time = time.time()
        
        # Process 1000 requests
        for i in range(1000):
            request = self.factory.get(f'/api/test/{i}/', REMOTE_ADDR=f'192.168.1.{i % 255}')
            
            # Apply all middlewares
            response = self.validation_middleware.process_request(request)
            if response is None:
                response = self.security_middleware.process_request(request)
            if response is None:
                response = self.honeypot_middleware.process_request(request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 5 seconds)
        self.assertLess(duration, 5.0)

    def test_memory_usage_stability(self):
        """Bug: Should not leak memory over time."""
        import gc
        import sys
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many requests
        for i in range(500):
            request = self.factory.get(f'/api/test/{i}/', REMOTE_ADDR=f'192.168.1.{i % 255}')
            
            response = self.validation_middleware.process_request(request)
            if response is None:
                response = self.security_middleware.process_request(request)
            if response is None:
                response = self.honeypot_middleware.process_request(request)
        
        # Check memory usage
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be reasonable (less than 50% increase)
        memory_growth = (final_objects - initial_objects) / initial_objects
        self.assertLess(memory_growth, 0.5)
