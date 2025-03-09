import React from 'react';
import ImpactAnalysis from '../components/Impact/ImpactAnalysis';

const ImpactPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold">Regulatory Impact Analysis</h1>
          <p className="text-neutral-light">Analyze how regulations affect your institution</p>
        </div>
        <div>
          <button className="btn btn-primary">Generate Impact Report</button>
        </div>
      </div>
      
      <ImpactAnalysis />
    </div>
  );
};

export default ImpactPage;