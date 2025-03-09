import React from 'react';
import ChatInterface from '../components/Assistant/ChatInterface';

const AssistantPage: React.FC = () => {
  return (
    <div className="h-[calc(100vh-10rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">AI Compliance Assistant</h1>
          <p className="text-neutral-light">Powered by Llama 3.2 6B fine-tuned on regulatory data</p>
        </div>
      </div>
      
      <ChatInterface />
    </div>
  );
};

export default AssistantPage;