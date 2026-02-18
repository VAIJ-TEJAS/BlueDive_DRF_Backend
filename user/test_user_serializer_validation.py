"""
F2P tests for user serializer validation bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer

User = get_user_model()


class UserSerializerF2PTest(TestCase):
    """Test user serializer validation fixes"""
    
    def test_user_serializer_empty_username(self):
        """Bug: Should reject empty username"""
        serializer = UserSerializer(data={
            'username': '',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Username is required', str(serializer.errors))
    
    def test_user_serializer_whitespace_only_username(self):
        """Bug: Should reject whitespace-only username"""
        serializer = UserSerializer(data={
            'username': '   ',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Username is required', str(serializer.errors))
    
    def test_user_serializer_short_username(self):
        """Bug: Should reject username shorter than 3 characters"""
        serializer = UserSerializer(data={
            'username': 'ab',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Username must be at least 3 characters long', str(serializer.errors))
    
    def test_user_serializer_invalid_username_chars(self):
        """Bug: Should reject username with special characters"""
        serializer = UserSerializer(data={
            'username': 'test@user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Username can only contain letters, numbers, and underscores', str(serializer.errors))
    
    def test_user_serializer_invalid_email_format(self):
        """Bug: Should reject invalid email format"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Invalid email format', str(serializer.errors))
    
    def test_user_serializer_email_without_domain(self):
        """Bug: Should reject email without domain"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Invalid email format', str(serializer.errors))
    
    def test_user_serializer_invalid_first_name(self):
        """Bug: Should reject first name with special characters"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test123',
            'last_name': 'User'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('First name can only contain letters and spaces', str(serializer.errors))
    
    def test_user_serializer_invalid_last_name(self):
        """Bug: Should reject last name with special characters"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User@123'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Last name can only contain letters and spaces', str(serializer.errors))
    
    def test_user_serializer_valid_username_with_underscore(self):
        """Bug: Should accept username with underscore"""
        serializer = UserSerializer(data={
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_user_serializer_valid_username_with_numbers(self):
        """Bug: Should accept username with numbers"""
        serializer = UserSerializer(data={
            'username': 'testuser123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_user_serializer_null_names(self):
        """Bug: Should accept null first and last names"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': None,
            'last_name': None
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_user_serializer_empty_names(self):
        """Bug: Should accept empty first and last names"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '',
            'last_name': ''
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_user_serializer_valid_data(self):
        """Bug: Should accept valid user data"""
        serializer = UserSerializer(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertTrue(serializer.is_valid())
