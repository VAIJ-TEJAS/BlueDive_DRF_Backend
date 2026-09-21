"""
Simple File Uploader Utility
Basic file handling with validation and storage
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError


class FileUploader:
    """Simple file uploader with validation and storage capabilities."""
    
    def __init__(self, upload_dir: str = 'uploads'):
        self.upload_dir = upload_dir
        self.allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.uploaded_files = []
    
    def validate_file(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Validate uploaded file.
        
        Args:
            file: UploadedFile instance
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': [],
            'file_info': {}
        }
        
        # Check if file is provided
        if not file or not hasattr(file, 'name'):
            result['valid'] = False
            result['errors'].append('No file provided')
            return result
        
        # Get file info
        file_name = file.name
        file_size = file.size if hasattr(file, 'size') else 0
        file_extension = os.path.splitext(file_name)[1].lower()
        
        result['file_info'] = {
            'name': file_name,
            'size': file_size,
            'extension': file_extension,
            'content_type': file.content_type if hasattr(file, 'content_type') else 'unknown'
        }
        
        # Validate file size
        if file_size > self.max_file_size:
            result['valid'] = False
            result['errors'].append(f'File size {file_size} bytes exceeds maximum {self.max_file_size} bytes')
        
        # Validate file extension
        if file_extension not in self.allowed_extensions:
            result['valid'] = False
            result['errors'].append(f'File extension {file_extension} not allowed')
        
        # Validate file name
        if len(file_name) > 255:
            result['valid'] = False
            result['errors'].append('File name too long (max 255 characters)')
        
        # Check for empty file
        if file_size == 0:
            result['valid'] = False
            result['errors'].append('File is empty')
        
        return result
    
    def generate_unique_filename(self, original_name: str) -> str:
        """
        Generate unique filename to prevent conflicts.
        
        Args:
            original_name: Original file name
            
        Returns:
            Unique filename
        """
        name, extension = os.path.splitext(original_name)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(os.path.getmtime(__file__)))
        
        return f"{name}_{unique_id}_{timestamp}{extension}"
    
    def upload_file(self, file: UploadedFile, custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload and store file.
        
        Args:
            file: UploadedFile instance
            custom_filename: Optional custom filename
            
        Returns:
            Dictionary with upload results
        """
        # Validate file first
        validation_result = self.validate_file(file)
        
        if not validation_result['valid']:
            return {
                'success': False,
                'errors': validation_result['errors'],
                'file_info': validation_result['file_info']
            }
        
        try:
            # Generate filename
            if custom_filename:
                filename = custom_filename
            else:
                filename = self.generate_unique_filename(file.name)
            
            # Create upload directory if it doesn't exist
            upload_path = os.path.join(self.upload_dir, filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            
            # Save file
            if hasattr(file, 'chunks'):
                # Handle chunked uploads
                with default_storage.open(upload_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
            else:
                # Handle simple uploads
                with default_storage.open(upload_path, 'wb') as destination:
                    destination.write(file.read())
            
            # Store upload info
            upload_info = {
                'original_name': file.name,
                'filename': filename,
                'path': upload_path,
                'size': file.size,
                'content_type': file.content_type if hasattr(file, 'content_type') else 'unknown',
                'upload_time': str(int(os.path.getmtime(__file__)))
            }
            
            self.uploaded_files.append(upload_info)
            
            return {
                'success': True,
                'file_info': upload_info,
                'validation': validation_result['file_info']
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f'Upload failed: {str(e)}'],
                'file_info': validation_result['file_info']
            }
    
    def upload_multiple_files(self, files: List[UploadedFile]) -> Dict[str, Any]:
        """
        Upload multiple files.
        
        Args:
            files: List of UploadedFile instances
            
        Returns:
            Dictionary with batch upload results
        """
        results = {
            'success': True,
            'uploaded_files': [],
            'failed_files': [],
            'total_files': len(files)
        }
        
        for file in files:
            upload_result = self.upload_file(file)
            
            if upload_result['success']:
                results['uploaded_files'].append(upload_result['file_info'])
            else:
                results['failed_files'].append({
                    'filename': file.name,
                    'errors': upload_result['errors']
                })
                results['success'] = False
        
        return results
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """
        Delete uploaded file.
        
        Args:
            filename: Filename to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            file_path = os.path.join(self.upload_dir, filename)
            
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                
                # Remove from uploaded files list
                self.uploaded_files = [
                    f for f in self.uploaded_files 
                    if f['filename'] != filename
                ]
                
                return {
                    'success': True,
                    'message': f'File {filename} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'errors': [f'File {filename} not found']
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [f'Deletion failed: {str(e)}']
            }
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get information about uploaded file.
        
        Args:
            filename: Filename to get info for
            
        Returns:
            File information dictionary or None
        """
        for file_info in self.uploaded_files:
            if file_info['filename'] == filename:
                return file_info
        
        return None
    
    def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        List all uploaded files.
        
        Returns:
            List of file information dictionaries
        """
        return self.uploaded_files.copy()
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Get upload statistics.
        
        Returns:
            Dictionary with upload statistics
        """
        if not self.uploaded_files:
            return {
                'total_files': 0,
                'total_size': 0,
                'average_size': 0,
                'file_types': {},
                'largest_file': None,
                'smallest_file': None
            }
        
        total_size = sum(f['size'] for f in self.uploaded_files)
        file_types = {}
        
        for file_info in self.uploaded_files:
            ext = os.path.splitext(file_info['filename'])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        largest_file = max(self.uploaded_files, key=lambda f: f['size'])
        smallest_file = min(self.uploaded_files, key=lambda f: f['size'])
        
        return {
            'total_files': len(self.uploaded_files),
            'total_size': total_size,
            'average_size': total_size // len(self.uploaded_files),
            'file_types': file_types,
            'largest_file': largest_file,
            'smallest_file': smallest_file
        }
    
    def clear_uploads(self) -> Dict[str, Any]:
        """
        Clear all uploaded files.
        
        Returns:
            Dictionary with clear results
        """
        deleted_count = 0
        errors = []
        
        for file_info in self.uploaded_files.copy():
            result = self.delete_file(file_info['filename'])
            if result['success']:
                deleted_count += 1
            else:
                errors.extend(result['errors'])
        
        return {
            'success': len(errors) == 0,
            'deleted_count': deleted_count,
            'errors': errors
        }
    
    def set_allowed_extensions(self, extensions: List[str]) -> None:
        """
        Set allowed file extensions.
        
        Args:
            extensions: List of allowed extensions
        """
        self.allowed_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                                  for ext in extensions]
    
    def set_max_file_size(self, size_bytes: int) -> None:
        """
        Set maximum file size.
        
        Args:
            size_bytes: Maximum file size in bytes
        """
        self.max_file_size = size_bytes
    
    def is_file_exists(self, filename: str) -> bool:
        """
        Check if file exists in upload directory.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = os.path.join(self.upload_dir, filename)
        return default_storage.exists(file_path)


# Utility functions
def create_image_uploader() -> FileUploader:
    """Create uploader configured for images only."""
    uploader = FileUploader('images')
    uploader.set_allowed_extensions(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
    uploader.set_max_file_size(5 * 1024 * 1024)  # 5MB
    return uploader


def create_document_uploader() -> FileUploader:
    """Create uploader configured for documents only."""
    uploader = FileUploader('documents')
    uploader.set_allowed_extensions(['.pdf', '.doc', '.docx', '.txt', '.rtf'])
    uploader.set_max_file_size(20 * 1024 * 1024)  # 20MB
    return uploader


def create_media_uploader() -> FileUploader:
    """Create uploader configured for media files."""
    uploader = FileUploader('media')
    uploader.set_allowed_extensions(['.mp4', '.avi', '.mov', '.mp3', '.wav', '.jpg', '.jpeg', '.png'])
    uploader.set_max_file_size(50 * 1024 * 1024)  # 50MB
    return uploader


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including dot)
    """
    return os.path.splitext(filename)[1].lower()


def is_valid_filename(filename: str) -> bool:
    """
    Check if filename is valid.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
    if any(char in filename for char in invalid_chars):
        return False
    
    # Check length
    if len(filename) == 0 or len(filename) > 255:
        return False
    
    # Check for reserved names (Windows)
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    return True
