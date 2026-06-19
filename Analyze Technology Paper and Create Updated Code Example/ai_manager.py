"""
Fibonacci Grid AI - Backend for Dataset and Model Management

This module provides the backend functionality for handling AI datasets and models,
including upload, compression, storage, and retrieval using the Fibonacci Grid System.
"""

import os
import sys
import json
import hashlib
import time
import shutil
import base64
from typing import List, Dict, Any, Tuple, Optional, Union, BinaryIO
import numpy as np
import io
import zipfile
import csv
import re
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from fibonacci_grid_e2e.backend.core import FibonacciGrid, CompressionDB
except ImportError:
    # If running directly, try relative import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.core import FibonacciGrid, CompressionDB


class DatasetManager:
    """
    Manages AI datasets using the Fibonacci Grid System for efficient storage.
    
    This class handles dataset upload, compression, indexing, and retrieval.
    """
    
    def __init__(self, storage_dir: str = "datasets", grid_size: int = 100):
        """
        Initialize the dataset manager.
        
        Args:
            storage_dir: Directory for storing datasets
            grid_size: Size of the Fibonacci grid for compression
        """
        self.storage_dir = storage_dir
        self.grid_size = grid_size
        self.compression_db = CompressionDB(grid_size)
        self.datasets = {}
        self.dataset_index = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing dataset index if available
        self._load_index()
    
    def _load_index(self):
        """Load the dataset index from disk."""
        index_path = os.path.join(self.storage_dir, "dataset_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    self.dataset_index = json.load(f)
            except Exception as e:
                print(f"Error loading dataset index: {e}")
                self.dataset_index = {}
    
    def _save_index(self):
        """Save the dataset index to disk."""
        index_path = os.path.join(self.storage_dir, "dataset_index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump(self.dataset_index, f, indent=2)
        except Exception as e:
            print(f"Error saving dataset index: {e}")
    
    def upload_dataset(self, file_obj: BinaryIO, filename: str, 
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Upload and process a dataset file.
        
        Args:
            file_obj: File-like object containing the dataset
            filename: Original filename
            metadata: Optional metadata about the dataset
            
        Returns:
            Dictionary containing dataset information
        """
        # Generate dataset ID
        timestamp = int(time.time())
        file_hash = hashlib.md5(f"{filename}_{timestamp}".encode()).hexdigest()[:12]
        dataset_id = f"dataset_{file_hash}"
        
        # Create dataset directory
        dataset_dir = os.path.join(self.storage_dir, dataset_id)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Save original file
        original_path = os.path.join(dataset_dir, filename)
        with open(original_path, 'wb') as f:
            file_obj.seek(0)
            shutil.copyfileobj(file_obj, f)
        
        # Process dataset based on file type
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.csv', '.txt', '.json']:
            dataset_info = self._process_text_dataset(original_path, dataset_id, file_extension)
        elif file_extension in ['.zip', '.gz', '.tar']:
            dataset_info = self._process_archive_dataset(original_path, dataset_id)
        elif file_extension in ['.pdf']:
            dataset_info = self._process_pdf_dataset(original_path, dataset_id)
        else:
            dataset_info = self._process_binary_dataset(original_path, dataset_id)
        
        # Add metadata
        if metadata:
            dataset_info['metadata'] = metadata
        else:
            dataset_info['metadata'] = {}
        
        # Add basic info
        dataset_info.update({
            'id': dataset_id,
            'filename': filename,
            'original_size': os.path.getsize(original_path),
            'upload_time': timestamp,
            'file_type': file_extension[1:] if file_extension else 'unknown'
        })
        
        # Save to index
        self.dataset_index[dataset_id] = dataset_info
        self._save_index()
        
        return dataset_info
    
    def _process_text_dataset(self, file_path: str, dataset_id: str, 
                             file_extension: str) -> Dict[str, Any]:
        """
        Process a text-based dataset file.
        
        Args:
            file_path: Path to the dataset file
            dataset_id: Unique identifier for the dataset
            file_extension: File extension
            
        Returns:
            Dictionary containing processing information
        """
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Compress the content
        compressed = self.compression_db.compress(content)
        
        # Save compressed data
        compressed_path = os.path.join(self.storage_dir, dataset_id, "compressed.json")
        with open(compressed_path, 'w') as f:
            json.dump(compressed, f)
        
        # Generate preview
        preview = self._generate_preview(content, file_extension)
        preview_path = os.path.join(self.storage_dir, dataset_id, "preview.json")
        with open(preview_path, 'w') as f:
            json.dump(preview, f)
        
        return {
            'compressed_path': compressed_path,
            'preview_path': preview_path,
            'compression_ratio': compressed['compression_ratio'],
            'compressed_size': compressed['compressed_size'],
            'preview': preview,
            'format': 'text',
            'extension': file_extension
        }
    
    def _process_archive_dataset(self, file_path: str, dataset_id: str) -> Dict[str, Any]:
        """
        Process an archive dataset file.
        
        Args:
            file_path: Path to the dataset file
            dataset_id: Unique identifier for the dataset
            
        Returns:
            Dictionary containing processing information
        """
        # Create extraction directory
        extract_dir = os.path.join(self.storage_dir, dataset_id, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extract archive
        try:
            shutil.unpack_archive(file_path, extract_dir)
        except Exception as e:
            return {
                'error': f"Failed to extract archive: {str(e)}",
                'format': 'archive',
                'is_processed': False
            }
        
        # Process each file in the archive
        processed_files = []
        total_original_size = 0
        total_compressed_size = 0
        
        for root, _, files in os.walk(extract_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, extract_dir)
                
                # Skip very large files and binary files
                if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB
                    processed_files.append({
                        'path': rel_path,
                        'size': os.path.getsize(file_path),
                        'is_processed': False,
                        'reason': 'File too large'
                    })
                    continue
                
                # Try to process as text
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Compress the content
                    compressed = self.compression_db.compress(content)
                    
                    # Save compressed data
                    compressed_dir = os.path.join(self.storage_dir, dataset_id, "compressed_files")
                    os.makedirs(compressed_dir, exist_ok=True)
                    
                    compressed_path = os.path.join(compressed_dir, f"{rel_path}.json")
                    os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
                    
                    with open(compressed_path, 'w') as f:
                        json.dump(compressed, f)
                    
                    file_info = {
                        'path': rel_path,
                        'original_size': len(content),
                        'compressed_size': compressed['compressed_size'],
                        'compression_ratio': compressed['compression_ratio'],
                        'compressed_path': os.path.relpath(compressed_path, self.storage_dir),
                        'is_processed': True
                    }
                    
                    processed_files.append(file_info)
                    total_original_size += len(content)
                    total_compressed_size += compressed['compressed_size']
                    
                except Exception as e:
                    processed_files.append({
                        'path': rel_path,
                        'size': os.path.getsize(file_path),
                        'is_processed': False,
                        'reason': f"Failed to process: {str(e)}"
                    })
        
        # Calculate overall compression ratio
        overall_ratio = total_original_size / total_compressed_size if total_compressed_size > 0 else 1.0
        
        return {
            'format': 'archive',
            'extracted_dir': extract_dir,
            'processed_files': processed_files,
            'total_files': len(processed_files),
            'processed_count': sum(1 for f in processed_files if f.get('is_processed', False)),
            'total_original_size': total_original_size,
            'total_compressed_size': total_compressed_size,
            'overall_compression_ratio': overall_ratio,
            'is_processed': True
        }
    
    def _process_pdf_dataset(self, file_path: str, dataset_id: str) -> Dict[str, Any]:
        """
        Process a PDF dataset file.
        
        Args:
            file_path: Path to the dataset file
            dataset_id: Unique identifier for the dataset
            
        Returns:
            Dictionary containing processing information
        """
        # For PDF processing, we'd typically use a library like PyPDF2 or pdfplumber
        # Here we'll use a simplified approach for demonstration
        
        try:
            # Try to extract text using external tools if available
            import subprocess
            text_path = os.path.join(self.storage_dir, dataset_id, "extracted_text.txt")
            
            try:
                # Try using pdftotext if available
                subprocess.run(['pdftotext', file_path, text_path], check=True)
                
                # Read extracted text
                with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
            except (subprocess.SubprocessError, FileNotFoundError):
                # Fallback to a simple binary read
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
            
            # Compress the content
            compressed = self.compression_db.compress(content)
            
            # Save compressed data
            compressed_path = os.path.join(self.storage_dir, dataset_id, "compressed.json")
            with open(compressed_path, 'w') as f:
                json.dump(compressed, f)
            
            # Generate preview
            preview = self._generate_preview(content, '.txt')
            preview_path = os.path.join(self.storage_dir, dataset_id, "preview.json")
            with open(preview_path, 'w') as f:
                json.dump(preview, f)
            
            return {
                'compressed_path': compressed_path,
                'preview_path': preview_path,
                'compression_ratio': compressed['compression_ratio'],
                'compressed_size': compressed['compressed_size'],
                'preview': preview,
                'format': 'pdf',
                'is_processed': True
            }
            
        except Exception as e:
            return {
                'error': f"Failed to process PDF: {str(e)}",
                'format': 'pdf',
                'is_processed': False
            }
    
    def _process_binary_dataset(self, file_path: str, dataset_id: str) -> Dict[str, Any]:
        """
        Process a binary dataset file.
        
        Args:
            file_path: Path to the dataset file
            dataset_id: Unique identifier for the dataset
            
        Returns:
            Dictionary containing processing information
        """
        # For binary files, we'll store metadata but won't attempt compression
        file_size = os.path.getsize(file_path)
        
        # Try to detect if it's a known binary format
        format_info = self._detect_binary_format(file_path)
        
        return {
            'format': 'binary',
            'binary_format': format_info.get('format', 'unknown'),
            'format_details': format_info,
            'size': file_size,
            'is_processed': False,
            'reason': 'Binary file not processed for compression'
        }
    
    def _detect_binary_format(self, file_path: str) -> Dict[str, Any]:
        """
        Detect the format of a binary file.
        
        Args:
            file_path: Path to the binary file
            
        Returns:
            Dictionary containing format information
        """
        # Read the first few bytes to detect format
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        # Check for common file signatures
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            return {'format': 'png', 'category': 'image'}
        elif header.startswith(b'\xff\xd8\xff'):
            return {'format': 'jpeg', 'category': 'image'}
        elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
            return {'format': 'gif', 'category': 'image'}
        elif header.startswith(b'PK\x03\x04'):
            return {'format': 'zip', 'category': 'archive'}
        elif header.startswith(b'%PDF'):
            return {'format': 'pdf', 'category': 'document'}
        elif header.startswith(b'\x1f\x8b'):
            return {'format': 'gzip', 'category': 'archive'}
        
        # If no specific format detected
        return {'format': 'unknown', 'category': 'binary'}
    
    def _generate_preview(self, content: str, file_extension: str) -> Dict[str, Any]:
        """
        Generate a preview of the dataset content.
        
        Args:
            content: Dataset content
            file_extension: File extension
            
        Returns:
            Dictionary containing preview information
        """
        preview = {}
        
        # Limit content size for preview
        if len(content) > 10000:
            preview_content = content[:10000] + "... (truncated)"
        else:
            preview_content = content
        
        preview['content'] = preview_content
        
        # For CSV files, try to extract column information
        if file_extension == '.csv':
            try:
                csv_reader = csv.reader(io.StringIO(content[:5000]))
                headers = next(csv_reader)
                preview['headers'] = headers
                
                # Sample a few rows
                sample_rows = []
                for _ in range(5):
                    try:
                        sample_rows.append(next(csv_reader))
                    except StopIteration:
                        break
                
                preview['sample_rows'] = sample_rows
                preview['column_count'] = len(headers)
                
            except Exception as e:
                preview['csv_error'] = str(e)
        
        # For JSON files, try to extract structure
        elif file_extension == '.json':
            try:
                # Try to parse the first part of the JSON
                json_data = json.loads(content[:10000] + ']' if '[' in content[:100] else '}')
                
                if isinstance(json_data, list) and len(json_data) > 0:
                    preview['structure'] = 'array'
                    preview['sample_item'] = json_data[0] if len(json_data) > 0 else None
                    preview['item_count_estimate'] = content.count('{')
                elif isinstance(json_data, dict):
                    preview['structure'] = 'object'
                    preview['keys'] = list(json_data.keys())
                
            except Exception as e:
                preview['json_error'] = str(e)
        
        # Calculate some basic statistics
        preview['char_count'] = len(content)
        preview['line_count'] = content.count('\n') + 1
        preview['word_estimate'] = len(re.findall(r'\b\w+\b', content[:10000])) * (len(content) / min(len(content), 10000))
        
        return preview
    
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get information about a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary containing dataset information
        """
        if dataset_id in self.dataset_index:
            return self.dataset_index[dataset_id]
        else:
            return {'error': 'Dataset not found'}
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets.
        
        Returns:
            List of dictionaries containing dataset information
        """
        return [
            {
                'id': dataset_id,
                'filename': info.get('filename', 'unknown'),
                'upload_time': info.get('upload_time', 0),
                'file_type': info.get('file_type', 'unknown'),
                'original_size': info.get('original_size', 0),
                'compressed_size': info.get('compressed_size', 0) if 'compressed_size' in info else None,
                'compression_ratio': info.get('compression_ratio', 0) if 'compression_ratio' in info else None,
                'is_processed': info.get('is_processed', True),
                'metadata': info.get('metadata', {})
            }
            for dataset_id, info in self.dataset_index.items()
        ]
    
    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Delete a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary containing deletion status
        """
        if dataset_id not in self.dataset_index:
            return {'error': 'Dataset not found'}
        
        # Remove dataset directory
        dataset_dir = os.path.join(self.storage_dir, dataset_id)
        try:
            shutil.rmtree(dataset_dir)
        except Exception as e:
            return {'error': f"Failed to delete dataset files: {str(e)}"}
        
        # Remove from index
        dataset_info = self.dataset_index.pop(dataset_id)
        self._save_index()
        
        return {
            'status': 'deleted',
            'dataset_id': dataset_id,
            'filename': dataset_info.get('filename', 'unknown')
        }
    
    def get_dataset_content(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get the content of a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary containing dataset content
        """
        if dataset_id not in self.dataset_index:
            return {'error': 'Dataset not found'}
        
        dataset_info = self.dataset_index[dataset_id]
        
        # Check if dataset is processed
        if not dataset_info.get('is_processed', True):
            return {
                'error': 'Dataset not processed',
                'reason': dataset_info.get('reason', 'Unknown reason')
            }
        
        # Handle different formats
        if dataset_info.get('format') == 'text':
            compressed_path = dataset_info.get('compressed_path')
            
            if not compressed_path or not os.path.exists(compressed_path):
                return {'error': 'Compressed data not found'}
            
            try:
                with open(compressed_path, 'r') as f:
                    compressed = json.load(f)
                
                decompressed = self.compression_db.decompress(compressed)
                
                if not decompressed.get('success', False):
                    return {'error': 'Decompression failed', 'details': decompressed.get('error', 'Unknown error')}
                
                return {
                    'content': decompressed['data'],
                    'original_size': decompressed['original_size']
                }
                
            except Exception as e:
                return {'error': f"Failed to read compressed data: {str(e)}"}
                
        elif dataset_info.get('format') == 'archive':
            # For archives, return list of processed files
            return {
                'format': 'archive',
                'processed_files': dataset_info.get('processed_files', []),
                'total_files': dataset_info.get('total_files', 0),
                'processed_count': dataset_info.get('processed_count', 0)
            }
            
        elif dataset_info.get('format') == 'pdf':
            compressed_path = dataset_info.get('compressed_path')
            
            if not compressed_path or not os.path.exists(compressed_path):
                return {'error': 'Compressed data not found'}
            
            try:
                with open(compressed_path, 'r') as f:
                    compressed = json.load(f)
                
                decompressed = self.compression_db.decompress(compressed)
                
                if not decompressed.get('success', False):
                    return {'error': 'Decompression failed', 'details': decompressed.get('error', 'Unknown error')}
                
                return {
                    'content': decompressed['data'],
                    'original_size': decompressed['original_size']
                }
                
            except Exception as e:
                return {'error': f"Failed to read compressed data: {str(e)}"}
                
        else:
            return {'error': 'Unsupported format', 'format': dataset_info.get('format', 'unknown')}
    
    def get_archive_file_content(self, dataset_id: str, file_path: str) -> Dict[str, Any]:
        """
        Get the content of a file within an archive dataset.
        
        Args:
            dataset_id: Dataset identifier
            file_path: Path to the file within the archive
            
        Returns:
            Dictionary containing file content
        """
        if dataset_id not in self.dataset_index:
            return {'error': 'Dataset not found'}
        
        dataset_info = self.dataset_index[dataset_id]
        
        if dataset_info.get('format') != 'archive':
            return {'error': 'Not an archive dataset'}
        
        # Find the file in processed files
        processed_files = dataset_info.get('processed_files', [])
        file_info = None
        
        for pf in processed_files:
            if pf.get('path') == file_path:
                file_info = pf
                break
        
        if not file_info:
            return {'error': 'File not found in archive'}
        
        if not file_info.get('is_processed', False):
            return {
                'error': 'File not processed',
                'reason': file_info.get('reason', 'Unknown reason')
            }
        
        compressed_path = os.path.join(self.storage_dir, file_info.get('compressed_path', ''))
        
        if not os.path.exists(compressed_path):
            return {'error': 'Compressed data not found'}
        
        try:
            with open(compressed_path, 'r') as f:
                compressed = json.load(f)
            
            decompressed = self.compression_db.decompress(compressed)
            
            if not decompressed.get('success', False):
                return {'error': 'Decompression failed', 'details': decompressed.get('error', 'Unknown error')}
            
            return {
                'content': decompressed['data'],
                'original_size': decompressed['original_size']
            }
            
        except Exception as e:
            return {'error': f"Failed to read compressed data: {str(e)}"}


class ModelManager:
    """
    Manages AI models using the Fibonacci Grid System for efficient training and storage.
    
    This class handles model upload, training, compression, and inference.
    """
    
    def __init__(self, storage_dir: str = "models", grid_size: int = 100):
        """
        Initialize the model manager.
        
        Args:
            storage_dir: Directory for storing models
            grid_size: Size of the Fibonacci grid for compression
        """
        self.storage_dir = storage_dir
        self.grid_size = grid_size
        self.grid = FibonacciGrid(grid_size)
        self.compression_db = CompressionDB(grid_size)
        self.models = {}
        self.model_index = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing model index if available
        self._load_index()
    
    def _load_index(self):
        """Load the model index from disk."""
        index_path = os.path.join(self.storage_dir, "model_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    self.model_index = json.load(f)
            except Exception as e:
                print(f"Error loading model index: {e}")
                self.model_index = {}
    
    def _save_index(self):
        """Save the model index to disk."""
        index_path = os.path.join(self.storage_dir, "model_index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump(self.model_index, f, indent=2)
        except Exception as e:
            print(f"Error saving model index: {e}")
    
    def upload_model(self, file_obj: BinaryIO, filename: str, 
                    metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Upload and process a model file.
        
        Args:
            file_obj: File-like object containing the model
            filename: Original filename
            metadata: Optional metadata about the model
            
        Returns:
            Dictionary containing model information
        """
        # Generate model ID
        timestamp = int(time.time())
        file_hash = hashlib.md5(f"{filename}_{timestamp}".encode()).hexdigest()[:12]
        model_id = f"model_{file_hash}"
        
        # Create model directory
        model_dir = os.path.join(self.storage_dir, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save original file
        original_path = os.path.join(model_dir, filename)
        with open(original_path, 'wb') as f:
            file_obj.seek(0)
            shutil.copyfileobj(file_obj, f)
        
        # Process model based on file type
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.json', '.txt']:
            model_info = self._process_text_model(original_path, model_id, file_extension)
        elif file_extension in ['.bin', '.pt', '.pth', '.h5', '.ckpt', '.pb']:
            model_info = self._process_binary_model(original_path, model_id, file_extension)
        elif file_extension in ['.zip', '.gz', '.tar']:
            model_info = self._process_archive_model(original_path, model_id)
        else:
            model_info = self._process_unknown_model(original_path, model_id)
        
        # Add metadata
        if metadata:
            model_info['metadata'] = metadata
        else:
            model_info['metadata'] = {}
        
        # Add basic info
        model_info.update({
            'id': model_id,
            'filename': filename,
            'original_size': os.path.getsize(original_path),
            'upload_time': timestamp,
            'file_type': file_extension[1:] if file_extension else 'unknown'
        })
        
        # Save to index
        self.model_index[model_id] = model_info
        self._save_index()
        
        return model_info
    
    def _process_text_model(self, file_path: str, model_id: str, 
                           file_extension: str) -> Dict[str, Any]:
        """
        Process a text-based model file.
        
        Args:
            file_path: Path to the model file
            model_id: Unique identifier for the model
            file_extension: File extension
            
        Returns:
            Dictionary containing processing information
        """
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Compress the content
        compressed = self.compression_db.compress(content)
        
        # Save compressed data
        compressed_path = os.path.join(self.storage_dir, model_id, "compressed.json")
        with open(compressed_path, 'w') as f:
            json.dump(compressed, f)
        
        # Try to determine model type
        model_type = self._detect_model_type(content, file_extension)
        
        return {
            'compressed_path': compressed_path,
            'compression_ratio': compressed['compression_ratio'],
            'compressed_size': compressed['compressed_size'],
            'model_type': model_type,
            'format': 'text',
            'extension': file_extension,
            'is_processed': True
        }
    
    def _process_binary_model(self, file_path: str, model_id: str, 
                             file_extension: str) -> Dict[str, Any]:
        """
        Process a binary model file.
        
        Args:
            file_path: Path to the model file
            model_id: Unique identifier for the model
            file_extension: File extension
            
        Returns:
            Dictionary containing processing information
        """
        # For binary models, we'll store metadata but won't attempt compression
        file_size = os.path.getsize(file_path)
        
        # Determine model type based on extension
        model_type = self._detect_model_type_from_extension(file_extension)
        
        return {
            'format': 'binary',
            'model_type': model_type,
            'size': file_size,
            'extension': file_extension,
            'is_processed': False,
            'reason': 'Binary model not processed for compression'
        }
    
    def _process_archive_model(self, file_path: str, model_id: str) -> Dict[str, Any]:
        """
        Process an archive model file.
        
        Args:
            file_path: Path to the model file
            model_id: Unique identifier for the model
            
        Returns:
            Dictionary containing processing information
        """
        # Create extraction directory
        extract_dir = os.path.join(self.storage_dir, model_id, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extract archive
        try:
            shutil.unpack_archive(file_path, extract_dir)
        except Exception as e:
            return {
                'error': f"Failed to extract archive: {str(e)}",
                'format': 'archive',
                'is_processed': False
            }
        
        # Process each file in the archive
        processed_files = []
        model_files = []
        config_files = []
        
        for root, _, files in os.walk(extract_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, extract_dir)
                file_extension = os.path.splitext(filename)[1].lower()
                
                file_info = {
                    'path': rel_path,
                    'size': os.path.getsize(file_path),
                    'extension': file_extension
                }
                
                # Identify model and config files
                if file_extension in ['.bin', '.pt', '.pth', '.h5', '.ckpt', '.pb']:
                    file_info['type'] = 'model'
                    model_files.append(file_info)
                elif file_extension in ['.json', '.yaml', '.yml', '.config']:
                    file_info['type'] = 'config'
                    config_files.append(file_info)
                    
                    # Try to read config file for additional info
                    try:
                        if file_extension == '.json':
                            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                config_content = json.load(f)
                            file_info['config_content'] = config_content
                    except Exception:
                        pass
                else:
                    file_info['type'] = 'other'
                
                processed_files.append(file_info)
        
        # Try to determine model type from config files
        model_type = 'unknown'
        for config in config_files:
            if 'config_content' in config:
                detected_type = self._detect_model_type_from_config(config['config_content'])
                if detected_type != 'unknown':
                    model_type = detected_type
                    break
        
        return {
            'format': 'archive',
            'extracted_dir': extract_dir,
            'processed_files': processed_files,
            'model_files': model_files,
            'config_files': config_files,
            'total_files': len(processed_files),
            'model_type': model_type,
            'is_processed': True
        }
    
    def _process_unknown_model(self, file_path: str, model_id: str) -> Dict[str, Any]:
        """
        Process a model file of unknown type.
        
        Args:
            file_path: Path to the model file
            model_id: Unique identifier for the model
            
        Returns:
            Dictionary containing processing information
        """
        # For unknown files, we'll store metadata but won't attempt processing
        file_size = os.path.getsize(file_path)
        
        return {
            'format': 'unknown',
            'size': file_size,
            'is_processed': False,
            'reason': 'Unknown file format'
        }
    
    def _detect_model_type(self, content: str, file_extension: str) -> str:
        """
        Detect the type of model from its content.
        
        Args:
            content: Model file content
            file_extension: File extension
            
        Returns:
            String indicating the model type
        """
        # Check for common model type indicators in content
        content_lower = content.lower()
        
        if '"model_type"' in content_lower:
            # Try to extract model_type from JSON
            try:
                data = json.loads(content)
                if 'model_type' in data:
                    return data['model_type']
            except Exception:
                pass
        
        # Check for common model frameworks
        if 'transformers' in content_lower:
            if 'gpt' in content_lower:
                return 'gpt'
            elif 'bert' in content_lower:
                return 'bert'
            elif 't5' in content_lower:
                return 't5'
            else:
                return 'transformer'
        elif 'pytorch' in content_lower or 'torch.' in content_lower:
            return 'pytorch'
        elif 'tensorflow' in content_lower or 'tf.' in content_lower:
            return 'tensorflow'
        elif 'keras' in content_lower:
            return 'keras'
        
        # Fallback to extension-based detection
        return self._detect_model_type_from_extension(file_extension)
    
    def _detect_model_type_from_extension(self, file_extension: str) -> str:
        """
        Detect the type of model from its file extension.
        
        Args:
            file_extension: File extension
            
        Returns:
            String indicating the model type
        """
        if file_extension == '.pt' or file_extension == '.pth':
            return 'pytorch'
        elif file_extension == '.h5':
            return 'keras'
        elif file_extension == '.pb':
            return 'tensorflow'
        elif file_extension == '.ckpt':
            return 'checkpoint'
        elif file_extension == '.bin':
            return 'binary'
        else:
            return 'unknown'
    
    def _detect_model_type_from_config(self, config: Dict[str, Any]) -> str:
        """
        Detect the type of model from its configuration.
        
        Args:
            config: Model configuration dictionary
            
        Returns:
            String indicating the model type
        """
        # Check for common model type indicators in config
        if 'model_type' in config:
            return config['model_type']
        elif 'architectures' in config:
            arch = config['architectures']
            if isinstance(arch, list) and len(arch) > 0:
                arch_name = arch[0].lower()
                if 'gpt' in arch_name:
                    return 'gpt'
                elif 'bert' in arch_name:
                    return 'bert'
                elif 't5' in arch_name:
                    return 't5'
                else:
                    return arch[0]
        
        # Check for framework-specific keys
        if 'torch_dtype' in config or 'pytorch' in str(config).lower():
            return 'pytorch'
        elif 'tensorflow' in str(config).lower():
            return 'tensorflow'
        elif 'keras' in str(config).lower():
            return 'keras'
        
        return 'unknown'
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dictionary containing model information
        """
        if model_id in self.model_index:
            return self.model_index[model_id]
        else:
            return {'error': 'Model not found'}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models.
        
        Returns:
            List of dictionaries containing model information
        """
        return [
            {
                'id': model_id,
                'filename': info.get('filename', 'unknown'),
                'upload_time': info.get('upload_time', 0),
                'file_type': info.get('file_type', 'unknown'),
                'model_type': info.get('model_type', 'unknown'),
                'original_size': info.get('original_size', 0),
                'compressed_size': info.get('compressed_size', 0) if 'compressed_size' in info else None,
                'compression_ratio': info.get('compression_ratio', 0) if 'compression_ratio' in info else None,
                'is_processed': info.get('is_processed', True),
                'metadata': info.get('metadata', {})
            }
            for model_id, info in self.model_index.items()
        ]
    
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dictionary containing deletion status
        """
        if model_id not in self.model_index:
            return {'error': 'Model not found'}
        
        # Remove model directory
        model_dir = os.path.join(self.storage_dir, model_id)
        try:
            shutil.rmtree(model_dir)
        except Exception as e:
            return {'error': f"Failed to delete model files: {str(e)}"}
        
        # Remove from index
        model_info = self.model_index.pop(model_id)
        self._save_index()
        
        return {
            'status': 'deleted',
            'model_id': model_id,
            'filename': model_info.get('filename', 'unknown')
        }
    
    def train_model(self, model_id: str, dataset_ids: List[str], 
                   params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Train a model using datasets.
        
        Args:
            model_id: Model identifier
            dataset_ids: List of dataset identifiers
            params: Training parameters
            
        Returns:
            Dictionary containing training status
        """
        # This is a placeholder for actual training implementation
        # In a real system, this would integrate with ML frameworks
        
        if model_id not in self.model_index:
            return {'error': 'Model not found'}
        
        # Create training record
        training_id = f"training_{int(time.time())}_{model_id[:8]}"
        training_dir = os.path.join(self.storage_dir, model_id, "training", training_id)
        os.makedirs(training_dir, exist_ok=True)
        
        # Save training parameters
        if params:
            with open(os.path.join(training_dir, "params.json"), 'w') as f:
                json.dump(params, f, indent=2)
        
        # Save dataset references
        with open(os.path.join(training_dir, "datasets.json"), 'w') as f:
            json.dump(dataset_ids, f, indent=2)
        
        # Update model info
        model_info = self.model_index[model_id]
        
        if 'training_history' not in model_info:
            model_info['training_history'] = []
        
        training_record = {
            'id': training_id,
            'timestamp': int(time.time()),
            'dataset_ids': dataset_ids,
            'params': params or {},
            'status': 'initiated'
        }
        
        model_info['training_history'].append(training_record)
        self._save_index()
        
        return {
            'training_id': training_id,
            'model_id': model_id,
            'status': 'initiated',
            'message': 'Training initiated (simulated)'
        }
    
    def get_training_status(self, model_id: str, training_id: str) -> Dict[str, Any]:
        """
        Get the status of a training job.
        
        Args:
            model_id: Model identifier
            training_id: Training job identifier
            
        Returns:
            Dictionary containing training status
        """
        if model_id not in self.model_index:
            return {'error': 'Model not found'}
        
        model_info = self.model_index[model_id]
        
        if 'training_history' not in model_info:
            return {'error': 'No training history found'}
        
        for training in model_info['training_history']:
            if training.get('id') == training_id:
                return training
        
        return {'error': 'Training job not found'}
    
    def chat_with_model(self, model_id: str, message: str, 
                       chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chat with a trained model.
        
        Args:
            model_id: Model identifier
            message: User message
            chat_history: Previous chat history
            
        Returns:
            Dictionary containing model response
        """
        # This is a placeholder for actual model inference
        # In a real system, this would integrate with ML frameworks
        
        if model_id not in self.model_index:
            return {'error': 'Model not found'}
        
        model_info = self.model_index[model_id]
        
        # Generate a simulated response based on model type
        model_type = model_info.get('model_type', 'unknown')
        
        # Create a deterministic but varied response based on the input
        seed = sum(ord(c) for c in message)
        np.random.seed(seed)
        
        # Get some words from the message to echo back
        words = message.split()
        if len(words) > 3:
            selected_words = [words[i] for i in np.random.choice(len(words), min(3, len(words)), replace=False)]
        else:
            selected_words = words
        
        # Generate response based on model type
        if model_type == 'gpt':
            response = f"As a GPT-style model compressed with the Fibonacci Grid System, I understand your interest in {', '.join(selected_words)}. The grid patterns allow me to efficiently process and respond to your query while maintaining contextual understanding."
        elif model_type == 'bert':
            response = f"Using BERT architecture optimized with Fibonacci Grid compression, I've analyzed your message about {', '.join(selected_words)}. This approach allows for bidirectional context understanding with significantly reduced memory footprint."
        elif model_type in ['transformer', 't5']:
            response = f"The Fibonacci Grid-enhanced transformer model has processed your query regarding {', '.join(selected_words)}. The grid's special mathematical properties enable more efficient attention mechanisms and token processing."
        else:
            response = f"I've processed your message about {', '.join(selected_words)} using the Fibonacci Grid System. This novel approach allows for efficient pattern recognition and response generation with minimal computational resources."
        
        # Add some variability
        suffixes = [
            "Would you like to know more about how the grid system enhances AI capabilities?",
            "Is there a specific aspect of the Fibonacci Grid System you'd like me to elaborate on?",
            "The grid's pattern recognition capabilities are particularly useful for this type of query.",
            "I can provide more detailed information if you're interested in the technical aspects."
        ]
        
        response += " " + suffixes[seed % len(suffixes)]
        
        # Log the interaction
        chat_log_dir = os.path.join(self.storage_dir, model_id, "chat_logs")
        os.makedirs(chat_log_dir, exist_ok=True)
        
        log_entry = {
            'timestamp': int(time.time()),
            'user_message': message,
            'model_response': response
        }
        
        with open(os.path.join(chat_log_dir, f"chat_{int(time.time())}.json"), 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        return {
            'response': response,
            'model_id': model_id,
            'model_type': model_type,
            'timestamp': int(time.time())
        }


class AIManager:
    """
    Main manager class for the Fibonacci Grid AI system.
    
    This class provides a unified interface to dataset and model management.
    """
    
    def __init__(self, base_dir: str = "fibonacci_grid_ai", grid_size: int = 100):
        """
        Initialize the AI manager.
        
        Args:
            base_dir: Base directory for storing AI data
            grid_size: Size of the Fibonacci grid
        """
        self.base_dir = base_dir
        self.grid_size = grid_size
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Initialize dataset and model managers
        self.dataset_manager = DatasetManager(
            storage_dir=os.path.join(base_dir, "datasets"),
            grid_size=grid_size
        )
        
        self.model_manager = ModelManager(
            storage_dir=os.path.join(base_dir, "models"),
            grid_size=grid_size
        )
        
        # Initialize grid and compression DB
        self.grid = FibonacciGrid(grid_size)
        self.compression_db = CompressionDB(grid_size)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the AI system.
        
        Returns:
            Dictionary containing system information
        """
        dataset_count = len(self.dataset_manager.dataset_index)
        model_count = len(self.model_manager.model_index)
        
        # Calculate total storage usage
        dataset_size = sum(
            info.get('original_size', 0)
            for info in self.dataset_manager.dataset_index.values()
        )
        
        compressed_dataset_size = sum(
            info.get('compressed_size', 0)
            for info in self.dataset_manager.dataset_index.values()
            if 'compressed_size' in info
        )
        
        model_size = sum(
            info.get('original_size', 0)
            for info in self.model_manager.model_index.values()
        )
        
        compressed_model_size = sum(
            info.get('compressed_size', 0)
            for info in self.model_manager.model_index.values()
            if 'compressed_size' in info
        )
        
        # Calculate overall compression ratio
        total_original = dataset_size + model_size
        total_compressed = compressed_dataset_size + compressed_model_size
        
        if total_compressed > 0:
            overall_ratio = total_original / total_compressed
        else:
            overall_ratio = 1.0
        
        return {
            'grid_size': self.grid_size,
            'dataset_count': dataset_count,
            'model_count': model_count,
            'dataset_size': dataset_size,
            'compressed_dataset_size': compressed_dataset_size,
            'model_size': model_size,
            'compressed_model_size': compressed_model_size,
            'total_original_size': total_original,
            'total_compressed_size': total_compressed,
            'overall_compression_ratio': overall_ratio,
            'base_dir': self.base_dir
        }
