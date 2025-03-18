import React from 'react';
import StatCards from '../components/Dashboard/StatCards';
import LatestUpdates from '../components/Dashboard/LatestUpdates';
import ComplianceAlertsList from '../components/Dashboard/ComplianceAlertsList';
import MonitoringStatus from '../components/Dashboard/MonitoringStatus';
import GraphVisualization from '../components/Graph/GraphVisualization';
import { useNavigate } from 'react-router-dom';
import { graphAPI } from '../api';

const Dashboard: React.FC = () => {
  const [graphData, setGraphData] = React.useState({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const navigate = useNavigate();

  React.useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const data = await graphAPI.getGraphData();
        setGraphData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching graph data:', err);
        setError('Failed to load graph data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchGraphData();
  }, []);

  const handleNodeClick = (nodeId: string, nodeType: string) => {
    navigate('/graph');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div>
          <button className="btn btn-primary">Generate Compliance Report</button>
        </div>
      </div>

      <StatCards />

      <MonitoringStatus />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LatestUpdates />
        <ComplianceAlertsList />
      </div>
      
      {error ? (
        <div className="card p-6 text-red-500 text-center">
          {error}
        </div>
      ) : (
        <GraphVisualization 
          data={graphData} 
          height={500}
          onNodeClick={handleNodeClick}
        />
      )}
    </div>
  );
};

export default Dashboard;