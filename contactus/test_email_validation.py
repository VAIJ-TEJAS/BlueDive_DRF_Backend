"""
F2P tests for contactus email validation bug fix.
These tests would fail on the base branch and pass after the fix.
"""
import pytest
from contactus.utils import validate_email


class ContactEmailValidationF2PTest:
    """Test contactus email validation handles edge cases"""
    
    def test_validate_email_handles_none_and_whitespace(self):
        """Bug: validate_email should handle None and whitespace-only strings"""
        # None input
        assert not validate_email(None)
        
        # Empty string
        assert not validate_email("")
        
        # Whitespace only
        assert not validate_email("   ")
        assert not validate_email("\t\n")
        assert not validate_email("\r\n")
        
        # Non-string input
        assert not validate_email(123)
        assert not validate_email([])
        assert not validate_email({})
        
        # Valid emails should still work
        assert validate_email("test@example.com")
        assert validate_email("  test@example.com  ")
        assert validate_email("user.name+tag@domain.co.uk")
        
        # Invalid emails should still fail
        assert not validate_email("invalid-email")
        assert not validate_email("@domain.com")
        assert not validate_email("user@")
