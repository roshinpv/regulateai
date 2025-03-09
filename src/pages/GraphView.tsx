import React, { useState, useEffect } from 'react';
import GraphVisualization from '../components/Graph/GraphVisualization';
import { Network, Filter, ZoomIn, ZoomOut, RefreshCw, Database } from 'lucide-react';
import { graphAPI } from '../api';
import { GraphData } from '../types';

const GraphView: React.FC = () => {
  const [filterOpen, setFilterOpen] = useState(false);
  const [nodeTypes, setNodeTypes] = useState({
    regulation: true,
    agency: true,
    bank: true
  });
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGraphData();
  }, [nodeTypes]);

  const fetchGraphData = async () => {
    setIsLoading(true);
    try {
      const data = await graphAPI.getGraphData({
        include_regulations: nodeTypes.regulation,
        include_agencies: nodeTypes.agency,
        include_banks: nodeTypes.bank
      });
      setGraphData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching graph data:', err);
      setError('Failed to load graph data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = async (nodeId: string, nodeType: string) => {
    try {
      const expandedData = await graphAPI.expandNode(nodeId, nodeType);

      // Merge the expanded data with the existing graph data
      const existingNodeIds = new Set(graphData.nodes.map(node => node.id));
      const existingLinkIds = new Set(graphData.links.map(link => `${link.source}-${link.target}`));

      const newNodes = expandedData.nodes.filter(node => !existingNodeIds.has(node.id));
      const newLinks = expandedData.links.filter(
        link => !existingLinkIds.has(`${link.source}-${link.target}`)
      );

      setGraphData({
        nodes: [...graphData.nodes, ...newNodes],
        links: [...graphData.links, ...newLinks]
      });
    } catch (err) {
      console.error('Error expanding node:', err);
    }
  };

  const handleNodeTypeToggle = (type: 'regulation' | 'agency' | 'bank') => {
    setNodeTypes(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const handleReset = () => {
    fetchGraphData();
  };

  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center py-16">
      <Database size={48} className="text-neutral-light mb-4" />
      <h3 className="text-lg font-medium text-neutral mb-2">No Data Available</h3>
      <p className="text-neutral-light text-center max-w-md mb-4">
        There are no regulations, agencies, or banks in the database to visualize. Add some data to see the knowledge graph.
      </p>
      <button
        className="btn btn-primary"
        onClick={() => window.location.href = '/settings'}
      >
        Add Data
      </button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold">Knowledge Graph</h1>
          <p className="text-neutral-light">Visualize relationships between regulations, agencies, and banks</p>
        </div>
        <div className="flex space-x-2">
          <button
            className="btn btn-outline flex items-center"
            onClick={() => setFilterOpen(!filterOpen)}
          >
            <Filter size={16} className="mr-2" />
            <span>Filter</span>
          </button>
          <button className="btn btn-outline p-2">
            <ZoomIn size={20} />
          </button>
          <button className="btn btn-outline p-2">
            <ZoomOut size={20} />
          </button>
          <button
            className="btn btn-outline p-2"
            onClick={handleReset}
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {filterOpen && (
        <div className="card mb-4">
          <h3 className="font-medium mb-3">Filter Graph</h3>
          <div className="flex space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={nodeTypes.regulation}
                onChange={() => handleNodeTypeToggle('regulation')}
              />
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-green-500 mr-1"></span>
                Regulations
              </span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={nodeTypes.agency}
                onChange={() => handleNodeTypeToggle('agency')}
              />
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-orange-500 mr-1"></span>
                Agencies
              </span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={nodeTypes.bank}
                onChange={() => handleNodeTypeToggle('bank')}
              />
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-blue-500 mr-1"></span>
                Banks
              </span>
            </label>
          </div>
        </div>
      )}

      <div className="card">
        <div className="flex items-center mb-4">
          <div className="p-3 rounded-full bg-neutral-lighter mr-4">
            <Network size={20} className="text-neutral" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Regulatory Knowledge Graph</h2>
            <p className="text-sm text-neutral-light">
              {isLoading
                ? 'Loading graph data...'
                : graphData.nodes.length > 0
                ? `Showing ${graphData.nodes.length} nodes and ${graphData.links.length} connections`
                : 'No data available'}
            </p>
          </div>
        </div>

        {error ? (
          <div className="border border-neutral-lighter rounded-lg p-8 text-center text-red-500">
            {error}
          </div>
        ) : (
          <div className="border border-neutral-lighter rounded-lg overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center" style={{ height: '500px' }}>
                <div className="text-neutral-light">Loading graph data...</div>
              </div>
            ) : graphData.nodes.length === 0 ? (
              renderEmptyState()
            ) : (
              <GraphVisualization
                data={graphData}
                height={700}
                onNodeClick={handleNodeClick}
              />
            )}
          </div>
        )}

        {graphData.nodes.length > 0 && (
          <div className="mt-4 text-sm text-neutral-light">
            <p>Tip: Click on a node to expand its connections. Click and drag nodes to rearrange the graph.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphView;