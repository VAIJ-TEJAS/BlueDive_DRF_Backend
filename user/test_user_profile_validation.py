"""
F2P tests for user profile model validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()


class UserProfileValidationF2PTest(TestCase):
    """Test user profile model validation fixes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_clean_with_invalid_phone(self):
        """Bug: UserProfile.clean() should reject invalid phone numbers"""
        from user.models import UserProfile
        
        profile = UserProfile(
            user=self.user,
            phone_number='abc123',  # Invalid phone number
            date_of_birth=date(1990, 1, 1)
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            profile.clean()
        
        self.assertIn('Please enter a valid phone number', str(cm.exception))
    
    def test_user_profile_clean_with_future_dob(self):
        """Bug: UserProfile.clean() should reject future dates of birth"""
        from user.models import UserProfile
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        profile = UserProfile(
            user=self.user,
            phone_number='+1234567890',
            date_of_birth=tomorrow
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            profile.clean()
        
        self.assertIn('Date of birth cannot be in the future', str(cm.exception))
    
    def test_user_profile_clean_with_valid_phone(self):
        """Bug: UserProfile.clean() should accept valid phone numbers"""
        from user.models import UserProfile
        
        # Test various valid phone formats
        valid_phones = ['+1234567890', '1234567890', '+919876543210']
        
        for phone in valid_phones:
            profile = UserProfile(
                user=self.user,
                phone_number=phone,
                date_of_birth=date(1990, 1, 1)
            )
            
            # Should not raise ValidationError
            try:
                profile.clean()
            except ValidationError:
                self.fail(f"UserProfile.clean() raised ValidationError for valid phone: {phone}")
    
    def test_user_profile_clean_with_null_values(self):
        """Bug: UserProfile.clean() should handle null values gracefully"""
        from user.models import UserProfile
        
        profile = UserProfile(
            user=self.user,
            phone_number=None,
            date_of_birth=None
        )
        
        # Should not raise ValidationError for null values
        try:
            profile.clean()
        except ValidationError:
            self.fail("UserProfile.clean() raised ValidationError unexpectedly for null values!")
    
    def test_user_profile_clean_with_past_dob(self):
        """Bug: UserProfile.clean() should accept past dates of birth"""
        from user.models import UserProfile
        
        past_date = date(1990, 1, 1)
        profile = UserProfile(
            user=self.user,
            phone_number='+1234567890',
            date_of_birth=past_date
        )
        
        # Should not raise ValidationError for past dates
        try:
            profile.clean()
        except ValidationError:
            self.fail("UserProfile.clean() raised ValidationError unexpectedly for past date of birth!")
