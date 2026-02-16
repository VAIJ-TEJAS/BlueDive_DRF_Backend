"""
Common validation utilities for the BlueDive application.
"""

import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip()
    if not email:
        return False
    
    # Basic email pattern - more comprehensive than Django's default
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone_number(phone: str, country_code: str = 'IN') -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country_code: Country code for validation rules (default: IN for India)
        
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    if country_code == 'IN':
        # Indian phone numbers: 10 digits, optionally with +91
        if phone.startswith('+91'):
            return len(phone) == 13 and phone[3:].isdigit()
        elif phone.startswith('91'):
            return len(phone) == 12 and phone[2:].isdigit()
        else:
            return len(phone) == 10 and phone.isdigit()
    
    # Generic validation for other countries
    return len(phone) >= 10 and phone.isdigit()


def sanitize_name(name: str) -> str:
    """
    Sanitize and validate person names.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name
    """
    if not name or not isinstance(name, str):
        return ''
    
    # Remove extra whitespace and special characters except hyphens and apostrophes
    sanitized = re.sub(r'\s+', ' ', name.strip())
    sanitized = re.sub(r"[^a-zA-Z\s\-']", '', sanitized)
    
    return sanitized


def validate_booking_reference(ref: str) -> bool:
    """
    Validate booking reference format.
    
    Args:
        ref: Booking reference to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not ref or not isinstance(ref, str):
        return False
    
    # Booking references should be alphanumeric, 6-20 characters
    pattern = r'^[A-Za-z0-9]{6,20}$'
    return bool(re.match(pattern, ref.strip()))


def validate_amount(amount: float) -> bool:
    """
    Validate payment amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    if amount is None:
        return False
    
    try:
        amount_float = float(amount)
        # Check for NaN and infinity
        if not (amount_float > 0 and amount_float <= 999999.99):
            return False
        # Ensure it's a finite number
        return not (amount_float != amount_float or amount_float == float('inf') or amount_float == float('-inf'))
    except (ValueError, TypeError):
        return False


def validate_pax_count(pax: int) -> bool:
    """
    Validate passenger count.
    
    Args:
        pax: Number of passengers
        
    Returns:
        True if valid, False otherwise
    """
    if pax is None:
        return False
    
    try:
        pax_int = int(pax)
        # Check for NaN and infinity
        if pax_int != pax_int or pax_int == float('inf') or pax_int == float('-inf'):
            return False
        return 1 <= pax_int <= 50  # Reasonable limits
    except (ValueError, TypeError, OverflowError):
        return False


def validate_date_range(start_date, end_date) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    if not start_date or not end_date:
        return False
    
    try:
        from datetime import date
        if isinstance(start_date, str):
            # Simple date parsing - would need proper implementation
            return False
        if isinstance(end_date, str):
            return False
            
        return start_date <= end_date
    except Exception:
        return False


def get_validation_errors(data: dict, validation_rules: dict) -> dict:
    """
    Validate data against provided rules and return errors.
    
    Args:
        data: Data to validate
        validation_rules: Dictionary of field -> validator function mappings
        
    Returns:
        Dictionary of field -> error message mappings
    """
    errors = {}
    
    for field, validator in validation_rules.items():
        value = data.get(field)
        
        if not validator(value):
            errors[field] = f"Invalid {field.replace('_', ' ')}"
    
    return errors
