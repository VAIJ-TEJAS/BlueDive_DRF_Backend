"""
F2P tests for booking models validation improvements.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from booking.models import Booking, PaxRecord, CustomerDetail, Payment
from trip.models import Trip
from package.models import Package

User = get_user_model()


class BookingModelsF2PTest(TestCase):
    """Test booking models validation improvements"""
    
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
    
    def test_booking_negative_amount_validation(self):
        """Bug: Should reject negative amount"""
        booking = Booking(
            user=self.user,
            trip=self.trip,
            amount=-1000.00,
            balance_amount=500.00
        )
        
        with self.assertRaises(ValidationError) as context:
            booking.full_clean()
        
        self.assertIn('Amount cannot be negative', str(context.exception))
    
    def test_booking_negative_balance_amount_validation(self):
        """Bug: Should reject negative balance amount"""
        booking = Booking(
            user=self.user,
            trip=self.trip,
            amount=1000.00,
            balance_amount=-500.00
        )
        
        with self.assertRaises(ValidationError) as context:
            booking.full_clean()
        
        self.assertIn('Balance amount cannot be negative', str(context.exception))
    
    def test_booking_valid_amounts(self):
        """Bug: Should accept valid amounts"""
        booking = Booking(
            user=self.user,
            trip=self.trip,
            amount=1000.00,
            balance_amount=500.00
        )
        
        # Should not raise validation error
        booking.full_clean()
        self.assertEqual(booking.amount, 1000.00)
        self.assertEqual(booking.balance_amount, 500.00)
    
    def test_pax_record_minimum_validation(self):
        """Bug: Should reject pax count less than 1"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        
        pax_record = PaxRecord(
            booking=booking,
            pax=0  # Invalid - less than 1
        )
        
        with self.assertRaises(ValidationError) as context:
            pax_record.full_clean()
        
        self.assertIn('Number of passengers must be at least 1', str(context.exception))
    
    def test_pax_record_maximum_validation(self):
        """Bug: Should reject pax count more than 50"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        
        pax_record = PaxRecord(
            booking=booking,
            pax=51  # Invalid - more than 50
        )
        
        with self.assertRaises(ValidationError) as context:
            pax_record.full_clean()
        
        self.assertIn('Number of passengers cannot exceed 50', str(context.exception))
    
    def test_pax_record_valid_range(self):
        """Bug: Should accept valid pax count range"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        
        pax_record = PaxRecord(
            booking=booking,
            pax=5  # Valid
        )
        
        # Should not raise validation error
        pax_record.full_clean()
        self.assertEqual(pax_record.pax, 5)
    
    def test_customer_detail_name_validation(self):
        """Bug: Should validate customer name format"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        # Test name too short
        customer = CustomerDetail(
            pax_record=pax_record,
            name='A',  # Too short
            contact_number='9876543210',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Name must be at least 2 characters long', str(context.exception))
    
    def test_customer_detail_name_regex_validation(self):
        """Bug: Should reject name with special characters"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test@User',  # Contains special character
            contact_number='9876543210',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Name can only contain letters and spaces', str(context.exception))
    
    def test_customer_detail_phone_validation(self):
        """Bug: Should validate phone number format"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='1234567890',  # Invalid - doesn't start with 6-9
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Please enter a valid 10-digit mobile number', str(context.exception))
    
    def test_customer_detail_valid_phone(self):
        """Bug: Should accept valid phone numbers"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='9876543210',  # Valid
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        # Should not raise validation error
        customer.full_clean()
        self.assertEqual(customer.contact_number, '9876543210')
    
    def test_customer_detail_negative_cost_validation(self):
        """Bug: Should reject negative package costs"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='9876543210',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost=-1000.00,  # Negative
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Package cost cannot be negative', str(context.exception))
    
    def test_customer_detail_pickup_point_validation(self):
        """Bug: Should validate pickup point minimum length"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='9876543210',
            pick_up_point='AB',  # Too short
            meal_option='Test Meal',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Pick up point must be at least 3 characters long', str(context.exception))
    
    def test_customer_detail_meal_option_validation(self):
        """Bug: Should validate meal option minimum length"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='9876543210',
            pick_up_point='Test Point',
            meal_option='A',  # Too short
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        
        self.assertIn('Meal option must be at least 2 characters long', str(context.exception))
    
    def test_customer_detail_valid_data(self):
        """Bug: Should accept valid customer detail data"""
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=1000.00
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        customer = CustomerDetail(
            pax_record=pax_record,
            name='Test User',
            contact_number='9876543210',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            watersports_option='Scuba Diving',
            package_cost=1000.00,
            discounted_package_cost=800.00
        )
        
        # Should not raise validation error
        customer.full_clean()
        self.assertEqual(customer.name, 'Test User')
        self.assertEqual(customer.contact_number, '9876543210')
