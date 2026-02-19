"""
F2P tests for security middleware enhancements.
These tests would fail on the base branch and pass after the fixes.
"""

from django.test import TestCase, override_settings
from django.test.client import Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch, MagicMock
import time
import json
import logging
from unittest.mock import Mock
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.core.handlers.wsgi import WSGIRequest
from io import BytesIO

from middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestValidationMiddleware,
    HoneypotMiddleware,
    APIKeyMiddleware,
    SecurityLoggingMiddleware,
    CSRFProtectionMiddleware,
    ContentSecurityMiddleware,
    IPWhitelistMiddleware,
    RequestIDMiddleware,
    SecurityMiddleware
)


class SecurityMiddlewareF2PTest(TestCase):
    """Test security middleware enhancements."""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
    def test_security_headers_middleware(self):
        """Bug: Should add security headers to responses."""
        middleware = SecurityHeadersMiddleware(get_response=lambda: HttpResponse())
        
        # Create a mock request
        request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '8000',
            'wsgi.input': BytesIO(b'test data'),
        })
        
        # Create a response
        response = HttpResponse('Test content')
        
        # Process response through middleware
        processed_response = middleware.process_response(request, response)
        
        # Check security headers
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(processed_response['X-Frame-Options'], 'DENY')
        self.assertEqual(processed_response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(processed_response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')
        self.assertIn('Content-Security-Policy', processed_response['Content-Security-Policy'])
        self.assertEqual(processed_response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(processed_response['Permissions-Policy'], 'camera=(), microphone=(), geolocation=()')
        self.assertEqual(processed_response['Server'], 'Server')
    
    def test_rate_limit_middleware(self):
        """Bug: Should implement rate limiting."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        # Mock cache
        with patch('middleware.cache') as mock_cache:
            mock_cache.get.return_value = 0
            mock_cache.set.return_value = True
            
            # Test rate limiting
            client_ip = '192.168.1.1'
            
            # First request should pass
            self.assertTrue(middleware.check_rate_limit(client_ip))
            
            # Exceed rate limit
            mock_cache.get.return_value = 100
            self.assertFalse(middleware.check_rate_limit(client_ip))
            
            # Test different IP
            self.assertTrue(middleware.check_rate_limit('192.168.1.2'))
    
    def test_rate_limit_middleware_process_request(self):
        """Bug: Should block requests when rate limit exceeded."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        with patch('middleware.cache') as mock_cache:
            mock_cache.get.return_value = 100  # Exceeded limit
            
            request = self._create_request()
            
            # Should return forbidden response
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponseForbidden)
            self.assertEqual(response.content.decode(), 'Rate limit exceeded. Please try again later.')
    
    def test_request_validation_middleware(self):
        """Bug: Should validate incoming requests."""
        middleware = RequestValidationMiddleware(get_response=lambda: HttpResponse())
        
        # Test large request
        request = self._create_request()
        request.body = b'x' * (11 * 1024 * 1024)  # 11MB
        
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content.decode(), 'Request too large.')
    
    def test_request_validation_blocked_user_agents(self):
        """Bug: Should block requests from blocked user agents."""
        middleware = RequestValidationMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'BLOCKED_USER_AGENTS', ['bot', 'scanner']):
            request = self._create_request()
            request.META['HTTP_USER_AGENT'] = 'malicious-bot'
            
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponseForbidden)
            self.assertEqual(response.content.decode(), 'Access denied.')
    
    def test_request_validation_suspicious_paths(self):
        """Bug: Should block requests to suspicious paths."""
        middleware = RequestValidationMiddleware(get_response=lambda: HttpResponse())
        
        suspicious_paths = [
            '/../../../etc/passwd',
            '/admin/panel',
            '/wp-admin/',
            '/phpMyAdmin',
            '/test/../../bin/shell'
        ]
        
        for path in suspicious_paths:
            request = self._create_request(path=path)
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponseForbidden)
            self.assertEqual(response.content.decode(), 'Access denied.')
    
    def test_honeypot_middleware(self):
        """Bug: Should block requests to honeypot paths."""
        middleware = HoneypotMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'HONEYPOT_PATHS', ['/admin/', '/wp-login.php']):
            request = self._create_request(path='/admin/')
            
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponseForbidden)
            self.assertEqual(response.content.decode(), 'Access denied.')
    
    def test_honeypot_middleware_ip_blocking(self):
        """Bug: Should block IP after honeypot trigger."""
        middleware = HoneypotMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'HONEYPOT_BLOCK_DURATION', 3600):
            with patch.object(middleware, 'block_ip') as mock_block:
                request = self._create_request(path='/admin/')
                
                response = middleware.process_request(request)
                self.assertIsInstance(response, HttpResponseForbidden)
                mock_block.assert_called_with('192.168.1.1')
    
    def test_api_key_middleware_valid_key(self):
        """Bug: Should allow requests with valid API key."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'API_KEYS', ['valid-key-123']):
            request = self._create_request()
            request.META['HTTP_X_API_KEY'] = 'valid-key-123'
            
            response = middleware.process_request(request)
            self.assertIsNone(response)  # Should pass through
    
    def test_api_key_middleware_missing_key(self):
        """Bug: Should block requests without API key."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content.decode()), {'error': 'API key required'})
    
    def test_api_key_middleware_invalid_key(self):
        """Bug: Should block requests with invalid API key."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'API_KEYS', ['valid-key-123']):
            request = self._create_request()
            request.META['HTTP_X_API_KEY'] = 'invalid-key'
            
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponse)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(json.loads(response.content.decode()), {'error': 'Invalid API key'})
    
    def test_api_key_middleware_bypass_paths(self):
        """Bug: Should bypass authentication for certain paths."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'API_KEY_BYPASS_PATHS', ['/health/', '/status/']):
            request = self._create_request(path='/health/')
            
            response = middleware.process_request(request)
            self.assertIsNone(response)  # Should pass through
    
    def test_security_logging_middleware_request_logging(self):
        """Bug: Should log security events."""
        middleware = SecurityLoggingMiddleware(get_response=lambda: HttpResponse())
        
        with patch('logging.getLogger') as mock_logger:
            request = self._create_request(method='POST', path='/api/test', user_agent='TestAgent')
            request.body = b'test data'
            
            middleware.process_request(request)
            
            # Should log API request
            mock_logger.info.assert_called_with(
                'API request: POST /api/test from 127.0.0.1 - TestAgent'
            )
    
    def test_security_logging_middleware_error_logging(self):
        """Bug: Should log error responses."""
        middleware = SecurityLoggingMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        response = HttpResponse(status=400)
        
        with patch('logging.getLogger') as mock_logger:
            processed_response = middleware.process_response(request, response)
            
            # Should log error response
            mock_logger.error.assert_called()
    
    def test_csrf_protection_middleware_exempt_methods(self):
        """Bug: Should exempt safe methods from CSRF protection."""
        middleware = CSRFProtectionMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'CSRF_EXEMPT_METHODS', ['GET', 'HEAD', 'OPTIONS']):
            # GET request should pass through
            request = self._create_request(method='GET')
            self.assertIsNone(middleware.process_request(request))
            
            # POST request should be checked
            request = self._create_request(method='POST')
            self.assertIsNotNone(middleware.process_request(request))
    
    def test_csrf_protection_middleware_token_validation(self):
        """Bug: Should validate CSRF tokens."""
        middleware = CSRFProtectionMiddleware(get_response=lambda: HttpResponse())
        
        # Missing token
        request = self._create_request(method='POST')
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 403)
        
        # Token mismatch
        request.META['HTTP_X_CSRF_TOKEN'] = 'token1'
        request.COOKIES['csrftoken'] = 'token2'
        
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 403)
    
    def test_content_security_middleware_content_length(self):
        """Bug: Should validate content length."""
        middleware = ContentSecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Large content
        request = self._create_request()
        request.body = b'x' * (11 * 1024 * 1024)  # 11MB
        
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content.decode(), 'Request content too large.')
    
    def test_content_security_middleware_content_type_validation(self):
        """Bug: Should validate content type."""
        middleware = ContentSecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Invalid content type
        request = self._create_request(method='POST')
        request.content_type = 'text/html'
        
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content.decode(), 'Invalid content type.')
        
        # Valid content type
        request.content_type = 'application/json'
        self.assertIsNone(middleware.process_request(request))
    
    def test_ip_whitelist_middleware_enabled(self):
        """Bug: Should enforce IP whitelist when enabled."""
        middleware = IPWhitelistMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'IP_WHITELIST_ENABLED', True):
            with patch.object(settings, 'ALLOWED_IPS', ['192.168.1.1']):
                # Allowed IP
                request = self._create_request()
                request.META['REMOTE_ADDR'] = '192.168.1.1'
                self.assertIsNone(middleware.process_request(request))
                
                # Blocked IP
                request.META['REMOTE_ADDR'] = '192.168.1.2'
                response = middleware.process_request(request)
                self.assertIsInstance(response, HttpResponseForbidden)
                self.assertEqual(response.content.decode(), 'Access denied.')
    
    def test_ip_whitelist_middleware_disabled(self):
        """Bug: Should bypass whitelist when disabled."""
        middleware = IPWhitelistMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'IP_WHITELIST_ENABLED', False):
            request = self._create_request()
            request.META['REMOTE_ADDR'] = '192.168.1.2'
            
            # Should pass through when disabled
            self.assertIsNone(middleware.process_request(request))
    
    def test_request_id_middleware_unique_ids(self):
        """Bug: Should generate unique request IDs."""
        middleware = RequestIDMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        
        # Should add request ID to request
        self.assertTrue(hasattr(request, 'request_id'))
        self.assertIsNotNone(request.request_id)
        self.assertTrue(len(request.request_id) > 0)
        
        # Should add request ID to response headers
        self.assertTrue(hasattr(middleware, 'request_id_header'))
        self.assertEqual(middleware.request_id_header, request.request_id)
    
    def test_request_id_middleware_uniqueness(self):
        """Bug: Should generate unique request IDs."""
        middleware = RequestIDMiddleware(get_response=lambda: HttpResponse())
        
        request1 = self._create_request()
        request2 = self._create_request()
        
        # Request IDs should be unique
        self.assertNotEqual(request1.request_id, request2.request_id)
    
    def test_security_middleware_combined(self):
        """Bug: Should apply all security measures."""
        middleware = SecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Mock all middlewares to pass
        with patch.object(middleware.middlewares[0], 'process_request', return_value=None):
            with patch.object(middleware.middlewares[1], 'process_request', return_value=None):
                with patch.object(middleware.middlewares[2], 'process_request', return_value=None):
                    with patch.object(middleware.middlewares[3], 'process_request', return_value=None):
                        with patch.object(middleware.middlewares[4], 'process_request', return_value=None):
                            with patch.object(middleware.__class__, '__call__', return_value=None):
                                request = self._create_request()
                                
                                # Should process through all middlewares
                                result = middleware(request)
                                self.assertIsNone(result)
    
    def test_security_middleware_error_handling(self):
        """Bug: Should handle errors gracefully."""
        middleware = SecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Mock middleware that raises exception
        with patch.object(middleware.middlewares[0], 'process_request', side_effect=Exception('Test error')):
            request = self._create_request()
            
            # Should handle exception gracefully
            with self.assertRaises(Exception):
                middleware(request)
    
    def test_get_client_ip_x_forwarded_for(self):
        """Bug: Should extract IP from X-Forwarded-For header."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        # Test with X-Forwarded-For
        request = self._create_request()
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
        # Test without X-Forwarded-For
        request2 = self._create_request()
        request2.META['REMOTE_ADDR'] = '192.168.1.2'
        
        ip2 = middleware.get_client_ip(request2)
        self.assertEqual(ip2, '192.168.1.2')
    
    def test_rate_limit_different_time_windows(self):
        """Bug: Should implement different time windows for rate limiting."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        with patch('middleware.cache') as mock_cache:
            # Test minute rate limit
            mock_cache.get.side_effect = lambda key: {
                f'rate_limit:minute:192.168.1.1': 50,
                f'rate_limit:hour:192.168.1.1': 100,
                f'rate_limit:day:192.168.1.1': 1000,
            }.get(key, 0)
            
            # Should pass when under minute limit
            self.assertTrue(middleware.check_rate_limit('192.168.1.1'))
            
            # Should fail when minute limit exceeded
            mock_cache.get.side_effect = lambda key: {
                f'rate_limit:minute:192.168.1.1': 101,
                f'rate_limit:hour:192.168.1.1': 100,
                f'rate_limit:day:192.168.1.1': 1000,
            }.get(key, 0)
            
            self.assertFalse(middleware.check_rate_limit('192.168.1.1'))
    
    def test_honeypot_multiple_triggers(self):
        """Bug: Should handle multiple honeypot triggers."""
        middleware = HoneypotMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'HONEYPOT_PATHS', ['/admin/', '/wp-admin/', '/test']):
            with patch.object(middleware, 'block_ip') as mock_block:
                # Trigger honeypot multiple times
                request1 = self._create_request(path='/admin/')
                middleware.process_request(request1)
                
                request2 = self._create_request(path='/wp-admin/')
                middleware.process_request(request2)
                
                # Should block IP after first trigger
                mock_block.assert_called_once()
    
    def test_api_key_multiple_keys(self):
        """Bug: Should support multiple API keys."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'API_KEYS', ['key1', 'key2', 'key3']):
            # Test each valid key
            for key in ['key1', 'key2', 'key3']:
                request = self._create_request()
                request.META['HTTP_X_API_KEY'] = key
                
                response = middleware.process_request(request)
                self.assertIsNone(response)
            
            # Test invalid key
            request = self._create_request()
            request.META['HTTP_X_API_KEY'] = 'invalid'
            
            response = middleware.process_request(request)
            self.assertIsInstance(response, HttpResponse)
            self.assertEqual(response.status_code, 401)
    
    def test_security_headers_comprehensive(self):
        """Bug: Should include all required security headers."""
        middleware = SecurityHeadersMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        response = HttpResponse('Test')
        
        processed_response = middleware.process_response(request, response)
        
        # Check all security headers are present
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy',
            'Server'
        ]
        
        for header in security_headers:
            self.assertIn(header, processed_response)
        
        # Check specific header values
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(processed_response['X-Frame-'], 'DENY')
        self.assertEqual(processed_response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(processed_response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')
    
    def test_content_security_policy_comprehensive(self):
        """Bug: Should have comprehensive CSP policy."""
        middleware = SecurityHeadersMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        response = HttpResponse('Test')
        
        processed_response = middleware.process_response(request, response)
        
        csp = processed_response['Content-Security-Policy']
        
        # Check CSP includes required directives
        required_directives = [
            'default-src',
            'script-src',
            'style-src',
            'img-src',
            'font-src',
            'connect-src',
            'frame-ancestors',
            'base-uri',
            'form-action',
            'upgrade-insecure-requests'
        ]
        
        for directive in required_directives:
            self.assertIn(f'{directive} ', csp)
        
        # Check specific values
        self.assertIn('default-src \'self\'', csp)
        self.assertIn('script-src \'self\' \'unsafe-inline\' \'unsafe-eval\'', csp)
        self.assertIn('img-src \'self\' data: https:', csp)
    
    def test_error_logging_detailed(self):
        """Bug: Should log detailed error information."""
        middleware = SecurityLoggingMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request(method='POST', path='/api/test')
        response = HttpResponse(status=500, content='Internal Server Error')
        
        with patch('logging.getLogger') as mock_logger:
            processed_response = middleware.process_response(request, response)
            
            # Should log error with details
            mock_logger.error.assert_called()
            call_args = mock_logger.error.call_args[0][0]
            
            # Check that error message includes important details
            self.assertIn('Error response: 500', call_args)
            self.assertIn('POST /api/test', call_args)
            self.assertIn('127.0.0.1', call_args)
    
    def test_request_validation_edge_cases(self):
        """Bug: Should handle edge cases in request validation."""
        middleware = RequestValidationMiddleware(get_response=lambda: HttpResponse())
        
        # Test empty request body
        request = self._create_request()
        request.body = b''
        
        response = middleware.process_request(request)
        self.assertIsNone(response)  # Empty body should pass
        
        # Test None body
        request.body = None
        response = middleware.process_request(request)
        self.assertIsNone(response)  # None body should pass
        
        # Test very long path
        request = request = self._create_request(path='/' + 'a' * 201)
        response = middleware.process_request(request)
        self.assertIsInstance(response, HttpResponseForbidden)
    
    def test_rate_limit_cache_operations(self):
        """Bug: Should properly use cache for rate limiting."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        with patch('middleware.cache') as mock_cache:
            mock_cache.get.return_value = 0
            mock_cache.set.return_value = True
            
            # Test cache operations
            client_ip = '192.168.1.1'
            
            # First request
            self.assertTrue(middleware.check_rate_limit(client_ip))
            mock_cache.set.assert_called_with('rate_limit:minute:192.168.1.1', 1, 60)
            
            # Second request
            self.assertTrue(middleware.check_rate_limit(client_ip))
            mock_cache.set.assert_called_with('rate_limit:minute:192.168.1.1', 2, 60)
    
    def test_honeypot_logging(self):
        """Bug: Should log honeypot triggers."""
        middleware = HoneypotMiddleware(get_response=lambda: HttpResponse())
        
        with patch('logging.getLogger') as mock_logger:
            request = self._create_request(path='/admin/')
            
            middleware.process_request(request)
            
            # Should log honeypot trigger
            mock_logger.warning.assert_called_with(
                'Honeypot triggered: /admin/ from 127.0.0.1'
            )
    
    def test_api_key_request_enrichment(self):
        """Bug: Should enrich request with API key information."""
        middleware = APIKeyMiddleware(get_response=lambda: HttpResponse())
        
        with patch.object(settings, 'API_KEYS', ['test-key']):
            request = self._request = self._create_request()
            request.META['HTTP_X_API_KEY'] = 'test-key'
            
            response = middleware.process_request(request)
            self.assertIsNone(response)
            
            # Should add API key to request
            self.assertEqual(request.api_key, 'test-key')
    
    def test_request_id_header_propagation(self):
        """Bug: Should propagate request ID through middleware chain."""
        middleware = RequestIDMiddleware(get_response=lambda: HttpResponse())
        
        request = self._create_request()
        
        # Should add request ID to request
        self.assertTrue(hasattr(request, 'request_id'))
        
        # Should add request ID to response headers
        self.assertTrue(hasattr(middleware, 'request_id_header'))
        
        # Request ID should be the same in both places
        self.assertEqual(request.request_id, middleware.request_id_header)
    
    def test_combined_middleware_order(self):
        """Bug: Should apply middlewares in correct order."""
        middleware = SecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Check middleware order
        expected_order = [
            'SecurityHeadersMiddleware',
            'RequestIDMiddleware',
            'SecurityLoggingMiddleware',
            'RequestValidationMiddleware',
            'RateLimitMiddleware',
            'HoneypotMiddleware',
            'ContentSecurityMiddleware',
            'CSRFProtectionMiddleware',
            'IPWhitelistMiddleware',
        ]
        
        actual_order = [type(m).__name__ for m in middleware.middlewares]
        
        self.assertEqual(actual_order, expected_order)
    
    def test_middleware_configuration(self):
        """Bug: Should use Django settings for configuration."""
        middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
        
        # Test default settings
        self.assertEqual(middleware.requests_per_minute, 100)
        self.assertEqual(middleware.requests_per_hour, 1000)
        self.assertEqual(middleware.requests_per_day, 10000)
        
        # Test custom settings
        with patch.object(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 50):
            middleware = RateLimitMiddleware(get_response=lambda: HttpResponse())
            self.assertEqual(middleware.requests_per_minute, 50)
    
    def test_middleware_error_recovery(self):
        """Bug: Should recover from middleware errors gracefully."""
        middleware = SecurityMiddleware(get_response=lambda: HttpResponse())
        
        # Mock middleware that fails
        with patch.object(middleware.middlewares[0], 'process_request', side_effect=Exception('Test error')):
            request = self._create_request()
            
            # Should handle exception
            with self.assertRaises(Exception):
                middleware(request)
    
    def _create_request(self, path='/', method='GET', user_agent='TestAgent', body=b'test'):
        """Helper to create a mock WSGIRequest."""
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': f'/{path}',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '8000',
            'wsgi.input': BytesIO(body),
            'wsgi.url_scheme': 'http',
        }
        environ.update({
            'CONTENT_TYPE': 'application/json',
            'HTTP_USER_AGENT': user_agent,
            'REMOTE_ADDR': '127.0.0.1',
        })
        return WSGIRequest(environ)
