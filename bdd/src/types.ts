export interface OpenAPISpec {
  paths: Record<string, any>;
  components?: {
    schemas?: Record<string, any>;
  };
}

export interface APIEndpoint {
  path: string;
  method: string;
  summary?: string;
  parameters?: any[];
  requestBody?: any;
  responses?: Record<string, any>;
}

export interface EndpointConfig {
  jiraStory: string;
  requestData: string;
  responseData: string;
  selected: boolean;
}

export interface TestCase {
  feature: string;
  scenario: string;
  steps: string[];
}

export interface TestResult {
  passed: boolean;
  message: string;
  duration: number;
  details?: string;
}