"""
Booking helper functions for common operations.
"""


def format_booking_id(booking_id):
    """Format a booking ID for display."""
    if booking_id is None or booking_id == '':
        return 'N/A'
    return f"#{booking_id}"


def get_booking_status_color(status):
    """Return CSS color class for booking status."""
    colors = {
        'Partially Confirmed': 'warning',
        'Confirmed': 'success',
        'Cancelled': 'danger',
    }
    return colors.get(status, 'secondary')


def get_booking_status_icon(status):
    """Return icon name for booking status."""
    icons = {
        'Partially Confirmed': 'clock',
        'Confirmed': 'check-circle',
        'Cancelled': 'x-circle',
    }
    return icons.get(status, 'question-circle')


def is_recent_booking(booking_date, days=7):
    """Check if a booking was made recently."""
    from datetime import datetime, timedelta
    if not booking_date:
        return False
    cutoff = datetime.now() - timedelta(days=days)
    return booking_date >= cutoff
