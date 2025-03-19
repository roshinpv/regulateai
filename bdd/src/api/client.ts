import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const parseOpenAPI = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/parse-openapi', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const generateTests = async (endpoints: Record<string, any>, openApiSpec: any) => {
  const response = await apiClient.post('/generate-tests', {
    endpoints,
    openApiSpec,
  });
  return response.data;
};

export const setupWiremock = async (endpoints: Record<string, any>, openApiSpec: any) => {
  const response = await apiClient.post('/setup-wiremock', {
    endpoints,
    openApiSpec,
  });
  return response.data;
};

export const executeTests = async (testScript: string) => {
  const response = await apiClient.post('/execute-tests', {
    testScript,
  });
  return response.data;
};

export default apiClient;