import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Loader2 } from 'lucide-react';

interface GridVisualizerProps {
  apiUrl: string;
}

const GridVisualizer: React.FC<GridVisualizerProps> = ({ apiUrl }) => {
  const [gridImage, setGridImage] = useState<string | null>(null);
  const [gridData, setGridData] = useState<number[][]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startRow, setStartRow] = useState(0);
  const [startCol, setStartCol] = useState(0);
  const [rows, setRows] = useState(10);
  const [cols, setCols] = useState(10);
  const [compressionStats, setCompressionStats] = useState<{
    ratio: number;
    originalSize: number;
    compressedSize: number;
    executionTime: number;
  } | null>(null);
  const [compressing, setCompressing] = useState(false);

  const fetchGridSection = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${apiUrl}/api/grid/section?start_row=${startRow}&start_col=${startCol}&rows=${rows}&cols=${cols}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch grid section: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setGridImage(`data:image/png;base64,${data.image}`);
        setGridData(data.grid_data);
      } else {
        throw new Error('Failed to fetch grid section');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const compressGrid = async () => {
    setCompressing(true);
    try {
      const response = await fetch(`${apiUrl}/api/grid/compress`);
      
      if (!response.ok) {
        throw new Error(`Failed to compress grid: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setCompressionStats({
          ratio: data.compression_ratio,
          originalSize: data.original_size,
          compressedSize: data.compressed_size,
          executionTime: data.execution_time
        });
      } else {
        throw new Error('Failed to compress grid');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setCompressing(false);
    }
  };

  const shuffleGrid = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/grid/shuffle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ seed: Math.floor(Math.random() * 1000) })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to shuffle grid: ${response.statusText}`);
      }
      
      await fetchGridSection(); // Refresh the grid view
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const generateNewGrid = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/grid/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rows: 100, cols: 100 })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to generate new grid: ${response.statusText}`);
      }
      
      await fetchGridSection(); // Refresh the grid view
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGridSection();
  }, []);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Fibonacci Grid Visualizer</CardTitle>
        <CardDescription>
          Explore the Fibonacci modulo 10 grid system with interactive controls
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="visualize">
          <TabsList className="mb-4">
            <TabsTrigger value="visualize">Visualize</TabsTrigger>
            <TabsTrigger value="compress">Compression</TabsTrigger>
            <TabsTrigger value="controls">Controls</TabsTrigger>
          </TabsList>
          
          <TabsContent value="visualize" className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2">Loading grid...</span>
              </div>
            ) : gridImage ? (
              <div className="flex flex-col items-center">
                <img 
                  src={gridImage} 
                  alt="Fibonacci Grid Visualization" 
                  className="max-w-full h-auto border rounded"
                />
                <div className="mt-4 text-sm text-gray-500">
                  Showing grid section [{startRow}:{startRow+rows}, {startCol}:{startCol+cols}]
                </div>
              </div>
            ) : (
              <div className="text-center py-8">No grid data available</div>
            )}
          </TabsContent>
          
          <TabsContent value="compress" className="space-y-4">
            <div className="flex flex-col space-y-4">
              <Button 
                onClick={compressGrid} 
                disabled={compressing}
                className="w-full"
              >
                {compressing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Compressing...
                  </>
                ) : (
                  'Compress Grid'
                )}
              </Button>
              
              {compressionStats && (
                <div className="bg-gray-100 p-4 rounded">
                  <h3 className="font-medium mb-2">Compression Results</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>Compression Ratio:</div>
                    <div className="font-mono">{compressionStats.ratio.toFixed(2)}x</div>
                    
                    <div>Original Size:</div>
                    <div className="font-mono">{compressionStats.originalSize} bytes</div>
                    
                    <div>Compressed Size:</div>
                    <div className="font-mono">{compressionStats.compressedSize} bytes</div>
                    
                    <div>Execution Time:</div>
                    <div className="font-mono">{compressionStats.executionTime.toFixed(4)} seconds</div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="controls" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startRow">Start Row</Label>
                <Input
                  id="startRow"
                  type="number"
                  value={startRow}
                  onChange={(e) => setStartRow(parseInt(e.target.value) || 0)}
                  min={0}
                  max={90}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="startCol">Start Column</Label>
                <Input
                  id="startCol"
                  type="number"
                  value={startCol}
                  onChange={(e) => setStartCol(parseInt(e.target.value) || 0)}
                  min={0}
                  max={90}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="rows">Number of Rows</Label>
                <Input
                  id="rows"
                  type="number"
                  value={rows}
                  onChange={(e) => setRows(parseInt(e.target.value) || 1)}
                  min={1}
                  max={20}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cols">Number of Columns</Label>
                <Input
                  id="cols"
                  type="number"
                  value={cols}
                  onChange={(e) => setCols(parseInt(e.target.value) || 1)}
                  min={1}
                  max={20}
                />
              </div>
            </div>
            
            <div className="flex space-x-2 pt-4">
              <Button onClick={fetchGridSection} className="flex-1">
                Update View
              </Button>
              <Button onClick={shuffleGrid} variant="outline" className="flex-1">
                Shuffle Grid
              </Button>
              <Button onClick={generateNewGrid} variant="secondary" className="flex-1">
                Generate New Grid
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-xs text-gray-500">
          The Fibonacci grid uses modulo 10 operations on the Fibonacci sequence
        </div>
      </CardFooter>
    </Card>
  );
};

export default GridVisualizer;
