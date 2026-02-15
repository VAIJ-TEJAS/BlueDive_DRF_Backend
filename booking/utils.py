from decimal import Decimal


def calculate_total_cost(pax_records):
    """Calculate the total package cost from a list of pax records."""
    total = Decimal('0.00')
    for record in pax_records:
        for detail in record.get('customer_details', []):
            total += Decimal(str(detail.get('package_cost', 0)))
    return total


def calculate_discounted_cost(pax_records):
    """Calculate the total discounted cost from a list of pax records."""
    total = Decimal('0.00')
    for record in pax_records:
        for detail in record.get('customer_details', []):
            total += Decimal(str(detail.get('discounted_package_cost', 0)))
    return total


def calculate_advance_cost(pax_records, advance_per_pax=2500):
    """Calculate the advance payment based on pax count."""
    total = 0
    for record in pax_records:
        total += record.get('pax', 0) * advance_per_pax
    return total


def count_total_customers(pax_records):
    """Count the total number of customers across all pax records."""
    total = 0
    for record in pax_records:
        total += len(record.get('customer_details', []))
    return total


def count_total_rooms(pax_records):
    """Count the total number of rooms (one per pax record)."""
    return len(pax_records)


def get_status_label(status):
    """Return a human-readable label for a booking status."""
    labels = {
        'Partially Confirmed': 'Awaiting Full Payment',
        'Confirmed': 'Booking Confirmed',
        'Cancelled': 'Booking Cancelled',
    }
    return labels.get(status, 'Unknown Status')


def is_booking_cancellable(status):
    """Check if a booking can be cancelled based on its current status."""
    return status not in ('Cancelled',)


def calculate_balance(total_cost, advance_cost):
    """Calculate the balance amount after advance payment."""
    balance = Decimal(str(total_cost)) - Decimal(str(advance_cost))
    return max(balance, Decimal('0.00'))
