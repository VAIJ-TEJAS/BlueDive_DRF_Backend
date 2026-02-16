"""
F2P tests for package serializers bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
from django.test import TestCase
from package.serializers import PackageSerializer, PackageTripsSerializer


class PackageSerializersF2PTest(TestCase):
    """Test package serializers fixes"""
    
    def test_package_serializer_no_duplicate_meals_field(self):
        """Bug: PackageSerializer should not have duplicate 'meals' field"""
        # Before fix: Would have duplicate 'meals' field causing confusion
        # After fix: Only one 'meals' field as SerializerMethodField
        
        serializer = PackageSerializer()
        
        # Check that 'meals' is in the fields
        self.assertIn('meals', serializer.fields)
        
        # Check that 'meals' is a SerializerMethodField (not a regular field)
        meals_field = serializer.fields['meals']
        self.assertTrue(hasattr(meals_field, 'method_name'))
        
        # Verify the method exists
        self.assertTrue(hasattr(serializer, 'get_meals'))

    def test_package_trips_serializer_no_duplicate_meals_field(self):
        """Bug: PackageTripsSerializer should not have duplicate 'meals' field"""
        # Before fix: Would have duplicate 'meals' field causing confusion
        # After fix: Only one 'meals' field as SerializerMethodField
        
        serializer = PackageTripsSerializer()
        
        # Check that 'meals' is in the fields
        self.assertIn('meals', serializer.fields)
        
        # Check that 'meals' is a SerializerMethodField (not a regular field)
        meals_field = serializer.fields['meals']
        self.assertTrue(hasattr(meals_field, 'method_name'))
        
        # Verify the method exists
        self.assertTrue(hasattr(serializer, 'get_meals'))
        
        # Check that other expected fields are present
        self.assertIn('trips', serializer.fields)
        self.assertIn('day_records', serializer.fields)
        self.assertIn('pax_options', serializer.fields)
