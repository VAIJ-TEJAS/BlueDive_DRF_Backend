"""
F2P tests for simple validators utility.
These tests would fail on the base branch and pass after the fixes.
"""

import pytest
from utils.simple_validators import (
    validate_email,
    validate_phone,
    validate_url,
    validate_date,
    validate_password,
    calculate_password_strength,
    validate_username,
    validate_numeric,
    validate_required_fields,
    sanitize_string,
    validate_json_structure,
    validate_pattern,
    ValidationError,
    PATTERNS
)


class TestSimpleValidators:
    """Test simple validation utilities."""

    def test_validate_email_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            'user123@test-domain.com',
            'a@b.c'
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            '',
            'invalid',
            '@example.com',
            'test@',
            'test.example.com',
            'test@.com',
            'test@com.',
            'test space@example.com',
            None,
            123
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_phone_valid_numbers(self):
        """Test valid phone numbers."""
        valid_phones = [
            '1234567890',
            '+1234567890',
            '(123) 456-7890',
            '123-456-7890',
            '+1 123 456 7890',
            '123456789012345'
        ]
        
        for phone in valid_phones:
            assert validate_phone(phone) is True

    def test_validate_phone_invalid_numbers(self):
        """Test invalid phone numbers."""
        invalid_phones = [
            '',
            '123',
            '1234567890123456',
            'abc123',
            '+',
            '()',
            None,
            123
        ]
        
        for phone in invalid_phones:
            assert validate_phone(phone) is False

    def test_validate_url_valid_urls(self):
        """Test valid URLs."""
        valid_urls = [
            'http://example.com',
            'https://example.com',
            'https://www.example.com',
            'https://example.com/path',
            'https://example.com/path?query=value',
            'https://example.com/path#section',
            'https://example.com:8080'
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            '',
            'example.com',
            'ftp://example.com',
            'http://',
            'https://',
            None,
            123
        ]
        
        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_date_valid_dates(self):
        """Test valid date strings."""
        valid_dates = [
            ('2023-01-01', '%Y-%m-%d'),
            ('01/01/2023', '%m/%d/%Y'),
            ('2023-01-01 12:00:00', '%Y-%m-%d %H:%M:%S')
        ]
        
        for date_str, format_str in valid_dates:
            assert validate_date(date_str, format_str) is True

    def test_validate_date_invalid_dates(self):
        """Test invalid date strings."""
        invalid_dates = [
            ('2023-13-01', '%Y-%m-%d'),
            ('2023-02-30', '%Y-%m-%d'),
            ('invalid', '%Y-%m-%d'),
            ('', '%Y-%m-%d'),
            (None, '%Y-%m-%d'),
            (123, '%Y-%m-%d')
        ]
        
        for date_str, format_str in invalid_dates:
            assert validate_date(date_str, format_str) is False

    def test_validate_password_strong_password(self):
        """Test strong password validation."""
        result = validate_password('StrongP@ssw0rd!')
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['strength'] == 'strong'

    def test_validate_password_weak_password(self):
        """Test weak password validation."""
        result = validate_password('weak')
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert result['strength'] in ['very_weak', 'weak']

    def test_validate_password_empty(self):
        """Test empty password validation."""
        result = validate_password('')
        
        assert result['valid'] is False
        assert 'Password is required' in result['errors']

    def test_validate_password_none(self):
        """Test None password validation."""
        result = validate_password(None)
        
        assert result['valid'] is False
        assert 'Password is required' in result['errors']

    def test_calculate_password_strength_levels(self):
        """Test password strength calculation."""
        test_cases = [
            ('', 'very_weak'),
            ('123', 'very_weak'),
            ('weak', 'very_weak'),
            ('Weak123', 'weak'),
            ('Weak123!', 'medium'),
            ('StrongP@ssw0rd!', 'strong')
        ]
        
        for password, expected_strength in test_cases:
            assert calculate_password_strength(password) == expected_strength

    def test_validate_username_valid_usernames(self):
        """Test valid usernames."""
        valid_usernames = [
            'user',
            'user123',
            'test_user',
            'a_b_c',
            'User123'
        ]
        
        for username in valid_usernames:
            result = validate_username(username)
            assert result['valid'] is True

    def test_validate_username_invalid_usernames(self):
        """Test invalid usernames."""
        invalid_usernames = [
            '',
            'ab',
            'a' * 21,
            'user@name',
            'user-name',
            '_user',
            'user_',
            'user name',
            None,
            123
        ]
        
        for username in invalid_usernames:
            result = validate_username(username)
            assert result['valid'] is False

    def test_validate_numeric_valid_numbers(self):
        """Test valid numeric values."""
        valid_numbers = [
            (123, None, None),
            (123.45, None, None),
            ('123', None, None),
            ('123.45', None, None),
            (50, 0, 100),
            (75, 50, 100)
        ]
        
        for value, min_val, max_val in valid_numbers:
            assert validate_numeric(value, min_val, max_val) is True

    def test_validate_numeric_invalid_numbers(self):
        """Test invalid numeric values."""
        invalid_numbers = [
            ('abc', None, None),
            (None, None, None),
            (150, 0, 100),
            (-10, 0, 100),
            ([], None, None)
        ]
        
        for value, min_val, max_val in invalid_numbers:
            assert validate_numeric(value, min_val, max_val) is False

    def test_validate_required_fields_all_present(self):
        """Test validation when all required fields are present."""
        data = {'name': 'John', 'email': 'john@example.com', 'age': 30}
        required_fields = ['name', 'email', 'age']
        
        result = validate_required_fields(data, required_fields)
        
        assert result['valid'] is True
        assert len(result['missing_fields']) == 0

    def test_validate_required_fields_missing_fields(self):
        """Test validation when fields are missing."""
        data = {'name': 'John'}
        required_fields = ['name', 'email', 'age']
        
        result = validate_required_fields(data, required_fields)
        
        assert result['valid'] is False
        assert set(result['missing_fields']) == {'email', 'age'}

    def test_validate_required_fields_empty_values(self):
        """Test validation when fields have empty values."""
        data = {'name': 'John', 'email': '', 'age': None}
        required_fields = ['name', 'email', 'age']
        
        result = validate_required_fields(data, required_fields)
        
        assert result['valid'] is False
        assert set(result['missing_fields']) == {'email', 'age'}

    def test_sanitize_string_removes_html(self):
        """Test HTML removal in string sanitization."""
        dirty_string = '<script>alert("xss")</script>Hello <b>World</b>'
        clean_string = sanitize_string(dirty_string)
        
        assert clean_string == 'Hello World'

    def test_sanitize_string_removes_special_chars(self):
        """Test special character removal in string sanitization."""
        dirty_string = 'Hello "World" & <Test>'
        clean_string = sanitize_string(dirty_string)
        
        assert clean_string == 'Hello World  Test'

    def test_sanitize_string_edge_cases(self):
        """Test edge cases in string sanitization."""
        test_cases = [
            ('', ''),
            (None, ''),
            (123, ''),
            ('   Hello   ', 'Hello'),
            ('<script>evil()</script>', ''),
            ('Normal text', 'Normal text')
        ]
        
        for input_str, expected in test_cases:
            assert sanitize_string(input_str) == expected

    def test_validate_json_structure_valid(self):
        """Test valid JSON structure validation."""
        data = {'name': 'John', 'age': 30, 'active': True}
        schema = {'name': 'string', 'age': 'number', 'active': 'boolean'}
        
        result = validate_json_structure(data, schema)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_json_structure_invalid_types(self):
        """Test invalid JSON structure validation."""
        data = {'name': 123, 'age': '30', 'active': 'true'}
        schema = {'name': 'string', 'age': 'number', 'active': 'boolean'}
        
        result = validate_json_structure(data, schema)
        
        assert result['valid'] is False
        assert len(result['errors']) == 3

    def test_validate_json_structure_missing_fields(self):
        """Test missing fields in JSON structure validation."""
        data = {'name': 'John'}
        schema = {'name': 'string', 'age': 'number', 'active': 'boolean'}
        
        result = validate_json_structure(data, schema)
        
        assert result['valid'] is False
        assert 'Missing required field: age' in result['errors']
        assert 'Missing required field: active' in result['errors']

    def test_validate_json_structure_not_object(self):
        """Test non-object JSON structure validation."""
        data = 'not an object'
        schema = {'name': 'string'}
        
        result = validate_json_structure(data, schema)
        
        assert result['valid'] is False
        assert 'Data must be a JSON object' in result['errors']

    def test_validate_pattern_valid_patterns(self):
        """Test valid pattern matching."""
        test_cases = [
            ('test@example.com', 'email'),
            ('user123', 'username'),
            ('valid-slug', 'slug'),
            ('550e8400-e29b-41d4-a716-446655440000', 'uuid')
        ]
        
        for text, pattern_name in test_cases:
            assert validate_pattern(text, pattern_name) is True

    def test_validate_pattern_invalid_patterns(self):
        """Test invalid pattern matching."""
        test_cases = [
            ('invalid', 'email'),
            ('ab', 'username'),
            ('invalid_slug!', 'slug'),
            ('not-uuid', 'uuid'),
            ('nonexistent', 'nonexistent')
        ]
        
        for text, pattern_name in test_cases:
            assert validate_pattern(text, pattern_name) is False

    def test_patterns_constant(self):
        """Test PATTERNS constant contains expected patterns."""
        expected_patterns = ['email', 'phone', 'url', 'username', 'slug', 'uuid']
        
        for pattern in expected_patterns:
            assert pattern in PATTERNS
            assert isinstance(PATTERNS[pattern], str)

    def test_validation_error_class(self):
        """Test ValidationError exception class."""
        with pytest.raises(ValidationError):
            raise ValidationError('Test error')

    def test_edge_cases_and_performance(self):
        """Test edge cases and performance."""
        # Test with very long strings
        long_email = 'a' * 100 + '@example.com'
        assert validate_email(long_email) is False
        
        # Test with special characters in username
        special_username = 'user_123_test'
        result = validate_username(special_username)
        assert result['valid'] is True
        
        # Test performance with large data
        large_data = {f'field_{i}': f'value_{i}' for i in range(100)}
        required_fields = [f'field_{i}' for i in range(50)]
        
        result = validate_required_fields(large_data, required_fields)
        assert result['valid'] is True

    def test_unicode_handling(self):
        """Test Unicode character handling."""
        unicode_email = 'tëst@éxample.com'
        assert validate_email(unicode_email) is False
        
        unicode_username = 'üser123'
        result = validate_username(unicode_username)
        assert result['valid'] is False

    def test_case_sensitivity(self):
        """Test case sensitivity in validations."""
        # Email should be case insensitive for local part
        assert validate_email('Test@Example.COM') is True
        
        # Username should be case sensitive
        result1 = validate_username('User123')
        result2 = validate_username('user123')
        assert result1['valid'] == result2['valid']  # Both should be valid

    def test_whitespace_handling(self):
        """Test whitespace handling in validations."""
        # Email with whitespace should fail
        assert validate_email(' test@example.com ') is False
        
        # Username with whitespace should fail
        result = validate_username('user 123')
        assert result['valid'] is False
        
        # Sanitize string should handle whitespace
        assert sanitize_string('  Hello World  ') == 'Hello World'
