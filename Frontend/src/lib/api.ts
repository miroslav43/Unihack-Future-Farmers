import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor to include token from localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  syncUser: async () => {
    const response = await api.post('/auth/sync');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  setUserRole: async (role: 'farmer' | 'buyer') => {
    const response = await api.post('/auth/role', { role });
    return response.data;
  },
  
  verifyToken: async () => {
    const response = await api.get('/auth/verify-token');
    return response.data;
  },
};

// Buyer API calls
export const buyerAPI = {
  createProfile: async (data: any) => {
    const response = await api.post('/buyers/', data);
    return response.data;
  },
  
  getMyProfile: async () => {
    const response = await api.get('/buyers/me/profile');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/buyers/${id}`);
    return response.data;
  },
  
  updateProfile: async (id: string, data: any) => {
    const response = await api.put(`/buyers/${id}`, data);
    return response.data;
  },
};

// Farmer API calls
export const farmerAPI = {
  createProfile: async (data: any) => {
    const response = await api.post('/farmers/', data);
    return response.data;
  },
  
  getMyProfile: async () => {
    const response = await api.get('/farmers/me/profile');
    return response.data;
  },
  
  getAll: async () => {
    const response = await api.get('/farmers/');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/farmers/${id}`);
    return response.data;
  },
  
  updateProfile: async (id: string, data: any) => {
    const response = await api.put(`/farmers/${id}`, data);
    return response.data;
  },
};

// Inventory API calls
export const inventoryAPI = {
  getAll: async () => {
    const response = await api.get('/inventory/');
    return response.data;
  },
  
  getByFarmer: async (farmerId: string) => {
    const response = await api.get(`/inventory/farmer/${farmerId}`);
    return response.data;
  },
  
  getStatistics: async (farmerId: string) => {
    const response = await api.get(`/inventory/farmer/${farmerId}/statistics`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/inventory/', data);
    return response.data;
  },
  
  update: async (id: string, data: any) => {
    const response = await api.put(`/inventory/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/inventory/${id}`);
    return response.data;
  },
  
  getAvailable: async (params?: { category?: string; min_price?: number; max_price?: number }) => {
    const response = await api.get('/inventory/available', { params });
    return response.data;
  },
};

// Order API calls
export const orderAPI = {
  create: async (data: any) => {
    const response = await api.post('/orders/', data);
    return response.data;
  },
  
  getAll: async () => {
    const response = await api.get('/orders/');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/orders/${id}`);
    return response.data;
  },
  
  accept: async (id: string, farmer_response?: string) => {
    const response = await api.put(`/orders/${id}/accept`, 
      farmer_response ? { farmer_response } : {}
    );
    return response.data;
  },
  
  reject: async (id: string, farmer_response: string) => {
    const response = await api.put(`/orders/${id}/reject`, { farmer_response });
    return response.data;
  },
};

// Contract API calls
export const contractAPI = {
  create: async (data: any) => {
    const response = await api.post('/contracts/', data);
    return response.data;
  },
  
  getAll: async (status?: string) => {
    const response = await api.get('/contracts/', { params: status ? { status } : {} });
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/contracts/${id}`);
    return response.data;
  },
  
  sign: async (id: string, signature: string, publicKey: string) => {
    const response = await api.post(`/contracts/${id}/sign`, {
      signature,
      public_key: publicKey,
    });
    return response.data;
  },
  
  reject: async (id: string) => {
    const response = await api.post(`/contracts/${id}/reject`);
    return response.data;
  },
  
  generateKeys: async (id: string) => {
    const response = await api.get(`/contracts/${id}/generate-keys`);
    return response.data;
  },
};
