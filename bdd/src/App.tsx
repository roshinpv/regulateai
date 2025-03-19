import React, { useState } from 'react';
import { FileJson, Upload, Play, Download, ChevronDown, ChevronUp, AlertTriangle, Clock, BarChart3, Activity, PlayCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { parse } from 'yaml';
import { Toaster, toast } from 'react-hot-toast';
import Editor from '@monaco-editor/react';
import type { OpenAPISpec, EndpointConfig, TestResult } from './types';
import { parseOpenAPI, generateTests, setupWiremock, executeTests } from './api/client';

function App() {
  const [spec, setSpec] = useState<OpenAPISpec | null>(null);
  const [endpointConfigs, setEndpointConfigs] = useState<Record<string, EndpointConfig>>({});
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [testScript, setTestScript] = useState<string>('');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [showEditor, setShowEditor] = useState<boolean>(false);

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    setIsLoading(true);

    try {
      const { spec: parsedSpec } = await parseOpenAPI(file);
      setSpec(parsedSpec);
      
      const initialConfigs: Record<string, EndpointConfig> = {};
      Object.keys(parsedSpec.paths).forEach(path => {
        initialConfigs[path] = {
          jiraStory: '',
          requestData: '',
          responseData: '',
          selected: false
        };
      });
      setEndpointConfigs(initialConfigs);
      toast.success('OpenAPI specification loaded successfully');
    } catch (error) {
      console.error('Failed to parse OpenAPI spec:', error);
      toast.error('Failed to parse the OpenAPI specification. Please check the file format.');
    } finally {
      setIsLoading(false);
    }
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

  const handleGenerateTests = async () => {
    setIsGenerating(true);
    try {
      const selectedEndpoints = Object.entries(endpointConfigs)
        .filter(([_, config]) => config.selected)
        .reduce((acc, [path, config]) => ({
          ...acc,
          [path]: config
        }), {});

      const { testCases } = await generateTests(selectedEndpoints, spec);
      
      // Setup WireMock stubs
      await setupWiremock(selectedEndpoints, spec);
      toast.success('WireMock stubs created successfully');

      // Format test cases as a string and set to editor
      const formattedTests = Object.entries(testCases)
        .map(([path, testCase]) => testCase)
        .join('\n\n');
      
      setTestScript(formattedTests);
      setShowEditor(true);
      toast.success('Test cases generated successfully');
    } catch (error) {
      console.error('Failed to generate tests:', error);
      toast.error('Failed to generate test cases. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteTests = async () => {
    setIsExecuting(true);
    try {
      const results = await executeTests(testScript);
      setTestResults(results);
      
      const passedTests = results.filter(r => r.passed).length;
      const totalTests = results.length;
      
      toast.success(`Tests executed: ${passedTests}/${totalTests} passed`);
    } catch (error) {
      console.error('Failed to execute tests:', error);
      toast.error('Failed to execute test cases. Please check the WireMock setup.');
    } finally {
      setIsExecuting(false);
    }
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
      <Toaster position="top-right" />
      
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
                  ${isDragActive ? 'border-primary bg-primary/5' : 'border-neutral-lighter hover:border-primary'}
                  ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} disabled={isLoading} />
                <Upload className={`mx-auto h-12 w-12 ${isLoading ? 'text-neutral-light animate-pulse' : 'text-primary'}`} />
                <p className="mt-4 text-sm text-neutral-light">
                  {isLoading ? 'Processing...' : 'Drag & drop your OpenAPI specification file here, or click to select'}
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
                disabled={selectedEndpointsCount === 0 || isGenerating}
                className="wf-button-primary"
                onClick={handleGenerateTests}
              >
                <Play className={`h-4 w-4 ${isGenerating ? 'animate-pulse' : ''}`} />
                <span>{isGenerating ? 'Generating...' : 'Generate Tests'}</span>
              </button>
              <button
                disabled={selectedEndpointsCount === 0 || isGenerating}
                className="wf-button-secondary"
              >
                <Download className="h-4 w-4" />
                <span>Export Tests</span>
              </button>
            </div>

            {/* Test Editor and Results */}
            {showEditor && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-neutral">Test Scripts</h2>
                    <button
                      onClick={handleExecuteTests}
                      disabled={isExecuting || !testScript}
                      className="wf-button-primary"
                    >
                      <PlayCircle className={`h-4 w-4 ${isExecuting ? 'animate-pulse' : ''}`} />
                      <span>{isExecuting ? 'Executing...' : 'Execute Tests'}</span>
                    </button>
                  </div>
                  <div className="h-[500px] border border-neutral-lighter rounded-lg overflow-hidden">
                    <Editor
                      height="100%"
                      defaultLanguage="gherkin"
                      value={testScript}
                      onChange={(value) => setTestScript(value || '')}
                      theme="vs-light"
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: 'on',
                        readOnly: isExecuting,
                      }}
                    />
                  </div>
                </div>

                {testResults.length > 0 && (
                  <div className="bg-white rounded-lg shadow-card p-6">
                    <h2 className="text-xl font-semibold text-neutral mb-4">Test Results</h2>
                    <div className="space-y-4">
                      {testResults.map((result, index) => (
                        <div
                          key={index}
                          className={`p-4 rounded-lg border ${
                            result.passed ? 'border-success bg-success/5' : 'border-danger bg-danger/5'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className={`font-medium ${result.passed ? 'text-success' : 'text-danger'}`}>
                              Test #{index + 1}: {result.passed ? 'Passed' : 'Failed'}
                            </span>
                            <span className="text-sm text-neutral-light">
                              Duration: {result.duration}ms
                            </span>
                          </div>
                          <p className="mt-2 text-sm text-neutral">{result.message}</p>
                          {result.details && (
                            <pre className="mt-2 p-2 bg-neutral-50 rounded text-xs overflow-x-auto">
                              {result.details}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;