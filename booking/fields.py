"""
Custom Django REST framework fields for booking app.
"""

from rest_framework import serializers


class BookingStatusField(serializers.CharField):
    """Custom field for booking status with validation."""
    
    def to_representation(self, value):
        """Return display-friendly status."""
        status_map = {
            'Partially Confirmed': 'Pending',
            'Confirmed': 'Confirmed',
            'Cancelled': 'Cancelled',
        }
        return status_map.get(value, value)


class PaxCountField(serializers.IntegerField):
    """Custom field for pax count with validation."""
    
    def to_representation(self, value):
        """Return formatted pax count."""
        if value == 1:
            return f"{value} Person"
        else:
            return f"{value} Persons"


class CurrencyField(serializers.DecimalField):
    """Custom field for currency amounts."""
    
    def to_representation(self, value):
        """Return formatted currency."""
        if value is None:
            return "₹0.00"
        return f"₹{value:,.2f}"


class PhoneNumberField(serializers.CharField):
    """Custom field for phone numbers with formatting."""
    
    def to_representation(self, value):
        """Return formatted phone number."""
        if not value or len(value) < 10:
            return value
        
        # Format as +91 XXXXX XXXXX for Indian numbers
        if len(value) == 10:
            return f"+91 {value[:5]} {value[5:]}"
        elif value.startswith('+91') and len(value) == 13:
            return f"{value[:3]} {value[3:8]} {value[8:]}"
        
        return value
