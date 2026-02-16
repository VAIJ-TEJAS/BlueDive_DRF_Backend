"""
F2P tests for booking serializers validation fixes.
These tests would fail on the base branch and pass after the fixes.
"""
import pytest
from django.test import TestCase
from rest_framework import serializers
from booking.serializers import CustomerDetailSerializer, PaxRecordSerializer


class BookingSerializersValidationF2PTest(TestCase):
    """Test booking serializers validation fixes"""
    
    def test_customer_detail_name_validation(self):
        """Bug: CustomerDetailSerializer should validate name field"""
        serializer = CustomerDetailSerializer()
        
        # Test empty name
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_name("")
        self.assertIn("Name is required", str(cm.exception))
        
        # Test whitespace-only name
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_name("   ")
        self.assertIn("Name is required", str(cm.exception))
        
        # Test None name
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_name(None)
        self.assertIn("Name is required", str(cm.exception))
        
        # Test valid name with whitespace
        result = serializer.validate_name("  John Doe  ")
        self.assertEqual(result, "John Doe")
        
        # Test valid name
        result = serializer.validate_name("Jane Smith")
        self.assertEqual(result, "Jane Smith")

    def test_customer_detail_contact_number_validation(self):
        """Bug: CustomerDetailSerializer should validate contact_number field"""
        serializer = CustomerDetailSerializer()
        
        # Test empty contact number
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_contact_number("")
        self.assertIn("Contact number is required", str(cm.exception))
        
        # Test whitespace-only contact number
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_contact_number("   ")
        self.assertIn("Contact number is required", str(cm.exception))
        
        # Test None contact number
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_contact_number(None)
        self.assertIn("Contact number is required", str(cm.exception))
        
        # Test valid contact number with whitespace
        result = serializer.validate_contact_number("  1234567890  ")
        self.assertEqual(result, "1234567890")
        
        # Test valid contact number
        result = serializer.validate_contact_number("9876543210")
        self.assertEqual(result, "9876543210")

    def test_pax_record_pax_validation(self):
        """Bug: PaxRecordSerializer should validate pax field"""
        serializer = PaxRecordSerializer()
        
        # Test zero pax
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_pax(0)
        self.assertIn("Pax count must be greater than 0", str(cm.exception))
        
        # Test negative pax
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_pax(-1)
        self.assertIn("Pax count must be greater than 0", str(cm.exception))
        
        # Test None pax
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_pax(None)
        self.assertIn("Pax count must be greater than 0", str(cm.exception))
        
        # Test valid pax
        result = serializer.validate_pax(2)
        self.assertEqual(result, 2)
        
        result = serializer.validate_pax(1)
        self.assertEqual(result, 1)
