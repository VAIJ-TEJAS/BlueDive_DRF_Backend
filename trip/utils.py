from datetime import date, timedelta


def get_days_until_trip(start_date):
    """Calculate the number of days until a trip starts."""
    if not start_date:
        return 0
    delta = start_date - date.today()
    return delta.days


def is_trip_upcoming(start_date):
    """Check if a trip hasn't started yet."""
    if not start_date:
        return False
    return start_date > date.today()


def is_trip_bookable(status, available_seats):
    """Check if a trip can be booked."""
    return status == 'Scheduled' and available_seats > 0


def get_trip_status_label(status):
    """Return a display-friendly label for a trip status."""
    labels = {
        'Scheduled': 'Upcoming',
        'Ongoing': 'In Progress',
        'Completed': 'Finished',
        'Cancelled': 'Cancelled',
        'Omitted': 'Skipped',
    }
    return labels.get(status, 'Unknown')


def format_date_range(start_date, end_date):
    """Format a date range as a readable string."""
    if not start_date or not end_date:
        return ''
    return f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"


def get_trip_duration_days(start_date, end_date):
    """Calculate the duration of a trip in days."""
    if not start_date or not end_date:
        return 0
    delta = end_date - start_date
    return max(0, delta.days)


def has_enough_seats(available_seats, requested_customers):
    """Check if there are enough seats for the requested number of customers."""
    return available_seats >= requested_customers


def has_enough_rooms(available_rooms, requested_rooms):
    """Check if there are enough rooms for the requested number."""
    return available_rooms >= requested_rooms
