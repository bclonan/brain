"""
Fibonacci Grid System - API Module

This module provides a RESTful API for the Fibonacci Grid E2E system.
It exposes endpoints for grid operations, observer management, frequency processing,
and data compression.

Author: Manus AI
Date: May 19, 2025
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import json
import time
import os
import uuid
import logging
import io
import base64
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys

# Add the parent directory to the path so we can import the core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core import (
    FibonacciGrid, Observer, StackedGridSystem, FrequencyProcessor, CompressionDB,
    create_fibonacci_grid, create_observer, create_stacked_grid_system,
    create_frequency_processor, create_compression_db
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fibonacci_grid_api')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for objects
grids = {}
observers = {}
stacked_systems = {}
frequency_processors = {}
compression_dbs = {}

# Data directory for persistence
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Helper functions
def generate_grid_visualization(grid, start_row=0, start_col=0, rows=10, cols=10, 
                               lightning_target=None, whirlwind_center=None, 
                               whirlwind_intensity=1.0):
    """
    Generate a visualization of a grid section.
    
    Args:
        grid: The FibonacciGrid object
        start_row: Starting row index
        start_col: Starting column index
        rows: Number of rows to include
        cols: Number of columns to include
        lightning_target: (row, col) of the lightning target cell
        whirlwind_center: (row, col) of the whirlwind center cell
        whirlwind_intensity: Intensity of the whirlwind effect
        
    Returns:
        Base64-encoded PNG image
    """
    section = grid.get_section(start_row, start_col, rows, cols)
    
    # Create a custom colormap for the grid
    colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', 
             '#4292c6', '#2171b5', '#08519c', '#08306b', '#041A4B']
    cmap = LinearSegmentedColormap.from_list('fibonacci', colors, N=10)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot the grid with colors
    im = ax.imshow(section, cmap=cmap, interpolation='nearest')
    
    # Add grid lines
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    
    # Add value labels
    for i in range(min(rows, section.shape[0])):
        for j in range(min(cols, section.shape[1])):
            ax.text(j, i, str(section[i, j]), ha='center', va='center', 
                   color='white' if section[i, j] > 5 else 'black', fontweight='bold')
    
    # Add row and column labels
    ax.set_xticks(np.arange(min(cols, section.shape[1])))
    ax.set_yticks(np.arange(min(rows, section.shape[0])))
    ax.set_xticklabels([str(start_col + j) for j in range(min(cols, section.shape[1]))])
    ax.set_yticklabels([str(start_row + i) for i in range(min(rows, section.shape[0]))])
    
    # Add lightning effect if specified
    if lightning_target is not None:
        target_row, target_col = lightning_target
        
        # Ensure the target is within the visible section
        if (start_row <= target_row < start_row + rows and 
            start_col <= target_col < start_col + cols):
            
            lightning = grid.generate_lightning_path(target_row, target_col)
            
            # Adjust positions to section coordinates
            adjusted_paths = []
            for (r1, c1), (r2, c2) in lightning["paths"]:
                # Only include paths where both endpoints are in the visible section
                if (start_row <= r1 < start_row + rows and 
                    start_col <= c1 < start_col + cols and
                    start_row <= r2 < start_row + rows and 
                    start_col <= c2 < start_col + cols):
                    
                    adjusted_paths.append(
                        ((r1 - start_row, c1 - start_col), 
                         (r2 - start_row, c2 - start_col))
                    )
            
            # Draw the lightning paths
            for (r1, c1), (r2, c2) in adjusted_paths:
                ax.plot([c1, c2], [r1, r2], color="yellow", linewidth=2, alpha=0.7, zorder=5)
            
            # Highlight the target cell
            target_r_adj = target_row - start_row
            target_c_adj = target_col - start_col
            if 0 <= target_r_adj < rows and 0 <= target_c_adj < cols:
                ax.add_patch(plt.Rectangle(
                    (target_c_adj - 0.5, target_r_adj - 0.5), 
                    1, 1, fill=False, edgecolor='yellow', linewidth=3, zorder=4
                ))
    
    # Add whirlwind effect if specified
    if whirlwind_center is not None:
        center_row, center_col = whirlwind_center
        
        # Ensure the center is within the visible section
        if (start_row <= center_row < start_row + rows and 
            start_col <= center_col < start_col + cols):
            
            # Simulate the whirlwind
            affected_grid = grid.simulate_whirlwind(
                center_row, center_col, whirlwind_intensity
            )
            
            # Get the affected section
            affected_section = affected_grid[start_row:start_row+rows, start_col:start_col+cols]
            
            # Create a mask for cells that changed
            changed_mask = section != affected_section
            
            # Highlight changed cells
            for i in range(min(rows, section.shape[0])):
                for j in range(min(cols, section.shape[1])):
                    if i < changed_mask.shape[0] and j < changed_mask.shape[1] and changed_mask[i, j]:
                        ax.add_patch(plt.Rectangle(
                            (j - 0.5, i - 0.5), 
                            1, 1, fill=False, edgecolor='red', linewidth=2, zorder=3
                        ))
                        # Update the text to show the new value
                        for txt in ax.texts:
                            if txt.get_position() == (j, i):
                                txt.set_text(f"{section[i, j]}→{affected_section[i, j]}")
                                txt.set_fontweight('bold')
                                txt.set_color('red')
            
            # Highlight the center cell
            center_r_adj = center_row - start_row
            center_c_adj = center_col - start_col
            if 0 <= center_r_adj < rows and 0 <= center_c_adj < cols:
                ax.add_patch(plt.Rectangle(
                    (center_c_adj - 0.5, center_r_adj - 0.5), 
                    1, 1, fill=False, edgecolor='purple', linewidth=3, zorder=4
                ))
    
    plt.title(f"Fibonacci Grid Section [{start_row}:{start_row+rows}, {start_col}:{start_col+cols}]")
    plt.tight_layout()
    
    # Convert to base64 for web display
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    
    # Encode as base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

def generate_beat_pattern_visualization(freq1, freq2, duration=1.0, sample_rate=1000):
    """
    Generate a visualization of a beat pattern.
    
    Args:
        freq1: First frequency in Hz
        freq2: Second frequency in Hz
        duration: Duration of the pattern in seconds
        sample_rate: Number of samples per second
        
    Returns:
        Base64-encoded PNG image
    """
    # Calculate the beat frequency
    beat_frequency = abs(freq1 - freq2)
    
    # Generate time points
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    # Generate the individual waves
    wave1 = np.sin(2 * np.pi * freq1 * t)
    wave2 = np.sin(2 * np.pi * freq2 * t)
    
    # Combine the waves to create the beat pattern
    combined = wave1 + wave2
    
    # Create the visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    
    # Plot the first wave
    ax1.plot(t, wave1, label=f'Frequency 1: {freq1} Hz')
    ax1.set_ylabel('Amplitude')
    ax1.legend(loc='upper right')
    ax1.grid(True)
    
    # Plot the second wave
    ax2.plot(t, wave2, label=f'Frequency 2: {freq2} Hz', color='orange')
    ax2.set_ylabel('Amplitude')
    ax2.legend(loc='upper right')
    ax2.grid(True)
    
    # Plot the combined wave showing the beat pattern
    ax3.plot(t, combined, label=f'Beat Frequency: {beat_frequency} Hz', color='green')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Amplitude')
    ax3.legend(loc='upper right')
    ax3.grid(True)
    
    plt.title(f'Beat Pattern: {freq1} Hz + {freq2} Hz = {beat_frequency} Hz Beat')
    plt.tight_layout()
    
    # Convert to base64 for web display
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    
    # Encode as base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

# API Routes

@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        "name": "Fibonacci Grid System API",
        "version": "1.0.0",
        "endpoints": {
            "grids": "/api/grids",
            "observers": "/api/observers",
            "stacked_systems": "/api/stacked",
            "frequency_processors": "/api/frequency",
            "compression": "/api/compression"
        }
    })

# Grid endpoints
@app.route('/api/grids', methods=['GET'])
def list_grids():
    """List all grids."""
    return jsonify({
        "grids": [
            {
                "id": grid_id,
                "size": grid.size,
                "metadata": grid.metadata
            }
            for grid_id, grid in grids.items()
        ]
    })

@app.route('/api/grids', methods=['POST'])
def create_grid():
    """Create a new grid."""
    data = request.json
    size = data.get('size', 100)
    
    grid = create_fibonacci_grid(size)
    grids[grid.grid_id] = grid
    
    return jsonify({
        "id": grid.grid_id,
        "size": grid.size,
        "metadata": grid.metadata
    }), 201

@app.route('/api/grids/<grid_id>', methods=['GET'])
def get_grid(grid_id):
    """Get a specific grid."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    
    return jsonify({
        "id": grid.grid_id,
        "size": grid.size,
        "metadata": grid.metadata
    })

@app.route('/api/grids/<grid_id>/section', methods=['GET'])
def get_grid_section(grid_id):
    """Get a section of a grid."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    
    start_row = int(request.args.get('start_row', 0))
    start_col = int(request.args.get('start_col', 0))
    rows = int(request.args.get('rows', 10))
    cols = int(request.args.get('cols', 10))
    
    section = grid.get_section(start_row, start_col, rows, cols)
    
    return jsonify({
        "grid_id": grid.grid_id,
        "start_row": start_row,
        "start_col": start_col,
        "rows": rows,
        "cols": cols,
        "section": section.tolist()
    })

@app.route('/api/grids/<grid_id>/visualize', methods=['GET'])
def visualize_grid(grid_id):
    """Visualize a section of a grid."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    
    start_row = int(request.args.get('start_row', 0))
    start_col = int(request.args.get('start_col', 0))
    rows = int(request.args.get('rows', 10))
    cols = int(request.args.get('cols', 10))
    
    # Optional lightning target
    lightning_target = None
    if 'lightning_row' in request.args and 'lightning_col' in request.args:
        lightning_target = (
            int(request.args.get('lightning_row')),
            int(request.args.get('lightning_col'))
        )
    
    # Optional whirlwind center
    whirlwind_center = None
    if 'whirlwind_row' in request.args and 'whirlwind_col' in request.args:
        whirlwind_center = (
            int(request.args.get('whirlwind_row')),
            int(request.args.get('whirlwind_col'))
        )
    
    whirlwind_intensity = float(request.args.get('whirlwind_intensity', 1.0))
    
    # Generate the visualization
    img_str = generate_grid_visualization(
        grid, start_row, start_col, rows, cols,
        lightning_target, whirlwind_center, whirlwind_intensity
    )
    
    return jsonify({
        "grid_id": grid.grid_id,
        "image": img_str
    })

@app.route('/api/grids/<grid_id>/lineage', methods=['GET'])
def get_cell_lineage(grid_id):
    """Get the lineage of a cell."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    
    row = int(request.args.get('row', 0))
    col = int(request.args.get('col', 0))
    
    try:
        lineage = grid.trace_lineage(row, col)
        return jsonify({
            "grid_id": grid.grid_id,
            "row": row,
            "col": col,
            "lineage": lineage
        })
    except IndexError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/grids/<grid_id>/lightning', methods=['GET'])
def get_lightning_path(grid_id):
    """Get the lightning path for a cell."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    
    row = int(request.args.get('row', 0))
    col = int(request.args.get('col', 0))
    
    try:
        lightning = grid.generate_lightning_path(row, col)
        return jsonify({
            "grid_id": grid.grid_id,
            "row": row,
            "col": col,
            "lightning": lightning
        })
    except IndexError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/grids/<grid_id>/whirlwind', methods=['POST'])
def simulate_whirlwind(grid_id):
    """Simulate a whirlwind effect on a grid."""
    if grid_id not in grids:
        return jsonify({"error": "Grid not found"}), 404
    
    grid = grids[grid_id]
    data = request.json
    
    row = data.get('row', 0)
    col = data.get('col', 0)
    intensity = data.get('intensity', 1.0)
    
    try:
        affected_grid = grid.simulate_whirlwind(row, col, intensity)
        return jsonify({
            "grid_id": grid.grid_id,
            "row": row,
            "col": col,
            "intensity": intensity,
            "affected_grid": affected_grid.tolist()
        })
    except (IndexError, ValueError) as e:
        return jsonify({"error": str(e)}), 400

# Observer endpoints
@app.route('/api/observers', methods=['GET'])
def list_observers():
    """List all observers."""
    return jsonify({
        "observers": [
            {
                "id": observer_id,
                "name": observer.name,
                "metadata": observer.metadata
            }
            for observer_id, observer in observers.items()
        ]
    })

@app.route('/api/observers', methods=['POST'])
def create_observer_endpoint():
    """Create a new observer."""
    data = request.json
    name = data.get('name', 'Observer')
    focus_layers = data.get('focus_layers', [0])
    
    # Optional transformation matrix
    transformation_matrix = None
    if 'transformation_matrix' in da
(Content truncated due to size limit. Use line ranges to read in chunks)