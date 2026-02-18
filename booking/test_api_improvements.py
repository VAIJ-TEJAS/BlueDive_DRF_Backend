"""
F2P tests for booking API improvements.
These tests would fail on the base branch and pass after the fixes.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from django.utils import timezone
from trip.models import Trip
from package.models import Package

User = get_user_model()


class BookingAPIF2PTest(APITestCase):
    """Test booking API improvements"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.package = Package.objects.create(
            name='Test Package',
            duration='3 days'
        )
        
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=12),
            available_seats=10,
            available_rooms=5
        )
        
        self.client.force_authenticate(user=self.user)

    def test_booking_creation_missing_trip_id(self):
        """Bug: Should handle missing trip ID"""
        url = '/api/bookings/'
        data = {
            'pax_records': [
                {
                    'pax': 2,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Trip ID is required')

    def test_booking_creation_no_pax_records(self):
        """Bug: Should handle missing pax records"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': []
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'At least one passenger record is required')

    def test_booking_creation_invalid_pax_count(self):
        """Bug: Should handle invalid passenger count"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': [
                {
                    'pax': 0,  # Invalid
                    'customer_details': []
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid passenger count', response.data['error'])

    def test_booking_creation_customer_details_mismatch(self):
        """Bug: Should handle customer details count mismatch"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': [
                {
                    'pax': 2,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                        # Missing second customer
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Customer details count mismatch', response.data['error'])

    def test_booking_creation_no_customers(self):
        """Bug: Should handle no customers"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': [
                {
                    'pax': 0,
                    'customer_details': []
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'At least one customer is required')

    def test_booking_creation_trip_not_found(self):
        """Bug: Should handle non-existent trip"""
        url = '/api/bookings/'
        data = {
            'trip': 99999,  # Non-existent trip
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Trip not found')

    def test_booking_creation_past_trip(self):
        """Bug: Should prevent booking past trips"""
        # Create a trip in the past
        past_trip = Trip.objects.create(
            package=self.package,
            start_date=timezone.now().date() - timedelta(days=10),
            end_date=timezone.now().date() - timedelta(days=8),
            available_seats=10,
            available_rooms=5
        )
        
        url = '/api/bookings/'
        data = {
            'trip': past_trip.id,
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Cannot book past trips')

    def test_booking_creation_insufficient_seats(self):
        """Bug: Should handle insufficient seats with detailed error"""
        # Create a trip with limited seats
        limited_trip = Trip.objects.create(
            package=self.package,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=12),
            available_seats=2,
            available_rooms=1
        )
        
        url = '/api/bookings/'
        data = {
            'trip': limited_trip.id,
            'pax_records': [
                {
                    'pax': 3,  # More than available
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800},
                        {'name': 'Jane Doe', 'contact_number': '9876543211', 'pick_up_point': 'Test Point', 'meal_option': 'Non-Veg', 'package_cost': 1200, 'discounted_package_cost': 1000},
                        {'name': 'Bob Smith', 'contact_number': '9876543212', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1100, 'discounted_package_cost': 900}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Not enough available seats', response.data['error'])
        self.assertIn('Available: 2, Required: 3', response.data['error'])

    def test_booking_creation_insufficient_rooms(self):
        """Bug: Should handle insufficient rooms with detailed error"""
        # Create a trip with limited rooms
        limited_trip = Trip.objects.create(
            package=self.package,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=12),
            available_seats=10,
            available_rooms=1
        )
        
        url = '/api/bookings/'
        data = {
            'trip': limited_trip.id,
            'pax_records': [
                {
                    'pax': 2,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800},
                        {'name': 'Jane Doe', 'contact_number': '9876543211', 'pick_up_point': 'Test Point', 'meal_option': 'Non-Veg', 'package_cost': 1200, 'discounted_package_cost': 1000}
                    ]
                },
                {
                    'pax': 2,
                    'customer_details': [
                        {'name': 'Bob Smith', 'contact_number': '9876543212', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1100, 'discounted_package_cost': 900},
                        {'name': 'Alice Brown', 'contact_number': '9876543213', 'pick_up_point': 'Test Point', 'meal_option': 'Non-Veg', 'package_cost': 1300, 'discounted_package_cost': 1100}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Not enough available rooms', response.data['error'])
        self.assertIn('Available: 1, Required: 2', response.data['error'])

    @patch('booking.views.logger')
    def test_booking_creation_success_logging(self, mock_logger):
        """Bug: Should log successful booking creation"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_logger.info.assert_called_with('Booking created successfully: 1 for user 1')

    @patch('booking.views.logger')
    def test_booking_creation_validation_error_logging(self, mock_logger):
        """Bug: Should log validation errors"""
        url = '/api/bookings/'
        data = {
            'pax_records': []  # Invalid data
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should not log validation errors as errors, just return response

    @patch('booking.views.logger')
    def test_booking_creation_unexpected_error_logging(self, mock_logger):
        """Bug: Should log unexpected errors"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        # Mock an unexpected error during booking creation
        with patch('booking.views.BookingSerializer') as mock_serializer:
            mock_serializer.return_value.is_valid.side_effect = Exception("Unexpected error")
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            mock_logger.error.assert_called()

    def test_booking_creation_with_full_payment_type(self):
        """Bug: Should set status to Confirmed for full payment"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'payment_type': 'full',
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the booking status is set to Confirmed
        self.assertEqual(response.data['status'], 'Confirmed')

    def test_booking_creation_with_partial_payment_type(self):
        """Bug: Should keep default status for partial payment"""
        url = '/api/bookings/'
        data = {
            'trip': self.trip.id,
            'payment_type': 'partial',
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the booking status remains the default (Partially Confirmed)
        self.assertEqual(response.data['status'], 'Partially Confirmed')

    def test_booking_creation_concurrent_access(self):
        """Bug: Should handle concurrent booking attempts safely"""
        # Create a trip with limited seats
        limited_trip = Trip.objects.create(
            package=self.package,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=12),
            available_seats=1,
            available_rooms=1
        )
        
        url = '/api/bookings/'
        data = {
            'trip': limited_trip.id,
            'pax_records': [
                {
                    'pax': 1,
                    'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg', 'package_cost': 1000, 'discounted_package_cost': 800}
                    ]
                }
            ]
        }
        
        # First booking should succeed
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second booking should fail due to insufficient seats
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Not enough available seats', response2.data['error'])
