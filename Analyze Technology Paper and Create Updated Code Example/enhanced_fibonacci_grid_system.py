"""
Enhanced Fibonacci Grid System with Lightning, Whirlwind, and Observer Perspectives

This implementation integrates the new concepts from the supplementary materials:
- Origin and lineage tracking
- Lightning representation for path visualization
- Whirlwind effects for dynamic grid interactions
- Observer perspectives for multiple interpretations
- Frequency and resonance for pattern generation
- Stacked grids for layered information
- CompressionDB for efficient storage

Author: Manus AI
Date: May 19, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.animation as animation
from matplotlib.patches import ConnectionPatch
import json
import time
import hashlib
from io import BytesIO
import base64

class FibonacciGrid:
    def __init__(self, size=100):
        """
        Initialize a Fibonacci grid of the specified size.
        
        Args:
            size: The size of the grid (size x size)
        """
        self.size = size
        self.grid = self._generate_fibonacci_grid(size)
        self.lineage_cache = {}
        
    def _generate_fibonacci_grid(self, size):
        """
        Generate a Fibonacci grid based on the modulo 10 pattern.
        
        Args:
            size: The size of the grid
            
        Returns:
            A numpy array containing the Fibonacci grid
        """
        grid = np.zeros((size, size), dtype=int)
        
        # Initialize the first row with the row number
        for i in range(size):
            grid[i, 0] = i + 1
            
        # Initialize the first column with the column number
        for j in range(size):
            grid[0, j] = j + 1
            
        # Fill the grid using Fibonacci-like addition with modulo 10
        for i in range(1, size):
            for j in range(1, size):
                if i == 1 and j == 1:
                    # Special case for position [1,1]
                    grid[i, j] = (grid[i-1, j] + grid[i, j-1]) % 10
                else:
                    # Standard Fibonacci addition with modulo 10
                    grid[i, j] = (grid[i-1, j] + grid[i, j-1]) % 10
                    if grid[i, j] == 0:  # Replace 0 with 10 for better visualization
                        grid[i, j] = 10
        
        return grid
    
    def get_section(self, start_row=0, start_col=0, rows=10, cols=10):
        """
        Get a section of the grid.
        
        Args:
            start_row: Starting row index
            start_col: Starting column index
            rows: Number of rows to include
            cols: Number of columns to include
            
        Returns:
            A numpy array containing the specified section
        """
        end_row = min(start_row + rows, self.size)
        end_col = min(start_col + cols, self.size)
        
        return self.grid[start_row:end_row, start_col:end_col]
    
    def trace_lineage(self, row, col):
        """
        Trace the lineage of a cell back to its origin points.
        
        Args:
            row: Row index of the cell
            col: Column index of the cell
            
        Returns:
            A dictionary containing the lineage information
        """
        # Check if we've already computed this lineage
        cache_key = f"{row},{col}"
        if cache_key in self.lineage_cache:
            return self.lineage_cache[cache_key]
        
        # Base cases: first row or first column
        if row == 0 or col == 0:
            lineage = {
                "value": int(self.grid[row, col]),
                "position": (int(row), int(col)),
                "is_origin": True,
                "parents": []
            }
            self.lineage_cache[cache_key] = lineage
            return lineage
        
        # Recursive case: trace back to parents
        parent1 = self.trace_lineage(row-1, col)
        parent2 = self.trace_lineage(row, col-1)
        
        lineage = {
            "value": int(self.grid[row, col]),
            "position": (int(row), int(col)),
            "is_origin": False,
            "parents": [parent1, parent2]
        }
        
        self.lineage_cache[cache_key] = lineage
        return lineage
    
    def generate_lightning_path(self, target_row, target_col):
        """
        Generate a lightning path visualization for a cell.
        
        Args:
            target_row: Row index of the target cell
            target_col: Column index of the target cell
            
        Returns:
            A dictionary containing the lightning path information
        """
        lineage = self.trace_lineage(target_row, target_col)
        
        # Extract all positions in the lineage tree
        positions = []
        
        def extract_positions(node):
            positions.append(node["position"])
            for parent in node["parents"]:
                extract_positions(parent)
        
        extract_positions(lineage)
        
        # Create paths connecting the positions
        paths = []
        
        def create_paths(node):
            for parent in node["parents"]:
                paths.append((node["position"], parent["position"]))
                create_paths(parent)
        
        create_paths(lineage)
        
        return {
            "target": (int(target_row), int(target_col)),
            "value": int(self.grid[target_row, target_col]),
            "positions": positions,
            "paths": paths
        }
    
    def simulate_whirlwind(self, center_row, center_col, intensity=1.0):
        """
        Simulate a whirlwind effect centered at a specific cell.
        
        Args:
            center_row: Row index of the center cell
            center_col: Column index of the center cell
            intensity: Intensity of the whirlwind effect (0.0 to 1.0)
            
        Returns:
            A numpy array containing the affected grid
        """
        # Create a copy of the grid to modify
        affected_grid = self.grid.copy()
        
        # Get the value at the center
        center_value = self.grid[center_row, center_col]
        
        # Calculate affected radius based on intensity
        radius = int(np.ceil(intensity * np.log(center_value + 1) * 5))
        radius = max(radius, 2)  # Ensure minimum radius
        
        # Calculate if the center value would split in modulo 10
        splits = center_value > 9
        
        # Update affected cells
        for r in range(max(0, center_row - radius), min(self.size, center_row + radius + 1)):
            for c in range(max(0, center_col - radius), min(self.size, center_col + radius + 1)):
                if r == center_row and c == center_col:
                    continue  # Skip the center cell
                
                # Calculate distance from center
                distance = np.sqrt((r - center_row)**2 + (c - center_col)**2)
                
                if distance <= radius:
                    # Apply whirlwind effect with diminishing intensity
                    effect_intensity = (1 - distance / radius) * intensity
                    
                    if splits:
                        # If center value splits, apply more dramatic effect
                        digit1 = center_value // 10
                        digit2 = center_value % 10
                        
                        # Apply a transformation based on the split digits
                        if np.random.random() < effect_intensity:
                            affected_grid[r, c] = (affected_grid[r, c] + digit1) % 10
                        else:
                            affected_grid[r, c] = (affected_grid[r, c] + digit2) % 10
                    else:
                        # Apply a milder effect for non-splitting values
                        if np.random.random() < effect_intensity:
                            affected_grid[r, c] = (affected_grid[r, c] + 1) % 10
                        
                    # Replace 0 with 10 for better visualization
                    if affected_grid[r, c] == 0:
                        affected_grid[r, c] = 10
        
        return affected_grid
    
    def visualize_grid_section(self, start_row=0, start_col=0, rows=10, cols=10, 
                              lightning_target=None, whirlwind_center=None, 
                              whirlwind_intensity=1.0, filename=None):
        """
        Visualize a section of the grid with optional lightning and whirlwind effects.
        
        Args:
            start_row: Starting row index
            start_col: Starting column index
            rows: Number of rows to include
            cols: Number of columns to include
            lightning_target: (row, col) of the lightning target cell
            whirlwind_center: (row, col) of the whirlwind center cell
            whirlwind_intensity: Intensity of the whirlwind effect
            filename: If provided, save the visualization to this file
            
        Returns:
            The matplotlib figure or the filename if saved
        """
        section = self.get_section(start_row, start_col, rows, cols)
        
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
        for i in range(rows):
            for j in range(cols):
                ax.text(j, i, str(section[i, j]), ha='center', va='center', 
                       color='white' if section[i, j] > 5 else 'black', fontweight='bold')
        
        # Add row and column labels
        ax.set_xticks(np.arange(cols))
        ax.set_yticks(np.arange(rows))
        ax.set_xticklabels([str(start_col + j) for j in range(cols)])
        ax.set_yticklabels([str(start_row + i) for i in range(rows)])
        
        # Add lightning effect if specified
        if lightning_target is not None:
            target_row, target_col = lightning_target
            
            # Ensure the target is within the visible section
            if (start_row <= target_row < start_row + rows and 
                start_col <= target_col < start_col + cols):
                
                lightning = self.generate_lightning_path(target_row, target_col)
                
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
                    con = ConnectionPatch(
                        xyA=(c1, r1), xyB=(c2, r2), 
                        coordsA="data", coordsB="data",
                        axesA=ax, axesB=ax,
                        color="yellow", linewidth=2, alpha=0.7,
                        zorder=5
                    )
                    ax.add_artist(con)
                
                # Highlight the target cell
                target_r_adj = target_row - start_row
                target_c_adj = target_col - start_col
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
                affected_grid = self.simulate_whirlwind(
                    center_row, center_col, whirlwind_intensity
                )
                
                # Get the affected section
                affected_section = affected_grid[start_row:start_row+rows, start_col:start_col+cols]
                
                # Create a mask for cells that changed
                changed_mask = section != affected_section
                
                # Highlight changed cells
                for i in range(rows):
                    for j in range(cols):
                        if changed_mask[i, j]:
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
                ax.add_patch(plt.Rectangle(
                    (center_c_adj - 0.5, center_r_adj - 0.5), 
                    1, 1, fill=False, edgecolor='purple', linewidth=3, zorder=4
                ))
        
        plt.title(f"Fibonacci Grid Section [{start_row}:{start_row+rows}, {start_col}:{start_col+cols}]")
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return filename
        else:
            # Convert to base64 for web display
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str
    
    def generate_beat_pattern(self, freq1, freq2, duration=1.0, sample_rate=1000, filename=None):
        """
        Generate and visualize a beat pattern between two frequencies.
        
        Args:
            freq1: First frequency in Hz
            freq2: Second frequency in Hz
            duration: Duration of the pattern in seconds
            sample_rate: Number of samples per second
            filename: If provided, save the visualization to this file
            
        Returns:
            The beat frequency and the matplotlib figure or filename if saved
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
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return beat_frequency, filename
        else:
            # Convert to base64 for web display
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return beat_frequency, img_str

class Observer:
    def __init__(self, transformation_matrix=None, focus_layers=None, name="Default Observer"):
        """
        Initialize an observer with a specific transformation matrix and focus layers.
        
        Args:
            transformation_matrix: Matrix used to transform the grid
            focus_layers: List of grid layers to focus on
            name: Name of the observer
        """
        self.name = name
        
        if transformation_matrix is None:
            # Default to identity matrix
            self.matrix = np.eye(10)
        else:
            self.matrix = transformation_matrix
            
        if focus_layers is None:
            # Default to focus on the first layer
            self.focus_layers = [0]
        else:
            self.focus_layers = focus_layers
    
    def observe(self, grid_system):
        """
        Observe a grid system through this observer's lens.
        
        Args:
            grid_system: A grid system (single grid or stacked grids)
            
        Returns:
            The observed grid after applying the transformation
        """
        if hasattr(grid_system, 'layers'):
            # It's a stacked grid system
            if len(self.focus_layers) == 1:
                grid = grid_system.get_layer(self.focus_layers[0])
                return self._apply_transformation(grid)
            else:
                # Combine multiple layers
                combined_grid = grid_system.combine_layers(self.focus_layers)
                return self._apply_transformation(combined_grid)
        else:
            # It's a single grid
            return self._apply_transformation(grid_system.grid)
    
    def _apply_transformation(self, grid):
        """
        Apply the transformation matrix to a grid.
        
        Args:
            grid: The grid to transform
            
        Returns:
            The transformed grid
        """
        # Create a copy to avoid modifying the original
        transformed = grid.copy()
        
        # Apply the transformation to each cell
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                # Get the current value (1-indexed in the matrix)
                value = grid[i, j]
                if value == 0 or value == 10:
                    value = 10  # Handle 0 as 10
                
                # Apply the transformation (values are 1-indexed in the matrix)
                # Ensure index is within bounds (0-9)
                matrix_index = (value - 1) % 10
                transformed[i, j] = self.matrix[matrix_index, 0]
        
        return transformed

class StackedGridSystem:
    def __init__(self, num_layers=3, size=100):
        """
        Initialize a stacked grid system with multiple layers.
        
        Args:
            num_layers: Number of grid layers
            size: Size of each grid layer
        """
        self.num_layers = num_layers
        self.size = size
        self.layers = []
        
        # Create the layers
        for _ in range(num_layers):
            grid = FibonacciGrid(size)
            self.layers.append(grid)
    
    def get_layer(self, index):
        """
        Get a specific layer from the stack.
        
        Args:
            index: Index of the layer
            
        Returns:
            The grid at the specified layer
        """
        if 0 <= index < self.num_layers:
            return self.layers[index].grid
        else:
            raise IndexError(f"Layer index {index} out of range (0-{self.num_layers-1})")
    
    def combine_layers(self, indices, operation='hadamard'):
        """
        Combine multiple layers using the specified operation.
        
        Args:
            indices: List of layer indices to combine
            operation: Operation to use ('hadamard', 'difference', 'sum')
            
        Returns:
            The combined grid
        """
        if len(indices) < 1:
            raise ValueError("At least one layer index must be provided")
        
        if len(indices) == 1:
            return self.get_layer(indices[0])
        
        # Get the first layer
        result = self.get_layer(indices[0]).copy()
        
        # Combine with subsequent layers
        for i in indices[1:]:
            layer = self.get_layer(i)
            
            if operation == 'hadamard':
                # Element-wise multiplication (Hadamard product)
                result = result * layer
                # Apply modulo 10
                result = result % 10
            elif operation == 'difference':
                # Element-wise difference
                result = (result - layer) % 10
            elif operation == 'sum':
                # Element-wise sum
                result = (result + layer) % 10
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Replace 0 with 10 for better visualization
            result[result == 0] = 10
        
        return result
    
    def visualize_combined_layers(self, indices, operation='hadamard', 
                                 start_row=0, start_col=0, rows=10, cols=10,
                                 filename=None):
        """
        Visualize a combination of layers.
        
        Args:
            indices: List of layer indices to combine
            operation: Operation to use ('hadamard', 'difference', 'sum')
            start_row: Starting row index
            start_col: Starting column index
            rows: Number of rows to include
            cols: Number of columns to include
            filename: If provided, save the visualization to this file
            
        Returns:
            The matplotlib figure or the filename if saved
        """
        combined = self.combine_layers(indices, operation)
        
        # Extract the section
        end_row = min(start_row + rows, self.size)
        end_col = min(start_col + cols, self.size)
        section = combined[start_row:end_row, start_col:end_col]
        
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
        
        # Create title with layer information
        layer_str = ", ".join([str(i) for i in indices])
        plt.title(f"Combined Layers [{layer_str}] using {operation.capitalize()}\n"
                 f"Section [{start_row}:{start_row+rows}, {start_col}:{start_col+cols}]")
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return filename
        else:
            # Convert to base64 for web display
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str

class CompressionDB:
    def __init__(self, grid_size=100):
        """
        Initialize a compression database using the Fibonacci grid.
        
        Args:
            grid_size: Size of the underlying grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.compression_map = {}
        self.decompression_map = {}
        self.stats = {
            "total_compressed": 0,
            "total_original_size": 0,
            "total_compressed_size": 0,
            "compression_ratio": 0
        }
    
    def compress(self, data):
        """
        Compress data using the Fibonacci grid pattern.
        
        Args:
            data: Data to compress (string or bytes)
            
        Returns:
            A dictionary containing the compressed data and metadata
        """
        start_time = time.time()
        
        # Convert to bytes if it's a string
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        original_size = len(data_bytes)
        
        # Generate a hash for the data
        hash_value = hashlib.sha256(data_bytes).hexdigest()
        
        # Map the data to grid patterns
        grid_pattern = self._map_data_to_grid(data_bytes)
        
        # Encode the grid pattern efficiently
        encoded = self._encode_grid_pattern(grid_pattern)
        compressed_size = len(encoded)
        
        # Store the mapping for later retrieval
        self.compression_map[hash_value] = grid_pattern
        self.decompression_map[hash_value] = data_bytes
        
        # Update stats
        self.stats["total_compressed"] += 1
        self.stats["total_original_size"] += original_size
        self.stats["total_compressed_size"] += compressed_size
        self.stats["compression_ratio"] = self.stats["total_original_size"] / max(1, self.stats["total_compressed_size"])
        
        end_time = time.time()
        
        return {
            "hash": hash_value,
            "compressed_data": encoded,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": original_size / max(1, compressed_size),
            "execution_time": end_time - start_time
        }
    
    def decompress(self, compressed_data):
        """
        Decompress data using the stored mappings.
        
        Args:
            compressed_data: Dictionary containing the compressed data and hash
            
        Returns:
            The original data
        """
        start_time = time.time()
        
        hash_value = compressed_data["hash"]
        
        # Check if we have the data in our decompression map
        if hash_value in self.decompression_map:
            data = self.decompression_map[hash_value]
        else:
            # Decode the grid pattern
            encoded = compressed_data["compressed_data"]
            grid_pattern = self._decode_grid_pattern(encoded)
            
            # Map the grid pattern back to data
            data = self._map_grid_to_data(grid_pattern)
            
            # Store for future use
            self.decompression_map[hash_value] = data
        
        end_time = time.time()
        
        return {
            "data": data,
            "execution_time": end_time - start_time
        }
    
    def _map_data_to_grid(self, data_bytes):
        """
        Map binary data to grid patterns.
        
        Args:
            data_bytes: Binary data to map
            
        Returns:
            A list of grid coordinates representing the data
        """
        grid_pattern = []
        
        # Use the bytes to navigate through the grid
        row, col = 0, 0
        
        for byte in data_bytes:
            # Use the byte value to determine movement
            row_move = byte // 16  # High 4 bits
            col_move = byte % 16   # Low 4 bits
            
            # Update position (with wrapping)
            row = (row + row_move) % self.grid.size
            col = (col + col_move) % self.grid.size
            
            # Store the grid value at this position
            grid_pattern.append((row, col, int(self.grid.grid[row, col])))
        
        return grid_pattern
    
    def _map_grid_to_data(self, grid_pattern):
        """
        Map grid patterns back to binary data.
        
        Args:
            grid_pattern: List of grid coordinates
            
        Returns:
            The reconstructed binary data
        """
        data_bytes = bytearray()
        
        prev_row, prev_col = 0, 0
        
        for row, col, _ in grid_pattern:
            # Calculate the moves that would get us from the previous position to this one
            row_move = (row - prev_row) % self.grid.size
            col_move = (col - prev_col) % self.grid.size
            
            # Combine into a byte
            byte_value = (row_move * 16) + col_move
            data_bytes.append(byte_value)
            
            # Update previous position
            prev_row, prev_col = row, col
        
        return bytes(data_bytes)
    
    def _encode_grid_pattern(self, grid_pattern):
        """
        Encode a grid pattern efficiently.
        
        Args:
            grid_pattern: List of grid coordinates
            
        Returns:
            Encoded binary data
        """
        encoded = bytearray()
        
        for row, col, value in grid_pattern:
            # Pack row, col, and value into 3 bytes
            encoded.append(row)
            encoded.append(col)
            encoded.append(value)
        
        return bytes(encoded)
    
    def _decode_grid_pattern(self, encoded):
        """
        Decode an encoded grid pattern.
        
        Args:
            encoded: Encoded binary data
            
        Returns:
            The decoded grid pattern
        """
        grid_pattern = []
        
        # Each entry is 3 bytes (row, col, value)
        for i in range(0, len(encoded), 3):
            if i + 2 < len(encoded):
                row = encoded[i]
                col = encoded[i + 1]
                value = encoded[i + 2]
                grid_pattern.append((row, col, value))
        
        return grid_pattern
    
    def get_stats(self):
        """
        Get compression statistics.
        
        Returns:
            Dictionary of compression statistics
        """
        return self.stats
    
    def visualize_compression(self, data, start_row=0, start_col=0, rows=10, cols=10, filename=None):
        """
        Visualize how data is mapped to the grid during compression.
        
        Args:
            data: Data to compress and visualize
            start_row: Starting row index for visualization
            start_col: Starting column index for visualization
            rows: Number of rows to include
            cols: Number of columns to include
            filename: If provided, save the visualization to this file
            
        Returns:
            The matplotlib figure or the filename if saved
        """
        # Compress the data to get the grid pattern
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
            
        grid_pattern = self._map_data_to_grid(data_bytes)
        
        # Extract the section to visualize
        section = self.grid.get_section(start_row, start_col, rows, cols)
        
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
        for i in range(rows):
            for j in range(cols):
                ax.text(j, i, str(section[i, j]), ha='center', va='center', 
                       color='white' if section[i, j] > 5 else 'black')
        
        # Add row and column labels
        ax.set_xticks(np.arange(cols))
        ax.set_yticks(np.arange(rows))
        ax.set_xticklabels([str(start_col + j) for j in range(cols)])
        ax.set_yticklabels([str(start_row + i) for i in range(rows)])
        
        # Highlight cells used in the compression
        for row, col, _ in grid_pattern:
            # Check if the cell is in the visible section
            if (start_row <= row < start_row + rows and 
                start_col <= col < start_col + cols):
                
                # Adjust to section coordinates
                r_adj = row - start_row
                c_adj = col - start_col
                
                # Highlight the cell
                ax.add_patch(plt.Rectangle(
                    (c_adj - 0.5, r_adj - 0.5), 
                    1, 1, fill=False, edgecolor='red', linewidth=2, zorder=3
                ))
        
        plt.title(f"Compression Mapping Visualization\n"
                 f"Section [{start_row}:{start_row+rows}, {start_col}:{start_col+cols}]")
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return filename
        else:
            # Convert to base64 for web display
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str

class FrequencyProcessor:
    def __init__(self):
        """
        Initialize a frequency processor for generating and analyzing frequency patterns.
        """
        self.timeline = []
    
    def generate_beat_pattern(self, freq1, freq2, duration=1.0, sample_rate=1000):
        """
        Generate a beat pattern between two frequencies.
        
        Args:
            freq1: First frequency in Hz
            freq2: Second frequency in Hz
            duration: Duration of the pattern in seconds
            sample_rate: Number of samples per second
            
        Returns:
            Dictionary containing the beat frequency and pattern data
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
        
        return {
            "beat_frequency": beat_frequency,
            "time": t.tolist(),
            "wave1": wave1.tolist(),
            "wave2": wave2.tolist(),
            "combined": combined.tolist()
        }
    
    def create_entangled_frequency(self, frequency, entanglement_factor=10):
        """
        Create an entangled frequency pair.
        
        Args:
            frequency: Base frequency in Hz
            entanglement_factor: Factor determining the entanglement relationship
            
        Returns:
            Dictionary containing the entangled frequency information
        """
        # Create an entangled frequency using a non-linear transformation
        entangled_frequency = (frequency * entanglement_factor) % 1000
        
        # Record in the timeline
        timestamp = time.time()
        self.timeline.append({
            "timestamp": timestamp,
            "original_frequency": frequency,
            "entangled_frequency": entangled_frequency,
            "entanglement_factor": entanglement_factor
        })
        
        return {
            "original_frequency": frequency,
            "entangled_frequency": entangled_frequency,
            "entanglement_factor": entanglement_factor,
            "timestamp": timestamp
        }
    
    def get_timeline(self):
        """
        Get the timeline of frequency entanglements.
        
        Returns:
            List of entanglement events
        """
        return self.timeline
    
    def transmit_frequencies(self, frequencies):
        """
        Simulate transmission of frequencies through the grid system.
        
        Args:
            frequencies: List of frequencies to transmit
            
        Returns:
            Dictionary containing the transmitted frequencies
        """
        # Apply a transformation to simulate transmission
        transmitted = []
        
        for freq in frequencies:
            # Apply a Fibonacci-inspired transformation
            a, b = 1, 1
            for _ in range(10):  # Apply 10 iterations
                a, b = b, (a + b) % 1000
            
            # Transform the frequency
            transformed = (freq * a + b) % 1000
            transmitted.append(transformed)
        
        return {
            "original_frequencies": frequencies,
            "transmitted_frequencies": transmitted
        }
    
    def visualize_beat_pattern(self, freq1, freq2, duration=1.0, sample_rate=1000, filename=None):
        """
        Visualize a beat pattern between two frequencies.
        
        Args:
            freq1: First frequency in Hz
            freq2: Second frequency in Hz
            duration: Duration of the pattern in seconds
            sample_rate: Number of samples per second
            filename: If provided, save the visualization to this file
            
        Returns:
            The beat frequency and the matplotlib figure or filename if saved
        """
        # Generate the beat pattern
        pattern = self.generate_beat_pattern(freq1, freq2, duration, sample_rate)
        
        # Extract data for plotting
        t = np.array(pattern["time"])
        wave1 = np.array(pattern["wave1"])
        wave2 = np.array(pattern["wave2"])
        combined = np.array(pattern["combined"])
        beat_frequency = pattern["beat_frequency"]
        
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
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return beat_frequency, filename
        else:
            # Convert to base64 for web display
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return beat_frequency, img_str

# Example usage and demonstration
if __name__ == "__main__":
    # Create a Fibonacci grid
    grid = FibonacciGrid(100)
    
    # Visualize a section of the grid
    grid.visualize_grid_section(0, 0, 10, 10, filename="fibonacci_grid_section.png")
    
    # Demonstrate lightning effect
    grid.visualize_grid_section(0, 0, 10, 10, lightning_target=(5, 5), 
                               filename="lightning_effect.png")
    
    # Demonstrate whirlwind effect
    grid.visualize_grid_section(0, 0, 10, 10, whirlwind_center=(5, 5), 
                               whirlwind_intensity=0.8, filename="whirlwind_effect.png")
    
    # Create a frequency processor
    freq_processor = FrequencyProcessor()
    
    # Generate and visualize a beat pattern
    beat_freq, _ = freq_processor.visualize_beat_pattern(400, 405, filename="beat_pattern.png")
    
    # Create entangled frequencies
    entangled = freq_processor.create_entangled_frequency(100, 10)
    
    # Create a compression database
    compression_db = CompressionDB()
    
    # Compress some data
    test_data = "This is a test string for compression using the Fibonacci grid system."
    compressed = compression_db.compress(test_data)
    
    # Visualize the compression mapping
    compression_db.visualize_compression(test_data, 0, 0, 10, 10, filename="compression_mapping.png")
    
    # Create a stacked grid system
    stacked_grids = StackedGridSystem(3, 100)
    
    # Visualize combined layers
    stacked_grids.visualize_combined_layers([0, 1], 'hadamard', 0, 0, 10, 10, 
                                          filename="combined_layers.png")
    
    # Create observers with different perspectives
    observer1 = Observer(np.eye(10), [0], "Observer A")
    observer2 = Observer(np.roll(np.eye(10), 1, axis=0), [0, 1], "Observer B")
    
    # Have observers observe the grid
    observed1 = observer1.observe(grid)
    observed2 = observer2.observe(stacked_grids)
    
    # Export some data for demonstration
    export_data = {
        "grid_section": grid.get_section(0, 0, 10, 10).tolist(),
        "beat_frequency": beat_freq,
        "entangled_frequency": entangled,
        "compression_stats": compression_db.get_stats(),
        "timeline": freq_processor.get_timeline()
    }
    
    with open("lightning_db_export.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    print("Demonstration complete. Output files generated.")
