"""
Simple Data Exporter Utility
Basic data export functionality with multiple formats
"""

import csv
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Union, Optional, IO
from datetime import datetime
from io import StringIO
import xlsxwriter
import pandas as pd


class DataExporter:
    """Simple data exporter supporting multiple formats."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'xml', 'xlsx', 'txt']
    
    def export_to_csv(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        delimiter: str = ',',
        include_headers: bool = True
    ) -> Union[str, bytes]:
        """
        Export data to CSV format.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename for the export
            delimiter: CSV delimiter character
            include_headers: Whether to include column headers
            
        Returns:
            CSV string or bytes
        """
        if not data:
            return ""
        
        output = StringIO()
        
        if include_headers and data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output, delimiter=delimiter)
            for row in data:
                writer.writerow(row.values())
        
        return output.getvalue()
    
    def export_to_json(
        self, 
        data: Union[List[Dict[str, Any]], Dict[str, Any]], 
        filename: Optional[str] = None,
        indent: int = 2,
        sort_keys: bool = False
    ) -> str:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export (list of dicts or single dict)
            filename: Optional filename for the export
            indent: JSON indentation level
            sort_keys: Whether to sort JSON keys
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, sort_keys=sort_keys, default=str)
    
    def export_to_xml(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        root_name: str = 'data',
        row_name: str = 'row'
    ) -> str:
        """
        Export data to XML format.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename for the export
            root_name: Name for the root XML element
            row_name: Name for row elements
            
        Returns:
            XML string
        """
        root = ET.Element(root_name)
        
        for row_data in data:
            row = ET.SubElement(root, row_name)
            for key, value in row_data.items():
                child = ET.SubElement(row, key)
                child.text = str(value) if value is not None else ''
        
        return ET.tostring(root, encoding='unicode')
    
    def export_to_xlsx(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        sheet_name: str = 'Sheet1',
        include_headers: bool = True
    ) -> bytes:
        """
        Export data to Excel XLSX format.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename for the export
            sheet_name: Name for the Excel sheet
            include_headers: Whether to include column headers
            
        Returns:
            XLSX file as bytes
        """
        output = StringIO()
        
        # Create a workbook and add a worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(sheet_name)
        
        if data and include_headers:
            # Write headers
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write data
            for row_idx, row_data in enumerate(data, start=1):
                for col, header in enumerate(headers):
                    worksheet.write(row_idx, col, row_data.get(header, ''))
        else:
            # Write data without headers
            for row_idx, row_data in enumerate(data):
                for col, value in enumerate(row_data.values()):
                    worksheet.write(row_idx, col, value)
        
        workbook.close()
        return output.getvalue().encode('latin-1')
    
    def export_to_txt(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        separator: str = ' | ',
        include_headers: bool = True
    ) -> str:
        """
        Export data to plain text format.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename for the export
            separator: Column separator
            include_headers: Whether to include column headers
            
        Returns:
            Plain text string
        """
        if not data:
            return ""
        
        lines = []
        
        if include_headers and data:
            headers = list(data[0].keys())
            lines.append(separator.join(headers))
        
        for row_data in data:
            values = [str(row_data.get(key, '')) for key in row_data.keys()]
            lines.append(separator.join(values))
        
        return '\n'.join(lines)
    
    def export(
        self, 
        data: Union[List[Dict[str, Any]], Dict[str, Any]], 
        format_type: str,
        filename: Optional[str] = None,
        **kwargs
    ) -> Union[str, bytes]:
        """
        Export data to specified format.
        
        Args:
            data: Data to export
            format_type: Export format (csv, json, xml, xlsx, txt)
            filename: Optional filename for the export
            **kwargs: Format-specific options
            
        Returns:
            Exported data as string or bytes
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if format_type == 'csv':
            return self.export_to_csv(data, filename, **kwargs)
        elif format_type == 'json':
            return self.export_to_json(data, filename, **kwargs)
        elif format_type == 'xml':
            return self.export_to_xml(data, filename, **kwargs)
        elif format_type == 'xlsx':
            return self.export_to_xlsx(data, filename, **kwargs)
        elif format_type == 'txt':
            return self.export_to_txt(data, filename, **kwargs)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return self.supported_formats.copy()
    
    def validate_data(self, data: Any) -> bool:
        """
        Validate data structure for export.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid for export
        """
        if isinstance(data, dict):
            return True
        elif isinstance(data, list):
            return all(isinstance(row, dict) for row in data)
        return False
    
    def get_data_info(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get information about the data structure.
        
        Args:
            data: Data to analyze
            
        Returns:
            Dictionary with data information
        """
        info = {
            'type': type(data).__name__,
            'is_list': isinstance(data, list),
            'is_dict': isinstance(data, dict)
        }
        
        if isinstance(data, list) and data:
            info['length'] = len(data)
            info['columns'] = list(data[0].keys()) if isinstance(data[0], dict) else []
            info['sample_row'] = data[0] if data else None
        elif isinstance(data, dict):
            info['keys'] = list(data.keys())
            info['sample_data'] = data
        
        return info


# Utility functions for common export scenarios
def export_users_to_csv(users: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """Export user data to CSV format."""
    exporter = DataExporter()
    return exporter.export_to_csv(users, filename)


def export_products_to_json(products: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """Export product data to JSON format."""
    exporter = DataExporter()
    return exporter.export_to_json(products, filename)


def export_orders_to_xlsx(orders: List[Dict[str, Any]], filename: Optional[str] = None) -> bytes:
    """Export order data to Excel format."""
    exporter = DataExporter()
    return exporter.export_to_xlsx(orders, filename)


def export_report_to_txt(report_data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """Export report data to text format."""
    exporter = DataExporter()
    return exporter.export_to_txt(report_data, filename)


# Format-specific utility functions
def format_csv_value(value: Any) -> str:
    """Format a value for CSV export."""
    if value is None:
        return ''
    if isinstance(value, str):
        # Escape quotes and commas
        return f'"{value.replace('"', '""')}"'
    return str(value)


def format_json_value(value: Any) -> Any:
    """Format a value for JSON export."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def format_xml_value(value: Any) -> str:
    """Format a value for XML export."""
    if value is None:
        return ''
    # Escape XML special characters
    if isinstance(value, str):
        return (value.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    return str(value)


# Data validation utilities
def validate_csv_data(data: List[Dict[str, Any]]) -> List[str]:
    """Validate data for CSV export and return list of issues."""
    issues = []
    
    if not data:
        issues.append("Data is empty")
        return issues
    
    # Check for consistent columns
    if len(data) > 1:
        first_row_keys = set(data[0].keys())
        for i, row in enumerate(data[1:], 1):
            if set(row.keys()) != first_row_keys:
                issues.append(f"Row {i} has different columns than first row")
    
    # Check for problematic values
    for i, row in enumerate(data):
        for key, value in row.items():
            if isinstance(value, str) and '\n' in value:
                issues.append(f"Row {i}, column '{key}' contains newline character")
    
    return issues


def validate_json_data(data: Any) -> List[str]:
    """Validate data for JSON export and return list of issues."""
    issues = []
    
    try:
        json.dumps(data, default=str)
    except (TypeError, ValueError) as e:
        issues.append(f"Data is not JSON serializable: {str(e)}")
    
    return issues


def validate_xml_data(data: List[Dict[str, Any]]) -> List[str]:
    """Validate data for XML export and return list of issues."""
    issues = []
    
    if not isinstance(data, list):
        issues.append("Data must be a list for XML export")
        return issues
    
    if not data:
        issues.append("Data is empty")
        return issues
    
    # Check for valid XML tag names
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            issues.append(f"Row {i} is not a dictionary")
            continue
        
        for key in row.keys():
            if not isinstance(key, str) or not key.isalnum() and '_' not in key:
                issues.append(f"Row {i}, key '{key}' is not a valid XML tag name")
    
    return issues


# Batch export utilities
def batch_export(
    data_sets: Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]],
    format_type: str,
    output_dir: str = '.'
) -> Dict[str, Union[str, bytes]]:
    """
    Export multiple data sets to the same format.
    
    Args:
        data_sets: Dictionary of data sets with names as keys
        format_type: Export format
        output_dir: Directory to save files
        
    Returns:
        Dictionary with export results
    """
    exporter = DataExporter()
    results = {}
    
    for name, data in data_sets.items():
        try:
            filename = f"{name}.{format_type}"
            filepath = f"{output_dir}/{filename}"
            
            exported_data = exporter.export(data, format_type, filename)
            results[name] = {
                'data': exported_data,
                'filename': filename,
                'filepath': filepath,
                'success': True
            }
        except Exception as e:
            results[name] = {
                'error': str(e),
                'success': False
            }
    
    return results


# Statistics and analysis utilities
def get_export_statistics(data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about the data for export planning."""
    stats = {
        'total_records': 0,
        'total_fields': 0,
        'data_types': {},
        'null_count': 0,
        'empty_string_count': 0
    }
    
    if isinstance(data, list):
        stats['total_records'] = len(data)
        if data:
            stats['total_fields'] = len(data[0].keys())
            
            # Analyze field types and values
            for row in data:
                for value in row.values():
                    if value is None:
                        stats['null_count'] += 1
                    elif value == '':
                        stats['empty_string_count'] += 1
                    
                    value_type = type(value).__name__
                    stats['data_types'][value_type] = stats['data_types'].get(value_type, 0) + 1
    
    elif isinstance(data, dict):
        stats['total_records'] = 1
        stats['total_fields'] = len(data.keys())
        
        for value in data.values():
            if value is None:
                stats['null_count'] += 1
            elif value == '':
                stats['empty_string_count'] += 1
            
            value_type = type(value).__name__
            stats['data_types'][value_type] = stats['data_types'].get(value_type, 0) + 1
    
    return stats
