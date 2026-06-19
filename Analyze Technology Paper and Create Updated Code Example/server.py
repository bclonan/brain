#!/usr/bin/env python3
"""
Fibonacci Grid System - Server

This script runs the server for the Fibonacci Grid System, providing API endpoints
for frontend interaction with the grid system's functionality.
"""

import os
import sys
import json
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import backend modules
from backend.core import (
    FibonacciGrid, 
    Observer, 
    FrequencyProcessor, 
    CompressionDB,
    SecureMessaging,
    MemorySystem,
    PatternRecognition,
    NetworkTransfer,
    AIEnhancement
)
from backend.optimization import BenchmarkSuite, SystemOptimizer

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Initialize core components
grid = FibonacciGrid(100)
compression_db = CompressionDB(100)
frequency_processor = FrequencyProcessor()
secure_messaging = SecureMessaging(100)
memory_system = MemorySystem(100)
pattern_recognition = PatternRecognition(100)
network_transfer = NetworkTransfer(100)
ai_enhancement = AIEnhancement(100)
benchmark_suite = BenchmarkSuite()
system_optimizer = SystemOptimizer(100)

# Create default observers
default_observer_id = secure_messaging.add_observer("Default Observer")

# Create default route for network transfer
default_route = network_transfer.create_route("Default Route", hops=5)

# Create default AI model
default_model = ai_enhancement.create_model("Default Model", 5, 1)
ai_enhancement.add_observer(default_model['model_id'], "Observer 1")

# Serve static files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

# API endpoints for grid operations
@app.route('/api/grid/section', methods=['GET'])
def get_grid_section():
    start_row = int(request.args.get('start_row', 0))
    start_col = int(request.args.get('start_col', 0))
    rows = int(request.args.get('rows', 10))
    cols = int(request.args.get('cols', 10))
    
    section = grid.get_section(start_row, start_col, rows, cols).tolist()
    
    return jsonify({
        'section': section,
        'start_row': start_row,
        'start_col': start_col,
        'rows': rows,
        'cols': cols
    })

@app.route('/api/grid/visualize', methods=['GET'])
def visualize_grid():
    start_row = int(request.args.get('start_row', 0))
    start_col = int(request.args.get('start_col', 0))
    rows = int(request.args.get('rows', 10))
    cols = int(request.args.get('cols', 10))
    
    lightning_target = None
    if request.args.get('lightning_row') and request.args.get('lightning_col'):
        lightning_target = (
            int(request.args.get('lightning_row')),
            int(request.args.get('lightning_col'))
        )
    
    whirlwind_center = None
    if request.args.get('whirlwind_row') and request.args.get('whirlwind_col'):
        whirlwind_center = (
            int(request.args.get('whirlwind_row')),
            int(request.args.get('whirlwind_col'))
        )
    
    whirlwind_intensity = float(request.args.get('whirlwind_intensity', 0.8))
    
    img_base64 = grid.visualize_section(
        start_row, start_col, rows, cols,
        lightning_target=lightning_target,
        whirlwind_center=whirlwind_center,
        whirlwind_intensity=whirlwind_intensity
    )
    
    return jsonify({
        'image': img_base64,
        'start_row': start_row,
        'start_col': start_col,
        'rows': rows,
        'cols': cols
    })

@app.route('/api/grid/lightning', methods=['GET'])
def get_lightning_path():
    row = int(request.args.get('row', 0))
    col = int(request.args.get('col', 0))
    
    path = grid.get_lightning_path(row, col)
    
    return jsonify({
        'path': path,
        'row': row,
        'col': col,
        'is_origin': grid.is_origin(row, col)
    })

@app.route('/api/grid/whirlwind', methods=['GET'])
def get_whirlwind_effect():
    row = int(request.args.get('row', 0))
    col = int(request.args.get('col', 0))
    intensity = float(request.args.get('intensity', 0.8))
    
    affected_cells = grid.get_whirlwind_effect(row, col, intensity)
    
    return jsonify({
        'affected_cells': affected_cells,
        'row': row,
        'col': col,
        'intensity': intensity
    })

# API endpoints for frequency processing
@app.route('/api/frequency/beat', methods=['GET'])
def get_beat_pattern():
    freq1 = float(request.args.get('freq1', 10.0))
    freq2 = float(request.args.get('freq2', 12.0))
    duration = float(request.args.get('duration', 1.0))
    
    beat_pattern = frequency_processor.generate_beat_pattern(freq1, freq2, duration)
    
    return jsonify(beat_pattern)

@app.route('/api/frequency/entangle', methods=['GET'])
def create_entangled_pair():
    base_frequency = float(request.args.get('base_frequency', 10.0))
    entanglement_factor = float(request.args.get('entanglement_factor', 0.5))
    
    entangled_pair = frequency_processor.create_entangled_pair(base_frequency, entanglement_factor)
    
    return jsonify(entangled_pair)

@app.route('/api/frequency/analyze', methods=['POST'])
def analyze_resonance():
    data = request.get_json()
    frequencies = data.get('frequencies', [])
    
    resonance = frequency_processor.analyze_resonance(frequencies)
    
    return jsonify(resonance)

# API endpoints for compression
@app.route('/api/compression/compress', methods=['POST'])
def compress_data():
    data = request.get_json()
    text = data.get('text', '')
    
    result = compression_db.compress(text)
    
    return jsonify(result)

@app.route('/api/compression/decompress', methods=['POST'])
def decompress_data():
    data = request.get_json()
    
    result = compression_db.decompress(data)
    
    return jsonify(result)

@app.route('/api/compression/stats', methods=['GET'])
def get_compression_stats():
    stats = compression_db.get_stats()
    
    return jsonify(stats)

# API endpoints for secure messaging
@app.route('/api/messaging/observers', methods=['GET'])
def get_observers():
    observers = [
        {
            'id': observer_id,
            'name': secure_messaging.observers[observer_id].name
        }
        for observer_id in secure_messaging.observers
    ]
    
    return jsonify(observers)

@app.route('/api/messaging/add_observer', methods=['POST'])
def add_observer():
    data = request.get_json()
    name = data.get('name', 'New Observer')
    transformation_matrix = data.get('transformation_matrix')
    
    observer_id = secure_messaging.add_observer(name, transformation_matrix)
    
    return jsonify({
        'observer_id': observer_id,
        'name': name
    })

@app.route('/api/messaging/encode', methods=['POST'])
def encode_message():
    data = request.get_json()
    message = data.get('message', '')
    observer_id = data.get('observer_id', default_observer_id)
    
    result = secure_messaging.encode_message(message, observer_id)
    
    return jsonify(result)

@app.route('/api/messaging/decode', methods=['POST'])
def decode_message():
    data = request.get_json()
    encoded_message = data.get('encoded_message', '')
    observer_id = data.get('observer_id', default_observer_id)
    
    result = secure_messaging.decode_message(encoded_message, observer_id)
    
    return jsonify(result)

# API endpoints for memory system
@app.route('/api/memory/allocate', methods=['POST'])
def allocate_memory():
    data = request.get_json()
    block_id = data.get('block_id', f"block_{len(memory_system.memory_blocks)}")
    size = data.get('size', 100)
    
    result = memory_system.allocate(block_id, size)
    
    return jsonify(result)

@app.route('/api/memory/write', methods=['POST'])
def write_memory():
    data = request.get_json()
    block_id = data.get('block_id', '')
    values = data.get('data', [])
    
    result = memory_system.write(block_id, values)
    
    return jsonify(result)

@app.route('/api/memory/read', methods=['GET'])
def read_memory():
    block_id = request.args.get('block_id', '')
    offset = int(request.args.get('offset', 0))
    length = int(request.args.get('length', 0)) if request.args.get('length') else None
    
    result = memory_system.read(block_id, offset, length)
    
    return jsonify(result)

@app.route('/api/memory/free', methods=['POST'])
def free_memory():
    data = request.get_json()
    block_id = data.get('block_id', '')
    
    result = memory_system.free(block_id)
    
    return jsonify(result)

# API endpoints for pattern recognition
@app.route('/api/pattern/map', methods=['POST'])
def map_data_to_grid():
    data = request.get_json()
    values = data.get('data', [])
    
    result = pattern_recognition.map_data_to_grid(values)
    
    return jsonify(result)

@app.route('/api/pattern/analyze', methods=['GET'])
def analyze_pattern():
    pattern_id = request.args.get('pattern_id', '')
    
    result = pattern_recognition.analyze_pattern(pattern_id)
    
    return jsonify(result)

@app.route('/api/pattern/compare', methods=['GET'])
def compare_patterns():
    pattern_id1 = request.args.get('pattern_id1', '')
    pattern_id2 = request.args.get('pattern_id2', '')
    
    result = pattern_recognition.compare_patterns(pattern_id1, pattern_id2)
    
    return jsonify(result)

# API endpoints for network transfer
@app.route('/api/network/encode', methods=['POST'])
def encode_packet():
    data = request.get_json()
    text = data.get('data', '')
    route_id = data.get('route_id', default_route['id'])
    
    result = network_transfer.encode_packet(text, route_id)
    
    return jsonify(result)

@app.route('/api/network/decode', methods=['GET'])
def decode_packet():
    packet_id = request.args.get('packet_id', '')
    
    result = network_transfer.decode_packet(packet_id)
    
    return jsonify(result)

@app.route('/api/network/routes', methods=['GET'])
def get_routes():
    routes = [
        {
            'id': route_id,
            'name': network_transfer.routes[route_id]['name'],
            'length': network_transfer.routes[route_id]['length']
        }
        for route_id in network_transfer.routes
    ]
    
    return jsonify(routes)

@app.route('/api/network/create_route', methods=['POST'])
def create_route():
    data = request.get_json()
    name = data.get('name', f"Route_{len(network_transfer.routes)}")
    hops = data.get('hops', 5)
    
    result = network_transfer.create_route(name, hops)
    
    return jsonify({
        'id': result['id'],
        'name': result['name'],
        'length': result['length'],
        'path': result['path']
    })

@app.route('/api/network/simulate', methods=['POST'])
def simulate_transfer():
    data = request.get_json()
    packet_id = data.get('packet_id', '')
    route_id = data.get('route_id', default_route['id'])
    
    result = network_transfer.simulate_transfer(packet_id, route_id)
    
    return jsonify(result)

# API endpoints for AI enhancement
@app.route('/api/ai/models', methods=['GET'])
def get_models():
    models = [
        {
            'id': model_id,
            'name': ai_enhancement.models[model_id]['name'],
            'input_size': ai_enhancement.models[model_id]['input_size'],
            'output_size': ai_enhancement.models[model_id]['output_size']
        }
        for model_id in ai_enhancement.models
    ]
    
    return jsonify(models)

@app.route('/api/ai/create_model', methods=['POST'])
def create_model():
    data = request.get_json()
    name = data.get('name', f"Model_{len(ai_enhancement.models)}")
    input_size = data.get('input_size', 5)
    output_size = data.get('output_size', 1)
    
    result = ai_enhancement.create_model(name, input_size, output_size)
    
    return jsonify(result)

@app.route('/api/ai/add_observer', methods=['POST'])
def add_ai_observer():
    data = request.get_json()
    model_id = data.get('model_id', '')
    name = data.get('name', f"Observer_{len(ai_enhancement.observers)}")
    transformation_matrix = data.get('transformation_matrix')
    
    result = ai_enhancement.add_observer(model_id, name, transformation_matrix)
    
    return jsonify(result)

@app.route('/api/ai/train', methods=['POST'])
def train_model():
    data = request.get_json()
    model_id = data.get('model_id', '')
    inputs = data.get('inputs', [])
    targets = data.get('targets', [])
    epochs = data.get('epochs', 10)
    
    result = ai_enhancement.train(model_id, inputs, targets, epochs)
    
    return jsonify(result)

@app.route('/api/ai/predict', methods=['POST'])
def predict():
    data = request.get_json()
    model_id = data.get('model_id', '')
    input_vector = data.get('input', [])
    
    result = ai_enhancement.predict(model_id, input_vector)
    
    return jsonify(result)

# API endpoints for benchmarks
@app.route('/api/benchmark/run', methods=['GET'])
def run_benchmark():
    category = request.args.get('category', 'all')
    
    if category == 'all':
        results = benchmark_suite.run_all_benchmarks()
    elif category == 'compression':
        results = benchmark_suite.benchmark_compression()
    elif category == 'memory':
        results = benchmark_suite.benchmark_memory()
    elif category == 'network':
        results = benchmark_suite.benchmark_network()
    elif category == 'pattern':
        results = benchmark_suite.benchmark_pattern_recognition()
    elif category == 'messaging':
        results = benchmark_suite.benchmark_secure_messaging()
    elif category == 'ai':
        results = benchmark_suite.benchmark_ai_enhancement()
    else:
        return jsonify({'error': f"Unknown benchmark category: {category}"})
    
    return jsonify(results)

# API endpoints for optimizations
@app.route('/api/optimize/run', methods=['GET'])
def run_optimization():
    category = request.args.get('category', 'all')
    
    if category == 'all':
        results = system_optimizer.get_all_optimizations()
    elif category == 'grid':
        results = system_optimizer.optimize_grid_generation()
    elif category == 'lightning':
        results = system_optimizer.optimize_lightning_path()
    elif category == 'compression':
        results = system_optimizer.optimize_compression()
    elif category == 'observer':
        results = system_optimizer.optimize_observer_transformation()
    else:
        return jsonify({'error': f"Unknown optimization category: {category}"})
    
    return jsonify(results)

# Run the server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
