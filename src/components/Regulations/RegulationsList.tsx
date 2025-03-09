import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import { regulationsAPI } from '../../api';
import { Regulation } from '../../types';

const RegulationsList: React.FC = () => {
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const location = useLocation();
  const navigate = useNavigate();
  
  const categories = ['All', 'Risk', 'Capital', 'Consumer Protection', 'Fraud', 'Other'];
  
  useEffect(() => {
    // Check if there's a search query in the URL
    const params = new URLSearchParams(location.search);
    const searchQuery = params.get('search');
    if (searchQuery) {
      setSearchTerm(searchQuery);
    }
  }, [location.search]);
  
  useEffect(() => {
    const fetchRegulations = async () => {
      setIsLoading(true);
      try {
        let data;
        
        if (searchTerm) {
          // Use natural language search if there's a search term
          data = await regulationsAPI.search(searchTerm);
        } else {
          // Otherwise get all regulations with optional category filter
          const params: any = {};
          if (selectedCategory && selectedCategory !== 'All') {
            params.category = selectedCategory;
          }
          data = await regulationsAPI.getAll(params);
        }
        
        setRegulations(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching regulations:', err);
        setError('Failed to load regulations');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRegulations();
  }, [searchTerm, selectedCategory]);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Update URL with search query
    navigate(`/regulations?search=${encodeURIComponent(searchTerm)}`);
  };
  
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category === 'All' ? null : category);
    // Clear search when changing categories
    if (searchTerm) {
      setSearchTerm('');
      navigate('/regulations');
    }
  };
  
  const handleViewDetails = (id: string) => {
    navigate(`/regulations/${id}`);
  };
  
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Regulations Explorer</h2>
        </div>
        <div className="py-8 text-center text-neutral-light">Loading regulations...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Regulations Explorer</h2>
        </div>
        <div className="py-8 text-center text-red-500">{error}</div>
      </div>
    );
  }
  
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Regulations Explorer</h2>
        <div className="flex items-center space-x-2">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <input
                type="text"
                placeholder="Search regulations..."
                className="input pl-10 py-1 text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-light" size={16} />
            </div>
          </form>
          <div className="relative">
            <button className="btn btn-outline py-1 flex items-center">
              <Filter size={16} className="mr-2" />
              <span>Filter</span>
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex space-x-2 mb-6">
        {categories.map((category) => (
          <button
            key={category}
            className={`px-3 py-1 rounded-full text-sm ${
              selectedCategory === category || (category === 'All' && !selectedCategory)
                ? 'bg-primary text-white'
                : 'bg-neutral-lighter text-neutral-light hover:bg-neutral-light hover:text-white'
            }`}
            onClick={() => handleCategoryChange(category)}
          >
            {category}
          </button>
        ))}
      </div>
      
      {regulations.length === 0 ? (
        <div className="py-8 text-center text-neutral-light">
          {searchTerm 
            ? `No regulations found matching "${searchTerm}"` 
            : 'No regulations found'}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-lighter">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Regulation</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Agency</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Impact Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Last Updated</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-neutral-light uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-lighter">
              {regulations.map((regulation) => (
                <tr key={regulation.id} className="hover:bg-background">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium">{regulation.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm">{regulation.agency?.name || 'Unknown'}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm">{regulation.category}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${
                      regulation.impact_level === 'High' ? 'badge-high' : 
                      regulation.impact_level === 'Medium' ? 'badge-medium' : 'badge-low'
                    }`}>
                      {regulation.impact_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-light">
                    {new Date(regulation.last_updated).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button 
                      className="text-primary hover:text-primary-dark font-medium"
                      onClick={() => handleViewDetails(regulation.id)}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RegulationsList;