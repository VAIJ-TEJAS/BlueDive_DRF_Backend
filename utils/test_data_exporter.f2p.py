"""
F2P tests for data exporter utility.
These tests would fail on the base branch and pass after the fixes.
"""

import pytest
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO
from unittest.mock import Mock, patch
from utils.data_exporter import (
    DataExporter,
    export_users_to_csv,
    export_products_to_json,
    export_orders_to_xlsx,
    export_report_to_txt,
    format_csv_value,
    format_json_value,
    format_xml_value,
    validate_csv_data,
    validate_json_data,
    validate_xml_data,
    batch_export,
    get_export_statistics
)


class TestDataExporter:
    """Test DataExporter class functionality."""
    
    def setUp(self):
        self.exporter = DataExporter()
        self.sample_data = [
            {'id': 1, 'name': 'John', 'age': 30, 'city': 'New York'},
            {'id': 2, 'name': 'Jane', 'age': 25, 'city': 'London'},
            {'id': 3, 'name': 'Bob', 'age': 35, 'city': 'Paris'}
        ]
        self.single_record = {'id': 1, 'name': 'John', 'age': 30}
    
    def test_exporter_initialization(self):
        """Test DataExporter initialization."""
        exporter = DataExporter()
        expected_formats = ['csv', 'json', 'xml', 'xlsx', 'txt']
        assert exporter.get_supported_formats() == expected_formats
    
    def test_export_to_csv_with_headers(self):
        """Test CSV export with headers."""
        exporter = DataExporter()
        result = exporter.export_to_csv(self.sample_data)
        
        lines = result.strip().split('\n')
        assert len(lines) == 4  # 3 data rows + header
        assert 'id,name,age,city' in lines[0]
        assert '1,John,30,New York' in lines[1]
    
    def test_export_to_csv_without_headers(self):
        """Test CSV export without headers."""
        exporter = DataExporter()
        result = exporter.export_to_csv(self.sample_data, include_headers=False)
        
        lines = result.strip().split('\n')
        assert len(lines) == 3  # Only data rows
        assert '1,John,30,New York' in lines[0]
    
    def test_export_to_csv_custom_delimiter(self):
        """Test CSV export with custom delimiter."""
        exporter = DataExporter()
        result = exporter.export_to_csv(self.sample_data, delimiter=';')
        
        lines = result.strip().split('\n')
        assert 'id;name;age;city' in lines[0]
        assert '1;John;30;New York' in lines[1]
    
    def test_export_to_csv_empty_data(self):
        """Test CSV export with empty data."""
        exporter = DataExporter()
        result = exporter.export_to_csv([])
        
        assert result == ""
    
    def test_export_to_json_list(self):
        """Test JSON export with list data."""
        exporter = DataExporter()
        result = exporter.export_to_json(self.sample_data)
        
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[0]['id'] == 1
        assert parsed[0]['name'] == 'John'
    
    def test_export_to_json_single_dict(self):
        """Test JSON export with single dictionary."""
        exporter = DataExporter()
        result = exporter.export_to_json(self.single_record)
        
        parsed = json.loads(result)
        assert parsed['id'] == 1
        assert parsed['name'] == 'John'
    
    def test_export_to_json_with_options(self):
        """Test JSON export with formatting options."""
        exporter = DataExporter()
        result = exporter.export_to_json(self.sample_data, indent=4, sort_keys=True)
        
        parsed = json.loads(result)
        assert len(parsed) == 3
        # Check that output is properly indented
        assert '    ' in result
    
    def test_export_to_xml(self):
        """Test XML export."""
        exporter = DataExporter()
        result = exporter.export_to_xml(self.sample_data)
        
        # Parse XML to verify structure
        root = ET.fromstring(result)
        assert root.tag == 'data'
        assert len(root) == 3
        
        first_row = root[0]
        assert first_row.tag == 'row'
        assert first_row.find('id').text == '1'
        assert first_row.find('name').text == 'John'
    
    def test_export_to_xml_custom_names(self):
        """Test XML export with custom element names."""
        exporter = DataExporter()
        result = exporter.export_to_xml(self.sample_data, root_name='users', row_name='user')
        
        root = ET.fromstring(result)
        assert root.tag == 'users'
        assert len(root) == 3
        assert root[0].tag == 'user'
    
    def test_export_to_xml_empty_data(self):
        """Test XML export with empty data."""
        exporter = DataExporter()
        result = exporter.export_to_xml([])
        
        root = ET.fromstring(result)
        assert root.tag == 'data'
        assert len(root) == 0
    
    @patch('utils.data_exporter.xlsxwriter.Workbook')
    def test_export_to_xlsx(self, mock_workbook_class):
        """Test XLSX export."""
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.add_worksheet.return_value = mock_worksheet
        mock_workbook_class.return_value = mock_workbook
        
        exporter = DataExporter()
        result = exporter.export_to_xlsx(self.sample_data)
        
        # Verify workbook was created
        mock_workbook_class.assert_called_once()
        mock_workbook.add_worksheet.assert_called_once_with('Sheet1')
        
        # Verify headers were written
        mock_worksheet.write.assert_any_call(0, 0, 'id')
        mock_worksheet.write.assert_any_call(0, 1, 'name')
        
        # Verify data was written
        mock_worksheet.write.assert_any_call(1, 0, 1)
        mock_worksheet.write.assert_any_call(1, 1, 'John')
        
        # Verify workbook was closed
        mock_workbook.close.assert_called_once()
        
        # Should return bytes
        assert isinstance(result, bytes)
    
    @patch('utils.data_exporter.xlsxwriter.Workbook')
    def test_export_to_xlsx_no_headers(self, mock_workbook_class):
        """Test XLSX export without headers."""
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.add_worksheet.return_value = mock_worksheet
        mock_workbook_class.return_value = mock_workbook
        
        exporter = DataExporter()
        result = exporter.export_to_xlsx(self.sample_data, include_headers=False)
        
        # Verify data was written starting from row 0
        mock_worksheet.write.assert_any_call(0, 0, 1)
        mock_worksheet.write.assert_any_call(0, 1, 'John')
    
    def test_export_to_txt(self):
        """Test text export."""
        exporter = DataExporter()
        result = exporter.export_to_txt(self.sample_data)
        
        lines = result.strip().split('\n')
        assert len(lines) == 4  # 3 data rows + header
        assert 'id | name | age | city' in lines[0]
        assert '1 | John | 30 | New York' in lines[1]
    
    def test_export_to_txt_custom_separator(self):
        """Test text export with custom separator."""
        exporter = DataExporter()
        result = exporter.export_to_txt(self.sample_data, separator=' - ')
        
        lines = result.strip().split('\n')
        assert 'id - name - age - city' in lines[0]
        assert '1 - John - 30 - New York' in lines[1]
    
    def test_export_to_txt_no_headers(self):
        """Test text export without headers."""
        exporter = DataExporter()
        result = exporter.export_to_txt(self.sample_data, include_headers=False)
        
        lines = result.strip().split('\n')
        assert len(lines) == 3  # Only data rows
        assert '1 | John | 30 | New York' in lines[0]
    
    def test_export_unsupported_format(self):
        """Test export with unsupported format."""
        exporter = DataExporter()
        
        with pytest.raises(ValueError, match="Unsupported format"):
            exporter.export(self.sample_data, 'pdf')
    
    def test_export_method_csv(self):
        """Test generic export method with CSV format."""
        exporter = DataExporter()
        result = exporter.export(self.sample_data, 'csv')
        
        lines = result.strip().split('\n')
        assert len(lines) == 4
        assert 'id,name,age,city' in lines[0]
    
    def test_export_method_json(self):
        """Test generic export method with JSON format."""
        exporter = DataExporter()
        result = exporter.export(self.sample_data, 'json')
        
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[0]['id'] == 1
    
    def test_validate_data_valid_list(self):
        """Test data validation with valid list data."""
        exporter = DataExporter()
        assert exporter.validate_data(self.sample_data) is True
    
    def test_validate_data_valid_dict(self):
        """Test data validation with valid dict data."""
        exporter = DataExporter()
        assert exporter.validate_data(self.single_record) is True
    
    def test_validate_data_invalid(self):
        """Test data validation with invalid data."""
        exporter = DataExporter()
        assert exporter.validate_data("invalid data") is False
        assert exporter.validate_data([1, 2, 3]) is False
    
    def test_get_data_info_list(self):
        """Test getting data info for list data."""
        exporter = DataExporter()
        info = exporter.get_data_info(self.sample_data)
        
        assert info['type'] == 'list'
        assert info['is_list'] is True
        assert info['is_dict'] is False
        assert info['length'] == 3
        assert info['columns'] == ['id', 'name', 'age', 'city']
        assert info['sample_row'] == self.sample_data[0]
    
    def test_get_data_info_dict(self):
        """Test getting data info for dict data."""
        exporter = DataExporter()
        info = exporter.get_data_info(self.single_record)
        
        assert info['type'] == 'dict'
        assert info['is_list'] is False
        assert info['is_dict'] is True
        assert info['keys'] == ['id', 'name', 'age']
        assert info['sample_data'] == self.single_record


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_export_users_to_csv(self):
        """Test users CSV export utility."""
        users = [
            {'id': 1, 'name': 'John', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane', 'email': 'jane@example.com'}
        ]
        
        result = export_users_to_csv(users)
        lines = result.strip().split('\n')
        
        assert len(lines) == 3
        assert 'id,name,email' in lines[0]
        assert '1,John,john@example.com' in lines[1]
    
    def test_export_products_to_json(self):
        """Test products JSON export utility."""
        products = [
            {'id': 1, 'name': 'Product A', 'price': 10.99},
            {'id': 2, 'name': 'Product B', 'price': 15.99}
        ]
        
        result = export_products_to_json(products)
        parsed = json.loads(result)
        
        assert len(parsed) == 2
        assert parsed[0]['name'] == 'Product A'
        assert parsed[0]['price'] == 10.99
    
    @patch('utils.data_exporter.xlsxwriter.Workbook')
    def test_export_orders_to_xlsx(self, mock_workbook_class):
        """Test orders XLSX export utility."""
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.add_worksheet.return_value = mock_worksheet
        mock_workbook_class.return_value = mock_workbook
        
        orders = [
            {'id': 1, 'customer': 'John', 'total': 100.0},
            {'id': 2, 'customer': 'Jane', 'total': 150.0}
        ]
        
        result = export_orders_to_xlsx(orders)
        
        mock_workbook_class.assert_called_once()
        assert isinstance(result, bytes)
    
    def test_export_report_to_txt(self):
        """Test report text export utility."""
        report_data = [
            {'metric': 'sales', 'value': 1000, 'period': 'Jan'},
            {'metric': 'expenses', 'value': 500, 'period': 'Jan'}
        ]
        
        result = export_report_to_txt(report_data)
        lines = result.strip().split('\n')
        
        assert len(lines) == 3
        assert 'metric | value | period' in lines[0]
        assert 'sales | 1000 | Jan' in lines[1]


class TestFormatFunctions:
    """Test format utility functions."""
    
    def test_format_csv_value(self):
        """Test CSV value formatting."""
        assert format_csv_value(None) == ''
        assert format_csv_value('simple') == 'simple'
        assert format_csv_value('with,comma') == '"with,comma"'
        assert format_csv_value('with"quote') == '"with""quote"'
        assert format_csv_value(123) == '123'
        assert format_csv_value(45.67) == '45.67'
    
    def test_format_json_value(self):
        """Test JSON value formatting."""
        from datetime import datetime
        
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = format_json_value(dt)
        assert result == '2023-01-01T12:00:00'
        
        assert format_json_value('simple') == 'simple'
        assert format_json_value(123) == 123
    
    def test_format_xml_value(self):
        """Test XML value formatting."""
        assert format_xml_value(None) == ''
        assert format_xml_value('simple') == 'simple'
        assert format_xml_value('with&ampersand') == 'with&amp;ampersand'
        assert format_xml_value('with<tag>') == 'with&lt;tag&gt;'
        assert format_xml_value('with"quote') == 'with&quot;quote'
        assert format_xml_value("with'apostrophe") == 'with&apos;apostrophe'
        assert format_xml_value(123) == '123'


class TestValidationFunctions:
    """Test validation utility functions."""
    
    def test_validate_csv_data_valid(self):
        """Test CSV data validation with valid data."""
        data = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'}
        ]
        
        issues = validate_csv_data(data)
        assert len(issues) == 0
    
    def test_validate_csv_data_empty(self):
        """Test CSV data validation with empty data."""
        issues = validate_csv_data([])
        assert len(issues) == 1
        assert 'Data is empty' in issues[0]
    
    def test_validate_csv_data_inconsistent_columns(self):
        """Test CSV data validation with inconsistent columns."""
        data = [
            {'id': 1, 'name': 'John', 'age': 30},
            {'id': 2, 'name': 'Jane'},  # Missing age
            {'id': 3, 'name': 'Bob', 'city': 'NYC'}  # Different column
        ]
        
        issues = validate_csv_data(data)
        assert len(issues) >= 2  # Should detect inconsistent columns
    
    def test_validate_csv_data_newlines(self):
        """Test CSV data validation with newline characters."""
        data = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane\nDoe'}  # Contains newline
        ]
        
        issues = validate_csv_data(data)
        assert len(issues) >= 1
        assert 'newline character' in issues[0]
    
    def test_validate_json_data_valid(self):
        """Test JSON data validation with valid data."""
        data = {'id': 1, 'name': 'John'}
        
        issues = validate_json_data(data)
        assert len(issues) == 0
    
    def test_validate_json_data_invalid(self):
        """Test JSON data validation with invalid data."""
        # Create a non-serializable object
        class UnserializableObject:
            pass
        
        data = {'id': 1, 'obj': UnserializableObject()}
        
        issues = validate_json_data(data)
        assert len(issues) >= 1
        assert 'JSON serializable' in issues[0]
    
    def test_validate_xml_data_valid(self):
        """Test XML data validation with valid data."""
        data = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'}
        ]
        
        issues = validate_xml_data(data)
        assert len(issues) == 0
    
    def test_validate_xml_data_invalid_type(self):
        """Test XML data validation with invalid data type."""
        data = "not a list"
        
        issues = validate_xml_data(data)
        assert len(issues) >= 1
        assert 'must be a list' in issues[0]
    
    def test_validate_xml_data_empty(self):
        """Test XML data validation with empty data."""
        issues = validate_xml_data([])
        assert len(issues) >= 1
        assert 'Data is empty' in issues[0]
    
    def test_validate_xml_data_invalid_keys(self):
        """Test XML data validation with invalid keys."""
        data = [
            {'id': 1, 'name-with-dash': 'John'},  # Invalid XML tag
            {'id': 2, 'name': 'Jane'}
        ]
        
        issues = validate_xml_data(data)
        assert len(issues) >= 1
        assert 'XML tag name' in issues[0]


class TestBatchExport:
    """Test batch export functionality."""
    
    @patch('utils.data_exporter.xlsxwriter.Workbook')
    def test_batch_export_success(self, mock_workbook_class):
        """Test successful batch export."""
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.add_worksheet.return_value = mock_worksheet
        mock_workbook_class.return_value = mock_workbook
        
        data_sets = {
            'users': [{'id': 1, 'name': 'John'}],
            'products': [{'id': 1, 'name': 'Product A'}]
        }
        
        results = batch_export(data_sets, 'json')
        
        assert len(results) == 2
        assert results['users']['success'] is True
        assert results['products']['success'] is True
        assert 'filename' in results['users']
        assert 'filepath' in results['users']
    
    def test_batch_export_with_errors(self):
        """Test batch export with errors."""
        data_sets = {
            'valid': [{'id': 1, 'name': 'John'}],
            'invalid': 'not valid data'
        }
        
        results = batch_export(data_sets, 'json')
        
        assert len(results) == 2
        assert results['valid']['success'] is True
        assert results['invalid']['success'] is False
        assert 'error' in results['invalid']


class TestExportStatistics:
    """Test export statistics functionality."""
    
    def test_get_statistics_list_data(self):
        """Test statistics for list data."""
        data = [
            {'id': 1, 'name': 'John', 'age': 30},
            {'id': 2, 'name': None, 'age': 25},
            {'id': 3, 'name': '', 'age': 35}
        ]
        
        stats = get_export_statistics(data)
        
        assert stats['total_records'] == 3
        assert stats['total_fields'] == 3
        assert stats['null_count'] == 1
        assert stats['empty_string_count'] == 1
        assert stats['data_types']['int'] == 3  # Three id values
        assert stats['data_types']['str'] >= 3  # Names and ages
    
    def test_get_statistics_dict_data(self):
        """Test statistics for dict data."""
        data = {'id': 1, 'name': 'John', 'active': True, 'score': None}
        
        stats = get_export_statistics(data)
        
        assert stats['total_records'] == 1
        assert stats['total_fields'] == 4
        assert stats['null_count'] == 1
        assert stats['empty_string_count'] == 0
        assert stats['data_types']['int'] == 1
        assert stats['data_types']['str'] == 1
        assert stats['data_types']['bool'] == 1
    
    def test_get_statistics_empty_data(self):
        """Test statistics for empty data."""
        stats = get_export_statistics([])
        
        assert stats['total_records'] == 0
        assert stats['total_fields'] == 0
        assert stats['null_count'] == 0
        assert stats['empty_string_count'] == 0


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.exporter = DataExporter()
    
    def test_export_with_none_data(self):
        """Test export with None data."""
        with pytest.raises((TypeError, AttributeError)):
            self.exporter.export_to_json(None)
    
    def test_export_with_mixed_data_types(self):
        """Test export with mixed data types in rows."""
        data = [
            {'id': 1, 'name': 'John', 'score': 100},
            {'id': 2, 'name': 'Jane', 'score': 95.5},
            {'id': 3, 'name': 'Bob', 'score': None}
        ]
        
        # Should handle mixed types gracefully
        result = self.exporter.export_to_json(data)
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[2]['score'] is None
    
    def test_export_with_unicode_characters(self):
        """Test export with unicode characters."""
        data = [
            {'name': '张三', 'city': '北京'},
            {'name': 'José', 'city': 'São Paulo'}
        ]
        
        result = self.exporter.export_to_json(data)
        parsed = json.loads(result)
        assert parsed[0]['name'] == '张三'
        assert parsed[1]['name'] == 'José'
    
    def test_export_with_very_long_values(self):
        """Test export with very long values."""
        long_text = 'x' * 10000
        data = [{'id': 1, 'description': long_text}]
        
        result = self.exporter.export_to_json(data)
        parsed = json.loads(result)
        assert len(parsed[0]['description']) == 10000
    
    def test_export_with_nested_structures(self):
        """Test export with nested data structures."""
        data = [
            {'id': 1, 'profile': {'name': 'John', 'age': 30}},
            {'id': 2, 'profile': {'name': 'Jane', 'age': 25}}
        ]
        
        result = self.exporter.export_to_json(data)
        parsed = json.loads(result)
        assert parsed[0]['profile']['name'] == 'John'
    
    def test_export_with_special_characters_in_csv(self):
        """Test CSV export with special characters."""
        data = [
            {'name': 'John "The Man"', 'description': 'Has, commas, and "quotes"'},
            {'name': 'Jane', 'description': 'Normal text'}
        ]
        
        result = self.exporter.export_to_csv(data)
        
        # Should properly escape quotes and commas
        assert '"John ""The Man"""' in result
        assert '"Has, commas, and ""quotes"""' in result


class TestPerformanceAndScalability:
    """Test performance and scalability."""
    
    def setUp(self):
        self.exporter = DataExporter()
    
    def test_export_large_dataset(self):
        """Test exporting large dataset."""
        import time
        
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'score': i * 10
            })
        
        start_time = time.time()
        result = self.exporter.export_to_json(large_data)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds
        
        # Verify result
        parsed = json.loads(result)
        assert len(parsed) == 1000
        assert parsed[999]['id'] == 999
    
    def test_multiple_format_exports(self):
        """Test exporting same data to multiple formats."""
        import time
        
        data = [
            {'id': i, 'name': f'Item {i}'}
            for i in range(100)
        ]
        
        formats = ['csv', 'json', 'txt']
        results = {}
        
        start_time = time.time()
        
        for format_type in formats:
            results[format_type] = self.exporter.export(data, format_type)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 3.0  # 3 seconds
        
        # Verify all formats have results
        for format_type in formats:
            assert results[format_type] is not None
            assert len(results[format_type]) > 0
    
    def test_memory_usage_with_large_data(self):
        """Test memory usage with large data exports."""
        # This is a basic test - in practice you'd use memory profiling tools
        data = [
            {'id': i, 'data': 'x' * 1000}  # 1KB per row
            for i in range(100)  # 100KB total
        ]
        
        result = self.exporter.export_to_json(data)
        
        # Result should be significantly larger than input data due to JSON formatting
        assert len(result) > 100000  # Should be > 100KB
        
        # Verify data integrity
        parsed = json.loads(result)
        assert len(parsed) == 100
        assert len(parsed[0]['data']) == 1000
