import React, { useState } from 'react';
import { FileJson, Upload, Play, Download, ChevronDown, ChevronUp, AlertTriangle, Clock, BarChart3, Activity } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { parse } from 'yaml';
import type { OpenAPISpec, EndpointConfig } from './types';

function App() {
  const [spec, setSpec] = useState<OpenAPISpec | null>(null);
  const [endpointConfigs, setEndpointConfigs] = useState<Record<string, EndpointConfig>>({});
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);

  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const parsed = file.name.endsWith('.yaml') || file.name.endsWith('.yml')
          ? parse(content)
          : JSON.parse(content);
        setSpec(parsed);
        
        const initialConfigs: Record<string, EndpointConfig> = {};
        Object.keys(parsed.paths).forEach(path => {
          initialConfigs[path] = {
            jiraStory: '',
            requestData: '',
            responseData: '',
            selected: false
          };
        });
        setEndpointConfigs(initialConfigs);
      } catch (error) {
        console.error('Failed to parse OpenAPI spec:', error);
        alert('Failed to parse the OpenAPI specification. Please check the file format.');
      }
    };

    reader.readAsText(file);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'application/x-yaml': ['.yaml', '.yml'],
    },
    multiple: false,
  });

  const handleEndpointSelect = (path: string) => {
    setEndpointConfigs(prev => ({
      ...prev,
      [path]: {
        ...prev[path],
        selected: !prev[path].selected
      }
    }));
  };

  const handleConfigChange = (path: string, field: keyof EndpointConfig, value: string | boolean) => {
    setEndpointConfigs(prev => ({
      ...prev,
      [path]: {
        ...prev[path],
        [field]: value
      }
    }));
  };

  const toggleEndpoint = (path: string) => {
    setExpandedEndpoint(expandedEndpoint === path ? null : path);
  };

  const selectedEndpointsCount = Object.values(endpointConfigs).filter(config => config.selected).length;

  const DashboardCard = ({ icon: Icon, title, value, subtitle, trend }: any) => (
    <div className="bg-white rounded-lg shadow-card p-6">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Icon className="h-5 w-5 text-neutral" />
          <h3 className="text-sm font-medium text-neutral">{title}</h3>
        </div>
      </div>
      <div className="mt-2">
        <div className="text-3xl font-bold text-neutral">{value}</div>
        <p className="text-sm text-neutral-light mt-1">{subtitle}</p>
        {trend && (
          <p className={`text-sm mt-2 ${trend.includes('+') ? 'text-green-600' : 'text-primary'}`}>
            {trend}
          </p>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <FileJson className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-semibold text-neutral">Karate BDD Generator</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {!spec ? (
          <>
            {/* Dashboard Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <DashboardCard
                icon={AlertTriangle}
                title="Pending Tests"
                value="0"
                subtitle="No tests pending"
              />
              <DashboardCard
                icon={Activity}
                title="Active Endpoints"
                value="0"
                subtitle="No endpoints configured"
              />
              <DashboardCard
                icon={Clock}
                title="Recent Updates"
                value="0"
                subtitle="Last 30 days"
              />
            </div>

            {/* File Upload */}
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-lg font-semibold text-neutral mb-4">Upload OpenAPI Specification</h2>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                  ${isDragActive ? 'border-primary bg-primary/5' : 'border-neutral-lighter hover:border-primary'}`}
              >
                <input {...getInputProps()} />
                <Upload className="mx-auto h-12 w-12 text-primary" />
                <p className="mt-4 text-sm text-neutral-light">
                  Drag & drop your OpenAPI specification file here, or click to select
                </p>
                <p className="mt-2 text-xs text-neutral-light">
                  Supports JSON and YAML formats
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="space-y-6">
            {/* Stats for loaded spec */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <DashboardCard
                icon={AlertTriangle}
                title="Selected Endpoints"
                value={selectedEndpointsCount}
                subtitle="Ready for test generation"
              />
              <DashboardCard
                icon={Activity}
                title="Total Endpoints"
                value={Object.keys(spec.paths).length}
                subtitle="Available in specification"
              />
              <DashboardCard
                icon={BarChart3}
                title="Coverage"
                value={`${Math.round((selectedEndpointsCount / Object.keys(spec.paths).length) * 100)}%`}
                subtitle="Of total endpoints"
              />
            </div>

            {/* Endpoints List */}
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-semibold text-neutral mb-6 flex items-center justify-between">
                <span>API Endpoints</span>
                <span className="text-sm font-normal text-neutral-light">
                  {selectedEndpointsCount} endpoint{selectedEndpointsCount !== 1 ? 's' : ''} selected
                </span>
              </h2>
              <div className="space-y-4">
                {Object.entries(spec.paths).map(([path, methods]) => (
                  <div key={path} className="border border-neutral-lighter rounded-lg">
                    <div 
                      className="p-4 cursor-pointer flex items-center justify-between"
                      onClick={() => toggleEndpoint(path)}
                    >
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={endpointConfigs[path]?.selected}
                          onChange={(e) => {
                            e.stopPropagation();
                            handleEndpointSelect(path);
                          }}
                          className="h-5 w-5 text-primary rounded border-neutral-lighter focus:ring-primary"
                        />
                        <span className="font-medium text-neutral">{path}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        {expandedEndpoint === path ? (
                          <ChevronUp className="h-5 w-5 text-neutral-light" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-neutral-light" />
                        )}
                      </div>
                    </div>

                    {expandedEndpoint === path && (
                      <div className="p-4 border-t border-neutral-lighter">
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-neutral mb-2">
                              JIRA Story
                            </label>
                            <textarea
                              value={endpointConfigs[path]?.jiraStory}
                              onChange={(e) => handleConfigChange(path, 'jiraStory', e.target.value)}
                              placeholder="Enter JIRA story related to this endpoint..."
                              className="wf-input h-24"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-neutral mb-2">
                              Request Data
                            </label>
                            <textarea
                              value={endpointConfigs[path]?.requestData}
                              onChange={(e) => handleConfigChange(path, 'requestData', e.target.value)}
                              placeholder="Enter sample request data in JSON format..."
                              className="wf-input h-32 font-mono text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-neutral mb-2">
                              Response Data
                            </label>
                            <textarea
                              value={endpointConfigs[path]?.responseData}
                              onChange={(e) => handleConfigChange(path, 'responseData', e.target.value)}
                              placeholder="Enter expected response data in JSON format..."
                              className="wf-input h-32 font-mono text-sm"
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end space-x-4">
              <button
                disabled={selectedEndpointsCount === 0}
                className="wf-button-primary"
              >
                <Play className="h-4 w-4" />
                <span>Generate Tests</span>
              </button>
              <button
                disabled={selectedEndpointsCount === 0}
                className="wf-button-secondary"
              >
                <Download className="h-4 w-4" />
                <span>Export Tests</span>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;