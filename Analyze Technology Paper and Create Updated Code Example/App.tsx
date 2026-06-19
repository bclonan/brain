import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import GridVisualizer from './components/GridVisualizer';
import FrequencyProcessor from './components/FrequencyProcessor';
import Benchmark from './components/Benchmark';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

function App() {
  const [apiUrl, setApiUrl] = useState('http://localhost:5000');
  const [activeTab, setActiveTab] = useState('grid');

  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Fibonacci Grid System</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          An interactive demonstration of grid algorithms, compression, frequency-based data representation, 
          and the Fibonacci modulo 10 base grid with special mathematical rules
        </p>
      </header>

      <main className="max-w-6xl mx-auto">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex justify-center mb-6">
            <TabsList className="grid grid-cols-4 w-full max-w-xl">
              <TabsTrigger value="grid">Grid System</TabsTrigger>
              <TabsTrigger value="frequency">Frequency</TabsTrigger>
              <TabsTrigger value="benchmark">Benchmarks</TabsTrigger>
              <TabsTrigger value="about">About</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="grid" className="mt-6">
            <GridVisualizer apiUrl={apiUrl} />
          </TabsContent>

          <TabsContent value="frequency" className="mt-6">
            <FrequencyProcessor apiUrl={apiUrl} />
          </TabsContent>

          <TabsContent value="benchmark" className="mt-6">
            <Benchmark apiUrl={apiUrl} />
          </TabsContent>

          <TabsContent value="about" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>About the Fibonacci Grid System</CardTitle>
                <CardDescription>
                  Understanding the core concepts and applications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">Core Concepts</h3>
                  <p>
                    The Fibonacci Grid System is based on the Fibonacci sequence with modulo 10 operations,
                    arranged in a grid format. This creates a unique pattern that can be used for data
                    representation, compression, and various computational tasks.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">Key Features</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Grid-based data representation using Fibonacci patterns</li>
                    <li>Frequency manipulation and beat pattern generation</li>
                    <li>Quantum entanglement simulation through paired frequencies</li>
                    <li>Efficient data compression through grid mapping</li>
                    <li>Alternative approach to computer memory systems</li>
                    <li>Network data transfer optimization</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">Applications</h3>
                  <p>
                    This system can be applied to various domains including data compression,
                    secure data transmission, memory system design, and AI enhancement. The
                    benchmarks section demonstrates how it compares to traditional approaches
                    in these areas.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">How to Use This Demo</h3>
                  <p>
                    Explore the different tabs to interact with various aspects of the system:
                  </p>
                  <ul className="list-disc pl-5 space-y-1 mt-2">
                    <li><strong>Grid System:</strong> Visualize and manipulate the Fibonacci grid</li>
                    <li><strong>Frequency:</strong> Experiment with frequency processing and beat patterns</li>
                    <li><strong>Benchmarks:</strong> Compare performance against traditional approaches</li>
                  </ul>
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={() => setActiveTab('grid')} className="w-full">
                  Start Exploring
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      <footer className="mt-12 text-center text-sm text-gray-500">
        <p>Fibonacci Grid System Demo - Created with React and Flask</p>
        <p className="mt-1">API URL: {apiUrl}</p>
      </footer>
    </div>
  );
}

export default App;
