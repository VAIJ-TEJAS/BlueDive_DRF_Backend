"""
F2P tests for package model validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from package.models import Package


class PackageValidationF2PTest(TestCase):
    """Test package model validation fixes"""
    
    def test_package_clean_with_negative_price(self):
        """Bug: Package.clean() should reject negative display prices"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=-1000
        )
        
        # Should raise ValidationError for negative price
        with self.assertRaises(ValidationError) as cm:
            package.clean()
        
        self.assertIn('Display price cannot be negative', str(cm.exception))
    
    def test_package_clean_with_negative_discount(self):
        """Bug: Package.clean() should reject negative discount percentages"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=1000,
            display_discount_percentage=-10
        )
        
        # Should raise ValidationError for negative discount
        with self.assertRaises(ValidationError) as cm:
            package.clean()
        
        self.assertIn('Display discount percentage cannot be negative', str(cm.exception))
    
    def test_package_clean_with_valid_data(self):
        """Bug: Package.clean() should pass with valid data"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=1000,
            display_discount_percentage=10
        )
        
        # Should not raise ValidationError
        try:
            package.clean()
        except ValidationError:
            self.fail("Package.clean() raised ValidationError unexpectedly!")
    
    def test_package_clean_with_null_values(self):
        """Bug: Package.clean() should handle null values gracefully"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=None,
            display_discount_percentage=None
        )
        
        # Should not raise ValidationError for null values
        try:
            package.clean()
        except ValidationError:
            self.fail("Package.clean() raised ValidationError unexpectedly for null values!")
    
    def test_package_clean_with_zero_values(self):
        """Bug: Package.clean() should allow zero values"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=0,
            display_discount_percentage=0
        )
        
        # Should not raise ValidationError for zero values
        try:
            package.clean()
        except ValidationError:
            self.fail("Package.clean() raised ValidationError unexpectedly for zero values!")
