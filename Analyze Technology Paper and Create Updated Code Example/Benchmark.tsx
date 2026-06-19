import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BenchmarkProps {
  apiUrl: string;
}

const Benchmark: React.FC<BenchmarkProps> = ({ apiUrl }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hashingResults, setHashingResults] = useState<any | null>(null);
  const [compressionResults, setCompressionResults] = useState<any | null>(null);
  const [memoryResults, setMemoryResults] = useState<any | null>(null);
  const [networkResults, setNetworkResults] = useState<any | null>(null);
  
  const [hashingInput, setHashingInput] = useState('This is a test string for hashing benchmark');
  const [hashingIterations, setHashingIterations] = useState(1000);
  
  const [compressionInput, setCompressionInput] = useState('This is a test string for compression benchmark. It will be repeated multiple times to create a larger input for more meaningful compression results.');
  const [compressionIterations, setCompressionIterations] = useState(100);
  
  const [memoryOperations, setMemoryOperations] = useState(1000);
  const [memoryDataSize, setMemoryDataSize] = useState(1000);
  
  const [networkPacketSize, setNetworkPacketSize] = useState(1024);
  const [networkNumPackets, setNetworkNumPackets] = useState(100);

  const runHashingBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/benchmark/hashing`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          data: hashingInput,
          iterations: hashingIterations
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to run hashing benchmark: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setHashingResults(data.benchmark_results);
      } else {
        throw new Error('Failed to run hashing benchmark');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runCompressionBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/benchmark/compression`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          data: compressionInput.repeat(100), // Make it larger
          iterations: compressionIterations
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to run compression benchmark: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setCompressionResults(data.benchmark_results);
      } else {
        throw new Error('Failed to run compression benchmark');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runMemoryBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/benchmark/memory`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          operations: memoryOperations,
          data_size: memoryDataSize
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to run memory benchmark: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setMemoryResults(data.benchmark_results);
      } else {
        throw new Error('Failed to run memory benchmark');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runNetworkBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/benchmark/network`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          packet_size: networkPacketSize,
          num_packets: networkNumPackets
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to run network benchmark: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setNetworkResults(data.benchmark_results);
      } else {
        throw new Error('Failed to run network benchmark');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatHashingChartData = () => {
    if (!hashingResults) return [];
    
    return [
      {
        name: 'SHA256',
        ops: hashingResults.sha256.operations_per_second,
      },
      {
        name: 'MD5',
        ops: hashingResults.md5.operations_per_second,
      },
      {
        name: 'Fibonacci Grid',
        ops: hashingResults.fibonacci_grid.operations_per_second,
      },
    ];
  };

  const formatCompressionChartData = () => {
    if (!compressionResults) return [];
    
    return [
      {
        name: 'ZLIB',
        ratio: compressionResults.zlib.compression_ratio,
        speed: compressionResults.zlib.operations_per_second,
      },
      {
        name: 'Fibonacci Grid',
        ratio: compressionResults.fibonacci_grid.compression_ratio,
        speed: compressionResults.fibonacci_grid.operations_per_second,
      },
    ];
  };

  const formatMemoryChartData = () => {
    if (!memoryResults) return [];
    
    return [
      {
        name: 'Traditional',
        ops: memoryResults.traditional_memory.operations_per_second,
      },
      {
        name: 'Fibonacci Grid',
        ops: memoryResults.fibonacci_grid_memory.operations_per_second,
      },
    ];
  };

  const formatNetworkChartData = () => {
    if (!networkResults) return [];
    
    return [
      {
        name: 'Traditional',
        throughput: networkResults.traditional_network.throughput_bytes_per_second / 1024, // KB/s
        latency: networkResults.traditional_network.latency_per_packet_ms,
      },
      {
        name: 'Fibonacci Grid',
        throughput: networkResults.fibonacci_grid_network.throughput_bytes_per_second / 1024, // KB/s
        latency: networkResults.fibonacci_grid_network.latency_per_packet_ms,
      },
    ];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Performance Benchmarks</CardTitle>
        <CardDescription>
          Compare the Fibonacci Grid System against standard approaches
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="hashing">
          <TabsList className="mb-4">
            <TabsTrigger value="hashing">Hashing</TabsTrigger>
            <TabsTrigger value="compression">Compression</TabsTrigger>
            <TabsTrigger value="memory">Memory</TabsTrigger>
            <TabsTrigger value="network">Network</TabsTrigger>
          </TabsList>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <TabsContent value="hashing" className="space-y-4">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hashingInput">Input Text</Label>
                  <Input
                    id="hashingInput"
                    value={hashingInput}
                    onChange={(e) => setHashingInput(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="hashingIterations">Iterations</Label>
                  <Input
                    id="hashingIterations"
                    type="number"
                    value={hashingIterations}
                    onChange={(e) => setHashingIterations(parseInt(e.target.value) || 100)}
                    min={100}
                    max={10000}
                  />
                </div>
              </div>
              
              <Button 
                onClick={runHashingBenchmark} 
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Benchmark...
                  </>
                ) : (
                  'Run Hashing Benchmark'
                )}
              </Button>
              
              {hashingResults && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Benchmark Results</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={formatHashingChartData()}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis label={{ value: 'Operations/second', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="ops" name="Operations per Second" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-gray-100 rounded">
                      <h4 className="font-medium">SHA256</h4>
                      <p className="text-lg font-mono">{hashingResults.sha256.operations_per_second.toFixed(2)} ops/s</p>
                      <p className="text-sm text-gray-500">{hashingResults.sha256.time.toFixed(4)}s total</p>
                    </div>
                    
                    <div className="p-4 bg-gray-100 rounded">
                      <h4 className="font-medium">MD5</h4>
                      <p className="text-lg font-mono">{hashingResults.md5.operations_per_second.toFixed(2)} ops/s</p>
                      <p className="text-sm text-gray-500">{hashingResults.md5.time.toFixed(4)}s total</p>
                    </div>
                    
                    <div className="p-4 bg-gray-100 rounded">
                      <h4 className="font-medium">Fibonacci Grid</h4>
                      <p className="text-lg font-mono">{hashingResults.fibonacci_grid.operations_per_second.toFixed(2)} ops/s</p>
                      <p className="text-sm text-gray-500">{hashingResults.fibonacci_grid.time.toFixed(4)}s total</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="compression" className="space-y-4">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="compressionInput">Input Text (will be repeated)</Label>
                  <Input
                    id="compressionInput"
                    value={compressionInput}
                    onChange={(e) => setCompressionInput(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="compressionIterations">Iterations</Label>
                  <Input
                    id="compressionIterations"
                    type="number"
                    value={compressionIterations}
                    onChange={(e) => setCompressionIterations(parseInt(e.target.value) || 10)}
                    min={10}
                    max={1000}
                  />
                </div>
              </div>
              
              <Button 
                onClick={runCompressionBenchmark} 
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Benchmark...
                  </>
                ) : (
                  'Run Compression Benchmark'
                )}
              </Button>
              
              {compressionResults && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Benchmark Results</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={formatCompressionChartData()}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis yAxisId="left" orientation="left" label={{ value: 'Compression Ratio', angle: -90, position: 'insideLeft' }} />
                        <YAxis yAxisId="right" orientation="right" label={{ value: 'Operations/second', angle: 90, position: 'insideRight' }} />
                        <Tooltip />
                        <Legend />
                        <Bar yAxisId="left" dataKey="ratio" name="Compression Ratio" fill="#8884d8" />
                        <Bar yAxisId="right" dataKey="speed" name="Operations per Second" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                    <div className="p-4 bg-gray-100 rounded">
                      <h4 className="font-medium">ZLIB</h4>
                      <p className="text-lg font-mono">{compressionResults.zlib.compression_ratio.toFixed(2)}x ratio</p>
                      <p className="text-sm text-gray-500">{compressionResults.zlib.operations_per_second.toFixed(2)} ops/s</p>
                    </div>
                    
                    <div className="p-4 bg-gray-100 rounded">
                      <h4 className="font-medium">Fibonacci Grid</h4>
                      <p className="text-lg font-mono">{compressionResults.fibonacci_grid.compression_ratio.toFixed(2)}x ratio</p>
                      <p className="text-sm text-gray-500">{compressionResults.fibonacci_grid.operations_per_second.toFixed(2)} ops/s</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="memory" className="space-y-4">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="memoryOperations">Number of Operations</Label>
                  <Input
                    id="memoryOperations"
                    type="numbe
(Content truncated due to size limit. Use line ranges to read in chunks)