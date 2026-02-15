"""
Custom Django REST framework fields for trip app.
"""

from rest_framework import serializers
from datetime import date


class TripStatusField(serializers.CharField):
    """Custom field for trip status with display formatting."""
    
    def to_representation(self, value):
        """Return display-friendly trip status."""
        status_map = {
            'Scheduled': 'Upcoming',
            'Ongoing': 'In Progress',
            'Completed': 'Finished',
            'Cancelled': 'Cancelled',
            'Omitted': 'Skipped',
        }
        return status_map.get(value, value)


class DateRangeField(serializers.CharField):
    """Custom field for date range display."""
    
    def to_representation(self, value):
        """Format date range for display."""
        if not value or not hasattr(value, 'start_date') or not hasattr(value, 'end_date'):
            return 'No dates'
        
        start = value.start_date
        end = value.end_date
        
        if start.month == end.month:
            return f"{start.strftime('%b %d')} - {end.strftime('%d, %Y')}"
        else:
            return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"


class AvailabilityField(serializers.IntegerField):
    """Custom field for availability with status indicators."""
    
    def __init__(self, capacity=18, **kwargs):
        self.capacity = capacity
        super().__init__(**kwargs)
    
    def to_representation(self, value):
        """Return availability with status."""
        if value is None:
            return "Unknown"
        
        percentage = (value / self.capacity) * 100 if self.capacity > 0 else 0
        
        if percentage >= 75:
            return f"{value} (Plenty)"
        elif percentage >= 25:
            return f"{value} (Limited)"
        else:
            return f"{value} (Critical)"


class DurationField(serializers.CharField):
    """Custom field for trip duration."""
    
    def to_representation(self, value):
        """Format duration for display."""
        if not value or not hasattr(value, 'start_date') or not hasattr(value, 'end_date'):
            return 'Unknown'
        
        days = (value.end_date - value.start_date).days + 1
        
        if days == 1:
            return '1 Day'
        elif days == 2:
            return '2 Days'
        elif days == 3:
            return '3 Days'
        else:
            return f'{days} Days'
