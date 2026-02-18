"""
F2P tests for trip model validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from trip.models import Trip
from package.models import Package


class TripValidationF2PTest(TestCase):
    """Test trip model validation fixes"""
    
    def setUp(self):
        self.package = Package.objects.create(
            name='Test Package',
            duration='3 days'
        )
    
    def test_trip_clean_with_start_after_end(self):
        """Bug: Trip.clean() should reject start date after end date"""
        trip = Trip(
            package=self.package,
            start_date=date(2025, 2, 25),
            end_date=date(2025, 2, 20)
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            trip.clean()
        
        self.assertIn('Start date cannot be after end date', str(cm.exception))
    
    def test_trip_clean_with_past_start_date(self):
        """Bug: Trip.clean() should reject past start dates"""
        yesterday = date.today() - timedelta(days=1)
        trip = Trip(
            package=self.package,
            start_date=yesterday,
            end_date=date.today() + timedelta(days=2)
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            trip.clean()
        
        self.assertIn('Start date cannot be in the past', str(cm.exception))
    
    def test_trip_clean_with_negative_seats(self):
        """Bug: Trip.clean() should reject negative seats"""
        trip = Trip(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            available_seats=-5
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            trip.clean()
        
        self.assertIn('Available seats cannot be negative', str(cm.exception))
    
    def test_trip_clean_with_negative_rooms(self):
        """Bug: Trip.clean() should reject negative rooms"""
        trip = Trip(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            available_rooms=-2
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            trip.clean()
        
        self.assertIn('Available rooms cannot be negative', str(cm.exception))
    
    def test_trip_clean_with_valid_data(self):
        """Bug: Trip.clean() should pass with valid data"""
        trip = Trip(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            available_seats=18,
            available_rooms=6
        )
        
        # Should not raise ValidationError
        try:
            trip.clean()
        except ValidationError:
            self.fail("Trip.clean() raised ValidationError unexpectedly!")
    
    def test_trip_clean_with_null_dates(self):
        """Bug: Trip.clean() should handle null dates gracefully"""
        trip = Trip(
            package=self.package,
            start_date=None,
            end_date=None
        )
        
        # Should not raise ValidationError for null dates
        try:
            trip.clean()
        except ValidationError:
            self.fail("Trip.clean() raised ValidationError unexpectedly for null dates!")
