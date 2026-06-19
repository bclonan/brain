"""
Fibonacci Grid System - Core Implementation

This module provides the core functionality for the Fibonacci Grid System,
including grid generation, observer perspectives, frequency processing,
and compression algorithms.
"""

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import hashlib
import json
import time
import math
from typing import List, Tuple, Dict, Any, Optional, Union

class FibonacciGrid:
    """
    Implements the Fibonacci Grid System based on the Fibonacci sequence modulo 10.
    
    The grid is a 2D array where each cell's value is determined by the Fibonacci
    sequence with special rules for propagation and interaction.
    """
    
    def __init__(self, size: int = 100):
        """
        Initialize a Fibonacci Grid with the specified size.
        
        Args:
            size: The size of the grid (size x size)
        """
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self._generate_grid()
        self._calculate_origins()
        self._calculate_lineages()
    
    def _generate_grid(self):
        """Generate the Fibonacci grid based on modulo 10 arithmetic."""
        # Initialize the first two Fibonacci numbers
        self.grid[0, 0] = 1  # F(1) = 1
        self.grid[0, 1] = 1  # F(2) = 1
        
        # Fill the first row with Fibonacci sequence mod 10
        for j in range(2, self.size):
            self.grid[0, j] = (self.grid[0, j-1] + self.grid[0, j-2]) % 10
        
        # Fill the first column with Fibonacci sequence mod 10
        for i in range(1, self.size):
            self.grid[i, 0] = (self.grid[i-1, 0] + self.grid[i-2, 0] if i >= 2 else 1) % 10
        
        # Fill the rest of the grid using the Fibonacci rule
        for i in range(1, self.size):
            for j in range(1, self.size):
                self.grid[i, j] = (self.grid[i-1, j] + self.grid[i, j-1]) % 10
    
    def _calculate_origins(self):
        """Identify origin cells in the grid."""
        self.origins = set()
        
        # The corners and edges are always origins
        self.origins.add((0, 0))
        self.origins.add((0, 1))
        
        # Add other origins based on special patterns
        for i in range(self.size):
            for j in range(self.size):
                # Check if this cell is an origin point
                if i == 0 or j == 0:
                    self.origins.add((i, j))
                elif self._is_origin_cell(i, j):
                    self.origins.add((i, j))
    
    def _is_origin_cell(self, i: int, j: int) -> bool:
        """
        Determine if a cell is an origin cell based on special patterns.
        
        Args:
            i: Row index
            j: Column index
            
        Returns:
            True if the cell is an origin, False otherwise
        """
        # Check for Fibonacci sequence pattern
        if (i % 3 == 0 and j % 2 == 0) or (i % 2 == 0 and j % 3 == 0):
            return True
        
        # Check for special value patterns
        value = self.grid[i, j]
        if value == 1 or value == 2 or value == 3 or value == 5 or value == 8:
            # Check surrounding cells for pattern
            neighbors = self._get_neighbors(i, j)
            neighbor_values = [self.grid[ni, nj] for ni, nj in neighbors]
            
            # If surrounded by higher values, it's an origin
            if all(value <= nv for nv in neighbor_values):
                return True
        
        return False
    
    def _get_neighbors(self, i: int, j: int) -> List[Tuple[int, int]]:
        """
        Get valid neighboring cells for a given position.
        
        Args:
            i: Row index
            j: Column index
            
        Returns:
            List of (row, col) tuples for valid neighbors
        """
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.size and 0 <= nj < self.size:
                neighbors.append((ni, nj))
        return neighbors
    
    def _calculate_lineages(self):
        """Calculate the lineage of each cell in the grid."""
        self.lineages = {}
        
        # Origins have no lineage
        for origin in self.origins:
            self.lineages[origin] = []
        
        # Calculate lineage for all other cells
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) not in self.origins:
                    self.lineages[(i, j)] = self._calculate_cell_lineage(i, j)
    
    def _calculate_cell_lineage(self, i: int, j: int) -> List[Tuple[int, int]]:
        """
        Calculate the lineage of a specific cell.
        
        Args:
            i: Row index
            j: Column index
            
        Returns:
            List of (row, col) tuples representing the cell's lineage
        """
        lineage = []
        
        # Check if we can trace lineage from above
        if i > 0:
            lineage.append((i-1, j))
        
        # Check if we can trace lineage from left
        if j > 0:
            lineage.append((i, j-1))
        
        # For cells that have both parents, check which one is more influential
        if len(lineage) > 1:
            # If one parent is an origin and the other isn't, prioritize the origin
            parent1_is_origin = (i-1, j) in self.origins
            parent2_is_origin = (i, j-1) in self.origins
            
            if parent1_is_origin and not parent2_is_origin:
                lineage = [(i-1, j)]
            elif parent2_is_origin and not parent1_is_origin:
                lineage = [(i, j-1)]
        
        return lineage
    
    def get_section(self, start_row: int, start_col: int, rows: int, cols: int) -> np.ndarray:
        """
        Get a section of the grid.
        
        Args:
            start_row: Starting row index
            start_col: Starting column index
            rows: Number of rows to include
            cols: Number of columns to include
            
        Returns:
            NumPy array containing the grid section
        """
        end_row = min(start_row + rows, self.size)
        end_col = min(start_col + cols, self.size)
        
        return self.grid[start_row:end_row, start_col:end_col].copy()
    
    def get_value(self, row: int, col: int) -> int:
        """
        Get the value of a specific cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            The cell value
        """
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row, col]
        return -1  # Invalid position
    
    def is_origin(self, row: int, col: int) -> bool:
        """
        Check if a cell is an origin cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            True if the cell is an origin, False otherwise
        """
        return (row, col) in self.origins
    
    def get_lineage(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get the lineage of a specific cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            List of (row, col) tuples representing the cell's lineage
        """
        if (row, col) in self.lineages:
            return self.lineages[(row, col)]
        return []
    
    def get_lightning_path(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get the lightning path from origins to a specific cell.
        
        The lightning path represents the most direct path from an origin
        cell to the target cell, showing how the value propagates through
        the grid.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            List of (row, col) tuples representing the lightning path
        """
        if self.is_origin(row, col):
            return [(row, col)]
        
        path = []
        current = (row, col)
        
        while not self.is_origin(*current):
            path.append(current)
            lineage = self.get_lineage(*current)
            
            if not lineage:
                break
                
            # Choose the most influential parent
            current = lineage[0]
        
        # Add the origin cell
        path.append(current)
        
        # Reverse to get path from origin to target
        return path[::-1]
    
    def get_whirlwind_effect(self, center_row: int, center_col: int, intensity: float = 0.8) -> List[Tuple[int, int]]:
        """
        Get cells affected by a whirlwind centered at a specific cell.
        
        The whirlwind effect represents a spiral pattern of influence
        emanating from the center cell.
        
        Args:
            center_row: Center row index
            center_col: Center column index
            intensity: Intensity of the whirlwind (0.0 to 1.0)
            
        Returns:
            List of (row, col) tuples representing affected cells
        """
        affected_cells = []
        
        # Determine radius based on intensity
        radius = int(max(3, min(10, 10 * intensity)))
        
        # Generate spiral pattern
        for r in range(1, radius + 1):
            for theta in np.linspace(0, 2*np.pi, 8*r, endpoint=False):
                i = int(center_row + r * np.sin(theta))
                j = int(center_col + r * np.cos(theta))
                
                if 0 <= i < self.size and 0 <= j < self.size:
                    affected_cells.append((i, j))
        
        return affected_cells
    
    def visualize_section(self, start_row: int, start_col: int, rows: int, cols: int, 
                         lightning_target: Optional[Tuple[int, int]] = None,
                         whirlwind_center: Optional[Tuple[int, int]] = None,
                         whirlwind_intensity: float = 0.8) -> str:
        """
        Visualize a section of the grid with optional effects.
        
        Args:
            start_row: Starting row index
            start_col: Starting column index
            rows: Number of rows to include
            cols: Number of columns to include
            lightning_target: Optional (row, col) for lightning effect
            whirlwind_center: Optional (row, col) for whirlwind effect
            whirlwind_intensity: Intensity of whirlwind effect
            
        Returns:
            Base64-encoded PNG image
        """
        grid_section = self.get_section(start_row, start_col, rows, cols)
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create visualization
        cmap = plt.cm.viridis
        im = ax.imshow(grid_section, cmap=cmap)
        
        # Add grid lines
        ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
        ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
        
        # Add cell values
        for i in range(rows):
            for j in range(cols):
                text = ax.text(j, i, grid_section[i, j],
                              ha="center", va="center", color="white", fontweight="bold")
        
        # Add lightning effect if specified
        if lightning_target:
            lightning_row, lightning_col = lightning_target
            if (start_row <= lightning_row < start_row + rows and 
                start_col <= lightning_col < start_col + cols):
                # Highlight the target cell
                rect = plt.Rectangle((lightning_col - start_col - 0.5, lightning_row - start_row - 0.5), 
                                    1, 1, fill=False, edgecolor='yellow', linewidth=3)
                ax.add_patch(rect)
                
                # Get and highlight the lightning path
                lightning_path = self.get_lightning_path(lightning_row, lightning_col)
                for path_row, path_col in lightning_path:
                    if (start_row <= path_row < start_row + rows and 
                        start_col <= path_col < start_col + cols):
                        rect = plt.Rectangle((path_col - start_col - 0.5, path_row - start_row - 0.5), 
                                            1, 1, fill=False, edgecolor='orange', linewidth=2)
                        ax.add_patch(rect)
        
        # Add whirlwind effect if specified
        if whirlwind_center:
            whirlwind_row, whirlwind_col = whirlwind_center
            if (start_row <= whirlwind_row < start_row + rows and 
                start_col <= whirlwind_col < start_col + cols):
                # Highlight the center cell
                rect = plt.Rectangle((whirlwind_col - start_col - 0.5, whirlwind_row - start_row - 0.5), 
                                    1, 1, fill=False, edgecolor='cyan', linewidth=3)
                ax.add_patch(rect)
                
                # Get and highlight the whirlwind affected cells
                affected_cells = self.get_whirlwind_effect(whirlwind_row, whirlwind_col, whirlwind_intensity)
                for path_row, path_col in affected_cells:
                    if (start_row <= path_row < start_row + rows and 
                        start_col <= path_col < start_col + cols):
                        rect = plt.Rectangle((path_col - start_col - 0.5, path_row - start_row - 0.5), 
                                            1, 1, fill=False, edgecolor='blue', linewidth=2)
                        ax.add_patch(rect)
        
        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add title
        ax.set_title(f"Fibonacci Grid Section [{start_row}:{start_row+rows}, {start_col}:{start_col+cols}]")
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        plt.close(fig)
        
        return img_base64


class Observer:
    """
    Implements an observer perspective for the Fibonacci Grid System.
    
    An observer applies transformations to the grid based on its unique
    perspective, allowing for different interpretations of the same grid.
    """
    
    def __init__(self, name: str = "Default Observer", focus_layers: List[int] = None):
        """
        Initialize an observer with a name and focus layers.
        
        Args:
            name: Observer name
            focus_layers: List of grid layers to focus on (default: [0])
        """
        self.name = name
        self.focus_layers = focus_layers or [0]
        self.transformation_matrix = None
        self._initialize_transformation_matrix()
    
    def _initialize_transformation_matrix(self):
        """Initialize the transformation matrix as identity."""
        self.transformation_matrix = np.eye(10, dtype=int)
    
    def set_transformation_matrix(self, matrix: List[List[int]]):
        """
        Set the transformation matrix for this observer.
        
        Args:
            matrix: 10x10 transformation matrix or 10x1 mapping vector
        """
        if isinstance(matrix[0], list) and len(matrix) == 10 and len(matrix[0]) == 10:
            # Full 10x10 matrix
            self.transformation_matrix = np.array(matrix)
        elif isinstance(matrix[0], list) and len(matrix) == 10 and len(matrix[0]) == 1:
            # 10x1 mapping vector
            mapping = [row[0] for row in matrix]
            self.transformation_matrix = np.zeros((10, 10), dtype=int)
            for i, val in enumerate(mapping):
                if 1 <= val <= 10:
                    self.transformation_matrix[i, val-1] = 1
        else:
            raise ValueError("Transformation matrix must be 10x10 or 10x1")
    
    def observe(self, grid_section: np.ndarray) -> np.ndarray:
        """
        Apply the observer's perspective to a grid section.
        
        Args:
            grid_section: NumPy array representing a section of the grid
            
        Returns:
            Transformed grid section
        """
        rows, cols = grid_section.shape
        observed_grid = np.zeros_like(grid_section)
        
        for i in range(rows):
            for j in range(cols):
                value = grid_section[i, j]
                
                # Apply transformation
                observed_grid[i, j] = self._apply_transformation(value)
        
        return observed_grid
    
    def _apply_transformation(self, value: int) -> int:
        """
        Apply the transformation matrix to a single value.
        
        Args:
            value: Original value (0-9)
            
        Returns:
            Transformed value
        """
        if 0 <= value <= 9:
            # Get the corresponding row from the transformation matrix
            transformed = np.argmax(self.transformation_matrix[value])
            return transformed
        return value


class FrequencyProcessor:
    """
    Implements frequency processing for the Fibonacci Grid System.
    
    This class handles the generation and analysis of frequency patterns,
    beat patterns, and entangled frequency pairs.
    """
    
    def __init__(self):
        """Initialize the frequency processor."""
        pass
    
    def generate_beat_pattern(self, freq1: float, freq2: float, duration: float = 1.0, 
                             sample_rate: int = 1000) -> Dict[str, Any]:
        """
        Generate a beat pattern from two frequencies.
        
        Args:
            freq1: First frequency in Hz
            freq2: Second frequency in Hz
            duration: Duration in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            Dictionary containing wave data and beat frequency
        """
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        # Generate the two waves
        wave1 = np.sin(2 * np.pi * freq1 * t)
        wave2 = np.sin(2 * np.pi * freq2 * t)
        
        # Generate the beat pattern
        beat = wave1 + wave2
        
        # Calculate beat frequency
        beat_frequency = abs(freq1 - freq2)
        
        return {
            'wave1': wave1.tolist(),
            'wave2': wave2.tolist(),
            'beat': beat.tolist(),
            'beat_frequency': beat_frequency,
            't': t.tolist()
        }
    
    def create_entangled_pair(self, base_frequency: float, entanglement_factor: float) -> Dict[str, Any]:
        """
        Create an entangled frequency pair.
        
        Args:
            base_frequency: Base frequency in Hz
            entanglement_factor: Factor determining the relationship
            
        Returns:
            Dictionary containing the entangled pair information
        """
        # Calculate entangled frequency using Fibonacci relationship
        fib_ratio = (1 + math.sqrt(5)) / 2  # Golden ratio
        entangled_frequency = base_frequency * fib_ratio * (entanglement_factor / 10)
        
        return {
            'base_frequency': base_frequency,
            'entangled_frequency': entangled_frequency,
            'entanglement_factor': entanglement_factor,
            'relationship': 'fibonacci_golden_ratio'
        }
    
    def analyze_resonance(self, frequencies: List[float]) -> Dict[str, Any]:
        """
        Analyze resonance patterns in a set of frequencies.
        
        Args:
            frequencies: List of frequencies to analyze
            
        Returns:
            Dictionary containing resonance analysis
        """
        resonance_patterns = []
        
        # Find Fibonacci relationships
        for i, freq1 in enumerate(frequencies):
            for j, freq2 in enumerate(frequencies):
                if i < j:
                    ratio = freq2 / freq1 if freq1 > 0 else 0
                    
                    # Check if ratio is close to golden ratio
                    golden_ratio = (1 + math.sqrt(5)) / 2
                    if abs(ratio - golden_ratio) < 0.1:
                        resonance_patterns.append({
                            'type': 'golden_ratio',
                            'freq1': freq1,
                            'freq2': freq2,
                            'ratio': ratio
                        })
                    
                    # Check if ratio is close to a Fibonacci ratio
                    fib_ratios = [1, 2, 3/2, 5/3, 8/5, 13/8]
                    for fib_ratio in fib_ratios:
                        if abs(ratio - fib_ratio) < 0.1:
                            resonance_patterns.append({
                                'type': 'fibonacci_ratio',
                                'freq1': freq1,
                                'freq2': freq2,
                                'ratio': ratio,
                                'nearest_fib_ratio': fib_ratio
                            })
        
        return {
            'frequencies': frequencies,
            'resonance_patterns': resonance_patterns
        }


class CompressionDB:
    """
    Implements a compression database using the Fibonacci Grid System.
    
    This class provides methods for compressing and decompressing data
    using the patterns in the Fibonacci grid.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the compression database.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid_size = grid_size
        self.grid = FibonacciGrid(grid_size)
        self.compression_map = {}
        self.stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0
        }
    
    def compress(self, data: str) -> Dict[str, Any]:
        """
        Compress data using the Fibonacci grid.
        
        Args:
            data: String data to compress
            
        Returns:
            Dictionary containing compressed data information
        """
        if not data:
            return {
                'hash': '',
                'compressed_data': '',
                'original_size': 0,
                'compressed_size': 0,
                'compression_ratio': 1.0
            }
        
        # Calculate hash of original data
        hash_value = hashlib.md5(data.encode()).hexdigest()
        
        # Convert data to grid coordinates
        coordinates = self._data_to_coordinates(data)
        
        # Compress coordinates using grid patterns
        compressed_coords = self._compress_coordinates(coordinates)
        
        # Convert compressed coordinates to string
        compressed_data = base64.b64encode(json.dumps(compressed_coords).encode()).decode()
        
        # Calculate compression stats
        original_size = len(data)
        compressed_size = len(compressed_data)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        # Update stats
        self.stats['total_compressed'] += 1
        self.stats['total_original_size'] += original_size
        self.stats['total_compressed_size'] += compressed_size
        
        # Store in compression map
        self.compression_map[hash_value] = {
            'original_data': data,
            'compressed_data': compressed_data,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio
        }
        
        return {
            'hash': hash_value,
            'compressed_data': compressed_data,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio
        }
    
    def decompress(self, compressed: Dict[str, str]) -> Dict[str, Any]:
        """
        Decompress data using the Fibonacci grid.
        
        Args:
            compressed: Dictionary containing hash and compressed data
            
        Returns:
            Dictionary containing decompressed data information
        """
        hash_value = compressed.get('hash', '')
        compressed_data = compressed.get('compressed_data', '')
        
        if not hash_value or not compressed_data:
            return {
                'data': '',
                'original_size': 0,
                'success': False,
                'error': 'Invalid compressed data'
            }
        
        # Check if we have this hash in our map
        if hash_value in self.compression_map:
            return {
                'data': self.compression_map[hash_value]['original_data'],
                'original_size': self.compression_map[hash_value]['original_size'],
                'success': True
            }
        
        try:
            # Decode compressed data
            compressed_coords = json.loads(base64.b64decode(compressed_data).decode())
            
            # Decompress coordinates
            coordinates = self._decompress_coordinates(compressed_coords)
            
            # Convert coordinates back to data
            data = self._coordinates_to_data(coordinates)
            
            # Verify hash
            computed_hash = hashlib.md5(data.encode()).hexdigest()
            if computed_hash != hash_value:
                return {
                    'data': '',
                    'original_size': 0,
                    'success': False,
                    'error': 'Hash verification failed'
                }
            
            # Store in compression map for future use
            original_size = len(data)
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            self.compression_map[hash_value] = {
                'original_data': data,
                'compressed_data': compressed_data,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio
            }
            
            return {
                'data': data,
                'original_size': original_size,
                'success': True
            }
        except Exception as e:
            return {
                'data': '',
                'original_size': 0,
                'success': False,
                'error': str(e)
            }
    
    def _data_to_coordinates(self, data: str) -> List[Tuple[int, int]]:
        """
        Convert string data to grid coordinates.
        
        Args:
            data: String data to convert
            
        Returns:
            List of (row, col) coordinates
        """
        coordinates = []
        
        for char in data:
            # Use character code to determine coordinates
            code = ord(char)
            row = code % self.grid_size
            col = (code // self.grid_size) % self.grid_size
            
            coordinates.append((row, col))
        
        return coordinates
    
    def _coordinates_to_data(self, coordinates: List[Tuple[int, int]]) -> str:
        """
        Convert grid coordinates back to string data.
        
        Args:
            coordinates: List of (row, col) coordinates
            
        Returns:
            Reconstructed string data
        """
        data = ""
        
        for row, col in coordinates:
            # Convert coordinates back to character code
            code = row + col * self.grid_size
            
            # Ensure code is in valid ASCII range
            code = max(32, min(126, code))
            
            data += chr(code)
        
        return data
    
    def _compress_coordinates(self, coordinates: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
        """
        Compress coordinates using grid patterns.
        
        Args:
            coordinates: List of (row, col) coordinates
            
        Returns:
            Compressed representation of coordinates
        """
        compressed = []
        i = 0
        
        while i < len(coordinates):
            # Look for patterns
            pattern_length = self._find_pattern_length(coordinates, i)
            
            if pattern_length > 3:
                # We found a repeating pattern
                pattern = coordinates[i:i+pattern_length]
                
                # Count repetitions
                repetitions = 1
                j = i + pattern_length
                
                while j + pattern_length <= len(coordinates) and coordinates[j:j+pattern_length] == pattern:
                    repetitions += 1
                    j += pattern_length
                
                # Add compressed pattern
                compressed.append({
                    'type': 'pattern',
                    'pattern': pattern,
                    'repetitions': repetitions
                })
                
                i = j
            else:
                # No pattern, add individual coordinate
                compressed.append({
                    'type': 'single',
                    'coordinate': coordinates[i]
                })
                i += 1
        
        return compressed
    
    def _decompress_coordinates(self, compressed: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """
        Decompress coordinates from compressed representation.
        
        Args:
            compressed: Compressed representation of coordinates
            
        Returns:
            List of (row, col) coordinates
        """
        coordinates = []
        
        for item in compressed:
            if item['type'] == 'pattern':
                pattern = item['pattern']
                repetitions = item['repetitions']
                
                for _ in range(repetitions):
                    coordinates.extend(pattern)
            else:
                coordinates.append(tuple(item['coordinate']))
        
        return coordinates
    
    def _find_pattern_length(self, coordinates: List[Tuple[int, int]], start: int) -> int:
        """
        Find the length of a repeating pattern starting at a specific index.
        
        Args:
            coordinates: List of coordinates
            start: Starting index
            
        Returns:
            Length of the pattern (0 if no pattern found)
        """
        max_pattern_length = min(10, (len(coordinates) - start) // 2)
        
        for pattern_length in range(2, max_pattern_length + 1):
            pattern = coordinates[start:start+pattern_length]
            next_segment = coordinates[start+pattern_length:start+2*pattern_length]
            
            if pattern == next_segment:
                return pattern_length
        
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get compression statistics.
        
        Returns:
            Dictionary containing compression statistics
        """
        stats = self.stats.copy()
        
        # Calculate overall compression ratio
        if stats['total_compressed_size'] > 0:
            stats['compression_ratio'] = stats['total_original_size'] / stats['total_compressed_size']
        else:
            stats['compression_ratio'] = 1.0
        
        return stats


# Demo implementations for practical applications

class SecureMessaging:
    """
    Implements secure messaging using the Fibonacci Grid System.
    
    This class demonstrates how the grid system can be used for
    secure communication with multiple observer perspectives.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the secure messaging system.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.observers = {}
    
    def add_observer(self, name: str, transformation_matrix: Optional[List[List[int]]] = None) -> str:
        """
        Add an observer to the system.
        
        Args:
            name: Observer name
            transformation_matrix: Optional transformation matrix
            
        Returns:
            Observer ID
        """
        observer_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:8]
        observer = Observer(name)
        
        if transformation_matrix:
            observer.set_transformation_matrix(transformation_matrix)
        
        self.observers[observer_id] = observer
        return observer_id
    
    def encode_message(self, message: str, observer_id: str) -> Dict[str, Any]:
        """
        Encode a message using an observer's perspective.
        
        Args:
            message: Message to encode
            observer_id: ID of the observer to use
            
        Returns:
            Dictionary containing encoded message information
        """
        if observer_id not in self.observers:
            return {'error': 'Observer not found'}
        
        observer = self.observers[observer_id]
        
        # Convert message to coordinates
        coordinates = []
        for char in message:
            code = ord(char)
            row = code % self.grid.size
            col = (code // self.grid.size) % self.grid.size
            coordinates.append((row, col))
        
        # Get grid values at these coordinates
        values = [self.grid.get_value(row, col) for row, col in coordinates]
        
        # Apply observer transformation
        encoded_values = [observer._apply_transformation(val) for val in values]
        
        # Convert to string
        encoded_message = ''.join([str(val) for val in encoded_values])
        
        return {
            'original_message': message,
            'encoded_message': encoded_message,
            'observer_id': observer_id,
            'observer_name': observer.name
        }
    
    def decode_message(self, encoded_message: str, observer_id: str) -> Dict[str, Any]:
        """
        Decode a message using an observer's perspective.
        
        Args:
            encoded_message: Encoded message
            observer_id: ID of the observer to use
            
        Returns:
            Dictionary containing decoded message information
        """
        if observer_id not in self.observers:
            return {'error': 'Observer not found'}
        
        observer = self.observers[observer_id]
        
        # Parse encoded values
        encoded_values = [int(char) for char in encoded_message if char.isdigit()]
        
        # Create inverse transformation
        inverse_matrix = np.linalg.inv(observer.transformation_matrix)
        
        # Apply inverse transformation
        decoded_values = []
        for val in encoded_values:
            # Find the original value that would transform to this encoded value
            for original in range(10):
                if observer._apply_transformation(original) == val:
                    decoded_values.append(original)
                    break
            else:
                decoded_values.append(val)  # Keep as is if no match
        
        # Convert back to coordinates and then to characters
        message = ""
        for i in range(0, len(decoded_values), 2):
            if i + 1 < len(decoded_values):
                row = decoded_values[i]
                col = decoded_values[i + 1]
                
                # Find a character that would map to these coordinates
                code = row + col * self.grid.size
                code = max(32, min(126, code))  # Ensure valid ASCII
                message += chr(code)
        
        return {
            'encoded_message': encoded_message,
            'decoded_message': message,
            'observer_id': observer_id,
            'observer_name': observer.name
        }


class MemorySystem:
    """
    Implements a memory system using the Fibonacci Grid System.
    
    This class demonstrates how the grid system can be used as a
    new approach to computer memory with efficient access patterns.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the memory system.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.memory_blocks = {}
        self.address_map = {}
    
    def allocate(self, block_id: str, size: int) -> Dict[str, Any]:
        """
        Allocate a memory block.
        
        Args:
            block_id: Unique identifier for the block
            size: Size of the block in bytes
            
        Returns:
            Dictionary containing allocation information
        """
        if block_id in self.memory_blocks:
            return {'error': 'Block ID already exists'}
        
        # Find available grid cells
        cells = self._find_available_cells(size)
        
        if len(cells) < size:
            return {'error': 'Not enough available cells'}
        
        # Allocate cells
        self.memory_blocks[block_id] = {
            'cells': cells,
            'size': size,
            'data': [0] * size,
            'allocated_at': time.time()
        }
        
        # Update address map
        for i, cell in enumerate(cells):
            self.address_map[cell] = (block_id, i)
        
        return {
            'block_id': block_id,
            'size': size,
            'cells': cells
        }
    
    def write(self, block_id: str, data: List[int]) -> Dict[str, Any]:
        """
        Write data to a memory block.
        
        Args:
            block_id: Block identifier
            data: List of integer values to write
            
        Returns:
            Dictionary containing write operation information
        """
        if block_id not in self.memory_blocks:
            return {'error': 'Block not found'}
        
        block = self.memory_blocks[block_id]
        
        if len(data) > block['size']:
            return {'error': 'Data exceeds block size'}
        
        # Write data
        for i, value in enumerate(data):
            block['data'][i] = value
        
        return {
            'block_id': block_id,
            'written': len(data),
            'status': 'success'
        }
    
    def read(self, block_id: str, offset: int = 0, length: int = None) -> Dict[str, Any]:
        """
        Read data from a memory block.
        
        Args:
            block_id: Block identifier
            offset: Starting offset
            length: Number of bytes to read (None for all)
            
        Returns:
            Dictionary containing read operation information
        """
        if block_id not in self.memory_blocks:
            return {'error': 'Block not found'}
        
        block = self.memory_blocks[block_id]
        
        if offset >= block['size']:
            return {'error': 'Offset out of bounds'}
        
        if length is None:
            length = block['size'] - offset
        
        if offset + length > block['size']:
            return {'error': 'Read operation out of bounds'}
        
        # Read data
        data = block['data'][offset:offset+length]
        
        # Use lightning paths for access pattern
        access_paths = []
        for i, cell in enumerate(block['cells'][offset:offset+length]):
            path = self.grid.get_lightning_path(*cell)
            access_paths.append(path)
        
        return {
            'block_id': block_id,
            'data': data,
            'offset': offset,
            'length': length,
            'access_paths': access_paths
        }
    
    def free(self, block_id: str) -> Dict[str, Any]:
        """
        Free a memory block.
        
        Args:
            block_id: Block identifier
            
        Returns:
            Dictionary containing free operation information
        """
        if block_id not in self.memory_blocks:
            return {'error': 'Block not found'}
        
        block = self.memory_blocks[block_id]
        
        # Remove from address map
        for cell in block['cells']:
            if cell in self.address_map:
                del self.address_map[cell]
        
        # Remove block
        del self.memory_blocks[block_id]
        
        return {
            'block_id': block_id,
            'status': 'freed',
            'cells_freed': len(block['cells'])
        }
    
    def _find_available_cells(self, count: int) -> List[Tuple[int, int]]:
        """
        Find available grid cells for allocation.
        
        Args:
            count: Number of cells needed
            
        Returns:
            List of (row, col) tuples for available cells
        """
        cells = []
        
        # Prioritize cells along lightning paths from origins
        for origin in self.grid.origins:
            if len(cells) >= count:
                break
                
            # Get cells along lightning paths
            for i in range(self.grid.size):
                for j in range(self.grid.size):
                    if len(cells) >= count:
                        break
                        
                    cell = (i, j)
                    if cell not in self.address_map and cell not in cells:
                        path = self.grid.get_lightning_path(i, j)
                        if origin in path:
                            cells.append(cell)
        
        # If we still need more cells, add any available ones
        if len(cells) < count:
            for i in range(self.grid.size):
                for j in range(self.grid.size):
                    if len(cells) >= count:
                        break
                        
                    cell = (i, j)
                    if cell not in self.address_map and cell not in cells:
                        cells.append(cell)
        
        return cells[:count]


class PatternRecognition:
    """
    Implements pattern recognition using the Fibonacci Grid System.
    
    This class demonstrates how the grid system can be used for
    identifying patterns in data through frequency analysis and grid mapping.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the pattern recognition system.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.frequency_processor = FrequencyProcessor()
        self.patterns = {}
    
    def map_data_to_grid(self, data: List[float]) -> Dict[str, Any]:
        """
        Map numerical data to grid coordinates.
        
        Args:
            data: List of numerical values
            
        Returns:
            Dictionary containing mapping information
        """
        if not data:
            return {'error': 'No data provided'}
        
        # Normalize data to 0-1 range
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val
        
        if range_val == 0:
            normalized = [0.5 for _ in data]
        else:
            normalized = [(x - min_val) / range_val for x in data]
        
        # Map to grid coordinates
        coordinates = []
        for i, val in enumerate(normalized):
            row = int(val * (self.grid.size - 1))
            col = i % self.grid.size
            coordinates.append((row, col))
        
        # Get grid values at these coordinates
        values = [self.grid.get_value(row, col) for row, col in coordinates]
        
        # Calculate frequency distribution
        freq_dist = {}
        for val in values:
            freq_dist[val] = freq_dist.get(val, 0) + 1
        
        # Store pattern
        pattern_id = hashlib.md5(str(data).encode()).hexdigest()[:8]
        self.patterns[pattern_id] = {
            'data': data,
            'coordinates': coordinates,
            'grid_values': values,
            'frequency_distribution': freq_dist
        }
        
        return {
            'pattern_id': pattern_id,
            'coordinates': coordinates,
            'grid_values': values,
            'frequency_distribution': freq_dist
        }
    
    def analyze_pattern(self, pattern_id: str) -> Dict[str, Any]:
        """
        Analyze a mapped pattern for insights.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Dictionary containing analysis information
        """
        if pattern_id not in self.patterns:
            return {'error': 'Pattern not found'}
        
        pattern = self.patterns[pattern_id]
        
        # Analyze frequency distribution
        freq_dist = pattern['frequency_distribution']
        most_common = max(freq_dist.items(), key=lambda x: x[1])
        
        # Look for repeating sequences
        values = pattern['grid_values']
        sequences = self._find_repeating_sequences(values)
        
        # Analyze using frequency processor
        frequencies = [float(val) for val in values]
        resonance = self.frequency_processor.analyze_resonance(frequencies)
        
        # Check for lightning path patterns
        lightning_patterns = []
        for i, (row, col) in enumerate(pattern['coordinates']):
            path = self.grid.get_lightning_path(row, col)
            if len(path) > 3:
                lightning_patterns.append({
                    'index': i,
                    'coordinate': (row, col),
                    'path_length': len(path)
                })
        
        return {
            'pattern_id': pattern_id,
            'most_common_value': most_common[0],
            'most_common_count': most_common[1],
            'repeating_sequences': sequences,
            'resonance_patterns': resonance['resonance_patterns'],
            'lightning_patterns': lightning_patterns[:10]  # Limit to top 10
        }
    
    def compare_patterns(self, pattern_id1: str, pattern_id2: str) -> Dict[str, Any]:
        """
        Compare two patterns for similarities.
        
        Args:
            pattern_id1: First pattern identifier
            pattern_id2: Second pattern identifier
            
        Returns:
            Dictionary containing comparison information
        """
        if pattern_id1 not in self.patterns:
            return {'error': f'Pattern {pattern_id1} not found'}
        
        if pattern_id2 not in self.patterns:
            return {'error': f'Pattern {pattern_id2} not found'}
        
        pattern1 = self.patterns[pattern_id1]
        pattern2 = self.patterns[pattern_id2]
        
        # Compare frequency distributions
        freq_dist1 = pattern1['frequency_distribution']
        freq_dist2 = pattern2['frequency_distribution']
        
        # Calculate similarity score
        similarity = self._calculate_similarity(
            pattern1['grid_values'], 
            pattern2['grid_values']
        )
        
        # Find common sequences
        common_sequences = self._find_common_sequences(
            pattern1['grid_values'],
            pattern2['grid_values']
        )
        
        return {
            'pattern_id1': pattern_id1,
            'pattern_id2': pattern_id2,
            'similarity_score': similarity,
            'common_sequences': common_sequences
        }
    
    def _find_repeating_sequences(self, values: List[int], min_length: int = 3) -> List[Dict[str, Any]]:
        """
        Find repeating sequences in a list of values.
        
        Args:
            values: List of values to analyze
            min_length: Minimum sequence length
            
        Returns:
            List of dictionaries containing sequence information
        """
        sequences = []
        
        for length in range(min_length, min(10, len(values) // 2 + 1)):
            for i in range(len(values) - length + 1):
                seq = tuple(values[i:i+length])
                
                # Look for repetitions
                repetitions = []
                for j in range(i + 1, len(values) - length + 1):
                    if tuple(values[j:j+length]) == seq:
                        repetitions.append(j)
                
                if repetitions:
                    # Check if this is a new sequence
                    is_new = True
                    for existing in sequences:
                        if existing['sequence'] == seq:
                            is_new = False
                            break
                    
                    if is_new:
                        sequences.append({
                            'sequence': seq,
                            'length': length,
                            'first_occurrence': i,
                            'repetitions': repetitions,
                            'count': len(repetitions) + 1
                        })
        
        # Sort by count (most repetitions first)
        sequences.sort(key=lambda x: x['count'], reverse=True)
        
        return sequences
    
    def _find_common_sequences(self, values1: List[int], values2: List[int], min_length: int = 3) -> List[Dict[str, Any]]:
        """
        Find common sequences between two lists of values.
        
        Args:
            values1: First list of values
            values2: Second list of values
            min_length: Minimum sequence length
            
        Returns:
            List of dictionaries containing common sequence information
        """
        common_sequences = []
        
        for length in range(min_length, min(10, min(len(values1), len(values2)) // 2 + 1)):
            # Get all sequences of this length from values1
            seqs1 = {}
            for i in range(len(values1) - length + 1):
                seq = tuple(values1[i:i+length])
                if seq not in seqs1:
                    seqs1[seq] = []
                seqs1[seq].append(i)
            
            # Check for matches in values2
            for i in range(len(values2) - length + 1):
                seq = tuple(values2[i:i+length])
                if seq in seqs1:
                    # Found a common sequence
                    common_sequences.append({
                        'sequence': seq,
                        'length': length,
                        'occurrences1': seqs1[seq],
                        'occurrences2': [i],
                        'count1': len(seqs1[seq]),
                        'count2': 1
                    })
        
        # Sort by total count
        common_sequences.sort(key=lambda x: x['count1'] + x['count2'], reverse=True)
        
        return common_sequences
    
    def _calculate_similarity(self, values1: List[int], values2: List[int]) -> float:
        """
        Calculate similarity score between two lists of values.
        
        Args:
            values1: First list of values
            values2: Second list of values
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Ensure lists are the same length for comparison
        min_length = min(len(values1), len(values2))
        values1 = values1[:min_length]
        values2 = values2[:min_length]
        
        # Count exact matches
        exact_matches = sum(1 for v1, v2 in zip(values1, values2) if v1 == v2)
        
        # Count near matches (off by 1)
        near_matches = sum(1 for v1, v2 in zip(values1, values2) if abs(v1 - v2) == 1)
        
        # Calculate similarity score
        similarity = (exact_matches + 0.5 * near_matches) / min_length
        
        return similarity


class NetworkTransfer:
    """
    Implements network data transfer using the Fibonacci Grid System.
    
    This class demonstrates how the grid system can be used for
    optimizing data transfer using grid-based encoding.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the network transfer system.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.compression_db = CompressionDB(grid_size)
        self.packets = {}
        self.routes = {}
    
    def encode_packet(self, data: str, route_id: str = None) -> Dict[str, Any]:
        """
        Encode a data packet for transmission.
        
        Args:
            data: Data to encode
            route_id: Optional route identifier
            
        Returns:
            Dictionary containing encoded packet information
        """
        # Compress data
        compressed = self.compression_db.compress(data)
        
        # Generate packet ID
        packet_id = hashlib.md5(f"{compressed['hash']}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create packet
        packet = {
            'id': packet_id,
            'hash': compressed['hash'],
            'compressed_data': compressed['compressed_data'],
            'original_size': compressed['original_size'],
            'compressed_size': compressed['compressed_size'],
            'route_id': route_id,
            'created_at': time.time()
        }
        
        self.packets[packet_id] = packet
        
        return packet
    
    def decode_packet(self, packet_id: str) -> Dict[str, Any]:
        """
        Decode a data packet after transmission.
        
        Args:
            packet_id: Packet identifier
            
        Returns:
            Dictionary containing decoded packet information
        """
        if packet_id not in self.packets:
            return {'error': 'Packet not found'}
        
        packet = self.packets[packet_id]
        
        # Decompress data
        decompressed = self.compression_db.decompress({
            'hash': packet['hash'],
            'compressed_data': packet['compressed_data']
        })
        
        if not decompressed['success']:
            return {'error': 'Failed to decompress packet'}
        
        return {
            'packet_id': packet_id,
            'data': decompressed['data'],
            'original_size': packet['original_size'],
            'compressed_size': packet['compressed_size'],
            'route_id': packet['route_id']
        }
    
    def create_route(self, name: str, hops: int = 5) -> Dict[str, Any]:
        """
        Create a network route using grid-based path finding.
        
        Args:
            name: Route name
            hops: Number of hops in the route
            
        Returns:
            Dictionary containing route information
        """
        # Generate route ID
        route_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create route using lightning paths
        path = []
        
        # Start from a random origin
        origins = list(self.grid.origins)
        start = origins[hash(name) % len(origins)]
        path.append(start)
        
        # Add hops using lightning paths
        current = start
        for _ in range(hops):
            # Find cells affected by whirlwind from current position
            affected = self.grid.get_whirlwind_effect(*current)
            
            if affected:
                # Choose next hop
                next_hop = affected[hash(f"{name}_{len(path)}") % len(affected)]
                path.append(next_hop)
                current = next_hop
        
        # Calculate route metrics
        route_length = len(path)
        route_values = [self.grid.get_value(row, col) for row, col in path]
        
        # Calculate frequency signature
        frequencies = [float(val) for val in route_values]
        resonance = self.frequency_processor.analyze_resonance(frequencies)
        
        route = {
            'id': route_id,
            'name': name,
            'path': path,
            'length': route_length,
            'values': route_values,
            'resonance': resonance,
            'created_at': time.time()
        }
        
        self.routes[route_id] = route
        
        return route
    
    def simulate_transfer(self, packet_id: str, route_id: str) -> Dict[str, Any]:
        """
        Simulate data transfer of a packet through a route.
        
        Args:
            packet_id: Packet identifier
            route_id: Route identifier
            
        Returns:
            Dictionary containing transfer simulation information
        """
        if packet_id not in self.packets:
            return {'error': 'Packet not found'}
        
        if route_id not in self.routes:
            return {'error': 'Route not found'}
        
        packet = self.packets[packet_id]
        route = self.routes[route_id]
        
        # Update packet route
        packet['route_id'] = route_id
        
        # Simulate transfer
        hops = []
        for i, (row, col) in enumerate(route['path']):
            # Calculate hop metrics
            value = self.grid.get_value(row, col)
            lightning_path = self.grid.get_lightning_path(row, col)
            
            # Simulate transfer time based on grid value and path length
            transfer_time = (value / 10) * (len(lightning_path) / 5) * 0.01
            
            hops.append({
                'hop': i + 1,
                'position': (row, col),
                'value': value,
                'lightning_path_length': len(lightning_path),
                'transfer_time': transfer_time
            })
        
        # Calculate total transfer time
        total_time = sum(hop['transfer_time'] for hop in hops)
        
        # Calculate bandwidth usage
        bandwidth = packet['compressed_size'] / total_time if total_time > 0 else 0
        
        return {
            'packet_id': packet_id,
            'route_id': route_id,
            'hops': hops,
            'total_hops': len(hops),
            'total_transfer_time': total_time,
            'bandwidth_usage': bandwidth,
            'compression_ratio': packet['original_size'] / packet['compressed_size'] if packet['compressed_size'] > 0 else 1.0
        }


class AIEnhancement:
    """
    Implements AI enhancement using the Fibonacci Grid System.
    
    This class demonstrates how the grid system can be used for
    enhancing AI models with grid-based pattern recognition.
    """
    
    def __init__(self, grid_size: int = 100):
        """
        Initialize the AI enhancement system.
        
        Args:
            grid_size: Size of the underlying Fibonacci grid
        """
        self.grid = FibonacciGrid(grid_size)
        self.observers = {}
        self.models = {}
        self.pattern_recognition = PatternRecognition(grid_size)
    
    def create_model(self, name: str, input_size: int, output_size: int) -> Dict[str, Any]:
        """
        Create a grid-based neural network model.
        
        Args:
            name: Model name
            input_size: Input dimension
            output_size: Output dimension
            
        Returns:
            Dictionary containing model information
        """
        # Generate model ID
        model_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create model
        model = {
            'id': model_id,
            'name': name,
            'input_size': input_size,
            'output_size': output_size,
            'observers': [],
            'weights': self._initialize_weights(input_size, output_size),
            'created_at': time.time()
        }
        
        self.models[model_id] = model
        
        return {
            'model_id': model_id,
            'name': name,
            'input_size': input_size,
            'output_size': output_size
        }
    
    def add_observer(self, model_id: str, name: str, transformation_matrix: Optional[List[List[int]]] = None) -> Dict[str, Any]:
        """
        Add an observer to a model.
        
        Args:
            model_id: Model identifier
            name: Observer name
            transformation_matrix: Optional transformation matrix
            
        Returns:
            Dictionary containing observer information
        """
        if model_id not in self.models:
            return {'error': 'Model not found'}
        
        # Create observer
        observer_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:8]
        observer = Observer(name)
        
        if transformation_matrix:
            observer.set_transformation_matrix(transformation_matrix)
        
        self.observers[observer_id] = observer
        
        # Add to model
        self.models[model_id]['observers'].append(observer_id)
        
        return {
            'observer_id': observer_id,
            'model_id': model_id,
            'name': name
        }
    
    def train(self, model_id: str, inputs: List[List[float]], targets: List[List[float]], epochs: int = 10) -> Dict[str, Any]:
        """
        Train a model using grid-based learning.
        
        Args:
            model_id: Model identifier
            inputs: List of input vectors
            targets: List of target vectors
            epochs: Number of training epochs
            
        Returns:
            Dictionary containing training information
        """
        if model_id not in self.models:
            return {'error': 'Model not found'}
        
        model = self.models[model_id]
        
        if not model['observers']:
            return {'error': 'Model has no observers'}
        
        # Map inputs to grid
        input_patterns = []
        for input_vector in inputs:
            pattern = self.pattern_recognition.map_data_to_grid(input_vector)
            input_patterns.append(pattern)
        
        # Train for each epoch
        history = []
        for epoch in range(epochs):
            epoch_loss = 0
            
            for i, (input_vector, target_vector) in enumerate(zip(inputs, targets)):
                # Get input pattern
                pattern = input_patterns[i]
                
                # Forward pass through all observers
                outputs = []
                for observer_id in model['observers']:
                    observer = self.observers[observer_id]
                    
                    # Apply observer transformation to pattern
                    observed_values = []
                    for val in pattern['grid_values']:
                        observed_values.append(observer._apply_transformation(val))
                    
                    # Apply weights
                    output = self._forward_pass(observed_values, model['weights'])
                    outputs.append(output)
                
                # Combine outputs from all observers
                combined_output = [sum(out[j] for out in outputs) / len(outputs) for j in range(model['output_size'])]
                
                # Calculate loss
                loss = sum((t - o) ** 2 for t, o in zip(target_vector, combined_output)) / len(target_vector)
                epoch_loss += loss
                
                # Update weights (simplified)
                model['weights'] = self._update_weights(model['weights'], loss)
            
            # Record epoch results
            history.append({
                'epoch': epoch + 1,
                'loss': epoch_loss / len(inputs)
            })
        
        return {
            'model_id': model_id,
            'epochs': epochs,
            'final_loss': history[-1]['loss'],
            'history': history
        }
    
    def predict(self, model_id: str, input_vector: List[float]) -> Dict[str, Any]:
        """
        Make a prediction using a trained model.
        
        Args:
            model_id: Model identifier
            input_vector: Input data vector
            
        Returns:
            Dictionary containing prediction information
        """
        if model_id not in self.models:
            return {'error': 'Model not found'}
        
        model = self.models[model_id]
        
        if not model['observers']:
            return {'error': 'Model has no observers'}
        
        # Map input to grid
        pattern = self.pattern_recognition.map_data_to_grid(input_vector)
        
        # Forward pass through all observers
        outputs = []
        observer_outputs = {}
        
        for observer_id in model['observers']:
            observer = self.observers[observer_id]
            
            # Apply observer transformation to pattern
            observed_values = []
            for val in pattern['grid_values']:
                observed_values.append(observer._apply_transformation(val))
            
            # Apply weights
            output = self._forward_pass(observed_values, model['weights'])
            outputs.append(output)
            observer_outputs[observer_id] = output
        
        # Combine outputs from all observers
        combined_output = [sum(out[j] for out in outputs) / len(outputs) for j in range(model['output_size'])]
        
        return {
            'model_id': model_id,
            'input': input_vector,
            'output': combined_output,
            'observer_outputs': observer_outputs
        }
    
    def _initialize_weights(self, input_size: int, output_size: int) -> List[List[float]]:
        """
        Initialize weights for a grid-based neural network.
        
        Args:
            input_size: Input dimension
            output_size: Output dimension
            
        Returns:
            2D list of weights
        """
        weights = []
        for _ in range(input_size):
            row = [np.random.uniform(-0.1, 0.1) for _ in range(output_size)]
            weights.append(row)
        return weights
    
    def _forward_pass(self, input_values: List[int], weights: List[List[float]]) -> List[float]:
        """
        Perform a forward pass through the network.
        
        Args:
            input_values: Input values
            weights: Network weights
            
        Returns:
            Output values
        """
        output = [0] * len(weights[0])
        
        for i, input_val in enumerate(input_values):
            if i < len(weights):
                for j in range(len(output)):
                    output[j] += input_val * weights[i][j]
        
        # Apply activation function (sigmoid)
        output = [1 / (1 + math.exp(-x)) for x in output]
        
        return output
    
    def _update_weights(self, weights: List[List[float]], loss: float) -> List[List[float]]:
        """
        Update weights based on loss (simplified).
        
        Args:
            weights: Current weights
            loss: Loss value
            
        Returns:
            Updated weights
        """
        learning_rate = 0.01
        
        # Simple update rule (not a real backpropagation)
        updated_weights = []
        for row in weights:
            updated_row = [w - learning_rate * loss * w for w in row]
            updated_weights.append(updated_row)
        
        return updated_weights
