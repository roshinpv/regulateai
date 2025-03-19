import React, { useState, useEffect } from 'react';
import { Calendar, Users, CheckSquare, Shield, Layers } from 'lucide-react';
import { regulationsAPI } from '../../api';
import { Regulation } from '../../types';

interface RegulationDetailProps {
  regulationId: string;
  onClose: () => void;
}

const RegulationDetail: React.FC<RegulationDetailProps> = ({ regulationId, onClose }) => {
  const [regulation, setRegulation] = useState<Regulation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'units'>('overview');

  useEffect(() => {
    const fetchRegulation = async () => {
      try {
        const data = await regulationsAPI.getById(regulationId);
        setRegulation(data);
      } catch (err) {
        console.error('Error fetching regulation:', err);
        setError('Failed to load regulation details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRegulation();
  }, [regulationId]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Application':
        return <div className="p-2 rounded-full bg-blue-100 text-blue-600"><Layers size={16} /></div>;
      case 'Infrastructure':
        return <div className="p-2 rounded-full bg-green-100 text-green-600"><Shield size={16} /></div>;
      case 'Security':
        return <div className="p-2 rounded-full bg-red-100 text-red-600"><Shield size={16} /></div>;
      case 'Governance':
        return <div className="p-2 rounded-full bg-purple-100 text-purple-600"><Users size={16} /></div>;
      case 'Operations':
        return <div className="p-2 rounded-full bg-orange-100 text-orange-600"><CheckSquare size={16} /></div>;
      default:
        return <div className="p-2 rounded-full bg-neutral-lighter"><Layers size={16} /></div>;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Application':
        return 'bg-blue-100 text-blue-600';
      case 'Infrastructure':
        return 'bg-green-100 text-green-600';
      case 'Security':
        return 'bg-red-100 text-red-600';
      case 'Governance':
        return 'bg-purple-100 text-purple-600';
      case 'Operations':
        return 'bg-orange-100 text-orange-600';
      default:
        return 'bg-neutral-lighter text-neutral';
    }
  };

  const getUnitDistribution = (units: any[] = []) => {
    // Create distribution object with category counts
    const distribution = units.reduce((acc: Record<string, number>, unit) => {
      const category = unit.category;
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {});

    return distribution;
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Loading...</h2>
          <button 
            className="text-neutral-light hover:text-neutral"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        <div className="py-8 text-center text-neutral-light">Loading regulation details...</div>
      </div>
    );
  }

  if (error || !regulation) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Error</h2>
          <button 
            className="text-neutral-light hover:text-neutral"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        <div className="py-8 text-center text-red-500">{error || 'Failed to load regulation'}</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">{regulation.title}</h2>
        <button 
          className="text-neutral-light hover:text-neutral"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="flex border-b border-neutral-lighter mb-6">
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'overview' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'units' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('units')}
        >
          Risk Assessment Units
        </button>
      </div>
      
      {activeTab === 'overview' ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-neutral-lighter mr-3">
                <Calendar size={16} className="text-neutral" />
              </div>
              <div>
                <p className="text-xs text-neutral-light">Last Updated</p>
                <p className="font-medium">{new Date(regulation.last_updated).toLocaleDateString()}</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-neutral-lighter mr-3">
                <Users size={16} className="text-neutral" />
              </div>
              <div>
                <p className="text-xs text-neutral-light">Issuing Agency</p>
                <p className="font-medium">{regulation.agency?.name || 'Unknown'}</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className={`p-2 rounded-full mr-3 ${
                regulation.impact_level === 'High' ? 'bg-primary/10' : 
                regulation.impact_level === 'Medium' ? 'bg-secondary/20' : 'bg-neutral-lighter'
              }`}>
                <CheckSquare size={16} className={
                  regulation.impact_level === 'High' ? 'text-primary' : 
                  regulation.impact_level === 'Medium' ? 'text-secondary-dark' : 'text-neutral-light'
                } />
              </div>
              <div>
                <p className="text-xs text-neutral-light">Impact Level</p>
                <p className="font-medium">{regulation.impact_level}</p>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">Summary</h3>
            <p className="text-neutral-light">{regulation.summary}</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-3">Affected Banks</h3>
              {regulation.affected_banks && regulation.affected_banks.length > 0 ? (
                <ul className="space-y-2">
                  {regulation.affected_banks.map((bank) => (
                    <li key={bank.id} className="flex items-center">
                      <span className="w-2 h-2 rounded-full bg-primary mr-2"></span>
                      <span>{bank.name}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-neutral-light">No affected banks specified</p>
              )}
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-3">Compliance Steps</h3>
              {regulation.compliance_steps && regulation.compliance_steps.length > 0 ? (
                <ul className="space-y-2">
                  {regulation.compliance_steps
                    .sort((a, b) => a.order - b.order)
                    .map((step, index) => (
                      <li key={step.id} className="flex items-start">
                        <span className="flex-shrink-0 w-5 h-5 rounded-full bg-neutral-lighter text-neutral flex items-center justify-center mr-2 mt-0.5">
                          {index + 1}
                        </span>
                        <span>{step.description}</span>
                      </li>
                    ))}
                </ul>
              ) : (
                <p className="text-neutral-light">No compliance steps specified</p>
              )}
            </div>
          </div>
        </>
      ) : (
        <div>
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Responsible Units</h3>
            <p className="text-neutral-light mb-4">
              The following units are responsible for implementing and maintaining compliance with this regulation:
            </p>
            
            {regulation.responsible_units && regulation.responsible_units.length > 0 ? (
              <div className="space-y-4">
                {regulation.responsible_units.map((unit) => (
                  <div key={unit.id} className="border border-neutral-lighter rounded-lg p-4">
                    <div className="flex items-start">
                      {getCategoryIcon(unit.category)}
                      <div className="ml-3 flex-1">
                        <h4 className="font-medium">{unit.name}</h4>
                        <p className="text-sm text-neutral-light mt-1">{unit.description}</p>
                        <div className="flex items-center mt-2">
                          <span className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(unit.category)}`}>
                            {unit.category}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-neutral-light">No responsible units specified</p>
            )}
          </div>
          
          <div className="border-t border-neutral-lighter pt-6">
            <h3 className="text-lg font-medium mb-3">Unit Distribution</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(getUnitDistribution(regulation.responsible_units)).map(([category, count]) => (
                <div key={category} className={`rounded-lg p-4 text-center ${getCategoryColor(category)}`}>
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm">{category}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-end">
        <button className="btn btn-outline mr-2">Export PDF</button>
        <button className="btn btn-primary">Generate Compliance Report</button>
      </div>
    </div>
  );
};

export default RegulationDetail;