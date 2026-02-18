"""
F2P tests for payment webhook improvements.
These tests would fail on the base branch and pass after the fixes.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
import json
import hmac
import hashlib
import os


class PaymentWebhookF2PTest(APITestCase):
    """Test payment webhook security improvements"""

    def setUp(self):
        self.webhook_url = '/api/payment-webhook/payment-success/'
        self.webhook_secret = 'test_webhook_secret_key_for_testing'
        self.valid_payload = {
            'razorpay_order_id': 'order_123',
            'razorpay_payment_id': 'pay_123',
            'razorpay_signature': 'test_signature'
        }

    def test_webhook_missing_signature_header(self):
        """Bug: Should handle missing signature header"""
        data = self.valid_payload.copy()
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Signature missing')

    def test_webhook_empty_payload(self):
        """Bug: Should handle empty payload"""
        data = {}
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Empty payload')

    def test_webhook_missing_required_fields(self):
        """Bug: Should validate required fields"""
        # Test missing razorpay_order_id
        data = {
            'razorpay_payment_id': 'pay_123',
            'razorpay_signature': 'test_signature'
        }
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing required field: razorpay_order_id', response.data['error'])

    def test_webhook_missing_payment_id(self):
        """Bug: Should validate required fields"""
        data = {
            'razorpay_order_id': 'order_123',
            'razorpay_signature': 'test_signature'
        }
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing required field: razorpay_payment_id', response.data['error'])

    def test_webhook_missing_signature_field(self):
        """Bug: Should validate required fields"""
        data = {
            'razorpay_order_id': 'order_123',
            'razorpay_payment_id': 'pay_123'
        }
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing required field: razorpay_signature', response.data['error'])

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_invalid_signature(self, mock_env):
        """Bug: Should reject invalid signature"""
        data = self.valid_payload.copy()
        
        # Create an invalid signature
        invalid_signature = 'invalid_signature_value'
        headers = {'HTTP_X-Razorpay-Signature': invalid_signature}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid signature')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_valid_signature(self, mock_env):
        """Bug: Should accept valid signature"""
        data = self.valid_payload.copy()
        
        # Create a valid signature
        payload = json.dumps(data, separators=(',', ':'))
        valid_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {'HTTP_X-Razorpay-Signature': valid_signature}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'received')
        self.assertIn('message', response.data)

    @patch.dict(os.environ, {'WEBHOOK_SECRET': ''})
    def test_webhook_missing_secret_config(self, mock_env):
        """Bug: Should handle missing webhook secret"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Server configuration error')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'short'})
    def test_webhook_short_secret_config(self, mock_env):
        """Bug: Should reject short webhook secret"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Server configuration error')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_signature_verification_error(self, mock_env):
        """Bug: Should handle signature verification errors"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        # Mock hmac.compare_digest to raise an exception
        with patch('payment.views.hmac.compare_digest', side_effect=Exception('Verification error')):
            response = self.client.post(self.webhook_url, data, format='json', **headers)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'Signature verification failed')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_payload_serialization_error(self, mock_env):
        """Bug: Should handle payload serialization errors"""
        # Create data that can't be serialized to JSON
        data = {
            'razorpay_order_id': 'order_123',
            'razorpay_payment_id': 'pay_123',
            'razorpay_signature': 'test_signature',
            'invalid_field': object()  # This will cause serialization error
        }
        
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        # Should handle the serialization error gracefully
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    @patch('payment.views.logger')
    def test_webhook_logging_without_sensitive_data(self, mock_logger, mock_env):
        """Bug: Should log without exposing sensitive data"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        # Mock request.META
        with patch('payment.views.PaymentWebhookViewSet') as mock_viewset:
            mock_viewset.return_value.request.META = {'REMOTE_ADDR': '127.0.0.1'}
            
            response = self.client.post(self.webhook_url, data, format='json', **headers)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Check that logger.info was called with order ID but not signature
            mock_logger.info.assert_called_with('Processing payment webhook for order: order_123')
            
            # Check that debug logging excludes sensitive headers
            mock_logger.debug.assert_called()
            debug_call_args = mock_logger.debug.call_args[0][0]
            self.assertNotIn('x-razorpay-signature', str(debug_call_args).lower())

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    @patch('payment.views.logger')
    def test_webhook_signature_missing_warning(self, mock_logger, mock_env):
        """Bug: Should log warning when signature is missing"""
        data = self.valid_payload.copy()
        
        response = self.client.post(self.webhook_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_logger.warning.assert_called_with('Webhook signature missing from headers')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    @patch('payment.views.logger')
    def test_webhook_invalid_signature_warning(self, mock_logger, mock_env):
        """Bug: Should log warning when signature is invalid"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'invalid_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_logger.warning.assert_called_with('Webhook signature verification failed')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_successful_processing_logging(self, mock_env):
        """Bug: Should log successful webhook processing"""
        data = self.valid_payload.copy()
        
        # Create valid signature
        payload = json.dumps(data, separators=(',', ':'))
        valid_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {'HTTP_X-Razorpay-Signature': valid_signature}
        
        with patch('payment.views.logger') as mock_logger:
            response = self.client.post(self.webhook_url, data, format='json', **headers)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_logger.info.assert_called_with('Processing payment webhook for order: order_123')

    def test_webhook_invalid_request_method(self):
        """Bug: Should reject non-POST requests"""
        data = self.valid_payload.copy()
        
        # Try GET request
        response = self.client.get(self.webhook_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid request method')

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_secret_key_for_testing'})
    def test_webhook_unexpected_error_handling(self, mock_env):
        """Bug: Should handle unexpected errors gracefully"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        # Mock an unexpected error during processing
        with patch('payment.views.logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Unexpected processing error")
            
            response = self.client.post(self.webhook_url, data, format='json', **headers)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'Internal server error')
            mock_logger.error.assert_called()

    def test_webhook_timing_attack_prevention(self):
        """Bug: Should use secure signature comparison"""
        data = self.valid_payload.copy()
        
        # Create valid signature
        payload = json.dumps(data, separators=(',', ':'))
        valid_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {'HTTP_X-Razorpay-Signature': valid_signature}
        
        # Should use hmac.compare_digest for secure comparison
        with patch('payment.views.hmac.compare_digest') as mock_compare:
            mock_compare.return_value = True
            
            response = self.client.post(self.webhook_url, data, format='json', **headers)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_compare.assert_called_once()

    def test_webhook_payload_structure_validation(self):
        """Bug: Should validate payload structure before processing"""
        # Test with non-dict payload
        data = 'invalid_payload_string'
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        # Should handle the invalid payload gracefully
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])

    @patch.dict(os.environ, {'WEBHOOK_SECRET': 'test_webhook_key'})
    def test_webhook_minimum_secret_length_enforcement(self, mock_env):
        """Bug: Should enforce minimum secret length"""
        data = self.valid_payload.copy()
        headers = {'HTTP_X-Razorpay-Signature': 'test_signature'}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Server configuration error')

    def test_webhook_response_format(self):
        """Bug: Should return consistent response format"""
        data = self.valid_payload.copy()
        
        # Create valid signature
        payload = json.dumps(data, separators=(',', ':'))
        valid_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {'HTTP_X-Razorpay-Signature': valid_signature}
        
        response = self.client.post(self.webhook_url, data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['status'], 'received')
        self.assertEqual(response.data['message'], 'Payment webhook processed successfully')
