"""
F2P tests for package utils bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
from django.test import TestCase
from package.utils import get_package_display_price


class PackageUtilsF2PTest(TestCase):
    """Test package utils fixes"""
    
    def test_display_price_with_over_100_percent_discount(self):
        """Bug: get_package_display_price should handle discounts over 100%"""
        # Should handle discount over 100%
        result = get_package_display_price(1000, 150)
        self.assertEqual(result, 0)
        
        # Should handle exactly 100% discount
        result2 = get_package_display_price(1000, 100)
        self.assertEqual(result2, 0)
        
        # Should handle negative discount (treat as no discount)
        result3 = get_package_display_price(1000, -10)
        self.assertEqual(result3, 1000)
        
        # Should handle zero discount
        result4 = get_package_display_price(1000, 0)
        self.assertEqual(result4, 1000)
        
        # Should still work with normal discounts
        result5 = get_package_display_price(1000, 25)
        self.assertEqual(result5, 750)
        
        # Should handle None display_price
        result6 = get_package_display_price(None, 25)
        self.assertEqual(result6, 0)
