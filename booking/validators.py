from decimal import Decimal


def validate_pax_records(pax_records):
    """Validate pax records data before creating a booking."""
    errors = []

    if not pax_records:
        errors.append('At least one pax record is required')
        return errors

    for i, record in enumerate(pax_records):
        pax = record.get('pax')
        if pax is None:
            errors.append(f'Pax count is required for room {i + 1}')
        elif not isinstance(pax, int) or pax < 1:
            errors.append(f'Pax count must be a positive integer for room {i + 1}')

        customer_details = record.get('customer_details', [])
        if not customer_details:
            errors.append(f'Customer details are required for room {i + 1}')

        for j, detail in enumerate(customer_details):
            if not detail.get('name', '').strip():
                errors.append(f'Name is required for customer {j + 1} in room {i + 1}')
            if not detail.get('contact_number', '').strip():
                errors.append(f'Contact number is required for customer {j + 1} in room {i + 1}')

    return errors


def validate_payment_data(payment_data):
    """Validate payment data for booking confirmation."""
    errors = []

    if not payment_data:
        errors.append('Payment data is required')
        return errors

    if not payment_data.get('payment_id'):
        errors.append('Payment ID is required')
    if not payment_data.get('order_id'):
        errors.append('Order ID is required')
    if not payment_data.get('signature'):
        errors.append('Payment signature is required')

    amount = payment_data.get('amount')
    if amount is None:
        errors.append('Payment amount is required')
    elif not isinstance(amount, (int, float, Decimal)):
        errors.append('Payment amount must be a number')
    elif Decimal(str(amount)) <= 0:
        errors.append('Payment amount must be positive')

    return errors


def validate_booking_status_transition(current_status, new_status):
    """Validate that a booking status transition is allowed."""
    allowed_transitions = {
        'Partially Confirmed': ['Confirmed', 'Cancelled'],
        'Confirmed': ['Cancelled'],
        'Cancelled': [],
    }

    allowed = allowed_transitions.get(current_status, [])
    if new_status not in allowed:
        return False, f'Cannot transition from {current_status} to {new_status}'
    return True, ''
