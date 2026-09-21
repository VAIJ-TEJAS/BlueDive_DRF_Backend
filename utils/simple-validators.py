"""
Simple validation utilities for common data types
"""

import re
from datetime import datetime
from typing import Any, Optional


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number (basic format)
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common formatting
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    # Check if it's 10-15 digits
    return 10 <= len(clean_phone) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format
    """
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return bool(re.match(pattern, url))


def validate_date(date_str: str, format: str = '%Y-%m-%d') -> bool:
    """
    Validate date string format
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_password(password: str) -> dict:
    """
    Validate password strength
    Returns dict with validation results
    """
    if not password or not isinstance(password, str):
        return {'valid': False, 'errors': ['Password is required']}
    
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'strength': calculate_password_strength(password)
    }


def calculate_password_strength(password: str) -> str:
    """
    Calculate password strength
    """
    if not password:
        return 'very_weak'
    
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character types
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Complexity
    if len(set(password)) >= len(password) * 0.5:
        score += 1
    
    if score <= 2:
        return 'very_weak'
    elif score <= 4:
        return 'weak'
    elif score <= 6:
        return 'medium'
    else:
        return 'strong'


def validate_username(username: str) -> dict:
    """
    Validate username format
    """
    if not username or not isinstance(username, str):
        return {'valid': False, 'errors': ['Username is required']}
    
    errors = []
    
    if len(username) < 3:
        errors.append('Username must be at least 3 characters')
    
    if len(username) > 20:
        errors.append('Username must be no more than 20 characters')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append('Username can only contain letters, numbers, and underscores')
    
    if username.startswith('_') or username.endswith('_'):
        errors.append('Username cannot start or end with underscore')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_numeric(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """
    Validate numeric value with optional range
    """
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False
        
        if max_val is not None and num_value > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_required_fields(data: dict, required_fields: list) -> dict:
    """
    Validate required fields in data
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields
    }


def sanitize_string(text: str) -> str:
    """
    Sanitize string by removing potentially harmful characters
    """
    if not text or not isinstance(text, str):
        return ''
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags specifically
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()


def validate_json_structure(data: Any, schema: dict) -> dict:
    """
    Validate JSON data against a simple schema
    """
    errors = []
    
    if not isinstance(data, dict):
        return {'valid': False, 'errors': ['Data must be a JSON object']}
    
    for field, field_type in schema.items():
        if field not in data:
            errors.append(f'Missing required field: {field}')
            continue
        
        value = data[field]
        
        if field_type == 'string' and not isinstance(value, str):
            errors.append(f'Field {field} must be a string')
        elif field_type == 'number' and not isinstance(value, (int, float)):
            errors.append(f'Field {field} must be a number')
        elif field_type == 'boolean' and not isinstance(value, bool):
            errors.append(f'Field {field} must be a boolean')
        elif field_type == 'array' and not isinstance(value, list):
            errors.append(f'Field {field} must be an array')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


# Common validation patterns
PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?[\d\s\-\(\)]+$',
    'url': r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$',
    'username': r'^[a-zA-Z0-9_]{3,20}$',
    'slug': r'^[a-z0-9-]+$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
}


def validate_pattern(text: str, pattern_name: str) -> bool:
    """
    Validate text against predefined patterns
    """
    if pattern_name not in PATTERNS:
        return False
    
    pattern = PATTERNS[pattern_name]
    return bool(re.match(pattern, text))
