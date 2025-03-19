import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Building2, AlertCircle, Loader } from 'lucide-react';
import { entitiesAPI } from '../../api';
import { EntitySearchResult } from '../../types';

const EntitySearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EntitySearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await entitiesAPI.search(query);
      setResults(data);
    } catch (err) {
      console.error('Error searching entities:', err);
      setError('Failed to search entities');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleViewEntity = (id: string) => {
    navigate(`/entities/${id}`);
  };
  
  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full bg-neutral-lighter mr-4">
          <Building2 size={20} className="text-neutral" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Entity Analysis</h2>
          <p className="text-sm text-neutral-light">
            Search and analyze entities from transaction data
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search entities by name, registration number, or jurisdiction..."
            className="input pl-10 pr-4 w-full"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-light" size={18} />
          {isLoading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <Loader className="animate-spin text-neutral-light" size={18} />
            </div>
          )}
        </div>
      </form>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start">
          <AlertCircle size={20} className="text-red-500 mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}
      
      {results.length > 0 ? (
        <div className="space-y-4">
          {results.map((result) => (
            <div 
              key={result.entity.id} 
              className="border border-neutral-lighter rounded-lg p-4 hover:bg-neutral-lighter transition-colors cursor-pointer"
              onClick={() => handleViewEntity(result.entity.id)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium">{result.entity.name}</h3>
                  <div className="text-sm text-neutral-light mt-1">
                    <span className="mr-4">{result.entity.type}</span>
                    {result.entity.jurisdiction && (
                      <span className="mr-4">{result.entity.jurisdiction}</span>
                    )}
                    {result.entity.registration_number && (
                      <span>Reg: {result.entity.registration_number}</span>
                    )}
                  </div>
                </div>
                {result.entity.risk_score !== null && (
                  <div className={`text-sm font-medium px-3 py-1 rounded-full ${
                    result.entity.risk_score >= 70 ? 'bg-red-100 text-red-700' :
                    result.entity.risk_score >= 40 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    Risk Score: {result.entity.risk_score}
                  </div>
                )}
              </div>
              {result.matched_source && (
                <div className="mt-2 text-sm">
                  <span className="font-medium">Matched Source:</span>
                  <span className="text-neutral-light ml-2">{result.matched_source.source_type}</span>
                </div>
              )}
              <div className="mt-2 text-xs text-neutral-light">
                Relevance: {Math.round(result.relevance_score * 100)}%
              </div>
            </div>
          ))}
        </div>
      ) : query && !isLoading ? (
        <div className="text-center py-8 text-neutral-light">
          No entities found matching your search
        </div>
      ) : null}
    </div>
  );
};

export default EntitySearch;