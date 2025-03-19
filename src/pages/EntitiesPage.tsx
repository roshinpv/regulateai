import React from 'react';
import { useParams } from 'react-router-dom';
import EntitySearch from '../components/Entities/EntitySearch';
import EntityDetail from '../components/Entities/EntityDetail';

const EntitiesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold">Entity Analysis</h1>
          <p className="text-neutral-light">Research and analyze entities from transaction data</p>
        </div>
        <div>
          <button className="btn btn-primary">Add New Entity</button>
        </div>
      </div>
      
      {id ? <EntityDetail entityId={id} /> : <EntitySearch />}
    </div>
  );
};

export default EntitiesPage;