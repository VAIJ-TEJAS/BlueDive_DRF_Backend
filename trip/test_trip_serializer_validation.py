"""
F2P tests for trip serializer validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from rest_framework import serializers
from datetime import date, timedelta
from trip.serializers import TripOverviewSerializer
from package.models import Package


class TripSerializerF2PTest(TestCase):
    """Test trip serializer validation fixes"""
    
    def setUp(self):
        self.package = Package.objects.create(
            name='Test Package',
            duration='3 days'
        )
    
    def test_trip_serializer_past_start_date(self):
        """Bug: Should reject past start dates"""
        yesterday = date.today() - timedelta(days=1)
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': yesterday,
            'end_date': date.today() + timedelta(days=2),
            'available_seats': 18,
            'available_rooms': 6
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Start date cannot be in the past', str(serializer.errors))
    
    def test_trip_serializer_past_end_date(self):
        """Bug: Should reject past end dates"""
        yesterday = date.today() - timedelta(days=1)
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=1),
            'end_date': yesterday,
            'available_seats': 18,
            'available_rooms': 6
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('End date cannot be in the past', str(serializer.errors))
    
    def test_trip_serializer_start_after_end(self):
        """Bug: Should reject start date after end date"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=5),
            'end_date': date.today() + timedelta(days=2),
            'available_seats': 18,
            'available_rooms': 6
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Start date cannot be after end date', str(serializer.errors))
    
    def test_trip_serializer_negative_seats(self):
        """Bug: Should reject negative available seats"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'available_seats': -5,
            'available_rooms': 6
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Available seats cannot be negative', str(serializer.errors))
    
    def test_trip_serializer_negative_rooms(self):
        """Bug: Should reject negative available rooms"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'available_seats': 18,
            'available_rooms': -2
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Available rooms cannot be negative', str(serializer.errors))
    
    def test_trip_serializer_zero_seats(self):
        """Bug: Should accept zero available seats"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'available_seats': 0,
            'available_rooms': 6
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_trip_serializer_zero_rooms(self):
        """Bug: Should accept zero available rooms"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'available_seats': 18,
            'available_rooms': 0
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_trip_serializer_today_start_date(self):
        """Bug: Should accept today as start date"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=2),
            'available_seats': 18,
            'available_rooms': 6
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_trip_serializer_valid_data(self):
        """Bug: Should accept valid trip data"""
        serializer = TripOverviewSerializer(data={
            'package': self.package.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'available_seats': 18,
            'available_rooms': 6
        })
        
        self.assertTrue(serializer.is_valid())
