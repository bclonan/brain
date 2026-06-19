import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Loader2 } from 'lucide-react';

interface FrequencyProcessorProps {
  apiUrl: string;
}

const FrequencyProcessor: React.FC<FrequencyProcessorProps> = ({ apiUrl }) => {
  const [freq1, setFreq1] = useState(400);
  const [freq2, setFreq2] = useState(405);
  const [beatFrequency, setBeatFrequency] = useState<number | null>(null);
  const [beatImage, setBeatImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [entangledFrequency, setEntangledFrequency] = useState<number | null>(null);
  const [baseFrequency, setBaseFrequency] = useState(100);
  const [entanglementFactor, setEntanglementFactor] = useState(10);
  const [frequencies, setFrequencies] = useState<number[]>([100, 150, 200]);
  const [transmittedFrequencies, setTransmittedFrequencies] = useState<number[]>([]);

  const generateBeatFrequency = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/frequency/beat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ freq1, freq2 })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to generate beat frequency: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setBeatFrequency(data.beat_frequency);
        setBeatImage(`data:image/png;base64,${data.image}`);
      } else {
        throw new Error('Failed to generate beat frequency');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const createEntangledFrequency = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/frequency/entangle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          frequency: baseFrequency,
          entanglement_factor: entanglementFactor
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create entangled frequency: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setEntangledFrequency(data.entangled_frequency);
        fetchTimeline(); // Update the timeline
      } else {
        throw new Error('Failed to create entangled frequency');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchTimeline = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/frequency/timeline`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch timeline: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setTimeline(data.timeline);
      } else {
        throw new Error('Failed to fetch timeline');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  const transmitFrequencies = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/frequency/transmit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ frequencies })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to transmit frequencies: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        setTransmittedFrequencies(data.transmitted_frequencies);
      } else {
        throw new Error('Failed to transmit frequencies');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const updateFrequencies = (index: number, value: number) => {
    const newFrequencies = [...frequencies];
    newFrequencies[index] = value;
    setFrequencies(newFrequencies);
  };

  const addFrequency = () => {
    setFrequencies([...frequencies, 100]);
  };

  const removeFrequency = (index: number) => {
    const newFrequencies = [...frequencies];
    newFrequencies.splice(index, 1);
    setFrequencies(newFrequencies);
  };

  useEffect(() => {
    generateBeatFrequency();
    fetchTimeline();
  }, []);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Frequency Processor</CardTitle>
        <CardDescription>
          Explore frequency manipulation, beat patterns, and quantum entanglement simulation
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="beat">
          <TabsList className="mb-4">
            <TabsTrigger value="beat">Beat Frequency</TabsTrigger>
            <TabsTrigger value="entangle">Quantum Entanglement</TabsTrigger>
            <TabsTrigger value="transmit">Frequency Transmission</TabsTrigger>
          </TabsList>
          
          <TabsContent value="beat" className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="freq1">Frequency 1 (Hz)</Label>
                <Input
                  id="freq1"
                  type="number"
                  value={freq1}
                  onChange={(e) => setFreq1(parseInt(e.target.value) || 0)}
                  min={1}
                  max={2000}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="freq2">Frequency 2 (Hz)</Label>
                <Input
                  id="freq2"
                  type="number"
                  value={freq2}
                  onChange={(e) => setFreq2(parseInt(e.target.value) || 0)}
                  min={1}
                  max={2000}
                />
              </div>
            </div>
            
            <Button 
              onClick={generateBeatFrequency} 
              disabled={loading}
              className="w-full mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Beat Frequency'
              )}
            </Button>
            
            {beatFrequency !== null && (
              <div className="mt-4 p-4 bg-gray-100 rounded">
                <h3 className="font-medium mb-2">Beat Frequency Result</h3>
                <p className="text-lg font-mono">
                  {freq1} Hz + {freq2} Hz = <span className="font-bold">{beatFrequency} Hz</span> beat
                </p>
              </div>
            )}
            
            {beatImage && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Beat Pattern Visualization</h3>
                <img 
                  src={beatImage} 
                  alt="Beat Pattern Visualization" 
                  className="max-w-full h-auto border rounded"
                />
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="entangle" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="baseFrequency">Base Frequency (Hz)</Label>
                <Input
                  id="baseFrequency"
                  type="number"
                  value={baseFrequency}
                  onChange={(e) => setBaseFrequency(parseInt(e.target.value) || 0)}
                  min={1}
                  max={1000}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="entanglementFactor">Entanglement Factor (Hz)</Label>
                <Input
                  id="entanglementFactor"
                  type="number"
                  value={entanglementFactor}
                  onChange={(e) => setEntanglementFactor(parseInt(e.target.value) || 0)}
                  min={1}
                  max={100}
                />
              </div>
            </div>
            
            <Button 
              onClick={createEntangledFrequency} 
              disabled={loading}
              className="w-full mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Entangled Frequency'
              )}
            </Button>
            
            {entangledFrequency !== null && (
              <div className="mt-4 p-4 bg-gray-100 rounded">
                <h3 className="font-medium mb-2">Entangled Frequency Result</h3>
                <p className="text-lg font-mono">
                  Base: {baseFrequency} Hz → Entangled: <span className="font-bold">{entangledFrequency} Hz</span>
                </p>
              </div>
            )}
            
            {timeline.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Frequency Timeline</h3>
                <div className="max-h-60 overflow-y-auto border rounded">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Original (Hz)</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entangled (Hz)</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {timeline.map((event, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                            {event.original_frequency}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                            {event.entangled_frequency}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="transmit" className="space-y-4">
            <div className="space-y-4">
              <h3 className="font-medium">Frequency Sequence</h3>
              {frequencies.map((freq, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    type="number"
                    value={freq}
                    onChange={(e) => updateFrequencies(index, parseInt(e.target.value) || 0)}
                    min={1}
                    max={2000}
                    className="flex-1"
                  />
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => removeFrequency(index)}
                    disabled={frequencies.length <= 1}
                  >
                    Remove
                  </Button>
                </div>
              ))}
              
              <Button 
                variant="outline" 
                onClick={addFrequency}
                className="w-full"
              >
                Add Frequency
              </Button>
              
              <Button 
                onClick={transmitFrequencies} 
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Transmitting...
                  </>
                ) : (
                  'Transmit Frequencies'
                )}
              </Button>
              
              {transmittedFrequencies.length > 0 && (
                <div className="mt-4 p-4 bg-gray-100 rounded">
                  <h3 className="font-medium mb-2">Transmission Result</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium mb-1">Original Frequencies</h4>
                      <div className="font-mono space-y-1">
                        {frequencies.map((freq, index) => (
                          <div key={index}>{freq} Hz</div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-1">Transmitted Frequencies</h4>
                      <div className="font-mono space-y-1">
                        {transmittedFrequencies.map((freq, index) => (
                          <div key={index}>{freq} Hz</div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-xs text-gray-500">
          Frequency manipulation demonstrates the principles of quantum-inspired data representation
        </div>
      </CardFooter>
    </Card>
  );
};

export default FrequencyProcessor;
