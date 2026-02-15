"""
Trip helper functions for common operations.
"""


def format_trip_name(trip):
    """Format trip name for display."""
    if not trip or not hasattr(trip, 'package') or not trip.package:
        return 'Unknown Trip'
    return f"{trip.package.name} - {trip.start_date}"


def get_trip_progress_percentage(start_date, end_date):
    """Calculate trip progress percentage."""
    from datetime import date
    if not start_date or not end_date:
        return 0
    
    today = date.today()
    total_days = (end_date - start_date).days
    
    if today <= start_date:
        return 0
    elif today >= end_date:
        return 100
    else:
        elapsed = (today - start_date).days
        return int((elapsed / total_days) * 100)


def get_trip_capacity_status(available_seats, total_seats=18):
    """Get capacity status based on available seats."""
    if available_seats is None or not total_seats:
        return 'unknown'
    
    percentage = (available_seats / total_seats) * 100
    
    if percentage >= 75:
        return 'plenty'
    elif percentage >= 25:
        return 'limited'
    else:
        return 'critical'


def get_trip_duration_display(start_date, end_date):
    """Get human-readable trip duration."""
    if not start_date or not end_date:
        return 'Unknown'
    
    days = (end_date - start_date).days + 1  # Inclusive count
    if days == 1:
        return '1 Day'
    elif days == 2:
        return '2 Days'
    elif days == 3:
        return '3 Days'
    else:
        return f'{days} Days'
