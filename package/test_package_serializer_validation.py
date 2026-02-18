"""
F2P tests for package serializer validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from rest_framework import serializers
from package.serializers import PackageSerializer


class PackageSerializerF2PTest(TestCase):
    """Test package serializer validation fixes"""
    
    def test_package_serializer_empty_name(self):
        """Bug: Should reject empty package name"""
        serializer = PackageSerializer(data={
            'name': '',
            'duration': '3 days',
            'display_price': 1000
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Package name is required', str(serializer.errors))
    
    def test_package_serializer_whitespace_only_name(self):
        """Bug: Should reject whitespace-only name"""
        serializer = PackageSerializer(data={
            'name': '   ',
            'duration': '3 days',
            'display_price': 1000
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Package name is required', str(serializer.errors))
    
    def test_package_serializer_empty_duration(self):
        """Bug: Should reject empty duration"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '',
            'display_price': 1000
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Package duration is required', str(serializer.errors))
    
    def test_package_serializer_whitespace_only_duration(self):
        """Bug: Should reject whitespace-only duration"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '   ',
            'display_price': 1000
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Package duration is required', str(serializer.errors))
    
    def test_package_serializer_negative_price(self):
        """Bug: Should reject negative display price"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': -1000
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Display price cannot be negative', str(serializer.errors))
    
    def test_package_serializer_negative_discount(self):
        """Bug: Should reject negative discount percentage"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': -10
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Discount percentage must be between 0 and 100', str(serializer.errors))
    
    def test_package_serializer_discount_over_100(self):
        """Bug: Should reject discount percentage over 100"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': 150
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Discount percentage must be between 0 and 100', str(serializer.errors))
    
    def test_package_serializer_valid_discount_100(self):
        """Bug: Should accept discount percentage of 100"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': 100
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_package_serializer_valid_discount_0(self):
        """Bug: Should accept discount percentage of 0"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': 0
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_package_serializer_null_price(self):
        """Bug: Should accept null display price"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': None
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_package_serializer_null_discount(self):
        """Bug: Should accept null discount percentage"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': None
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_package_serializer_valid_data(self):
        """Bug: Should accept valid package data"""
        serializer = PackageSerializer(data={
            'name': 'Test Package',
            'duration': '3 days',
            'display_price': 1000,
            'display_discount_percentage': 10
        })
        
        self.assertTrue(serializer.is_valid())
