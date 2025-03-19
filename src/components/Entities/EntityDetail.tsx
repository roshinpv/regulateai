import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building2, AlertCircle, Loader, ArrowLeft, RefreshCw,
  BarChart3, FileText, Network, AlertTriangle
} from 'lucide-react';
import { entitiesAPI } from '../../api';
import { Entity, EntitySource, EntityTransaction, EntityRelationship, EntityRiskFactor } from '../../types';

interface EntityDetailProps {
  entityId: string;
}

const EntityDetail: React.FC<EntityDetailProps> = ({ entityId }) => {
  const [entity, setEntity] = useState<Entity | null>(null);
  const [sources, setSources] = useState<EntitySource[]>([]);
  const [transactions, setTransactions] = useState<EntityTransaction[]>([]);
  const [relationships, setRelationships] = useState<EntityRelationship[]>([]);
  const [riskFactors, setRiskFactors] = useState<EntityRiskFactor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchEntityData();
  }, [entityId]);
  
  const fetchEntityData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [
        entityData,
        sourcesData,
        transactionsData,
        relationshipsData,
        riskFactorsData
      ] = await Promise.all([
        entitiesAPI.getById(entityId),
        entitiesAPI.getSources(entityId),
        entitiesAPI.getTransactions(entityId),
        entitiesAPI.getRelationships(entityId),
        entitiesAPI.getRiskFactors(entityId)
      ]);
      
      setEntity(entityData);
      setSources(sourcesData);
      setTransactions(transactionsData);
      setRelationships(relationshipsData);
      setRiskFactors(riskFactorsData);
    } catch (err) {
      console.error('Error fetching entity data:', err);
      setError('Failed to load entity data');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const updatedEntity = await entitiesAPI.analyze(entityId);
      setEntity(updatedEntity);
      
      // Refresh risk factors after analysis
      const newRiskFactors = await entitiesAPI.getRiskFactors(entityId);
      setRiskFactors(newRiskFactors);
    } catch (err) {
      console.error('Error analyzing entity:', err);
      setError('Failed to analyze entity');
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const getRiskScoreColor = (score: number) => {
    if (score >= 70) return 'text-red-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };
  
  if (isLoading) {
    return (
      <div className="card flex items-center justify-center h-64">
        <Loader className="animate-spin text-neutral-light" size={24} />
      </div>
    );
  }
  
  if (error || !entity) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <button 
            className="text-neutral-light hover:text-neutral flex items-center"
            onClick={() => navigate('/entities')}
          >
            <ArrowLeft size={18} className="mr-2" />
            Back to Search
          </button>
        </div>
        <div className="flex items-center justify-center h-64 text-red-500">
          <AlertCircle size={24} className="mr-2" />
          <span>{error || 'Entity not found'}</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <button 
            className="text-neutral-light hover:text-neutral flex items-center"
            onClick={() => navigate('/entities')}
          >
            <ArrowLeft size={18} className="mr-2" />
            Back to Search
          </button>
          <button 
            className="btn btn-primary flex items-center"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            <RefreshCw size={18} className={`mr-2 ${isAnalyzing ? 'animate-spin' : ''}`} />
            {isAnalyzing ? 'Analyzing...' : 'Analyze Entity'}
          </button>
        </div>
        
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold">{entity.name}</h2>
            <div className="text-neutral-light mt-2">
              <span className="mr-4">{entity.type}</span>
              {entity.jurisdiction && (
                <span className="mr-4">{entity.jurisdiction}</span>
              )}
              {entity.registration_number && (
                <span>Reg: {entity.registration_number}</span>
              )}
            </div>
          </div>
          
          {entity.risk_score !== undefined && (
            <div className="text-center">
              <div className={`text-3xl font-bold ${getRiskScoreColor(entity.risk_score)}`}>
                {entity.risk_score}
              </div>
              <div className="text-sm text-neutral-light">Risk Score</div>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-neutral-lighter rounded-lg p-4">
            <div className="flex items-center text-neutral-light mb-2">
              <FileText size={16} className="mr-2" />
              Sources
            </div>
            <div className="text-2xl font-bold">{sources.length}</div>
          </div>
          
          <div className="bg-neutral-lighter rounded-lg p-4">
            <div className="flex items-center text-neutral-light mb-2">
              <BarChart3 size={16} className="mr-2" />
              Transactions
            </div>
            <div className="text-2xl font-bold">{transactions.length}</div>
          </div>
          
          <div className="bg-neutral-lighter rounded-lg p-4">
            <div className="flex items-center text-neutral-light mb-2">
              <Network size={16} className="mr-2" />
              Relationships
            </div>
            <div className="text-2xl font-bold">{relationships.length}</div>
          </div>
          
          <div className="bg-neutral-lighter rounded-lg p-4">
            <div className="flex items-center text-neutral-light mb-2">
              <AlertTriangle size={16} className="mr-2" />
              Risk Factors
            </div>
            <div className="text-2xl font-bold">{riskFactors.length}</div>
          </div>
        </div>
      </div>
      
      {/* Risk Factors */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Risk Factors</h3>
        {riskFactors.length > 0 ? (
          <div className="space-y-4">
            {riskFactors.map((factor) => (
              <div key={factor.id} className="border border-neutral-lighter rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">{factor.factor_type}</h4>
                    {factor.factor_value && (
                      <p className="text-sm text-neutral-light mt-1">{factor.factor_value}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getRiskScoreColor(factor.risk_contribution)}`}>
                      {factor.risk_contribution}%
                    </div>
                    <div className="text-xs text-neutral-light">
                      Confidence: {factor.confidence_score}%
                    </div>
                  </div>
                </div>
                {factor.evidence && Object.keys(factor.evidence).length > 0 && (
                  <div className="mt-2 text-sm">
                    <span className="font-medium">Evidence:</span>
                    <pre className="mt-1 text-neutral-light overflow-x-auto">
                      {JSON.stringify(factor.evidence, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-neutral-light">
            No risk factors identified yet
          </div>
        )}
      </div>
      
      {/* Sources */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Information Sources</h3>
        {sources.length > 0 ? (
          <div className="space-y-4">
            {sources.map((source) => (
              <div key={source.id} className="border border-neutral-lighter rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center">
                      <span className="font-medium">{source.source_type}</span>
                      <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                        source.verification_status === 'Verified' ? 'bg-green-100 text-green-700' :
                        source.verification_status === 'Disputed' ? 'bg-red-100 text-red-700' :
                        source.verification_status === 'Inconclusive' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-neutral-lighter text-neutral-light'
                      }`}>
                        {source.verification_status}
                      </span>
                    </div>
                    {source.source_date && (
                      <p className="text-sm text-neutral-light mt-1">
                        {new Date(source.source_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  {source.reliability_score !== undefined && (
                    <div className="text-sm">
                      Reliability: {source.reliability_score}%
                    </div>
                  )}
                </div>
                {source.content && (
                  <div className="mt-2 text-sm text-neutral-light">
                    {source.content}
                  </div>
                )}
                {source.source_url && (
                  <div className="mt-2">
                    <a 
                      href={source.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:text-primary-dark"
                    >
                      View Source
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-neutral-light">
            No sources available
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityDetail;