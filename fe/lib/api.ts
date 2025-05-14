// API base URL
import { handleFetchResponse } from './errors';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  id: string;
  username: string;
  email: string;
  // Optional fields that might be part of the response
  roles?: string[];
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  user_id: string;
  username: string;
  email: string;
  created_at: string;
}

// Helper to get auth header
export const getAuthHeader = (): HeadersInit => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// API service
export const apiService = {
  // Authentication
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      return await handleFetchResponse<LoginResponse>(response);
    } catch (error) {
      console.error('Login API error:', error);
      throw error;
    }
  },

  logout: async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Logout failed with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Logout API error:', error);
      throw error;
    }
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      return await handleFetchResponse<RegisterResponse>(response);
    } catch (error) {
      console.error('Register API error:', error);
      throw error;
    }
  },

  // Protected endpoints
  getUserProfile: async (): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        method: 'GET',
        headers: {
          ...getAuthHeader(),
        },
      });

      return await handleFetchResponse<any>(response);
    } catch (error) {
      console.error('Get profile API error:', error);
      throw error;
    }
  },

  // Example for other API calls (can be expanded as needed)
  fetchData: async (endpoint: string, options: RequestInit = {}): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          ...getAuthHeader(),
        },
      });

      return await handleFetchResponse<any>(response);
    } catch (error) {
      console.error('API error:', error);
      throw error;
    }
  },
}; 