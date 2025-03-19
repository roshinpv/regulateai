import React, { useState, useEffect } from 'react';
import { BarChart3, ArrowRight, Shield, Layers, Users, CheckSquare } from 'lucide-react';
import { regulationsAPI } from '../../api';
import { Regulation } from '../../types';

const ImpactAnalysis: React.FC = () => {
  const [selectedRegulation, setSelectedRegulation] = useState('');
  const [regulation, setRegulation] = useState<Regulation | null>(null);
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingList, setIsLoadingList] = useState(true);
  
  const bank = {
    name: 'Wells Fargo',
    id: 'bank-001'
  };

  useEffect(() => {
    const fetchRegulations = async () => {
      try {
        const data = await regulationsAPI.getAll();
        setRegulations(data);
      } catch (error) {
        console.error('Error fetching regulations:', error);
      } finally {
        setIsLoadingList(false);
      }
    };

    fetchRegulations();
  }, []);

  const handleRegulationSelect = async (regId: string) => {
    setSelectedRegulation(regId);
    setIsLoading(true);
    try {
      const data = await regulationsAPI.getById(regId);
      setRegulation(data);
    } catch (error) {
      console.error('Error fetching regulation:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Affected Regulations</h2>
          
          {isLoadingList ? (
            <div className="py-8 text-center text-neutral-light">
              Loading regulations...
            </div>
          ) : regulations.length === 0 ? (
            <div className="py-8 text-center text-neutral-light">
              No regulations found
            </div>
          ) : (
            <div className="space-y-2">
              {regulations.map((reg) => (
                <button
                  key={reg.id}
                  className={`w-full text-left px-4 py-3 rounded-md flex items-center justify-between ${
                    selectedRegulation === reg.id 
                      ? 'bg-primary/10 text-primary border border-primary/30' 
                      : 'bg-neutral-lighter hover:bg-neutral-light hover:text-white'
                  }`}
                  onClick={() => handleRegulationSelect(reg.id)}
                >
                  <div>
                    <span className="font-medium">{reg.title}</span>
                    <p className="text-xs text-neutral-light mt-1">{reg.agency?.name}</p>
                  </div>
                  <span className={`badge ${
                    reg.impact_level === 'High' ? 'badge-high' : 
                    reg.impact_level === 'Medium' ? 'badge-medium' : 'badge-low'
                  }`}>
                    {reg.impact_level}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="lg:col-span-2">
        {isLoading ? (
          <div className="card flex items-center justify-center h-64">
            <div className="text-neutral-light">Loading regulation details...</div>
          </div>
        ) : regulation ? (
          <div className="card">
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-full bg-primary/10 mr-4">
                <BarChart3 size={20} className="text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">{regulation.title} Impact Analysis</h2>
                <p className="text-sm text-neutral-light">
                  How {regulation.title} affects {bank.name}
                </p>
              </div>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Summary</h3>
              <p className="text-neutral-light">{regulation.summary}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-neutral-lighter rounded-lg p-4">
                <h4 className="font-medium mb-2">Risk Level</h4>
                <div className={`text-lg font-bold ${
                  regulation.impact_level === 'High' ? 'text-primary' : 
                  regulation.impact_level === 'Medium' ? 'text-secondary-dark' : 'text-neutral'
                }`}>
                  {regulation.impact_level}
                </div>
                <p className="text-xs text-neutral-light mt-1">
                  Based on institutional exposure
                </p>
              </div>
              
              <div className="bg-neutral-lighter rounded-lg p-4">
                <h4 className="font-medium mb-2">Compliance Deadline</h4>
                <div className="text-lg font-bold">
                  {regulation.compliance_deadline ? 
                    new Date(regulation.compliance_deadline).toLocaleDateString() :
                    'Not specified'
                  }
                </div>
                <p className="text-xs text-neutral-light mt-1">
                  {regulation.compliance_deadline ? 
                    `${Math.ceil((new Date(regulation.compliance_deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days remaining` :
                    'No deadline set'
                  }
                </p>
              </div>
              
              <div className="bg-neutral-lighter rounded-lg p-4">
                <h4 className="font-medium mb-2">Readiness Score</h4>
                <div className="text-lg font-bold text-green-600">
                  78%
                </div>
                <p className="text-xs text-neutral-light mt-1">
                  Based on completed compliance steps
                </p>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-medium mb-3">Impacted Risk Assessment Units</h3>
              <div className="space-y-4">
                {regulation.responsible_units?.map((unit) => (
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
            </div>

            <div className="mb-6">
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
            
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-3">Compliance Checklist</h3>
              <div className="space-y-3">
                {regulation.compliance_steps?.map((step, index) => (
                  <div key={index} className="flex items-start">
                    <input 
                      type="checkbox" 
                      id={`step-${index}`} 
                      className="mt-1 mr-3"
                      defaultChecked={index < 3}
                    />
                    <label htmlFor={`step-${index}`} className="flex-1">
                      <span className="font-medium">{step.description}</span>
                      <p className="text-xs text-neutral-light mt-1">
                        {index < 3 ? 'Completed on May 15, 2024' : 'Due by June 30, 2024'}
                      </p>
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-end">
              <button className="btn btn-outline mr-2">Export Analysis</button>
              <button className="btn btn-primary">Generate Compliance Plan</button>
            </div>
          </div>
        ) : (
          <div className="card flex flex-col items-center justify-center h-full">
            <BarChart3 size={48} className="text-neutral-light mb-4" />
            <h3 className="text-lg font-medium">Select a Regulation</h3>
            <p className="text-neutral-light text-center mt-2">
              Choose a regulation from the list to view its impact analysis on {bank.name}.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImpactAnalysis;