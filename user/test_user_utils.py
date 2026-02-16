"""
F2P tests for user utils bug fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from user.utils import get_display_name

User = get_user_model()


class UserUtilsF2PTest(TestCase):
    """Test user utils fixes"""
    
    def test_get_display_name_with_user_object(self):
        """Bug: get_display_name should handle Django user objects, not just dicts"""
        user = User.objects.create_user(
            username='testuser',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        
        # Should work with Django user object
        display_name = get_display_name(user)
        self.assertEqual(display_name, 'John Doe')
        
        # Should work with user object without names
        user2 = User.objects.create_user(
            username='testuser2',
            email='jane@example.com'
        )
        display_name2 = get_display_name(user2)
        self.assertEqual(display_name2, 'testuser2')
        
        # Should still work with dict-like objects
        user_dict = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'jsmith'
        }
        display_name3 = get_display_name(user_dict)
        self.assertEqual(display_name3, 'Jane Smith')
        
        # Should handle missing fields gracefully
        user_dict2 = {'username': 'missing'}
        display_name4 = get_display_name(user_dict2)
        self.assertEqual(display_name4, 'missing')
