import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import RegulationsList from '../components/Regulations/RegulationsList';
import RegulationDetail from '../components/Regulations/RegulationDetail';

const RegulationsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const handleCloseDetail = () => {
    navigate('/regulations');
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold">Regulations Explorer</h1>
        <div>
          <button className="btn btn-outline mr-2">Import Regulation</button>
          <button className="btn btn-primary">Add New Regulation</button>
        </div>
      </div>
      
      {id ? (
        <RegulationDetail 
          regulationId={id} 
          onClose={handleCloseDetail} 
        />
      ) : (
        <RegulationsList />
      )}
    </div>
  );
};

export default RegulationsPage;