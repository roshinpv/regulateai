import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';

interface AgencyStatus {
  name: string;
  lastUpdate: string;
  status: 'active' | 'error' | 'pending';
  updateCount: number;
}

const MonitoringStatus: React.FC = () => {
  const [agencies, setAgencies] = useState<AgencyStatus[]>([
    {
      name: "OCC",
      lastUpdate: new Date().toISOString(),
      status: 'active',
      updateCount: 12
    },
    {
      name: "CFPB", 
      lastUpdate: new Date().toISOString(),
      status: 'active',
      updateCount: 8
    },
    {
      name: "FDIC",
      lastUpdate: new Date().toISOString(),
      status: 'active', 
      updateCount: 5
    },
    {
      name: "FinCEN",
      lastUpdate: new Date().toISOString(),
      status: 'active',
      updateCount: 3
    },
    {
      name: "Federal Reserve",
      lastUpdate: new Date().toISOString(),
      status: 'active',
      updateCount: 7
    },
    {
      name: "SEC",
      lastUpdate: new Date().toISOString(),
      status: 'active',
      updateCount: 4
    }
  ]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'error':
        return <AlertTriangle size={16} className="text-red-500" />;
      case 'pending':
        return <Clock size={16} className="text-yellow-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-neutral-lighter mr-4">
            <Activity size={20} className="text-neutral" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Regulatory Monitoring Status</h2>
            <p className="text-sm text-neutral-light">Real-time agency monitoring status</p>
          </div>
        </div>
        <button className="btn btn-outline flex items-center">
          <RefreshCw size={16} className="mr-2" />
          Refresh
        </button>
      </div>

      <div className="space-y-4">
        {agencies.map((agency) => (
          <div key={agency.name} className="flex items-center justify-between p-4 bg-neutral-lighter rounded-lg">
            <div className="flex items-center">
              {getStatusIcon(agency.status)}
              <span className="ml-2 font-medium">{agency.name}</span>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-sm">
                <span className="text-neutral-light">Updates: </span>
                <span className="font-medium">{agency.updateCount}</span>
              </div>
              <div className="text-sm">
                <span className="text-neutral-light">Last Update: </span>
                <span className="font-medium">
                  {new Date(agency.lastUpdate).toLocaleTimeString()}
                </span>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                agency.status === 'active' ? 'bg-green-100 text-green-800' :
                agency.status === 'error' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {agency.status.toUpperCase()}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-neutral-lighter">
        <div className="flex justify-between text-sm text-neutral-light">
          <span>Next update in: 45 minutes</span>
          <span>Last system check: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};

export default MonitoringStatus;