from decimal import Decimal


def amount_to_paise(amount):
    """Convert a rupee amount to paise for Razorpay."""
    if amount is None:
        return 0
    return int(Decimal(str(amount)) * 100)


def paise_to_amount(paise):
    """Convert paise back to rupee amount."""
    if paise is None:
        return Decimal('0.00')
    return Decimal(str(paise)) / 100


def validate_payment_type(payment_type):
    """Check if the payment type is valid."""
    valid_types = ('advance', 'full')
    return payment_type in valid_types


def get_payment_status_label(status):
    """Return a human-readable label for a payment status."""
    labels = {
        'Created': 'Payment Initiated',
        'Authorized': 'Payment Authorized',
        'Captured': 'Payment Successful',
        'Failed': 'Payment Failed',
        'Refunded': 'Payment Refunded',
    }
    return labels.get(status, 'Unknown')


def is_payment_successful(status):
    """Check if a payment status indicates success."""
    return status in ('Authorized', 'Captured')


def generate_receipt_id(prefix='receipt'):
    """Generate a unique receipt ID."""
    import time
    return f"{prefix}_{int(time.time())}"


def calculate_order_amount(total_cost, advance_cost, payment_type):
    """Calculate the order amount based on payment type."""
    if payment_type == 'full':
        return amount_to_paise(total_cost)
    elif payment_type == 'advance':
        return amount_to_paise(advance_cost)
    return 0
