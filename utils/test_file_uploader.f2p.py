"""
F2P tests for file uploader utility.
These tests would fail on the base branch and pass after the fixes.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from utils.file_uploader import (
    FileUploader,
    create_image_uploader,
    create_document_uploader,
    create_media_uploader,
    format_file_size,
    get_file_extension,
    is_valid_filename
)


class TestFileUploader(TestCase):
    """Test FileUploader class functionality."""
    
    def setUp(self):
        self.uploader = FileUploader('test_uploads')
        self.test_file_content = b"Test file content"
    
    def create_test_file(self, name: str, content: bytes = None, size: int = None) -> Mock:
        """Create a mock uploaded file for testing."""
        mock_file = Mock(spec=UploadedFile)
        mock_file.name = name
        mock_file.content_type = 'text/plain'
        
        if content:
            mock_file.read.return_value = content
            mock_file.size = len(content)
        elif size:
            mock_file.size = size
            mock_file.read.return_value = b"x" * size
        else:
            mock_file.size = len(self.test_file_content)
            mock_file.read.return_value = self.test_file_content
        
        mock_file.chunks.return_value = [self.test_file_content]
        return mock_file
    
    def test_file_uploader_initialization(self):
        """Test FileUploader initialization."""
        uploader = FileUploader()
        self.assertEqual(uploader.upload_dir, 'uploads')
        self.assertEqual(uploader.max_file_size, 10 * 1024 * 1024)
        self.assertIn('.jpg', uploader.allowed_extensions)
    
    def test_file_uploader_custom_initialization(self):
        """Test FileUploader with custom parameters."""
        uploader = FileUploader('custom_dir')
        self.assertEqual(uploader.upload_dir, 'custom_dir')
    
    def test_validate_file_success(self):
        """Test successful file validation."""
        test_file = self.create_test_file('test.txt')
        result = self.uploader.validate_file(test_file)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['file_info']['name'], 'test.txt')
        self.assertEqual(result['file_info']['extension'], '.txt')
    
    def test_validate_file_no_file(self):
        """Test validation with no file provided."""
        result = self.uploader.validate_file(None)
        
        self.assertFalse(result['valid'])
        self.assertIn('No file provided', result['errors'])
    
    def test_validate_file_invalid_extension(self):
        """Test validation with invalid file extension."""
        test_file = self.create_test_file('test.exe')
        result = self.uploader.validate_file(test_file)
        
        self.assertFalse(result['valid'])
        self.assertIn('File extension .exe not allowed', result['errors'])
    
    def test_validate_file_too_large(self):
        """Test validation with file too large."""
        large_content = b"x" * (15 * 1024 * 1024)  # 15MB
        test_file = self.create_test_file('large.txt', content=large_content)
        result = self.uploader.validate_file(test_file)
        
        self.assertFalse(result['valid'])
        self.assertIn('exceeds maximum', result['errors'][0])
    
    def test_validate_file_empty(self):
        """Test validation with empty file."""
        test_file = self.create_test_file('empty.txt', content=b'')
        result = self.uploader.validate_file(test_file)
        
        self.assertFalse(result['valid'])
        self.assertIn('File is empty', result['errors'])
    
    def test_validate_file_name_too_long(self):
        """Test validation with filename too long."""
        long_name = 'a' * 260 + '.txt'
        test_file = self.create_test_file(long_name)
        result = self.uploader.validate_file(test_file)
        
        self.assertFalse(result['valid'])
        self.assertIn('File name too long', result['errors'])
    
    def test_generate_unique_filename(self):
        """Test unique filename generation."""
        original_name = 'test.txt'
        unique_name = self.uploader.generate_unique_filename(original_name)
        
        self.assertNotEqual(original_name, unique_name)
        self.assertTrue(unique_name.endswith('.txt'))
        self.assertIn('test_', unique_name)
        self.assertIn('_', unique_name)
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_file_success(self, mock_makedirs, mock_storage):
        """Test successful file upload."""
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        mock_storage.exists.return_value = True
        
        test_file = self.create_test_file('test.txt')
        result = self.uploader.upload_file(test_file)
        
        self.assertTrue(result['success'])
        self.assertIn('file_info', result)
        self.assertEqual(result['file_info']['original_name'], 'test.txt')
        self.assertIn('filename', result['file_info'])
    
    def test_upload_file_validation_failure(self):
        """Test file upload with validation failure."""
        test_file = self.create_test_file('test.exe')  # Invalid extension
        result = self.uploader.upload_file(test_file)
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_file_with_custom_filename(self, mock_makedirs, mock_storage):
        """Test file upload with custom filename."""
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        
        test_file = self.create_test_file('test.txt')
        custom_name = 'custom_file.txt'
        result = self.uploader.upload_file(test_file, custom_name)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_info']['filename'], custom_name)
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_file_storage_error(self, mock_makedirs, mock_storage):
        """Test file upload with storage error."""
        mock_storage.open.side_effect = Exception("Storage error")
        
        test_file = self.create_test_file('test.txt')
        result = self.uploader.upload_file(test_file)
        
        self.assertFalse(result['success'])
        self.assertIn('Upload failed', result['errors'][0])
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_multiple_files(self, mock_makedirs, mock_storage):
        """Test uploading multiple files."""
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        
        files = [
            self.create_test_file('file1.txt'),
            self.create_test_file('file2.txt'),
            self.create_test_file('file3.txt')
        ]
        
        result = self.uploader.upload_multiple_files(files)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['uploaded_files']), 3)
        self.assertEqual(len(result['failed_files']), 0)
        self.assertEqual(result['total_files'], 3)
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_multiple_files_with_failures(self, mock_makedirs, mock_storage):
        """Test uploading multiple files with some failures."""
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        
        files = [
            self.create_test_file('file1.txt'),
            self.create_test_file('file2.exe'),  # Invalid extension
            self.create_test_file('file3.txt')
        ]
        
        result = self.uploader.upload_multiple_files(files)
        
        self.assertFalse(result['success'])
        self.assertEqual(len(result['uploaded_files']), 2)
        self.assertEqual(len(result['failed_files']), 1)
        self.assertEqual(result['total_files'], 3)
    
    @patch('utils.file_uploader.default_storage')
    def test_delete_file_success(self, mock_storage):
        """Test successful file deletion."""
        mock_storage.exists.return_value = True
        mock_storage.delete = Mock()
        
        # Add file to uploaded files list
        self.uploader.uploaded_files.append({
            'filename': 'test.txt',
            'path': 'test_uploads/test.txt'
        })
        
        result = self.uploader.delete_file('test.txt')
        
        self.assertTrue(result['success'])
        mock_storage.delete.assert_called_once()
    
    @patch('utils.file_uploader.default_storage')
    def test_delete_file_not_found(self, mock_storage):
        """Test deleting non-existent file."""
        mock_storage.exists.return_value = False
        
        result = self.uploader.delete_file('nonexistent.txt')
        
        self.assertFalse(result['success'])
        self.assertIn('not found', result['errors'][0])
    
    @patch('utils.file_uploader.default_storage')
    def test_delete_file_error(self, mock_storage):
        """Test file deletion with error."""
        mock_storage.exists.return_value = True
        mock_storage.delete.side_effect = Exception("Delete error")
        
        result = self.uploader.delete_file('test.txt')
        
        self.assertFalse(result['success'])
        self.assertIn('Deletion failed', result['errors'][0])
    
    def test_get_file_info(self):
        """Test getting file information."""
        # Add file to uploaded files list
        file_info = {
            'filename': 'test.txt',
            'path': 'test_uploads/test.txt',
            'size': 100
        }
        self.uploader.uploaded_files.append(file_info)
        
        result = self.uploader.get_file_info('test.txt')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['filename'], 'test.txt')
        self.assertEqual(result['size'], 100)
    
    def test_get_file_info_not_found(self):
        """Test getting info for non-existent file."""
        result = self.uploader.get_file_info('nonexistent.txt')
        
        self.assertIsNone(result)
    
    def test_list_uploaded_files(self):
        """Test listing uploaded files."""
        # Add files to uploaded files list
        self.uploader.uploaded_files.extend([
            {'filename': 'file1.txt', 'size': 100},
            {'filename': 'file2.txt', 'size': 200}
        ])
        
        result = self.uploader.list_uploaded_files()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['filename'], 'file1.txt')
        self.assertEqual(result[1]['filename'], 'file2.txt')
    
    def test_get_upload_stats_empty(self):
        """Test upload statistics with no files."""
        stats = self.uploader.get_upload_stats()
        
        self.assertEqual(stats['total_files'], 0)
        self.assertEqual(stats['total_size'], 0)
        self.assertEqual(stats['average_size'], 0)
        self.assertEqual(stats['file_types'], {})
        self.assertIsNone(stats['largest_file'])
        self.assertIsNone(stats['smallest_file'])
    
    def test_get_upload_stats_with_files(self):
        """Test upload statistics with files."""
        # Add files to uploaded files list
        self.uploader.uploaded_files.extend([
            {'filename': 'file1.txt', 'size': 100, 'filename': 'file1.txt'},
            {'filename': 'file2.jpg', 'size': 200, 'filename': 'file2.jpg'},
            {'filename': 'file3.txt', 'size': 300, 'filename': 'file3.txt'}
        ])
        
        stats = self.uploader.get_upload_stats()
        
        self.assertEqual(stats['total_files'], 3)
        self.assertEqual(stats['total_size'], 600)
        self.assertEqual(stats['average_size'], 200)
        self.assertEqual(stats['file_types']['.txt'], 2)
        self.assertEqual(stats['file_types']['.jpg'], 1)
        self.assertEqual(stats['largest_file']['size'], 300)
        self.assertEqual(stats['smallest_file']['size'], 100)
    
    @patch('utils.file_uploader.default_storage')
    def test_clear_uploads_success(self, mock_storage):
        """Test clearing all uploads successfully."""
        mock_storage.exists.return_value = True
        mock_storage.delete = Mock()
        
        # Add files to uploaded files list
        self.uploader.uploaded_files.extend([
            {'filename': 'file1.txt', 'path': 'test_uploads/file1.txt'},
            {'filename': 'file2.txt', 'path': 'test_uploads/file2.txt'}
        ])
        
        result = self.uploader.clear_uploads()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['deleted_count'], 2)
        self.assertEqual(len(self.uploader.uploaded_files), 0)
    
    def test_set_allowed_extensions(self):
        """Test setting allowed extensions."""
        new_extensions = ['.pdf', '.doc', '.docx']
        self.uploader.set_allowed_extensions(new_extensions)
        
        self.assertEqual(self.uploader.allowed_extensions, new_extensions)
    
    def test_set_allowed_extensions_without_dots(self):
        """Test setting allowed extensions without dots."""
        new_extensions = ['pdf', 'doc', 'docx']
        self.uploader.set_allowed_extensions(new_extensions)
        
        expected = ['.pdf', '.doc', '.docx']
        self.assertEqual(self.uploader.allowed_extensions, expected)
    
    def test_set_max_file_size(self):
        """Test setting maximum file size."""
        new_size = 5 * 1024 * 1024  # 5MB
        self.uploader.set_max_file_size(new_size)
        
        self.assertEqual(self.uploader.max_file_size, new_size)
    
    @patch('utils.file_uploader.default_storage')
    def test_is_file_exists(self, mock_storage):
        """Test checking if file exists."""
        mock_storage.exists.return_value = True
        
        result = self.uploader.is_file_exists('test.txt')
        
        self.assertTrue(result)
        mock_storage.exists.assert_called_once_with('test_uploads/test.txt')


class TestUtilityFunctions(TestCase):
    """Test utility functions."""
    
    def test_create_image_uploader(self):
        """Test creating image uploader."""
        uploader = create_image_uploader()
        
        self.assertEqual(uploader.upload_dir, 'images')
        self.assertIn('.jpg', uploader.allowed_extensions)
        self.assertIn('.png', uploader.allowed_extensions)
        self.assertNotIn('.txt', uploader.allowed_extensions)
        self.assertEqual(uploader.max_file_size, 5 * 1024 * 1024)
    
    def test_create_document_uploader(self):
        """Test creating document uploader."""
        uploader = create_document_uploader()
        
        self.assertEqual(uploader.upload_dir, 'documents')
        self.assertIn('.pdf', uploader.allowed_extensions)
        self.assertIn('.doc', uploader.allowed_extensions)
        self.assertNotIn('.jpg', uploader.allowed_extensions)
        self.assertEqual(uploader.max_file_size, 20 * 1024 * 1024)
    
    def test_create_media_uploader(self):
        """Test creating media uploader."""
        uploader = create_media_uploader()
        
        self.assertEqual(uploader.upload_dir, 'media')
        self.assertIn('.mp4', uploader.allowed_extensions)
        self.assertIn('.jpg', uploader.allowed_extensions)
        self.assertEqual(uploader.max_file_size, 50 * 1024 * 1024)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        test_cases = [
            (0, "0 B"),
            (500, "500.0 B"),
            (1536, "1.5 KB"),
            (2 * 1024 * 1024, "2.0 MB"),
            (3 * 1024 * 1024 * 1024, "3.0 GB")
        ]
        
        for size_bytes, expected in test_cases:
            result = format_file_size(size_bytes)
            self.assertEqual(result, expected)
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        test_cases = [
            ('test.txt', '.txt'),
            ('image.JPG', '.jpg'),
            ('document.pdf', '.pdf'),
            ('no_extension', ''),
            ('multiple.dots.file.txt', '.txt')
        ]
        
        for filename, expected in test_cases:
            result = get_file_extension(filename)
            self.assertEqual(result, expected)
    
    def test_is_valid_filename(self):
        """Test filename validation."""
        valid_names = [
            'test.txt',
            'file_name.doc',
            'file-with-hyphen.pdf',
            'file123.txt',
            'a' * 255  # Max length
        ]
        
        invalid_names = [
            '',  # Empty
            'a' * 256,  # Too long
            'file<test>.txt',  # Invalid characters
            'CON.txt',  # Reserved name
            'PRN.doc',
            'AUX.pdf',
            'NUL.txt',
            'COM1.txt',
            'LPT1.doc'
        ]
        
        for name in valid_names:
            self.assertTrue(is_valid_filename(name), f"Should be valid: {name}")
        
        for name in invalid_names:
            self.assertFalse(is_valid_filename(name), f"Should be invalid: {name}")


class TestEdgeCasesAndErrorHandling(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.uploader = FileUploader('test_uploads')
    
    def test_file_without_name_attribute(self):
        """Test validation of file without name attribute."""
        mock_file = Mock()
        del mock_file.name  # Remove name attribute
        
        result = self.uploader.validate_file(mock_file)
        
        self.assertFalse(result['valid'])
        self.assertIn('No file provided', result['errors'])
    
    def test_file_without_size_attribute(self):
        """Test validation of file without size attribute."""
        mock_file = Mock(spec=UploadedFile)
        mock_file.name = 'test.txt'
        del mock_file.size  # Remove size attribute
        
        result = self.uploader.validate_file(mock_file)
        
        self.assertTrue(result['valid'])  # Should still be valid
        self.assertEqual(result['file_info']['size'], 0)
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_file_chunked_upload(self, mock_makedirs, mock_storage):
        """Test chunked file upload."""
        mock_file = Mock(spec=UploadedFile)
        mock_file.name = 'test.txt'
        mock_file.size = 20
        mock_file.content_type = 'text/plain'
        mock_file.chunks.return_value = [b'chunk1', b'chunk2']
        
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        
        result = self.uploader.upload_file(mock_file)
        
        self.assertTrue(result['success'])
        mock_storage.open.assert_called_once()
    
    @patch('utils.file_uploader.default_storage')
    def test_delete_nonexistent_file_from_list(self, mock_storage):
        """Test deleting file not in uploaded files list."""
        mock_storage.exists.return_value = True
        mock_storage.delete = Mock()
        
        result = self.uploader.delete_file('not_in_list.txt')
        
        self.assertFalse(result['success'])
        self.assertIn('not found', result['errors'][0])
    
    def test_upload_stats_with_zero_size_files(self):
        """Test upload stats with zero-size files."""
        self.uploader.uploaded_files.extend([
            {'filename': 'file1.txt', 'size': 0},
            {'filename': 'file2.txt', 'size': 0}
        ])
        
        stats = self.uploader.get_upload_stats()
        
        self.assertEqual(stats['total_size'], 0)
        self.assertEqual(stats['average_size'], 0)
    
    def test_set_allowed_extensions_empty_list(self):
        """Test setting empty allowed extensions list."""
        self.uploader.set_allowed_extensions([])
        
        self.assertEqual(self.uploader.allowed_extensions, [])
    
    def test_upload_file_with_path_traversal(self):
        """Test upload with path traversal attempt."""
        mock_file = Mock(spec=UploadedFile)
        mock_file.name = '../../../etc/passwd'
        mock_file.size = 100
        mock_file.content_type = 'text/plain'
        mock_file.read.return_value = b'test'
        mock_file.chunks.return_value = [b'test']
        
        # Should still validate (path handling is storage's responsibility)
        result = self.uploader.validate_file(mock_file)
        self.assertTrue(result['valid'])  # Name validation doesn't check path traversal
    
    @patch('utils.file_uploader.default_storage')
    @patch('os.makedirs')
    def test_upload_file_unicode_filename(self, mock_makedirs, mock_storage):
        """Test upload with unicode filename."""
        mock_storage.open.return_value.__enter__.return_value.write = Mock()
        
        mock_file = Mock(spec=UploadedFile)
        mock_file.name = '测试文件.txt'
        mock_file.size = 100
        mock_file.content_type = 'text/plain'
        mock_file.read.return_value = b'test'
        mock_file.chunks.return_value = [b'test']
        
        result = self.uploader.upload_file(mock_file)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_info']['original_name'], '测试文件.txt')


class TestPerformanceAndScalability(TestCase):
    """Test performance and scalability."""
    
    def setUp(self):
        self.uploader = FileUploader('test_uploads')
    
    def test_upload_many_files_performance(self):
        """Test performance with many files."""
        from unittest.mock import patch
        import time
        
        with patch('utils.file_uploader.default_storage') as mock_storage:
            mock_storage.open.return_value.__enter__.return_value.write = Mock()
            
            files = []
            for i in range(100):
                mock_file = Mock()
                mock_file.name = f'file_{i}.txt'
                mock_file.size = 1000
                mock_file.content_type = 'text/plain'
                mock_file.read.return_value = b'x' * 1000
                mock_file.chunks.return_value = [b'x' * 1000]
                files.append(mock_file)
            
            start_time = time.time()
            result = self.uploader.upload_multiple_files(files)
            end_time = time.time()
            
            duration = end_time - start_time
            
            self.assertTrue(result['success'])
            self.assertEqual(len(result['uploaded_files']), 100)
            self.assertLess(duration, 5.0)  # Should complete within 5 seconds
    
    def test_large_upload_stats_calculation(self):
        """Test stats calculation with many files."""
        # Add many files
        for i in range(1000):
            self.uploader.uploaded_files.append({
                'filename': f'file_{i}.txt',
                'size': 1000 + (i % 100)  # Varying sizes
            })
        
        start_time = time.time()
        stats = self.uploader.get_upload_stats()
        end_time = time.time()
        
        duration = end_time - start_time
        
        self.assertEqual(stats['total_files'], 1000)
        self.assertLess(duration, 1.0)  # Should complete within 1 second
