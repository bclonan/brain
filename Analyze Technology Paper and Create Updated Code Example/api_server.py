"""
Fibonacci Grid AI - API Server

This module provides the API server for the Fibonacci Grid AI system,
enabling dataset and model upload, management, training, and chat functionality.
"""

import os
import sys
import json
import time
import tempfile
from typing import List, Dict, Any, Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ai_manager import AIManager, DatasetManager, ModelManager

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {
    'dataset': {'csv', 'txt', 'json', 'pdf', 'zip', 'gz', 'tar'},
    'model': {'json', 'txt', 'bin', 'pt', 'pth', 'h5', 'ckpt', 'pb', 'zip', 'gz', 'tar'}
}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize AI Manager
ai_manager = AIManager(base_dir="fibonacci_grid_ai", grid_size=100)

# Helper functions
def allowed_file(filename: str, file_type: str) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        file_type: Type of file ('dataset' or 'model')
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

# Serve static files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

# API endpoints for system information
@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get information about the AI system."""
    info = ai_manager.get_system_info()
    return jsonify(info)

# API endpoints for dataset management
@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all available datasets."""
    datasets = ai_manager.dataset_manager.list_datasets()
    return jsonify(datasets)

@app.route('/api/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Get information about a specific dataset."""
    dataset = ai_manager.dataset_manager.get_dataset(dataset_id)
    return jsonify(dataset)

@app.route('/api/datasets/<dataset_id>/content', methods=['GET'])
def get_dataset_content(dataset_id):
    """Get the content of a dataset."""
    content = ai_manager.dataset_manager.get_dataset_content(dataset_id)
    return jsonify(content)

@app.route('/api/datasets/<dataset_id>/archive/<path:file_path>', methods=['GET'])
def get_archive_file_content(dataset_id, file_path):
    """Get the content of a file within an archive dataset."""
    content = ai_manager.dataset_manager.get_archive_file_content(dataset_id, file_path)
    return jsonify(content)

@app.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset."""
    result = ai_manager.dataset_manager.delete_dataset(dataset_id)
    return jsonify(result)

@app.route('/api/datasets/upload', methods=['POST'])
def upload_dataset():
    """Upload a new dataset."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename, 'dataset'):
        filename = secure_filename(file.filename)
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except Exception as e:
                return jsonify({'error': f"Invalid metadata format: {str(e)}"}), 400
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Process the dataset
        with open(temp_path, 'rb') as f:
            result = ai_manager.dataset_manager.upload_dataset(f, filename, metadata)
        
        # Remove temporary file
        os.remove(temp_path)
        
        return jsonify(result)
    
    return jsonify({'error': 'File type not allowed'}), 400

# API endpoints for model management
@app.route('/api/models', methods=['GET'])
def list_models():
    """List all available models."""
    models = ai_manager.model_manager.list_models()
    return jsonify(models)

@app.route('/api/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """Get information about a specific model."""
    model = ai_manager.model_manager.get_model(model_id)
    return jsonify(model)

@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model."""
    result = ai_manager.model_manager.delete_model(model_id)
    return jsonify(result)

@app.route('/api/models/upload', methods=['POST'])
def upload_model():
    """Upload a new model."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename, 'model'):
        filename = secure_filename(file.filename)
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except Exception as e:
                return jsonify({'error': f"Invalid metadata format: {str(e)}"}), 400
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Process the model
        with open(temp_path, 'rb') as f:
            result = ai_manager.model_manager.upload_model(f, filename, metadata)
        
        # Remove temporary file
        os.remove(temp_path)
        
        return jsonify(result)
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/models/<model_id>/train', methods=['POST'])
def train_model(model_id):
    """Train a model using datasets."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    dataset_ids = data.get('dataset_ids', [])
    params = data.get('params', {})
    
    if not dataset_ids:
        return jsonify({'error': 'No datasets specified'}), 400
    
    # Validate dataset IDs
    for dataset_id in dataset_ids:
        dataset = ai_manager.dataset_manager.get_dataset(dataset_id)
        if 'error' in dataset:
            return jsonify({'error': f"Dataset not found: {dataset_id}"}), 404
    
    # Train the model
    result = ai_manager.model_manager.train_model(model_id, dataset_ids, params)
    
    return jsonify(result)

@app.route('/api/models/<model_id>/training/<training_id>', methods=['GET'])
def get_training_status(model_id, training_id):
    """Get the status of a training job."""
    status = ai_manager.model_manager.get_training_status(model_id, training_id)
    return jsonify(status)

# API endpoints for chat functionality
@app.route('/api/chat/<model_id>', methods=['POST'])
def chat_with_model(model_id):
    """Chat with a trained model."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    message = data.get('message', '')
    chat_history = data.get('chat_history', [])
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Chat with the model
    result = ai_manager.model_manager.chat_with_model(model_id, message, chat_history)
    
    return jsonify(result)

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large',
        'max_size': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
        'max_size_unit': 'MB'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error."""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# Run the server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
