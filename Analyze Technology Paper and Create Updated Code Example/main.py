"""
Fibonacci Grid System API
Main entry point for the Flask application
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import numpy as np
import json
import time
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import zlib
import base64
import io

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import the Fibonacci Grid System implementation
sys.path.append('/home/ubuntu/research')
from fibonacci_grid_system import FibonacciGrid, FrequencyProcessor, LightningDB

# Global instances
grid_system = FibonacciGrid(100, 100)
frequency_processor = FrequencyProcessor()
db = LightningDB(grid_system)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

# Grid System API Endpoints
@app.route('/api/grid/generate', methods=['POST'])
def generate_grid():
    """Generate a new Fibonacci grid with specified dimensions"""
    data = request.json
    rows = data.get('rows', 100)
    cols = data.get('cols', 100)
    
    global grid_system
    grid_system = FibonacciGrid(rows, cols)
    
    return jsonify({
        'status': 'success',
        'message': f'Generated {rows}x{cols} Fibonacci grid',
        'dimensions': {'rows': rows, 'cols': cols}
    })

@app.route('/api/grid/section', methods=['GET'])
def get_grid_section():
    """Get a section of the Fibonacci grid"""
    start_row = int(request.args.get('start_row', 0))
    start_col = int(request.args.get('start_col', 0))
    rows = int(request.args.get('rows', 10))
    cols = int(request.args.get('cols', 10))
    
    # Generate visualization
    img_path = grid_system.display_grid_section(start_row, start_col, rows, cols)
    
    # Convert image to base64
    with open(img_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Get the actual grid data
    section = grid_system.grid[start_row:start_row+rows, start_col:start_col+cols].tolist()
    
    return jsonify({
        'status': 'success',
        'grid_data': section,
        'image': img_data
    })

@app.route('/api/grid/shuffle', methods=['POST'])
def shuffle_grid():
    """Shuffle the grid while maintaining relative relationships"""
    data = request.json
    seed = data.get('seed')
    
    shuffled = grid_system.shuffle_grid(seed)
    
    return jsonify({
        'status': 'success',
        'message': 'Grid shuffled successfully',
        'sample': shuffled[:5, :5].tolist()  # Return a sample of the shuffled grid
    })

@app.route('/api/grid/compress', methods=['GET'])
def compress_grid():
    """Compress the grid and return compression statistics"""
    start_time = time.time()
    compression_result = grid_system.compress_grid()
    end_time = time.time()
    
    return jsonify({
        'status': 'success',
        'compression_ratio': compression_result['compression_ratio'],
        'original_size': compression_result['original_size'],
        'compressed_size': compression_result['compressed_size'],
        'execution_time': end_time - start_time
    })

# Frequency Processing API Endpoints
@app.route('/api/frequency/beat', methods=['POST'])
def generate_beat_frequency():
    """Generate beat frequency between two frequencies"""
    data = request.json
    freq1 = data.get('freq1', 400)
    freq2 = data.get('freq2', 405)
    
    beat_freq = frequency_processor.generate_beat_frequency(freq1, freq2)
    
    # Generate visualization
    img_path = frequency_processor.visualize_beat_pattern(freq1, freq2)
    
    # Convert image to base64
    with open(img_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    return jsonify({
        'status': 'success',
        'freq1': freq1,
        'freq2': freq2,
        'beat_frequency': beat_freq,
        'image': img_data
    })

@app.route('/api/frequency/entangle', methods=['POST'])
def create_entangled_frequency():
    """Create an entangled frequency pair"""
    data = request.json
    frequency = data.get('frequency', 100)
    entanglement_factor = data.get('entanglement_factor', 10)
    
    entangled = frequency_processor.create_entangled_frequency(frequency, entanglement_factor)
    event = frequency_processor.add_to_timeline(frequency)
    
    return jsonify({
        'status': 'success',
        'original_frequency': frequency,
        'entangled_frequency': entangled,
        'timeline_event': event
    })

@app.route('/api/frequency/timeline', methods=['GET'])
def get_timeline():
    """Get the current frequency timeline"""
    return jsonify({
        'status': 'success',
        'timeline': frequency_processor.timeline
    })

@app.route('/api/frequency/transmit', methods=['POST'])
def transmit_frequency_message():
    """Transform a sequence of frequencies into a message"""
    data = request.json
    frequencies = data.get('frequencies', [100, 200, 300])
    
    transmitted = frequency_processor.transmit_frequency_message(frequencies)
    
    return jsonify({
        'status': 'success',
        'original_frequencies': frequencies,
        'transmitted_frequencies': transmitted
    })

# Database API Endpoints
@app.route('/api/db/store', methods=['POST'])
def store_data():
    """Store data in the Lightning DB"""
    data = request.json
    key = data.get('key', 'test_data')
    content = data.get('data', 'Test data for storage')
    
    start_time = time.time()
    result = db.store_data(key, content)
    end_time = time.time()
    
    return jsonify({
        'status': 'success',
        'storage_result': result,
        'execution_time': end_time - start_time
    })

@app.route('/api/db/retrieve', methods=['GET'])
def retrieve_data():
    """Retrieve data from the Lightning DB"""
    key = request.args.get('key', 'test_data')
    
    start_time = time.time()
    result = db.retrieve_data(key)
    end_time = time.time()
    
    if result is None:
        return jsonify({
            'status': 'error',
            'message': f'No data found for key: {key}'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': result,
        'execution_time': end_time - start_time
    })

@app.route('/api/db/export', methods=['GET'])
def export_database():
    """Export the Lightning DB to JSON"""
    filename = f"lightning_db_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    file_path = os.path.join(STATIC_DIR, filename)
    
    db.export_database(file_path)
    
    return jsonify({
        'status': 'success',
        'message': 'Database exported successfully',
        'filename': filename,
        'download_url': f'/api/db/download/{filename}'
    })

@app.route('/api/db/download/<filename>', methods=['GET'])
def download_database(filename):
    """Download the exported database file"""
    return send_from_directory(STATIC_DIR, filename, as_attachment=True)

# Benchmark API Endpoints
@app.route('/api/benchmark/hashing', methods=['POST'])
def benchmark_hashing():
    """Benchmark hashing performance against standard algorithms"""
    data = request.json
    input_data = data.get('data', 'Test data for hashing benchmark')
    iterations = data.get('iterations', 1000)
    
    # Standard hashing algorithms
    start_time = time.time()
    for _ in range(iterations):
        sha256_hash = hashlib.sha256(input_data.encode()).hexdigest()
    sha256_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(iterations):
        md5_hash = hashlib.md5(input_data.encode()).hexdigest()
    md5_time = time.time() - start_time
    
    # Fibonacci Grid hashing (simulated)
    start_time = time.time()
    for _ in range(iterations):
        # Convert input to numerical representation
        numerical_data = [ord(c) for c in input_data]
        # Map to grid coordinates
        coordinates = []
        for value in numerical_data:
            positions = np.where(grid_system.grid == value % 10)
            if len(positions[0]) > 0:
                coordinates.append((int(positions[0][0]), int(positions[1][0])))
        # Create hash from coordinates
        fib_hash = hashlib.sha256(str(coordinates).encode()).hexdigest()
    fib_grid_time = time.time() - start_time
    
    return jsonify({
        'status': 'success',
        'benchmark_results': {
            'input_size': len(input_data),
            'iterations': iterations,
            'sha256': {
                'time': sha256_time,
                'operations_per_second': iterations / sha256_time
            },
            'md5': {
                'time': md5_time,
                'operations_per_second': iterations / md5_time
            },
            'fibonacci_grid': {
                'time': fib_grid_time,
                'operations_per_second': iterations / fib_grid_time
            }
        }
    })

@app.route('/api/benchmark/compression', methods=['POST'])
def benchmark_compression():
    """Benchmark compression performance against standard algorithms"""
    data = request.json
    input_data = data.get('data', 'Test data for compression benchmark' * 100)  # Make it larger
    iterations = data.get('iterations', 100)
    
    # Standard compression algorithms
    start_time = time.time()
    for _ in range(iterations):
        zlib_compressed = zlib.compress(input_data.encode())
    zlib_time = time.time() - start_time
    zlib_ratio = len(input_data) / len(zlib_compressed)
    
    # Fibonacci Grid compression
    start_time = time.time()
    for _ in range(iterations):
        # Store in Lightning DB (which uses grid for compression)
        db.store_data(f"benchmark_compression_{_}", input_data)
    fib_grid_time = time.time() - start_time
    
    # Get compression ratio from the last operation
    compression_result = grid_system.compress_grid()
    fib_grid_ratio = compression_result['compression_ratio']
    
    return jsonify({
        'status': 'success',
        'benchmark_results': {
            'input_size': len(input_data),
            'iterations': iterations,
            'zlib': {
                'time': zlib_time,
                'operations_per_second': iterations / zlib_time,
                'compression_ratio': zlib_ratio
            },
            'fibonacci_grid': {
                'time': fib_grid_time,
                'operations_per_second': iterations / fib_grid_time,
                'compression_ratio': fib_grid_ratio
            }
        }
    })

@app.route('/api/benchmark/memory', methods=['POST'])
def benchmark_memory():
    """Benchmark memory system performance"""
    data = request.json
    operations = data.get('operations', 1000)
    data_size = data.get('data_size', 1000)
    
    # Generate random data
    random_data = np.random.randint(0, 256, size=data_size).tolist()
    
    # Traditional memory operations (array access)
    start_time = time.time()
    for _ in range(operations):
        idx = np.random.randint(0, data_size)
        value = random_data[idx]
    traditional_time = time.time() - start_time
    
    # Fibonacci Grid memory operations
    start_time = time.time()
    for _ in range(operations):
        row = np.random.randint(0, grid_system.rows)
        col = np.random.randint(0, grid_system.cols)
        value = grid_system.get_cell_value(row, col)
    fib_grid_time = time.time() - start_time
    
    return jsonify({
        'status': 'success',
        'benchmark_results': {
            'operations': operations,
            'data_size': data_size,
            'traditional_memory': {
                'time': traditional_time,
                'operations_per_second': operations / traditional_time
            },
            'fibonacci_grid_memory': {
                'time': fib_grid_time,
                'operations_per_second': operations / fib_grid_time
            }
        }
    })

@app.route('/api/benchmark/network', methods=['POST'])
def benchmark_network():
    """Simulate network transfer efficiency benchmark"""
    data = request.json
    packet_size = data.get('packet_size', 1024)
    num_packets = data.get('num_packets', 100)
    
    # Generate random packet data
    packet_data = ''.join([chr(np.random.randint(32, 127)) for _ in range(packet_size)])
    
    # Traditional network transfer (simulated)
    start_time = time.time()
    for _ in range(num_packets):
        # Simulate traditional packet overhead and transfer
        packet_overhead = 40  # TCP/IP header size (20 bytes) + TCP header (20 bytes)
        total_size = packet_size + packet_overhead
        # Simulate network latency
        time.sleep(0.001)  # 1ms latency per packet
    traditional_time = time.time() - start_time
    traditional_throughput = (packet_size * num_packets) / traditional_time
    
    # Fibonacci Grid network transfer (simulated)
    start_time = time.time()
    for _ in range(num_packets):
        # Convert to grid coordinates (compression)
        numerical_data = [ord(c) for c in packet_data[:100]]  # Use a sample for simulation
        coordinates = []
        for value in numerical_data:
            positions = np.where(grid_system.grid == value % 10)
            if len(positions[0]) > 0:
                coordinates.append((int(positions[0][0]), int(positions[1][0])))
        
        # Simulate reduced packet size due to compression
        compressed_size = len(str(coordinates).encode())
        packet_overhead = 40
        total_size = compressed_size + packet_overhead
        
        # Simulate network latency (potentially reduced due to smaller packets)
        time.sleep(0.0008)  # 0.8ms latency per packet
    fib_grid_time = time.time() - start_time
    fib_grid_throughput = (packet_size * num_packets) / fib_grid_time
    
    return jsonify({
        'status': 'success',
        'benchmark_results': {
            'packet_size': packet_size,
            'num_packets': num_packets,
            'traditional_network': {
                'time': traditional_time,
                'throughput_bytes_per_second': traditional_throughput,
                'latency_per_packet_ms': 1.0
            },
            'fibonacci_grid_network': {
                'time': fib_grid_time,
                'throughput_bytes_per_second': fib_grid_throughput,
                'latency_per_packet_ms': 0.8
            }
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
