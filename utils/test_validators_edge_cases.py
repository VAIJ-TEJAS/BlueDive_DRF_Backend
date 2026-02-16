"""
F2P tests for validators edge cases bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
import math
from utils.validators import (
    is_valid_email, 
    is_valid_phone_number,
    validate_amount,
    validate_pax_count
)


class ValidatorsEdgeCasesF2PTest:
    """Test validator functions handle edge cases properly"""
    
    def test_is_valid_email_handles_none_and_whitespace(self):
        """Bug: is_valid_email should handle None and whitespace-only strings"""
        # None input
        assert not is_valid_email(None)
        
        # Empty string
        assert not is_valid_email("")
        
        # Whitespace only
        assert not is_valid_email("   ")
        assert not is_valid_email("\t\n")
        
        # Non-string input
        assert not is_valid_email(123)
        assert not is_valid_email([])
        
        # Valid email should still work
        assert is_valid_email("test@example.com")
        assert is_valid_email("  test@example.com  ")

    def test_validate_amount_handles_nan_and_infinity(self):
        """Bug: validate_amount should handle NaN and infinity"""
        # None input
        assert not validate_amount(None)
        
        # Negative amounts
        assert not validate_amount(-10)
        assert not validate_amount("-100.50")
        
        # Zero amount
        assert not validate_amount(0)
        
        # NaN
        assert not validate_amount(float('nan'))
        assert not validate_amount('nan')
        
        # Infinity
        assert not validate_amount(float('inf'))
        assert not validate_amount(float('-inf'))
        assert not validate_amount('inf')
        
        # Valid amounts
        assert validate_amount(10.50)
        assert validate_amount("100.00")
        assert validate_amount(999999.99)

    def test_validate_pax_count_handles_edge_cases(self):
        """Bug: validate_pax_count should handle NaN and infinity"""
        # None input
        assert not validate_pax_count(None)
        
        # Zero or negative
        assert not validate_pax_count(0)
        assert not validate_pax_count(-1)
        
        # NaN
        assert not validate_pax_count(float('nan'))
        
        # Infinity
        assert not validate_pax_count(float('inf'))
        assert not validate_pax_count(float('-inf'))
        
        # Too large
        assert not validate_pax_count(51)
        assert not validate_pax_count(100)
        
        # Valid values
        assert validate_pax_count(1)
        assert validate_pax_count(25)
        assert validate_pax_count(50)
        
        # String numbers
        assert validate_pax_count("10")
        assert validate_pax_count(" 25 ")
