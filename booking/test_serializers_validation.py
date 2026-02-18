"""
F2P tests for booking serializers validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from rest_framework import serializers
from booking.serializers import CustomerDetailSerializer, BookingSerializer
from trip.models import Trip
from package.models import Package
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingSerializersF2PTest(TestCase):
    """Test booking serializers validation fixes"""
    
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
            start_date='2025-02-20',
            end_date='2025-02-22'
        )
    
    def test_customer_detail_serializer_invalid_phone_length(self):
        """Bug: Should reject phone numbers with wrong length"""
        serializer = CustomerDetailSerializer(data={
            'name': 'Test Customer',
            'contact_number': '123456789',  # 9 digits
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Contact number must be exactly 10 digits', str(serializer.errors))
    
    def test_customer_detail_serializer_invalid_phone_prefix(self):
        """Bug: Should reject phone numbers with invalid prefix"""
        serializer = CustomerDetailSerializer(data={
            'name': 'Test Customer',
            'contact_number': '5234567890',  # Starts with 5
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Contact number must start with 6, 7, 8, or 9', str(serializer.errors))
    
    def test_customer_detail_serializer_phone_with_special_chars(self):
        """Bug: Should handle phone numbers with special characters"""
        serializer = CustomerDetailSerializer(data={
            'name': 'Test Customer',
            'contact_number': '+91-9876543210',  # Should be valid after cleaning
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_customer_detail_serializer_empty_name(self):
        """Bug: Should reject empty name"""
        serializer = CustomerDetailSerializer(data={
            'name': '',
            'contact_number': '9876543210',
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'watersports_option': 'Test WaterSport',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Name is required', str(serializer.errors))
    
    def test_customer_detail_serializer_whitespace_only_name(self):
        """Bug: Should reject whitespace-only name"""
        serializer = CustomerDetailSerializer(data={
            'name': '   ',
            'contact_number': '9876543210',
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Name is required', str(serializer.errors))
    
    def test_booking_serializer_negative_amount(self):
        """Bug: Should reject negative amount"""
        serializer = BookingSerializer(data={
            'user': self.user.id,
            'trip': self.trip.id,
            'amount': -1000.00,
            'balance_amount': 500.00
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Amount cannot be negative', str(serializer.errors))
    
    def test_booking_serializer_negative_balance_amount(self):
        """Bug: Should reject negative balance amount"""
        serializer = BookingSerializer(data={
            'user': self.user.id,
            'trip': self.trip.id,
            'amount': 1000.00,
            'balance_amount': -500.00
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Balance amount cannot be negative', str(serializer.errors))
    
    def test_booking_serializer_valid_amounts(self):
        """Bug: Should accept valid amounts"""
        serializer = BookingSerializer(data={
            'user': self.user.id,
            'trip': self.trip.id,
            'amount': 1000.00,
            'balance_amount': 500.00
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_customer_detail_serializer_valid_data(self):
        """Bug: Should accept valid customer detail data"""
        serializer = CustomerDetailSerializer(data={
            'name': 'Test Customer',
            'contact_number': '9876543210',
            'pick_up_point': 'Test Point',
            'meal_option': 'Test Meal',
            'package_cost': '1000.00',
            'discounted_package_cost': '800.00'
        })
        
        self.assertTrue(serializer.is_valid())
