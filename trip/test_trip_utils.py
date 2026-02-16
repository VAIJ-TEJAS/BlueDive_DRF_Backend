"""
F2P tests for trip utils bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
from django.test import TestCase
from trip.utils import format_date_range
from datetime import date


class TripUtilsF2PTest(TestCase):
    """Test trip utils fixes"""
    
    def test_format_date_range_with_non_date_objects(self):
        """Bug: format_date_range should handle non-date objects gracefully"""
        # Should handle string dates
        result = format_date_range('2025-02-20', '2025-02-22')
        self.assertEqual(result, '2025-02-20 - 2025-02-22')
        
        # Should handle mixed types
        result2 = format_date_range(date(2025, 2, 20), '2025-02-22')
        # After fix: should handle AttributeError and return string representation
        self.assertEqual(result2, '2025-02-20 - 2025-02-22')
        
        # Should handle None values
        result3 = format_date_range(None, '2025-02-22')
        self.assertEqual(result3, '')
        
        result4 = format_date_range('2025-02-20', None)
        self.assertEqual(result4, '')
        
        # Should still work with proper date objects
        result5 = format_date_range(date(2025, 2, 20), date(2025, 2, 22))
        self.assertEqual(result5, '20 Feb - 22 Feb 2025')
