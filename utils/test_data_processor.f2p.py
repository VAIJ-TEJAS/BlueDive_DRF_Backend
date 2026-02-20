"""
F2P tests for data processor utility.
These tests would fail on the base branch and pass after the fixes.
"""

import pytest
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, date
from decimal import Decimal
from utils.data_processor import (
    DataProcessor,
    clean_dataset,
    validate_emails,
    format_prices,
    calculate_ages,
    generate_slugs,
    mask_sensitive_fields,
    extract_numeric_data,
    transform_to_csv,
    transform_to_json,
    transform_to_xml,
    analyze_data_quality,
    detect_duplicates,
    find_outliers
)


class TestDataProcessor:
    """Test DataProcessor class functionality."""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test basic cleaning
        assert self.processor.clean_text("  Hello   World  ") == "Hello World"
        assert self.processor.clean_text("Hello@World#123") == "HelloWorld123"
        assert self.processor.clean_text("") == ""
        assert self.processor.clean_text(None) == ""
        assert self.processor.clean_text(123) == "123"
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        assert self.processor.normalize_phone("(123) 456-7890") == "+1 123 456 7890"
        assert self.processor.normalize_phone("+44 20 7946 0958") == "+44 20 7946 0958"
        assert self.processor.normalize_phone("1234567890") == "+1 123 456 7890"
        assert self.processor.normalize_phone("123") == "123"
        assert self.processor.normalize_phone("") == ""
        assert self.processor.normalize_phone(None) == ""
    
    def test_normalize_email(self):
        """Test email normalization."""
        assert self.processor.normalize_email("  USER@EXAMPLE.COM  ") == "user@example.com"
        assert self.processor.normalize_email("user.name@domain.co.uk") == "user.name@domain.co.uk"
        assert self.processor.normalize_email("invalid-email") == ""
        assert self.processor.normalize_email("") == ""
        assert self.processor.normalize_email(None) == ""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert self.processor.format_currency(1234.56) == "$1,234.56"
        assert self.processor.format_currency("1234.56") == "$1,234.56"
        assert self.processor.format_currency(Decimal("1234.56")) == "$1,234.56"
        assert self.processor.format_currency(1234.56, "EUR") == "€1,234.56"
        assert self.processor.format_currency(1234.56, "GBP") == "£1,234.56"
        assert self.processor.format_currency("invalid") == "0.00"
        assert self.processor.format_currency(None) == "0.00"
    
    def test_calculate_age(self):
        """Test age calculation."""
        # Test with date string
        today = date.today()
        birth_date = date(today.year - 25, today.month, today.day)
        assert self.processor.calculate_age(birth_date.strftime("%Y-%m-%d")) == 25
        
        # Test with date object
        assert self.processor.calculate_age(birth_date) == 25
        
        # Test with datetime object
        birth_datetime = datetime(today.year - 30, today.month, today.day)
        assert self.processor.calculate_age(birth_datetime) == 30
        
        # Test invalid formats
        assert self.processor.calculate_age("invalid-date") is None
        assert self.processor.calculate_age(None) is None
        assert self.processor.calculate_age("") is None
    
    def test_generate_slug(self):
        """Test slug generation."""
        assert self.processor.generate_slug("Hello World!") == "hello-world"
        assert self.processor.generate_slug("  Multiple   Spaces  ") == "multiple-spaces"
        assert self.processor.generate_slug("Special@Characters#Here") == "specialcharactershere"
        assert self.processor.generate_slug("Already-slugified") == "already-slugified"
        assert self.processor.generate_slug("") == ""
        assert self.processor.generate_slug(None) == ""
        assert self.processor.generate_slug(123) == "123"
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        assert self.processor.mask_sensitive_data("1234567890123456") == "************3456"
        assert self.processor.mask_sensitive_data("test@example.com", "*", 4) == "********@example.com"
        assert self.processor.mask_sensitive_data("123", "*", 4) == "123"
        assert self.processor.mask_sensitive_data("", "*", 4) == ""
        assert self.processor.mask_sensitive_data(None, "*", 4) == "None"
    
    def test_calculate_checksum(self):
        """Test checksum calculation."""
        data1 = {"key": "value"}
        data2 = {"key": "value"}
        data3 = {"key": "different"}
        
        checksum1 = self.processor.calculate_checksum(data1)
        checksum2 = self.processor.calculate_checksum(data2)
        checksum3 = self.processor.calculate_checksum(data3)
        
        assert checksum1 == checksum2  # Same data should have same checksum
        assert checksum1 != checksum3  # Different data should have different checksum
        assert len(checksum1) == 32  # MD5 hash length
    
    def test_encode_decode_base64(self):
        """Test base64 encoding and decoding."""
        original = "Hello, World!"
        encoded = self.processor.encode_base64(original)
        decoded = self.processor.decode_base64(encoded)
        
        assert decoded == original
        assert self.processor.decode_base64("invalid") == ""
    
    def test_extract_numbers(self):
        """Test number extraction from text."""
        text = "The price is $123.45 and the quantity is 67 items"
        numbers = self.processor.extract_numbers(text)
        
        assert 123.45 in numbers
        assert 67.0 in numbers
        assert len(numbers) == 2
        
        # Test with no numbers
        assert self.processor.extract_numbers("No numbers here") == []
        
        # Test with negative numbers
        numbers = self.processor.extract_numbers("Temperature is -5.5 degrees")
        assert -5.5 in numbers
    
    def test_calculate_percentage(self):
        """Test percentage calculation."""
        assert self.processor.calculate_percentage(25, 100) == 25.0
        assert self.processor.calculate_percentage(1, 4) == 25.0
        assert self.processor.calculate_percentage(0, 100) == 0.0
        assert self.processor.calculate_percentage(50, 0) == 0.0
        assert self.processor.calculate_percentage("25", "100") == 25.0
    
    def test_round_to_nearest(self):
        """Test rounding to nearest number."""
        assert self.processor.round_to_nearest(123, 10) == 120.0
        assert self.processor.round_to_nearest(127, 10) == 130.0
        assert self.processor.round_to_nearest(125, 25) == 125.0
        assert self.processor.round_to_nearest(123.7, 5) == 125.0
        assert self.processor.round_to_nearest("invalid", 10) == 0.0
    
    def test_validate_credit_card(self):
        """Test credit card validation."""
        # Valid test cards (Luhn algorithm)
        assert self.processor.validate_credit_card("4539 1488 0343 6467") == True
        assert self.processor.validate_credit_card("6011-1111-1111-1117") == True
        assert self.processor.validate_credit_card("378282246310005") == True
        
        # Invalid cards
        assert self.processor.validate_credit_card("1234 5678 9012 3456") == False
        assert self.processor.validate_credit_card("abcd-efgh-ijkl-mnop") == False
        assert self.processor.validate_credit_card("") == False
        assert self.processor.validate_credit_card(None) == False
    
    def test_parse_json_safe(self):
        """Test safe JSON parsing."""
        valid_json = '{"name": "John", "age": 30}'
        invalid_json = '{"name": "John", age: 30}'  # Missing quotes around age
        
        result = self.processor.parse_json_safe(valid_json)
        assert result == {"name": "John", "age": 30}
        
        result = self.processor.parse_json_safe(invalid_json)
        assert result is None
        
        result = self.processor.parse_json_safe("not json")
        assert result is None
    
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {
            "user": {
                "name": "John",
                "address": {
                    "street": "123 Main St",
                    "city": "New York"
                }
            },
            "score": 100
        }
        
        flattened = self.processor.flatten_dict(nested)
        
        expected = {
            "user.name": "John",
            "user.address.street": "123 Main St",
            "user.address.city": "New York",
            "score": 100
        }
        
        assert flattened == expected
    
    def test_group_by_key(self):
        """Test grouping by key."""
        data = [
            {"name": "John", "department": "IT"},
            {"name": "Jane", "department": "HR"},
            {"name": "Bob", "department": "IT"},
            {"name": "Alice", "department": "HR"}
        ]
        
        grouped = self.processor.group_by_key(data, "department")
        
        assert "IT" in grouped
        assert "HR" in grouped
        assert len(grouped["IT"]) == 2
        assert len(grouped["HR"]) == 2
        assert grouped["IT"][0]["name"] == "John"
        assert grouped["HR"][0]["name"] == "Jane"
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = self.processor.calculate_statistics(numbers)
        
        assert stats['count'] == 10
        assert stats['sum'] == 55
        assert stats['mean'] == 5.5
        assert stats['median'] == 5.5
        assert stats['min'] == 1
        assert stats['max'] == 10
        assert stats['std_dev'] > 0
        
        # Test empty list
        empty_stats = self.processor.calculate_statistics([])
        assert empty_stats['count'] == 0
        assert empty_stats['mean'] == 0
    
    def test_process_data_batch(self):
        """Test batch data processing."""
        data = [
            {"name": "  John  ", "email": "JOHN@EXAMPLE.COM"},
            {"name": "  Jane  ", "email": "JANE@EXAMPLE.COM"}
        ]
        
        processors = [
            ("name", self.processor.clean_text),
            ("email", self.processor.normalize_email)
        ]
        
        processed = self.processor.process_data_batch(data, processors)
        
        assert processed[0]["name"] == "John"
        assert processed[0]["email"] == "john@example.com"
        assert processed[1]["name"] == "Jane"
        assert processed[1]["email"] == "jane@example.com"
        
        # Check stats
        stats = self.processor.get_processing_stats()
        assert stats['processed_count'] == 4  # 2 records * 2 fields
        assert stats['error_count'] == 0
    
    def test_get_processing_stats(self):
        """Test processing statistics."""
        # Reset stats first
        self.processor.reset_stats()
        
        stats = self.processor.get_processing_stats()
        assert stats['processed_count'] == 0
        assert stats['error_count'] == 0
        assert stats['success_rate'] == 0
    
    def test_reset_stats(self):
        """Test statistics reset."""
        # Process some data to generate stats
        data = [{"name": "John"}]
        processors = [("name", self.processor.clean_text)]
        self.processor.process_data_batch(data, processors)
        
        # Verify stats exist
        stats = self.processor.get_processing_stats()
        assert stats['processed_count'] > 0
        
        # Reset and verify
        self.processor.reset_stats()
        stats = self.processor.get_processing_stats()
        assert stats['processed_count'] == 0
        assert stats['error_count'] == 0


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_clean_dataset(self):
        """Test dataset cleaning."""
        data = [
            {"name": "John", "email": "john@example.com", "age": 30},
            {"name": "", "email": "jane@example.com", "age": None},
            {"name": "  Bob  ", "email": "", "age": 25},
            {"name": None, "email": "alice@example.com", "age": 35}
        ]
        
        cleaned = clean_dataset(data)
        
        # Should remove empty values and clean text
        assert len(cleaned) == 4
        assert cleaned[0]["name"] == "John"
        assert cleaned[1]["name"] == "jane@example.com"  # Empty name removed
        assert cleaned[2]["name"] == "Bob"  # Text cleaned
        assert "age" not in cleaned[1]  # None age removed
    
    def test_validate_emails(self):
        """Test email validation."""
        emails = [
            "user@example.com",
            "INVALID@EXAMPLE.COM",
            "invalid-email",
            "user.name@domain.co.uk",
            "",
            None
        ]
        
        valid_emails = validate_emails(emails)
        
        assert len(valid_emails) == 3
        assert "user@example.com" in valid_emails
        assert "invalid@example.com" in valid_emails
        assert "user.name@domain.co.uk" in valid_emails
    
    def test_format_prices(self):
        """Test price formatting."""
        prices = [1234.56, "987.65", 45.32, "invalid"]
        
        formatted = format_prices(prices)
        
        assert formatted[0] == "$1,234.56"
        assert formatted[1] == "$987.65"
        assert formatted[2] == "$45.32"
        assert formatted[3] == "$0.00"
        
        # Test with different currency
        euro_formatted = format_prices(prices, "EUR")
        assert euro_formatted[0] == "€1,234.56"
    
    def test_calculate_ages(self):
        """Test age calculation for lists."""
        today = date.today()
        birth_dates = [
            (today.year - 25, today.month, today.day),
            (today.year - 30, today.month, today.day),
            "invalid-date",
            None
        ]
        
        # Convert to date objects for first two
        birth_date_objs = [
            date(*birth_dates[0]),
            date(*birth_dates[1]),
            birth_dates[2],
            birth_dates[3]
        ]
        
        ages = calculate_ages(birth_date_objs)
        
        assert ages[0] == 25
        assert ages[1] == 30
        assert ages[2] is None
        assert ages[3] is None
    
    def test_generate_slugs(self):
        """Test slug generation for lists."""
        texts = [
            "Hello World!",
            "  Multiple   Spaces  ",
            "Special@Characters#Here",
            ""
        ]
        
        slugs = generate_slugs(texts)
        
        assert slugs[0] == "hello-world"
        assert slugs[1] == "multiple-spaces"
        assert slugs[2] == "specialcharactershere"
        assert slugs[3] == ""
    
    def test_mask_sensitive_fields(self):
        """Test masking sensitive fields in datasets."""
        data = [
            {"name": "John", "ssn": "123456789", "cc": "4111111111111111"},
            {"name": "Jane", "ssn": "987654321", "cc": "5555555555554444"}
        ]
        
        masked = mask_sensitive_fields(data, ["ssn", "cc"])
        
        assert masked[0]["name"] == "John"
        assert masked[0]["ssn"] == "*****6789"
        assert masked[0]["cc"] == "************1111"
        assert masked[1]["name"] == "Jane"
        assert masked[1]["ssn"] == "*****4321"
        assert masked[1]["cc"] == "************4444"
    
    def test_extract_numeric_data(self):
        """Test numeric data extraction from text lists."""
        texts = [
            "Price: $123.45, Quantity: 67",
            "Temperature: -5.5°C, Humidity: 45%",
            "No numbers here"
        ]
        
        numeric_data = extract_numeric_data(texts)
        
        assert 123.45 in numeric_data[0]
        assert 67.0 in numeric_data[0]
        assert -5.5 in numeric_data[1]
        assert 45.0 in numeric_data[1]
        assert len(numeric_data[2]) == 0


class TestDataTransformation:
    """Test data transformation utilities."""
    
    def test_transform_to_csv(self):
        """Test CSV transformation."""
        data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Los Angeles"}
        ]
        
        csv_output = transform_to_csv(data)
        
        lines = csv_output.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        assert 'name,age,city' in lines[0]
        assert 'John,30,New York' in lines[1]
        assert 'Jane,25,Los Angeles' in lines[2]
        
        # Test with custom fieldnames
        custom_csv = transform_to_csv(data, ['name', 'city'])
        lines = custom_csv.strip().split('\n')
        assert len(lines) == 3
        assert 'name,city' in lines[0]
        assert 'John,New York' in lines[1]
    
    def test_transform_to_json(self):
        """Test JSON transformation."""
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        json_output = transform_to_json(data)
        parsed = json.loads(json_output)
        
        assert len(parsed) == 2
        assert parsed[0]["name"] == "John"
        assert parsed[1]["name"] == "Jane"
        
        # Test with single dict
        single_data = {"name": "John", "age": 30}
        single_json = transform_to_json(single_data)
        single_parsed = json.loads(single_json)
        assert single_parsed["name"] == "John"
    
    def test_transform_to_xml(self):
        """Test XML transformation."""
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        xml_output = transform_to_xml(data)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_output)
        assert root.tag == 'data'
        assert len(root) == 2
        
        first_row = root[0]
        assert first_row.tag == 'row'
        assert first_row.find('name').text == 'John'
        assert first_row.find('age').text == '30'
        
        # Test with custom names
        custom_xml = transform_to_xml(data, 'users', 'user')
        root = ET.fromstring(custom_xml)
        assert root.tag == 'users'
        assert root[0].tag == 'user'


class TestDataAnalysis:
    """Test data analysis utilities."""
    
    def test_analyze_data_quality(self):
        """Test data quality analysis."""
        data = [
            {"name": "John", "email": "john@example.com", "age": 30},
            {"name": "Jane", "email": "", "age": None},
            {"name": "Bob", "email": "bob@example.com", "age": 25},
            {"name": "", "email": "alice@example.com", "age": 35}
        ]
        
        quality = analyze_data_quality(data)
        
        assert quality['total_records'] == 4
        assert quality['complete_records'] == 1  # Only first record is complete
        assert quality['completeness_rate'] == 25.0
        
        # Check field stats
        field_stats = quality['field_stats']
        assert field_stats['name']['non_empty_count'] == 3
        assert field_stats['name']['completeness_rate'] == 75.0
        assert field_stats['email']['non_empty_count'] == 3
        assert field_stats['age']['non_empty_count'] == 2
    
    def test_detect_duplicates(self):
        """Test duplicate detection."""
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"},
            {"name": "John", "email": "john@example.com"},  # Duplicate
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Jane", "email": "jane@example.com"}   # Duplicate
        ]
        
        duplicates = detect_duplicates(data)
        
        assert len(duplicates) == 2
        # Check that duplicates are found (indices may vary)
        duplicate_pairs = [tuple(sorted(pair)) for pair in duplicates]
        assert (0, 2) in duplicate_pairs or (2, 0) in duplicate_pairs
        assert (1, 4) in duplicate_pairs or (4, 1) in duplicate_pairs
        
        # Test with specific key fields
        key_duplicates = detect_duplicates(data, ['name'])
        assert len(key_duplicates) >= 2  # Should find more duplicates with just name
    
    def test_find_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50]  # 50 is an outlier
        
        outliers = find_outliers(numbers, 'iqr')
        
        assert len(outliers) >= 1
        assert 10 in outliers  # Index of 50 should be detected as outlier
    
    def test_find_outliers_zscore(self):
        """Test outlier detection using Z-score method."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50]  # 50 is an outlier
        
        outliers = find_outliers(numbers, 'zscore')
        
        assert len(outliers) >= 1
        assert 10 in outliers  # Index of 50 should be detected as outlier
    
    def test_find_outliers_empty(self):
        """Test outlier detection with empty data."""
        outliers = find_outliers([])
        assert outliers == []
        
        outliers = find_outliers([1, 2, 3])
        assert outliers == []  # No outliers in small, uniform dataset


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_handle_unicode_characters(self):
        """Test handling of Unicode characters."""
        text = "Héllo Wörld 🌍"
        cleaned = self.processor.clean_text(text)
        assert "Héllo" in cleaned
        assert "Wörld" in cleaned
        
        slug = self.processor.generate_slug(text)
        assert "héllo" in slug.lower()
    
    def test_handle_very_long_strings(self):
        """Test handling of very long strings."""
        long_text = "a" * 10000
        cleaned = self.processor.clean_text(long_text)
        assert len(cleaned) == 10000
        
        slug = self.processor.generate_slug(long_text)
        assert len(slug) <= 10000
    
    def test_handle_nested_data_structures(self):
        """Test handling of deeply nested data structures."""
        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": "deep value"
                    }
                }
            }
        }
        
        flattened = self.processor.flatten_dict(nested)
        assert "level1.level2.level3.level4" in flattened
        assert flattened["level1.level2.level3.level4"] == "deep value"
    
    def test_handle_mixed_data_types(self):
        """Test handling of mixed data types in processing."""
        data = [
            {"value": "123"},
            {"value": 123},
            {"value": 123.45},
            {"value": None},
            {"value": "invalid"}
        ]
        
        processors = [("value", self.processor.extract_numbers)]
        processed = self.processor.process_data_batch(data, processors)
        
        # Should handle different types gracefully
        assert len(processed) == 5
        assert isinstance(processed[0]["value"], list)
        assert isinstance(processed[1]["value"], list)
        assert isinstance(processed[2]["value"], list)
    
    def test_handle_invalid_json_in_parse_json_safe(self):
        """Test safe JSON parsing with various invalid inputs."""
        invalid_inputs = [
            "",
            None,
            "not json",
            '{"incomplete": json',
            '["unclosed array"',
            '{"key": undefined}',
            'null',
            'true',
            'false'
        ]
        
        for invalid_input in invalid_inputs:
            result = self.processor.parse_json_safe(invalid_input)
            assert result is None or isinstance(result, (dict, list, str, int, float, bool, type(None)))
    
    def test_handle_empty_datasets_in_analysis(self):
        """Test analysis functions with empty datasets."""
        empty_data = []
        
        quality = analyze_data_quality(empty_data)
        assert quality['total_records'] == 0
        assert quality['completeness_rate'] == 0
        
        duplicates = detect_duplicates(empty_data)
        assert duplicates == []
        
        outliers = find_outliers([])
        assert outliers == []
    
    def test_handle_special_characters_in_transformation(self):
        """Test data transformation with special characters."""
        data = [
            {"name": "John \"The Man\"", "description": "Has, commas; and: colons"},
            {"name": "Jane\nDoe", "description": "New\nLine\tCharacters"}
        ]
        
        csv_output = transform_to_csv(data)
        lines = csv_output.strip().split('\n')
        
        # Should properly escape special characters
        assert len(lines) == 3
        assert '"John ""The Man"""' in lines[1] or 'John' in lines[1]
    
    def test_handle_large_numbers_in_statistics(self):
        """Test statistics calculation with very large numbers."""
        large_numbers = [1e10, 2e10, 3e10, 4e10, 5e10]
        stats = self.processor.calculate_statistics(large_numbers)
        
        assert stats['count'] == 5
        assert stats['sum'] == 1.5e11
        assert stats['mean'] == 3e10
        assert stats['max'] == 5e10
        assert stats['min'] == 1e10


class TestPerformanceAndScalability:
    """Test performance and scalability."""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_process_large_dataset_efficiently(self):
        """Test processing of large datasets."""
        import time
        
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50)
            })
        
        processors = [
            ("name", self.processor.clean_text),
            ("email", self.processor.normalize_email)
        ]
        
        start_time = time.time()
        processed = self.processor.process_data_batch(large_data, processors)
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert len(processed) == 1000
        assert duration < 5.0  # Should complete within 5 seconds
        assert processed[0]["name"] == "User 0"
        assert processed[0]["email"] == "user0@example.com"
    
    def test_calculate_statistics_on_large_dataset(self):
        """Test statistics calculation on large dataset."""
        import time
        
        # Create large number list
        large_numbers = list(range(10000))
        
        start_time = time.time()
        stats = self.processor.calculate_statistics(large_numbers)
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert stats['count'] == 10000
        assert stats['mean'] == 4999.5
        assert duration < 1.0  # Should complete within 1 second
    
    def test_group_large_dataset_efficiently(self):
        """Test grouping of large dataset."""
        import time
        
        # Create large dataset with groups
        large_data = []
        departments = ["IT", "HR", "Finance", "Marketing"]
        for i in range(5000):
            large_data.append({
                "name": f"User {i}",
                "department": departments[i % len(departments)]
            })
        
        start_time = time.time()
        grouped = self.processor.group_by_key(large_data, "department")
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert len(grouped) == 4
        assert len(grouped["IT"]) == 1250
        assert duration < 2.0  # Should complete within 2 seconds
    
    def test_transform_large_dataset_to_csv(self):
        """Test CSV transformation of large dataset."""
        import time
        
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                "id": i,
                "name": f"User {i}",
                "value": i * 10
            })
        
        start_time = time.time()
        csv_output = transform_to_csv(large_data)
        end_time = time.time()
        
        duration = end_time - start_time
        
        lines = csv_output.strip().split('\n')
        assert len(lines) == 1001  # Header + 1000 data rows
        assert duration < 2.0  # Should complete within 2 seconds
        assert len(csv_output) > 50000  # Should be substantial output


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_complete_data_processing_pipeline(self):
        """Test complete data processing pipeline."""
        # Raw data with various issues
        raw_data = [
            {"name": "  John Doe  ", "email": "JOHN@EXAMPLE.COM", "phone": "(123) 456-7890", "age": "1990-05-15"},
            {"name": "  Jane Smith  ", "email": "jane.smith@company.com", "phone": "+44 20 7946 0958", "age": "25/12/1985"},
            {"name": "", "email": "invalid-email", "phone": "123", "age": "invalid-date"},
            {"name": "Bob Johnson", "email": "bob@domain.org", "phone": "", "age": None}
        ]
        
        # Define processing pipeline
        processors = [
            ("name", self.processor.clean_text),
            ("email", self.processor.normalize_email),
            ("phone", self.processor.normalize_phone),
            ("age", self.processor.calculate_age)
        ]
        
        # Process data
        processed_data = self.processor.process_data_batch(raw_data, processors)
        
        # Clean dataset (remove invalid records)
        cleaned_data = clean_dataset(processed_data)
        
        # Analyze quality
        quality = analyze_data_quality(cleaned_data)
        
        # Transform to different formats
        csv_output = transform_to_csv(cleaned_data)
        json_output = transform_to_json(cleaned_data)
        
        # Verify results
        assert len(cleaned_data) >= 2  # At least 2 valid records
        assert quality['completeness_rate'] > 50
        assert len(csv_output) > 0
        assert len(json_output) > 0
        
        # Check specific transformations
        valid_records = [r for r in cleaned_data if r.get('email')]
        assert len(valid_records) >= 2
        assert all('@' in record['email'] for record in valid_records)
    
    def test_user_data_enrichment_pipeline(self):
        """Test user data enrichment pipeline."""
        users = [
            {"first_name": "John", "last_name": "Doe", "birth_date": "1990-05-15", "salary": "50000"},
            {"first_name": "Jane", "last_name": "Smith", "birth_date": "1985-12-25", "salary": "75000"}
        ]
        
        # Enrich data
        enriched_users = []
        for user in users:
            enriched = user.copy()
            
            # Add full name
            enriched['full_name'] = f"{user['first_name']} {user['last_name']}"
            
            # Add age
            enriched['age'] = self.processor.calculate_age(user['birth_date'])
            
            # Add formatted salary
            enriched['formatted_salary'] = self.processor.format_currency(user['salary'])
            
            # Add slug
            enriched['slug'] = self.processor.generate_slug(enriched['full_name'])
            
            enriched_users.append(enriched)
        
        # Verify enrichment
        assert len(enriched_users) == 2
        assert enriched_users[0]['full_name'] == "John Doe"
        assert enriched_users[0]['age'] > 30
        assert enriched_users[0]['formatted_salary'] == "$50,000.00"
        assert enriched_users[0]['slug'] == "john-doe"
        
        # Analyze enriched data
        quality = analyze_data_quality(enriched_users)
        assert quality['completeness_rate'] == 100.0
    
    def test_financial_data_processing_pipeline(self):
        """Test financial data processing pipeline."""
        transactions = [
            {"date": "2023-01-01", "amount": "1234.56", "type": "income", "description": "Salary"},
            {"date": "2023-01-05", "amount": "-234.56", "type": "expense", "description": "Grocery shopping"},
            {"date": "2023-01-10", "amount": "3456.78", "type": "income", "description": "Bonus"},
            {"date": "2023-01-15", "amount": "-123.45", "type": "expense", "description": "Gas"}
        ]
        
        # Process transactions
        processed_transactions = []
        for transaction in transactions:
            processed = transaction.copy()
            
            # Convert amount to float and format
            amount = float(transaction['amount'])
            processed['amount_float'] = amount
            processed['formatted_amount'] = self.processor.format_currency(abs(amount))
            
            # Add transaction type indicator
            processed['is_income'] = amount > 0
            
            processed_transactions.append(processed)
        
        # Calculate statistics
        amounts = [t['amount_float'] for t in processed_transactions]
        stats = self.processor.calculate_statistics(amounts)
        
        # Group by type
        grouped = self.processor.group_by_key(processed_transactions, 'is_income')
        
        # Verify results
        assert len(processed_transactions) == 4
        assert stats['count'] == 4
        assert len(grouped) == 2
        assert len(grouped[True]) == 2  # Income transactions
        assert len(grouped[False]) == 2  # Expense transactions
        
        # Calculate totals
        income_total = sum(t['amount_float'] for t in grouped[True])
        expense_total = sum(t['amount_float'] for t in grouped[False])
        net_total = income_total + expense_total  # expenses are negative
        
        assert net_total > 0  # Should have positive net income
