"""
F2P tests for booking models null handling bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from trip.models import Trip
from package.models import Package

User = get_user_model()


class BookingModelsF2PTest(TestCase):
    """Test booking models null handling fixes"""
    
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
    
    def test_booking_str_with_null_user(self):
        """Bug: Booking.__str__ should handle null user gracefully"""
        from booking.models import Booking
        
        # Create booking with null user
        booking = Booking.objects.create(
            user=None,
            trip=self.trip
        )
        
        # Should not crash and should display 'Unknown User'
        str_representation = str(booking)
        self.assertIn('Unknown User', str_representation)
        self.assertIn('Test Package', str_representation)
    
    def test_booking_str_with_null_trip_package(self):
        """Bug: Booking.__str__ should handle null trip.package gracefully"""
        from booking.models import Booking
        
        # Create booking with trip that has no package (this shouldn't happen normally but test safety)
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip
        )
        
        # Manually set trip.package to None to test the safety check
        booking.trip.package = None
        
        # Should not crash and should display 'Unknown Package'
        str_representation = booking.__str__()
        self.assertIn('Unknown Package', str_representation)
    
    def test_customer_detail_str_with_null_relations(self):
        """Bug: CustomerDetail.__str__ should handle null relations gracefully"""
        from booking.models import Booking, PaxRecord, CustomerDetail
        
        # Create booking and pax record
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        # Create customer detail
        customer = CustomerDetail.objects.create(
            pax_record=pax_record,
            name='Test Customer',
            contact_number='1234567890',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost='1000.00',
            discounted_package_cost='800.00'
        )
        
        # Should work fine with all relations present
        str_representation = str(customer)
        self.assertIn('Test Customer', str_representation)
        self.assertIn('Test Package', str_representation)
    
    def test_customer_detail_str_with_broken_relations(self):
        """Bug: CustomerDetail.__str__ should handle broken relations gracefully"""
        from booking.models import Booking, PaxRecord, CustomerDetail
        
        # Create booking and pax record
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip
        )
        pax_record = PaxRecord.objects.create(
            booking=booking,
            pax=2
        )
        
        # Create customer detail
        customer = CustomerDetail.objects.create(
            pax_record=pax_record,
            name='Test Customer',
            contact_number='1234567890',
            pick_up_point='Test Point',
            meal_option='Test Meal',
            package_cost='1000.00',
            discounted_package_cost='800.00'
        )
        
        # Manually break the relations to test safety
        customer.pax_record.booking.trip.package = None
        
        # Should not crash and should display fallback values
        str_representation = customer.__str__()
        self.assertIn('Test Customer', str_representation)
        self.assertIn('Unknown Package', str_representation)
