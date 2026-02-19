"""
F2P tests for payment webhook enhancements.
These tests would fail on the base branch and pass after the fixes.
"""

import json
import hmac
import hashlib
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from booking.models import Booking, Trip
from payment.views import PaymentWebhookViewSet


class PaymentWebhookEnhancementsF2PTests(TestCase):
    """Test payment webhook enhancements with comprehensive coverage."""

    def setUp(self):
        """Set up test data and environment."""
        self.factory = RequestFactory()
        self.webhook_secret = "test_webhook_secret_32_chars_long"
        self.viewset = PaymentWebhookViewSet()
        
        # Create test trip
        self.trip = Trip.objects.create(
            name="Test Trip",
            description="Test Description",
            price=1000,
            start_date=timezone.now(),
            end_date=timezone.now()
        )
        
        # Create test booking
        self.booking = Booking.objects.create(
            trip=self.trip,
            customer_name="Test Customer",
            customer_email="test@example.com",
            razorpay_order_id="order_test_123",
            payment_status="pending",
            total_amount=1000
        )

    def test_webhook_signature_verification_success(self):
        """Bug: Should verify webhook signature correctly."""
        # Prepare webhook payload
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Create request with valid signature
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        # Mock environment variable
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('booking_id', response.data)

    def test_webhook_signature_verification_failure(self):
        """Bug: Should reject webhook with invalid signature."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "invalid_signature"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE="invalid_signature"
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid signature', response.data['error'])

    def test_webhook_missing_signature_header(self):
        """Bug: Should reject webhook without signature header."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json'
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Signature missing', response.data['error'])

    def test_webhook_missing_required_fields(self):
        """Bug: Should reject webhook with missing required fields."""
        payload = {
            "razorpay_order_id": "order_test_123"
            # Missing razorpay_payment_id and razorpay_signature
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json'
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required field', response.data['error'])

    def test_webhook_empty_payload(self):
        """Bug: Should reject webhook with empty payload."""
        request = self.factory.post(
            '/api/payment/payment-success/',
            data={},
            content_type='application/json'
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Empty payload', response.data['error'])

    def test_webhook_invalid_method(self):
        """Bug: Should reject non-POST requests."""
        request = self.factory.get('/api/payment/payment-success/')
        
        response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn('Invalid request method', response.data['error'])

    def test_webhook_missing_webhook_secret(self):
        """Bug: Should handle missing webhook secret environment variable."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json'
        )
        
        # Remove webhook secret from environment
        with patch.dict('os.environ', {}, clear=True):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Server configuration error', response.data['error'])

    def test_webhook_short_webhook_secret(self):
        """Bug: Should reject webhook secret that's too short."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json'
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': 'short'}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Server configuration error', response.data['error'])

    def test_webhook_booking_update_success(self):
        """Bug: Should successfully update booking payment status."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        # Verify initial state
        self.assertEqual(self.booking.payment_status, 'pending')
        self.assertIsNone(self.booking.razorpay_payment_id)
        self.assertIsNone(self.booking.paid_at)
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        # Refresh booking from database
        self.booking.refresh_from_db()
        
        # Verify booking was updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertEqual(self.booking.razorpay_payment_id, 'pay_test_123')
        self.assertIsNotNone(self.booking.paid_at)
        self.assertIn('booking_id', response.data)
        self.assertEqual(response.data['booking_id'], self.booking.id)

    def test_webhook_booking_not_found(self):
        """Bug: Should handle case where booking is not found."""
        payload = {
            "razorpay_order_id": "nonexistent_order",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Booking not found', response.data['error'])

    def test_webhook_booking_update_error(self):
        """Bug: Should handle database errors during booking update."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        # Mock booking.save() to raise an exception
        with patch.object(Booking.objects, 'filter') as mock_filter:
            mock_booking = Mock()
            mock_booking.save.side_effect = Exception("Database error")
            mock_filter.return_value.first.return_value = mock_booking
            
            with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
                response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Failed to update booking', response.data['error'])

    def test_webhook_signature_verification_exception(self):
        """Bug: Should handle exceptions during signature verification."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE="some_signature"
        )
        
        # Mock hmac.new to raise an exception
        with patch('hmac.new', side_effect=Exception("Crypto error")):
            with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
                response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Signature verification failed', response.data['error'])

    def test_webhook_json_serialization_error(self):
        """Bug: Should handle JSON serialization errors."""
        # Create payload with non-serializable data
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test",
            "invalid_data": {"key": object()}  # Non-serializable object
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE="some_signature"
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Signature verification failed', response.data['error'])

    def test_webhook_logging_functionality(self):
        """Bug: Should properly log webhook processing events."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        with patch('payment.views.logger') as mock_logger:
            with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
                response = self.viewset.payment_successful_webhook(request)
        
        # Verify logging calls
        mock_logger.info.assert_called()
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        
        # Should log webhook receipt and processing
        self.assertTrue(any('webhook received' in call.lower() for call in log_calls))
        self.assertTrue(any('processing payment webhook' in call.lower() for call in log_calls))

    def test_webhook_response_format(self):
        """Bug: Should return properly formatted response on success."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        # Verify response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertIn('booking_id', response.data)
        self.assertIn('payment_id', response.data)
        
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Payment processed successfully')
        self.assertEqual(response.data['payment_id'], 'pay_test_123')

    def test_webhook_concurrent_processing(self):
        """Bug: Should handle concurrent webhook processing safely."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Create multiple concurrent requests
        requests = []
        for i in range(5):
            request = self.factory.post(
                '/api/payment/payment-success/',
                data=payload,
                content_type='application/json',
                HTTP_X_RAZORPAY_SIGNATURE=expected_signature
            )
            requests.append(request)
        
        responses = []
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            for request in requests:
                response = self.viewset.payment_successful_webhook(request)
                responses.append(response)
        
        # All requests should succeed
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Booking should be updated only once
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'paid')

    def test_webhook_performance_with_large_payload(self):
        """Bug: Should handle large webhook payloads efficiently."""
        # Create large payload
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test",
            "metadata": {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        # Measure processing time
        import time
        start_time = time.time()
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process quickly even with large payload
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(processing_time, 1.0)  # Should complete within 1 second

    def test_webhook_security_headers_filtering(self):
        """Bug: Should filter sensitive headers from debug logs."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE="test_signature",
            HTTP_AUTHORIZATION="Bearer secret_token",
            HTTP_X_SENSITIVE_HEADER="sensitive_value",
            HTTP_NORMAL_HEADER="normal_value"
        )
        
        with patch('payment.views.logger') as mock_logger:
            with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
                response = self.viewset.payment_successful_webhook(request)
        
        # Check that sensitive headers are filtered from logs
        debug_calls = [call.args[1] for call in mock_logger.debug.call_args_list if 'headers' in call.args[0]]
        if debug_calls:
            logged_headers = debug_calls[0]
            self.assertNotIn('authorization', logged_headers)
            self.assertNotIn('x-razorpay-signature', logged_headers)
            self.assertIn('normal_header', logged_headers)

    def test_webhook_edge_case_empty_signature(self):
        """Bug: Should handle empty signature header."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123"
        }
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=""  # Empty signature
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Signature missing', response.data['error'])

    def test_webhook_edge_case_unicode_payload(self):
        """Bug: Should handle unicode characters in payload."""
        payload = {
            "razorpay_order_id": "order_test_123",
            "razorpay_payment_id": "pay_test_123",
            "razorpay_signature": "signature_test",
            "customer_name": "测试客户",  # Unicode characters
            "description": "🎉 Payment successful"  # Emoji
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request = self.factory.post(
            '/api/payment/payment-success/',
            data=payload,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=expected_signature
        )
        
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.viewset.payment_successful_webhook(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentWebhookIntegrationTests(TestCase):
    """Integration tests for payment webhook."""

    def setUp(self):
        """Set up integration test environment."""
        self.client = APIClient()
        self.webhook_secret = "integration_test_webhook_secret_32_chars"
        
        # Create test trip
        self.trip = Trip.objects.create(
            name="Integration Test Trip",
            description="Test Description",
            price=2000,
            start_date=timezone.now(),
            end_date=timezone.now()
        )
        
        # Create test booking
        self.booking = Booking.objects.create(
            trip=self.trip,
            customer_name="Integration Test Customer",
            customer_email="integration@test.com",
            razorpay_order_id="integration_order_123",
            payment_status="pending",
            total_amount=2000
        )

    def test_webhook_end_to_end_flow(self):
        """Bug: Should handle complete webhook flow end-to-end."""
        payload = {
            "razorpay_order_id": "integration_order_123",
            "razorpay_payment_id": "integration_pay_123",
            "razorpay_signature": "integration_signature"
        }
        
        # Generate valid signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Make API call
        with patch.dict('os.environ', {'WEBHOOK_SECRET': self.webhook_secret}):
            response = self.client.post(
                '/api/payment/payment-success/',
                data=payload,
                format='json',
                HTTP_X_RAZORPAY_SIGNATURE=expected_signature
            )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify booking was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertEqual(self.booking.razorpay_payment_id, 'integration_pay_123')
        self.assertIsNotNone(self.booking.paid_at)
