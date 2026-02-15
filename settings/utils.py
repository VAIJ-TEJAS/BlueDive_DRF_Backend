from datetime import date, timedelta


def is_scuba_free_for_trip(start_date, scuba_limit_days):
    """Check if scuba is free based on days until trip start."""
    if not start_date or scuba_limit_days is None:
        return False
    days_until = (start_date - date.today()).days
    return days_until >= scuba_limit_days


def is_discount_applicable_for_trip(start_date, discount_limit_days):
    """Check if early-bird discount applies based on days until trip start."""
    if not start_date or discount_limit_days is None:
        return False
    days_until = (start_date - date.today()).days
    return days_until >= discount_limit_days


def can_do_advance_payment(start_date, balance_payment_limit_days):
    """Check if advance payment is still allowed based on days until trip."""
    if not start_date or balance_payment_limit_days is None:
        return False
    days_until = (start_date - date.today()).days
    return days_until > balance_payment_limit_days


def get_scuba_cutoff_date(start_date, scuba_limit_days):
    """Get the last date when scuba is free for a trip."""
    if not start_date or scuba_limit_days is None:
        return None
    return start_date - timedelta(days=scuba_limit_days)


def get_discount_cutoff_date(start_date, discount_limit_days):
    """Get the last date when discount applies for a trip."""
    if not start_date or discount_limit_days is None:
        return None
    return start_date - timedelta(days=discount_limit_days)


def get_balance_payment_due_date(start_date, balance_payment_limit_days):
    """Get the due date for balance payment."""
    if not start_date or balance_payment_limit_days is None:
        return None
    return start_date - timedelta(days=balance_payment_limit_days)


def validate_settings_values(scuba_limit, discount_limit, balance_limit):
    """Validate that settings values are reasonable."""
    errors = []
    if scuba_limit is not None and scuba_limit < 0:
        errors.append('scuba_limit_days cannot be negative')
    if discount_limit is not None and discount_limit < 0:
        errors.append('discount_limit_days cannot be negative')
    if balance_limit is not None and balance_limit < 0:
        errors.append('balance_payment_limit_days cannot be negative')
    if (scuba_limit is not None and discount_limit is not None
            and scuba_limit < discount_limit):
        errors.append('scuba_limit_days should be >= discount_limit_days')
    return errors
