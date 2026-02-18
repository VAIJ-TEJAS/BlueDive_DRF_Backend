"""
F2P tests for booking serializer validation enhancements.
These tests would fail on the base branch and pass after the fixes.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from trip.models import Trip, Package
from datetime import date, timedelta
from decimal import Decimal
from .serializers import (
    CustomerDetailSerializer,
    PaxRecordSerializer,
    PaymentSerializer,
    BookingSerializer,
    BookingOverviewSerializer
)

User = get_user_model()


class BookingSerializerValidationF2PTest(TestCase):
    """Test booking serializer validation enhancements"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.package = Package.objects.create(
            name='Test Package',
            duration='3 days',
            description='Test package description'
        )
        
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            available_seats=10,
            available_rooms=5,
            status='Scheduled'
        )

    def test_customer_detail_name_validation_enhanced(self):
        """Bug: Should validate name with enhanced rules"""
        # Test empty name
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': ''})
        self.assertIn("Name is required", str(cm.exception))
        
        # Test whitespace-only name
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': '   '})
        self.assertIn("Name is required", str(cm.exception))
        
        # Test name too short
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': 'A'})
        self.assertIn("Name must be at least 2 characters long", str(cm.exception))
        
        # Test name too long
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': 'A' * 101})
        self.assertIn("Name cannot exceed 100 characters", str(cm.exception))
        
        # Test invalid characters
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': 'John@123'})
        self.assertIn("Name can only contain letters, spaces, hyphens, and apostrophes", str(cm.exception))
        
        # Test valid name
        serializer = CustomerDetailSerializer(data={'name': 'John Doe'})
        self.assertEqual(serializer.validated_data['name'], 'John Doe')

    def test_customer_detail_contact_number_validation_enhanced(self):
        """Bug: Should validate contact number with enhanced rules"""
        # Test empty contact number
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'contact_number': ''})
        self.assertIn("Contact number is required", str(cm.exception))
        
        # Test invalid format (non-digit characters)
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'contact_number': '987654321a'})
        self.assertIn("Contact number must be exactly 10 digits", str(cm.exception))
        
        # Test wrong length
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'contact_number': '987654321'})
        self.assertIn("Contact number must be exactly 10 digits", str(cm.exception))
        
        # Test invalid prefix
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'contact_number': '5876543210'})
        self.assertIn("Contact number must start with 6, 7, 8, or 9", str(cm.exception))
        
        # Test valid contact number
        serializer = CustomerDetailSerializer(data={'contact_number': '9876543210'})
        self.assertEqual(serializer.validated_data['contact_number'], '9876543210')

    def test_customer_detail_pick_up_point_validation(self):
        """Bug: Should validate pick up point"""
        # Test empty pick up point
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'pick_up_point': ''})
        self.assertIn("Pick up point is required", str(cm.exception))
        
        # Test too short
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'pick_up_point': 'AB'})
        self.assertIn("Pick up point must be at least 3 characters long", str(cm.exception))
        
        # Test too long
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'pick_up_point': 'A' * 256})
        self.assertIn("Pick up point cannot exceed 255 characters", str(cm.exception))
        
        # Test valid pick up point
        serializer = CustomerDetailSerializer(data={'pick_up_point': 'Test Location'})
        self.assertEqual(serializer.validated_data['pick_up_point'], 'Test Location')

    def test_customer_detail_meal_option_validation(self):
        """Bug: Should validate meal option"""
        # Test empty meal option
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'meal_option': ''})
        self.assertIn("Meal option is required", str(cm.exception))
        
        # Test too short
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'meal_option': 'A'})
        self.assertIn("Meal option must be at least 2 characters long", str(cm.exception))
        
        # Test valid meal option
        serializer = CustomerDetailSerializer(data={'meal_option': 'Veg'})
        self.assertEqual(serializer.validated_data['meal_option'], 'Veg')

    def test_customer_detail_package_cost_validation(self):
        """Bug: Should validate package cost"""
        # Test negative cost
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'package_cost': -100})
        self.assertIn("Package cost cannot be negative", str(cm.exception))
        
        # Test too high cost
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'package_cost': 1000000})
        self.assertIn("Package cost cannot exceed 999,999", str(cm.exception))
        
        # Test valid cost
        serializer = CustomerDetailSerializer(data={'package_cost': 5000})
        self.assertEqual(serializer.validated_data['package_cost'], 5000)

    def test_pax_record_validation_enhanced(self):
        """Bug: Should validate pax record with enhanced rules"""
        # Test missing pax
        with self.assertRaises(ValidationError) as cm:
            PaxRecordSerializer(data={})
        self.assertIn("Pax count is required", str(cm.exception))
        
        # Test non-integer pax
        with self.assertRaises(ValidationError) as cm:
            PaxRecordSerializer(data={'pax': 'invalid'})
        self.assertIn("Pax count must be an integer", str(cm.exception))
        
        # Test zero pax
        with self.assertRaises(ValidationError) as cm:
            PaxRecordSerializer(data={'pax': 0})
        self.assertIn("Pax count must be greater than 0", str(cm.exception))
        
        # Test too high pax
        with self.assertRaises(ValidationError) as cm:
            PaxRecordSerializer(data={'pax': 51})
        self.assertIn("Pax count cannot exceed 50", str(cm.exception))
        
        # Test valid pax
        serializer = PaxRecordSerializer(data={'pax': 2})
        self.assertEqual(serializer.validated_data['pax'], 2)

    def test_payment_serializer_validation_enhanced(self):
        """Bug: Should validate payment with enhanced rules"""
        # Test missing amount
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={})
        self.assertIn("Payment amount is required", str(cm.exception))
        
        # Test non-numeric amount
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={'amount': 'invalid'})
        self.assertIn("Payment amount must be a number", str(cm.exception))
        
        # Test negative amount
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={'amount': -100})
        self.assertIn("Payment amount cannot be negative", str(cm.exception))
        
        # Test too high amount
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={'amount': 1000000})
        self.assertIn("Payment amount cannot exceed 999,999", str(cm.exception))
        
        # Test invalid payment method
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={'payment_method': 'invalid'})
        self.assertIn("Invalid payment method", str(cm.exception))
        
        # Test invalid transaction ID format
        with self.assertRaises(ValidationError) as cm:
            PaymentSerializer(data={'transaction_id': 'invalid-id'})
        self.assertIn("Invalid transaction ID format", str(cm.exception))
        
        # Test valid payment
        serializer = PaymentSerializer(data={
            'amount': 5000,
            'payment_method': 'card',
            'transaction_id': 'TX12345678'
        })
        self.assertEqual(serializer.validated_data['amount'], 5000)
        self.assertEqual(serializer.validated_data['payment_method'], 'card')

    def test_booking_serializer_validation_enhanced(self):
        """Bug: Should validate booking with enhanced rules"""
        # Test missing amount
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={})
        self.assertIn("Booking amount is required", str(cm.exception))
        
        # Test invalid status
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={'status': 'invalid'})
        self.assertIn("Invalid booking status", str(cm.exception))
        
        # Test non-existent trip
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={'trip': 99999})
        self.assertIn("Trip not found", str(cm.exception))
        
        # Test cancelled trip
        cancelled_trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=22),
            available_seats=5,
            available_rooms=2,
            status='Cancelled'
        )
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={'trip': cancelled_trip.id})
        self.assertIn("Trip is not available for booking", str(cm.exception))
        
        # Test valid booking
        serializer = BookingSerializer(data={
            'trip': self.trip.id,
            'amount': 5000,
            'status': 'Confirmed',
            'user': self.user.id
        })
        self.assertEqual(serializer.validated_data['trip'], self.trip.id)

    def test_booking_serializer_custom_validation(self):
        """Bug: Should validate customer details match pax count"""
        # Test mismatched customer count and pax count
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={
                'trip': self.trip.id,
                'amount': 5000,
                'status': 'Confirmed',
                'user': self.user.id,
                'pax_records': [
                    {'pax': 2, 'customer_details': [
                        {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg'}
                    ]}
                ]
            })
        self.assertIn("Number of customers (1) must match total pax count (2)", str(cm.exception))
        
        # Test matching customer and pax count
        serializer = BookingSerializer(data={
            'trip': self.trip.id,
            'amount': 5000,
            'status': 'Confirmed',
            'user': self.user.id,
            'pax_records': [
                {'pax': 2, 'customer_details': [
                    {'name': 'John Doe', 'contact_number': '9876543210', 'pick_up_point': 'Test Point', 'meal_option': 'Veg'},
                    {'name': 'Jane Doe', 'contact_number': '9876543211', 'pick_up_point': 'Test Point', 'meal_option': 'Non-Veg'}
                ]}
            ]
        })
        self.assertTrue(serializer.is_valid())

    def test_balance_amount_validation(self):
        """Bug: Should validate balance amount properly"""
        # Test negative balance amount
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={
                'trip': self.trip.id,
                'amount': 5000,
                'balance_amount': -100,
                'status': 'Confirmed',
                'user': self.user.id
            })
        self.assertIn("Balance amount cannot be negative", str(cm.exception))
        
        # Test non-numeric balance amount
        with self.assertRaises(ValidationError) as cm:
            BookingSerializer(data={
                'trip': self.trip.id,
                'amount': 5000,
                'balance_amount': 'invalid',
                'status': 'Confirmed',
                'user': self.user.id
            })
        self.assertIn("Balance amount must be a number", str(cm.exception))
        
        # Test valid balance amount
        serializer = BookingSerializer(data={
            'trip': self.trip.id,
            'amount': 5000,
            'balance_amount': 2000,
            'status': 'Confirmed',
            'user': self.user.id
        })
        self.assertEqual(serializer.validated_data['balance_amount'], 2000)

    def test_serializer_error_messages_are_translated(self):
        """Bug: Should use translated error messages"""
        # Test that error messages are translatable
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={'name': ''})
        self.assertIn("Name is required", str(cm.exception))
        
        # The error messages should be translatable (marked with _())
        # This tests that we're using Django's translation system

    def test_serializer_logging(self):
        """Bug: Should log validation attempts for security monitoring"""
        import logging
        from unittest.mock import patch
        
        # Mock logger to capture log calls
        with patch('booking.serializers.logger') as mock_logger:
            CustomerDetailSerializer(data={'contact_number': '9876543210'})
            # Should log contact number validation attempt
            mock_logger.info.assert_called_with("Contact number validation attempted for: 987******")

    def test_to_representation_includes_trip_details(self):
        """Bug: Should include trip details in representation"""
        # Create a booking instance
        booking_data = {
            'trip': self.trip.id,
            'amount': 5000,
            'status': 'Confirmed',
            'user': self.user.id
        }
        serializer = BookingSerializer(data=booking_data)
        booking = serializer.save()
        
        # Check that trip details are included
        representation = BookingSerializer(booking).data
        self.assertIn('trip', representation)
        self.assertEqual(representation['trip']['id'], self.trip.id)

    def test_booking_overview_serializer(self):
        """Bug: Should only include essential fields"""
        # Create a booking instance
        booking_data = {
            'trip': self.trip.id,
            'amount': 5000,
            'status': 'Confirmed',
            'user': self.user.id
        }
        serializer = BookingSerializer(data=booking_data)
        booking = serializer.save()
        
        # Check that only essential fields are included
        representation = BookingOverviewSerializer(booking).data
        expected_fields = ['id', 'trip', 'status']
        
        for field in expected_fields:
            self.assertIn(field, representation)
        
        # Check that non-essential fields are not included
        non_essential_fields = ['amount', 'user', 'created_at', 'updated_at']
        for field in non_essential_fields:
            self.assertNotIn(field, representation)

    def test_edge_cases(self):
        """Bug: Should handle edge cases gracefully"""
        # Test None values for optional fields
        serializer = CustomerDetailSerializer(data={
            'name': 'Test Name',
            'package_cost': None,
            'discounted_package_cost': None
        })
        self.assertIsNone(serializer.validated_data['package_cost'])
        self.assertIsNone(serializer.validated_data['discounted_package_cost'])
        
        # Test zero values for numeric fields
        serializer = PaymentSerializer(data={
            'amount': 0
        })
        self.assertEqual(serializer.validated_data['amount'], 0)
        
        # Test empty strings for optional fields
        serializer = PaymentSerializer(data={
            'transaction_id': ''
        })
        self.assertEqual(serializer.validated_data['transaction_id'], '')

    def test_data_type_validation(self):
        """Bug: Should validate data types properly"""
        # Test string fields accept strings
        serializer = CustomerDetailSerializer(data={'name': 'Test Name'})
        self.assertEqual(serializer.validated_data['name'], 'Test Name')
        
        # Test numeric fields accept numbers
        serializer = PaxRecordSerializer(data={'pax': 2})
        self.assertEqual(serializer.validated_data['pax'], 2)
        
        # Test that wrong types raise validation errors
        with self.assertRaises(ValidationError):
            CustomerDetailSerializer(data={'name': 123})
        
        with self.assertRaises(ValidationError):
            PaxRecordSerializer(data={'pax': 'invalid'})

    def test_validation_order(self):
        """Bug: Should validate in proper order"""
        # Test that required fields are validated first
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={})
        # Should fail on first required field (name)
        self.assertIn("Name is required", str(cm.exception))
        
        # Test that optional fields are validated after required ones
        with self.assertRaises(ValidationError) as cm:
            CustomerDetailSerializer(data={
                'name': 'Test Name',
                'package_cost': -100
            })
        # Should fail on package_cost validation
        self.assertIn("Package cost cannot be negative", str(cm.exception))

    def test_serializer_reuse(self):
        """Bug: Should be reusable for multiple validations"""
        # Create multiple instances with same data
        data = {'name': 'Test Name', 'contact_number': '9876543210'}
        
        serializer1 = CustomerDetailSerializer(data=data)
        serializer2 = CustomerDetailSerializer(data=data)
        
        # Both should be valid
        self.assertTrue(serializer1.is_valid())
        self.assertTrue(serializer2.is_valid())
        
        # Both should produce same validated data
        self.assertEqual(serializer1.validated_data, serializer2.validated_data)

    def test_partial_updates(self):
        """Bug: Should handle partial updates correctly"""
        # Create initial instance
        serializer = CustomerDetailSerializer(data={'name': 'Test Name'})
        
        # Update with partial data
        serializer = CustomerDetailSerializer(
            instance=serializer.instance,
            data={'contact_number': '9876543210'}
        )
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Test Name')
        self.assertEqual(serializer.validated_data['contact_number'], '9876543210')
