from rest_framework import serializers
from django.contrib.auth.models import User
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']
    
    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required")
        
        # Check for valid username format (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value.strip()):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        
        # Check minimum length
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        
        return value.strip()
    
    def validate_email(self, value):
        if value and value.strip():
            # Basic email format validation
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, value.strip()):
                raise serializers.ValidationError("Invalid email format")
            return value.strip()
        return value
    
    def validate_first_name(self, value):
        if value and value.strip():
            # Check for valid name format (letters and spaces only)
            if not re.match(r'^[a-zA-Z\s]+$', value.strip()):
                raise serializers.ValidationError("First name can only contain letters and spaces")
            return value.strip()
        return value
    
    def validate_last_name(self, value):
        if value and value.strip():
            # Check for valid name format (letters and spaces only)
            if not re.match(r'^[a-zA-Z\s]+$', value.strip()):
                raise serializers.ValidationError("Last name can only contain letters and spaces")
            return value.strip()
        return value 
