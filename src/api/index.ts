import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

interface JWTPayload {
  exp: number;
  sub: string;
}

// Add request interceptor to include auth token and check expiry
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        // Check token expiry
        const decoded = jwtDecode<JWTPayload>(token);
        const currentTime = Date.now() / 1000;

        if (decoded.exp < currentTime) {
          // Token has expired, remove it and redirect to login
          localStorage.removeItem('token');
          window.location.href = '/login';
          throw new Error('Token expired');
        }

        config.headers.Authorization = `Bearer ${token}`;
      } catch (err) {
        // Invalid token, remove it and redirect to login
        localStorage.removeItem('token');
        window.location.href = '/login';
        throw err;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized, token might be expired
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
};

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData: { username: string; email: string; password: string; is_admin?: boolean }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
};

// Regulations API
export const regulationsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    category?: string;
    impact_level?: string;
    agency_id?: string;
    jurisdiction_id?: string;
    search?: string;
  }) => {
    const response = await api.get('/regulations', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/regulations/${id}`);
    return response.data;
  },

  create: async (regulationData: any) => {
    const response = await api.post('/regulations', regulationData);
    return response.data;
  },

  update: async (id: string, regulationData: any) => {
    const response = await api.put(`/regulations/${id}`, regulationData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/regulations/${id}`);
    return response.data;
  },

  search: async (query: string) => {
    const response = await api.get(`/regulations/search/natural?query=${encodeURIComponent(query)}`);
    return response.data;
  },
};

// Agencies API
export const agenciesAPI = {
  getAll: async (params?: { skip?: number; limit?: number; jurisdiction_id?: string }) => {
    const response = await api.get('/agencies', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/agencies/${id}`);
    return response.data;
  },

  create: async (agencyData: { name: string; description: string; jurisdiction_id?: string; website?: string }) => {
    const response = await api.post('/agencies', agencyData);
    return response.data;
  },

  update: async (id: string, agencyData: { name: string; description: string; jurisdiction_id?: string; website?: string }) => {
    const response = await api.put(`/agencies/${id}`, agencyData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/agencies/${id}`);
    return response.data;
  },
};

// Banks API
export const banksAPI = {
  getAll: async (params?: { skip?: number; limit?: number; jurisdiction_id?: string }) => {
    const response = await api.get('/banks', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/banks/${id}`);
    return response.data;
  },

  getRegulations: async (id: string) => {
    const response = await api.get(`/banks/${id}/regulations`);
    return response.data;
  },

  create: async (bankData: { name: string; jurisdiction_id?: string; size_category?: string }) => {
    const response = await api.post('/banks', bankData);
    return response.data;
  },

  update: async (id: string, bankData: { name: string; jurisdiction_id?: string; size_category?: string }) => {
    const response = await api.put(`/banks/${id}`, bankData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/banks/${id}`);
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    priority?: string;
    regulation_id?: string;
    due_before?: string;
    due_after?: string;
  }) => {
    const response = await api.get('/alerts', { params });
    return response.data;
  },

  getUpcoming: async (days: number = 30) => {
    const response = await api.get(`/alerts/upcoming?days=${days}`);
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },

  create: async (alertData: any) => {
    const response = await api.post('/alerts', alertData);
    return response.data;
  },

  update: async (id: string, alertData: any) => {
    const response = await api.put(`/alerts/${id}`, alertData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/alerts/${id}`);
    return response.data;
  },
};

// Updates API
export const updatesAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    regulation_id?: string;
    agency?: string;
    since?: string;
  }) => {
    const response = await api.get('/updates', { params });
    return response.data;
  },

  getRecent: async (days: number = 30) => {
    const response = await api.get(`/updates/recent?days=${days}`);
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/updates/${id}`);
    return response.data;
  },

  create: async (updateData: any) => {
    const response = await api.post('/updates', updateData);
    return response.data;
  },

  update: async (id: string, updateData: any) => {
    const response = await api.put(`/updates/${id}`, updateData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/updates/${id}`);
    return response.data;
  },
};

// Graph API
export const graphAPI = {
  getGraphData: async (params?: {
    include_regulations?: boolean;
    include_agencies?: boolean;
    include_banks?: boolean;
    include_jurisdictions?: boolean;
    regulation_id?: string;
    agency_id?: string;
    bank_id?: string;
    jurisdiction_id?: string;
  }) => {
    const response = await api.get('/graph', { params });
    return response.data;
  },

  expandNode: async (nodeId: string, nodeType: string) => {
    const response = await api.get(`/graph/expand/${nodeId}?node_type=${nodeType}`);
    return response.data;
  },
};

// Assistant API
export const assistantAPI = {
  query: async (query: string, userId: string) => {
    const response = await api.post('/assistant/query', { query, user_id: userId });
    return response.data;
  },

  getHistory: async (userId: string, limit: number = 50) => {
    const response = await api.get(`/assistant/history/${userId}?limit=${limit}`);
    return response.data;
  },

  clearHistory: async (userId: string) => {
    const response = await api.delete(`/assistant/history/${userId}`);
    return response.data;
  },
};

// Jurisdictions API
export const jurisdictionsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    type?: string;
    parent_id?: string;
  }) => {
    const response = await api.get('/jurisdictions', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/jurisdictions/${id}`);
    return response.data;
  },

  create: async (jurisdictionData: {
    name: string;
    code: string;
    type: string;
    parent_id?: string;
  }) => {
    const response = await api.post('/jurisdictions', jurisdictionData);
    return response.data;
  },

  update: async (id: string, jurisdictionData: {
    name: string;
    code: string;
    type: string;
    parent_id?: string;
  }) => {
    const response = await api.put(`/jurisdictions/${id}`, jurisdictionData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/jurisdictions/${id}`);
    return response.data;
  },

  getRegulations: async (id: string, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/jurisdictions/${id}/regulations`, { params });
    return response.data;
  },

  getAgencies: async (id: string, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/jurisdictions/${id}/agencies`, { params });
    return response.data;
  },

  getBanks: async (id: string, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/jurisdictions/${id}/banks`, { params });
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    regulation_id?: string;
    jurisdiction_id?: string;
    processed?: boolean;
  }) => {
    const response = await api.get('/documents', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  uploadFile: async (formData: FormData) => {
    const response = await api.post('/documents/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  uploadUrl: async (documentData: {
    title: string;
    description?: string;
    url: string;
    content_type: string;
    regulation_id?: string;
    jurisdiction_id?: string;
  }) => {
    const response = await api.post('/documents/upload-url', documentData);
    return response.data;
  },

  update: async (id: string, documentData: {
    title: string;
    description?: string;
    regulation_id?: string;
    jurisdiction_id?: string;
    url?: string;
  }) => {
    const response = await api.put(`/documents/${id}`, documentData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },

  process: async (id: string) => {
    const response = await api.post(`/documents/${id}/process`);
    return response.data;
  },

  processBatch: async (documentIds: string[]) => {
    const response = await api.post('/documents/process-batch', { document_ids: documentIds });
    return response.data;
  },
};

export default api;