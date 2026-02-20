"""
Simple Data Processor Utility
Basic data processing and transformation functions
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Union, Optional, Callable, Tuple
from datetime import datetime, date
import re
import hashlib
import base64
from decimal import Decimal, InvalidOperation


class DataProcessor:
    """Simple data processor with transformation and analysis capabilities."""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.processing_history = []
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s\.\,\!\?\-\_\@]', '', text)
        
        return text.strip()
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number format.
        
        Args:
            phone: Phone number to normalize
            
        Returns:
            Normalized phone number
        """
        if not isinstance(phone, str):
            phone = str(phone)
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as +XXX XXX XXX XXXX if possible
        if len(digits) == 10:
            return f"+1 {digits[:3]} {digits[3:6]} {digits[6:]}"
        elif len(digits) > 10:
            return f"+{digits[:-10]} {digits[-10:-7]} {digits[-7:-4]} {digits[-4:]}"
        else:
            return digits
    
    def normalize_email(self, email: str) -> str:
        """
        Normalize email address.
        
        Args:
            email: Email address to normalize
            
        Returns:
            Normalized email address
        """
        if not isinstance(email, str):
            email = str(email)
        
        # Convert to lowercase and remove whitespace
        email = email.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if re.match(email_pattern, email):
            return email
        else:
            return ""
    
    def format_currency(self, amount: Union[int, float, str, Decimal], currency: str = 'USD') -> str:
        """
        Format amount as currency.
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        try:
            # Convert to Decimal for precision
            if isinstance(amount, str):
                amount = Decimal(amount.replace(',', ''))
            else:
                amount = Decimal(str(amount))
            
            # Format based on currency
            if currency.upper() == 'USD':
                return f"${amount:,.2f}"
            elif currency.upper() == 'EUR':
                return f"€{amount:,.2f}"
            elif currency.upper() == 'GBP':
                return f"£{amount:,.2f}"
            else:
                return f"{amount:,.2f} {currency.upper()}"
        except (InvalidOperation, ValueError):
            return "0.00"
    
    def calculate_age(self, birth_date: Union[str, date, datetime]) -> Optional[int]:
        """
        Calculate age from birth date.
        
        Args:
            birth_date: Birth date
            
        Returns:
            Age in years or None if invalid
        """
        try:
            if isinstance(birth_date, str):
                # Try different date formats
                formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                for fmt in formats:
                    try:
                        birth_date = datetime.strptime(birth_date, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return None
            elif isinstance(birth_date, datetime):
                birth_date = birth_date.date()
            elif not isinstance(birth_date, date):
                return None
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except Exception:
            return None
    
    def generate_slug(self, text: str) -> str:
        """
        Generate URL-friendly slug from text.
        
        Args:
            text: Text to convert to slug
            
        Returns:
            URL-friendly slug
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase and replace spaces with hyphens
        slug = text.lower().strip()
        
        # Remove special characters except hyphens and underscores
        slug = re.sub(r'[^\w\s\-_]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    def mask_sensitive_data(self, data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """
        Mask sensitive data like credit card numbers.
        
        Args:
            data: Sensitive data to mask
            mask_char: Character to use for masking
            visible_chars: Number of characters to keep visible at the end
            
        Returns:
            Masked data
        """
        if not isinstance(data, str):
            data = str(data)
        
        if len(data) <= visible_chars:
            return data
        
        masked_length = len(data) - visible_chars
        return mask_char * masked_length + data[-visible_chars:]
    
    def calculate_checksum(self, data: Union[str, Dict, List]) -> str:
        """
        Calculate checksum for data integrity verification.
        
        Args:
            data: Data to calculate checksum for
            
        Returns:
            Checksum hash
        """
        if isinstance(data, (dict, list)):
            # Convert to JSON string for consistent hashing
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def encode_base64(self, data: str) -> str:
        """
        Encode data to base64.
        
        Args:
            data: Data to encode
            
        Returns:
            Base64 encoded string
        """
        if not isinstance(data, str):
            data = str(data)
        
        return base64.b64encode(data.encode()).decode()
    
    def decode_base64(self, encoded_data: str) -> str:
        """
        Decode base64 data.
        
        Args:
            encoded_data: Base64 encoded data
            
        Returns:
            Decoded string
        """
        try:
            return base64.b64decode(encoded_data.encode()).decode()
        except Exception:
            return ""
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extract all numbers from text.
        
        Args:
            text: Text to extract numbers from
            
        Returns:
            List of numbers found
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Find all numbers (including decimals)
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(num) for num in numbers]
    
    def calculate_percentage(self, part: Union[int, float], total: Union[int, float]) -> float:
        """
        Calculate percentage.
        
        Args:
            part: Part value
            total: Total value
            
        Returns:
            Percentage (0-100)
        """
        try:
            if total == 0:
                return 0.0
            return (float(part) / float(total)) * 100
        except (ValueError, TypeError):
            return 0.0
    
    def round_to_nearest(self, value: Union[int, float], nearest: Union[int, float] = 1) -> float:
        """
        Round value to nearest specified number.
        
        Args:
            value: Value to round
            nearest: Number to round to nearest
            
        Returns:
            Rounded value
        """
        try:
            return round(float(value) / float(nearest)) * float(nearest)
        except (ValueError, TypeError):
            return 0.0
    
    def validate_credit_card(self, card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(card_number, str):
            card_number = str(card_number)
        
        # Remove spaces and dashes
        card_number = re.sub(r'[\s\-]', '', card_number)
        
        # Check if all digits
        if not card_number.isdigit():
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    def parse_json_safe(self, json_str: str) -> Union[Dict, List, None]:
        """
        Safely parse JSON string.
        
        Args:
            json_str: JSON string to parse
            
        Returns:
            Parsed JSON data or None if invalid
        """
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def flatten_dict(self, data: Dict, separator: str = '.') -> Dict:
        """
        Flatten nested dictionary.
        
        Args:
            data: Dictionary to flatten
            separator: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        def _flatten(obj, parent_key=''):
            items = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    items.extend(_flatten(value, new_key).items())
            else:
                return {parent_key: obj}
            
            return dict(items)
        
        return _flatten(data)
    
    def group_by_key(self, data: List[Dict], key: str) -> Dict[Any, List[Dict]]:
        """
        Group list of dictionaries by key.
        
        Args:
            data: List of dictionaries to group
            key: Key to group by
            
        Returns:
            Grouped dictionary
        """
        groups = {}
        
        for item in data:
            if isinstance(item, dict) and key in item:
                group_key = item[key]
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(item)
        
        return groups
    
    def calculate_statistics(self, numbers: List[Union[int, float]]) -> Dict[str, float]:
        """
        Calculate basic statistics for a list of numbers.
        
        Args:
            numbers: List of numbers
            
        Returns:
            Statistics dictionary
        """
        if not numbers:
            return {
                'count': 0,
                'sum': 0,
                'mean': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0
            }
        
        # Convert to float
        nums = [float(n) for n in numbers]
        
        # Sort for median calculation
        sorted_nums = sorted(nums)
        n = len(sorted_nums)
        
        # Calculate median
        if n % 2 == 0:
            median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        else:
            median = sorted_nums[n//2]
        
        # Calculate mean
        mean = sum(nums) / n
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in nums) / n
        std_dev = variance ** 0.5
        
        return {
            'count': n,
            'sum': sum(nums),
            'mean': mean,
            'median': median,
            'min': min(nums),
            'max': max(nums),
            'std_dev': std_dev
        }
    
    def process_data_batch(
        self, 
        data: List[Dict], 
        processors: List[Tuple[str, Callable]]
    ) -> List[Dict]:
        """
        Process a batch of data with multiple processors.
        
        Args:
            data: List of data dictionaries
            processors: List of (field_name, processor_function) tuples
            
        Returns:
            Processed data
        """
        processed_data = []
        
        for item in data:
            processed_item = item.copy()
            
            for field_name, processor in processors:
                if field_name in processed_item:
                    try:
                        processed_item[field_name] = processor(processed_item[field_name])
                        self.processed_count += 1
                    except Exception:
                        self.error_count += 1
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Processing statistics
        """
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': (self.processed_count / max(1, self.processed_count + self.error_count)) * 100,
            'processing_history': self.processing_history.copy()
        }
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.processed_count = 0
        self.error_count = 0
        self.processing_history = []


# Utility functions for common data processing tasks
def clean_dataset(data: List[Dict]) -> List[Dict]:
    """Clean a dataset by removing empty records and normalizing fields."""
    processor = DataProcessor()
    
    cleaned_data = []
    for record in data:
        if isinstance(record, dict):
            # Remove empty values
            cleaned_record = {k: v for k, v in record.items() if v is not None and v != ''}
            
            # Clean text fields
            for key, value in cleaned_record.items():
                if isinstance(value, str):
                    cleaned_record[key] = processor.clean_text(value)
            
            cleaned_data.append(cleaned_record)
    
    return cleaned_data


def validate_emails(email_list: List[str]) -> List[str]:
    """Validate and normalize a list of email addresses."""
    processor = DataProcessor()
    valid_emails = []
    
    for email in email_list:
        normalized = processor.normalize_email(email)
        if normalized:
            valid_emails.append(normalized)
    
    return valid_emails


def format_prices(prices: List[Union[int, float, str]], currency: str = 'USD') -> List[str]:
    """Format a list of prices as currency."""
    processor = DataProcessor()
    return [processor.format_currency(price, currency) for price in prices]


def calculate_ages(birth_dates: List[Union[str, date, datetime]]) -> List[Optional[int]]:
    """Calculate ages from a list of birth dates."""
    processor = DataProcessor()
    return [processor.calculate_age(birth_date) for birth_date in birth_dates]


def generate_slugs(texts: List[str]) -> List[str]:
    """Generate URL-friendly slugs from a list of texts."""
    processor = DataProcessor()
    return [processor.generate_slug(text) for text in texts]


def mask_sensitive_fields(data: List[Dict], sensitive_fields: List[str]) -> List[Dict]:
    """Mask sensitive fields in a list of dictionaries."""
    processor = DataProcessor()
    masked_data = []
    
    for record in data:
        masked_record = record.copy()
        for field in sensitive_fields:
            if field in masked_record:
                masked_record[field] = processor.mask_sensitive_data(str(masked_record[field]))
        masked_data.append(masked_record)
    
    return masked_data


def extract_numeric_data(text_data: List[str]) -> List[List[float]]:
    """Extract numeric data from a list of text strings."""
    processor = DataProcessor()
    return [processor.extract_numbers(text) for text in text_data]


# Data transformation utilities
def transform_to_csv(data: List[Dict], fieldnames: Optional[List[str]] = None) -> str:
    """Transform list of dictionaries to CSV format."""
    if not data:
        return ""
    
    if not fieldnames:
        fieldnames = list(data[0].keys())
    
    output = []
    
    # Add header
    output.append(','.join(fieldnames))
    
    # Add rows
    for record in data:
        row = []
        for field in fieldnames:
            value = record.get(field, '')
            # Escape quotes and commas
            if isinstance(value, str) and (',' in value or '"' in value):
                value = f'"{value.replace('"', '""')}"'
            row.append(str(value))
        output.append(','.join(row))
    
    return '\n'.join(output)


def transform_to_json(data: Union[List[Dict], Dict], indent: int = 2) -> str:
    """Transform data to JSON format."""
    return json.dumps(data, indent=indent, default=str)


def transform_to_xml(data: List[Dict], root_name: str = 'data', row_name: str = 'row') -> str:
    """Transform list of dictionaries to XML format."""
    root = ET.Element(root_name)
    
    for record in data:
        row = ET.SubElement(root, row_name)
        for key, value in record.items():
            child = ET.SubElement(row, key)
            child.text = str(value) if value is not None else ''
    
    return ET.tostring(root, encoding='unicode')


# Data analysis utilities
def analyze_data_quality(data: List[Dict]) -> Dict[str, Any]:
    """Analyze data quality metrics."""
    if not data:
        return {
            'total_records': 0,
            'complete_records': 0,
            'completeness_rate': 0,
            'field_stats': {}
        }
    
    total_records = len(data)
    field_stats = {}
    
    # Get all fields
    all_fields = set()
    for record in data:
        if isinstance(record, dict):
            all_fields.update(record.keys())
    
    # Analyze each field
    for field in all_fields:
        non_empty_count = sum(1 for record in data 
                            if isinstance(record, dict) and record.get(field) not in [None, ''])
        field_stats[field] = {
            'non_empty_count': non_empty_count,
            'empty_count': total_records - non_empty_count,
            'completeness_rate': (non_empty_count / total_records) * 100
        }
    
    # Calculate overall completeness
    complete_records = sum(1 for record in data 
                         if isinstance(record, dict) and all(record.get(field) not in [None, ''] for field in record.keys()))
    
    return {
        'total_records': total_records,
        'complete_records': complete_records,
        'completeness_rate': (complete_records / total_records) * 100,
        'field_stats': field_stats
    }


def detect_duplicates(data: List[Dict], key_fields: Optional[List[str]] = None) -> List[List[int]]:
    """Detect duplicate records based on key fields."""
    if not data:
        return []
    
    if not key_fields:
        # Use all fields
        key_fields = list(data[0].keys()) if data and isinstance(data[0], dict) else []
    
    # Create signature for each record
    signatures = {}
    duplicates = []
    
    for i, record in enumerate(data):
        if isinstance(record, dict):
            # Create signature from key fields
            signature_parts = []
            for field in key_fields:
                value = record.get(field, '')
                signature_parts.append(str(value))
            
            signature = '|'.join(signature_parts)
            
            if signature in signatures:
                duplicates.append([signatures[signature], i])
            else:
                signatures[signature] = i
    
    return duplicates


def find_outliers(numbers: List[Union[int, float]], method: str = 'iqr') -> List[int]:
    """Find outliers in a list of numbers."""
    if not numbers:
        return []
    
    nums = [float(n) for n in numbers]
    sorted_nums = sorted(nums)
    n = len(sorted_nums)
    
    if method == 'iqr':
        # Interquartile Range method
        q1 = sorted_nums[n // 4]
        q3 = sorted_nums[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [i for i, num in enumerate(nums) if num < lower_bound or num > upper_bound]
        return outliers
    
    elif method == 'zscore':
        # Z-score method
        mean = sum(nums) / n
        std_dev = (sum((x - mean) ** 2 for x in nums) / n) ** 0.5
        
        outliers = [i for i, num in enumerate(nums) if abs((num - mean) / std_dev) > 2]
        return outliers
    
    return []
