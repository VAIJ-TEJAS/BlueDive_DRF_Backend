import re


def format_phone_number(phone):
    """Normalize a phone number to E.164 format with +91 prefix."""
    if not phone:
        return ''
    cleaned = re.sub(r'\D', '', phone)
    if cleaned.startswith('91') and len(cleaned) == 12:
        return f'+{cleaned}'
    if len(cleaned) == 10:
        return f'+91{cleaned}'
    return phone


def mask_phone_number(phone):
    """Mask a phone number showing only last 4 digits."""
    if not phone:
        return ''
    cleaned = re.sub(r'\D', '', phone)
    if len(cleaned) < 4:
        return cleaned
    return '*' * (len(cleaned) - 4) + cleaned[-4:]


def validate_phone_number(phone):
    """Validate that a phone number is a valid Indian mobile number."""
    if not phone:
        return False
    cleaned = re.sub(r'\D', '', phone)
    if cleaned.startswith('91'):
        cleaned = cleaned[2:]
    if len(cleaned) != 10:
        return False
    return cleaned[0] in '6789'


def get_display_name(user):
    """Get a display name for a user, falling back to username."""
    if not user:
        return 'Unknown'
    
    # Handle both dict-like objects and Django user objects
    if hasattr(user, 'get'):
        # Dict-like object
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        if full_name:
            return full_name
        return user.get('username', 'Unknown')
    else:
        # Django user object
        full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        if full_name:
            return full_name
        return getattr(user, 'username', 'Unknown')


def validate_otp(otp):
    """Validate that an OTP is a 6-digit string."""
    if not otp:
        return False
    cleaned = str(otp).strip()
    return len(cleaned) == 6 and cleaned.isdigit()
