"""
F2P tests for contact message model validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from contactus.models import ContactMessage


class ContactValidationF2PTest(TestCase):
    """Test contact message model validation fixes"""
    
    def test_contact_message_clean_with_empty_name(self):
        """Bug: ContactMessage.clean() should reject empty name"""
        message = ContactMessage(
            name='',
            email='test@example.com',
            subject='Test Subject',
            message='Test message'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        self.assertIn('Name is required', str(cm.exception))
    
    def test_contact_message_clean_with_whitespace_name(self):
        """Bug: ContactMessage.clean() should reject whitespace-only name"""
        message = ContactMessage(
            name='   ',
            email='test@example.com',
            subject='Test Subject',
            message='Test message'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        self.assertIn('Name is required', str(cm.exception))
    
    def test_contact_message_clean_with_empty_subject(self):
        """Bug: ContactMessage.clean() should reject empty subject"""
        message = ContactMessage(
            name='Test Name',
            email='test@example.com',
            subject='',
            message='Test message'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        self.assertIn('Subject is required', str(cm.exception))
    
    def test_contact_message_clean_with_empty_message(self):
        """Bug: ContactMessage.clean() should reject empty message"""
        message = ContactMessage(
            name='Test Name',
            email='test@example.com',
            subject='Test Subject',
            message=''
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        self.assertIn('Message is required', str(cm.exception))
    
    def test_contact_message_clean_with_whitespace_message(self):
        """Bug: ContactMessage.clean() should reject whitespace-only message"""
        message = ContactMessage(
            name='Test Name',
            email='test@example.com',
            subject='Test Subject',
            message='   '
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        self.assertIn('Message is required', str(cm.exception))
    
    def test_contact_message_clean_with_valid_data(self):
        """Bug: ContactMessage.clean() should pass with valid data"""
        message = ContactMessage(
            name='Test Name',
            email='test@example.com',
            subject='Test Subject',
            message='Test message content'
        )
        
        # Should not raise ValidationError
        try:
            message.clean()
        except ValidationError:
            self.fail("ContactMessage.clean() raised ValidationError unexpectedly!")
    
    def test_contact_message_clean_with_null_values(self):
        """Bug: ContactMessage.clean() should handle null values gracefully"""
        # Note: CharField doesn't allow null by default, but we test the validation logic
        message = ContactMessage(
            name='Test Name',
            email='test@example.com',
            subject='Test Subject',
            message='Test message'
        )
        
        # Manually set to None to test the validation (this would normally be handled by model field)
        message.name = None
        
        with self.assertRaises(ValidationError) as cm:
            message.clean()
        
        # The validation should catch None values
        error_message = str(cm.exception)
        self.assertTrue('Name is required' in error_message or 
                       'NoneType' in error_message)  # Depending on how None is handled
