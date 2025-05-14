// API base URL
import { handleFetchResponse } from './errors';
// We will load the crypto module dynamically

// Based on the API endpoints documentation, update the base URL path 
const API_BASE_URL = 'http://localhost:8000/api';

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

// Algorithm and Curve Types
export interface Algorithm {
  id: string;
  name: string;
  type: string;
  description: string;
  is_default?: boolean;
  status?: string;
  curves?: any[];
}

export interface Curve {
  id: string;
  name: string;
  algorithm_id: string;
  algorithm_name: string;
  status: string;
  parameters?: Record<string, any>;
}

export interface SignRequest {
  document: string;
  private_key: string;
  curve_name: string;
}

export interface SignResponse {
  signature: string;
  document_hash: string;
  signing_id: string; 
  signing_time: string;
  public_key: string;
}

export interface VerifyRequest {
  document: string;
  signature: string;
  public_key: string;
  algorithm_id: string;
  curve_name: string;
}

export interface VerifyResponse {
  verification: boolean;
  meta_data: {
    document: string;
    public_key: string;
    curve_name: string;
    bit_size: number;
    verification_id?: string;
    verification_time?: string;
  };
}

// Helper to get auth header
export const getAuthHeader = (): HeadersInit => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Mock data for development & testing
const MOCK_ALGORITHMS: Algorithm[] = [
  { id: "algo-1", name: "ECDSA", type: "Elliptic Curve", description: "Elliptic Curve Digital Signature Algorithm", is_default: true, status: "enabled" },
  { id: "algo-2", name: "RSA", type: "RSA", description: "Rivest–Shamir–Adleman algorithm", is_default: false, status: "enabled" },
  { id: "algo-3", name: "EdDSA", type: "Edwards-curve", description: "Edwards-curve Digital Signature Algorithm", is_default: false, status: "enabled" },
];

const MOCK_CURVES: Record<string, Curve[]> = {
  "algo-1": [
    { id: "curve-1", name: "secp256k1", algorithm_id: "algo-1", algorithm_name: "ECDSA", status: "enabled" },
    { id: "curve-2", name: "P-256", algorithm_id: "algo-1", algorithm_name: "ECDSA", status: "enabled" },
    { id: "curve-3", name: "P-384", algorithm_id: "algo-1", algorithm_name: "ECDSA", status: "enabled" },
    { id: "curve-4", name: "P-521", algorithm_id: "algo-1", algorithm_name: "ECDSA", status: "enabled" },
  ],
  "algo-2": [
    { id: "curve-5", name: "RSA-2048", algorithm_id: "algo-2", algorithm_name: "RSA", status: "enabled" },
    { id: "curve-6", name: "RSA-3072", algorithm_id: "algo-2", algorithm_name: "RSA", status: "enabled" },
    { id: "curve-7", name: "RSA-4096", algorithm_id: "algo-2", algorithm_name: "RSA", status: "enabled" },
  ],
  "algo-3": [
    { id: "curve-8", name: "Ed25519", algorithm_id: "algo-3", algorithm_name: "EdDSA", status: "enabled" },
  ],
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

  // Algorithms and Curves
  getAlgorithms: async (): Promise<Algorithm[]> => {
    try {
      console.log('Fetching algorithms from API...');
      const response = await fetch(`${API_BASE_URL}/algorithms`, {
        method: 'GET',
        headers: {
          ...getAuthHeader(),
        },
      });

      const data = await handleFetchResponse<any>(response);
      console.log('Raw algorithms response:', data);
      
      // The API returns { items: Algorithm[], count: number } or { algorithms: Algorithm[] }
      let result: Algorithm[] = [];
      if (data && Array.isArray(data.items)) {
        // This is the actual response format from the backend
        result = data.items;
      } else if (Array.isArray(data)) {
        // Direct array format
        result = data;
      } else if (data && Array.isArray(data.algorithms)) {
        // Alternative format from documentation
        result = data.algorithms;
      }
      
      // If the API returned no data, use mock data for development/testing
      if (result.length === 0) {
        console.log('Using mock algorithm data');
        result = MOCK_ALGORITHMS;
      }
      
      console.log('Processed algorithms:', result);
      return result;
    } catch (error) {
      console.error('Get algorithms API error:', error);
      console.log('Using mock algorithm data due to API error');
      return MOCK_ALGORITHMS;
    }
  },

  getDefaultAlgorithm: async (): Promise<Algorithm | null> => {
    try {
      console.log('Fetching default algorithm from API...');
      const response = await fetch(`${API_BASE_URL}/algorithms/default`, {
        method: 'GET',
        headers: {
          ...getAuthHeader(),
        },
      });

      const data = await handleFetchResponse<any>(response);
      console.log('Default algorithm response:', data);
      
      return data;
    } catch (error) {
      console.error('Get default algorithm API error:', error);
      // Return the first mock algorithm that is marked as default
      return MOCK_ALGORITHMS.find(algo => algo.is_default) || null;
    }
  },

  getAlgorithmByName: async (algorithmName: string): Promise<any> => {
    try {
      console.log(`Fetching algorithm details for name: ${algorithmName}`);
      const response = await fetch(`${API_BASE_URL}/algorithms/${algorithmName}`, {
        method: 'GET',
        headers: {
          ...getAuthHeader(),
        },
      });

      const data = await handleFetchResponse<any>(response);
      console.log('Algorithm details response:', data);
      
      return data;
    } catch (error) {
      console.error(`Get algorithm details API error for ${algorithmName}:`, error);
      throw error;
    }
  },

  getCurves: async (algorithmId?: string): Promise<Curve[]> => {
    try {
      // For the response structure shown, we need to get curves in different ways
      if (algorithmId) {
        // First try to find the algorithm name from our list of algorithms
        let algorithm;
        try {
          const algorithms = await apiService.getAlgorithms();
          algorithm = algorithms.find(a => a.id === algorithmId);
        } catch (e) {
          console.error('Error fetching algorithms for curve lookup:', e);
        }

        if (algorithm && algorithm.name) {
          // If we have the algorithm name, use it to get the algorithm details with curves
          console.log(`Fetching curves for algorithm name: ${algorithm.name}`);
          try {
            const algorithmDetails = await apiService.getAlgorithmByName(algorithm.name);
            if (algorithmDetails && Array.isArray(algorithmDetails.curves)) {
              const result = algorithmDetails.curves.map((curve: any) => ({
                id: curve.id,
                name: curve.name,
                algorithm_id: algorithmId,
                algorithm_name: algorithm.name,
                status: curve.status || 'enabled',
                parameters: curve.parameters
              }));
              console.log('Processed curves from algorithm details:', result);
              return result;
            }
          } catch (e) {
            console.error(`Error fetching algorithm details for curves: ${e}`);
          }
        }

        // Fallback to direct curve fetch if we couldn't get by algorithm name
        console.log(`Falling back to direct curve fetch for algorithm ID: ${algorithmId}`);
        const url = `${API_BASE_URL}/curves?algorithm_id=${algorithmId}&status=enabled`;
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            ...getAuthHeader(),
          },
        });

        const data = await handleFetchResponse<any>(response);
        console.log('Curves response:', data);
        
        let result: Curve[] = [];
        if (data && Array.isArray(data.curves)) {
          result = data.curves;
        } else if (Array.isArray(data)) {
          result = data;
        }
        
        if (result.length > 0) {
          return result;
        }
      } else {
        // If no algorithm ID is provided, fetch all curves
        const url = `${API_BASE_URL}/curves?status=enabled`;
        console.log('Fetching all curves from API...', url);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            ...getAuthHeader(),
          },
        });

        const data = await handleFetchResponse<any>(response);
        console.log('Raw curves response:', data);
        
        // Handle different response formats for curves endpoint
        let result: Curve[] = [];
        if (data && Array.isArray(data.curves)) {
          result = data.curves;
        } else if (Array.isArray(data)) {
          result = data;
        }
        
        console.log('Processed all curves:', result);
        return result;
      }
      
      // Fallback to mock data if needed
      if (algorithmId && MOCK_CURVES[algorithmId]) {
        console.log('Using mock curve data');
        return MOCK_CURVES[algorithmId];
      }
      
      return [];
    } catch (error) {
      console.error('Get curves API error:', error);
      if (algorithmId && MOCK_CURVES[algorithmId]) {
        console.log('Using mock curve data due to API error');
        return MOCK_CURVES[algorithmId];
      }
      return [];
    }
  },

  // Document Signing
  signDocument: async (document: string, privateKey: string, curveName: string): Promise<SignResponse> => {
    try {
      // First, get the curve parameters if available
      let curveParameters = null;
      
      // Try to find the curve parameters in our data
      for (const algoKey in MOCK_CURVES) {
        const curves = MOCK_CURVES[algoKey];
        const curve = curves.find(c => c.name === curveName);
        if (curve && curve.parameters) {
          curveParameters = curve.parameters;
          break;
        }
      }
      
      // Hash the document according to the curve type and parameters - dynamic import
      let hashedDocument = '';
      try {
        // Dynamically import the crypto module
        const cryptoModule = await import('./crypto');
        // Always use integer format for the hash when signing
        hashedDocument = await cryptoModule.calculateDocumentHash(document, curveName, curveParameters, true);
        console.log('Document hashed as integer:', hashedDocument);
      } catch (err) {
        console.error('Error hashing document:', err);
        throw new Error('Failed to hash document for signing');
      }
      
      console.log(`Signing document with curve: ${curveName}`);
      const response = await fetch(`${API_BASE_URL}/sign`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document: hashedDocument,
          private_key: privateKey,
          curve_name: curveName
        }),
      });

      return await handleFetchResponse<SignResponse>(response);
    } catch (error) {
      console.error('Sign document API error:', error);
      throw error;
    }
  },

  // Document Verification
  verifyDocument: async (
    document: string, 
    signature: string, 
    publicKey: string, 
    algorithmId: string,
    curveName: string
  ): Promise<VerifyResponse> => {
    try {
      // Get the algorithm to pass its name to the API
      let algorithmName = "";
      try {
        const algorithms = await apiService.getAlgorithms();
        const algorithm = algorithms.find(a => a.id === algorithmId);
        if (algorithm) {
          algorithmName = algorithm.name;
        }
      } catch (e) {
        console.error('Error getting algorithm name:', e);
      }

      if (!algorithmName) {
        // Fallback to mock data if needed
        const mockAlgo = MOCK_ALGORITHMS.find(a => a.id === algorithmId);
        algorithmName = mockAlgo?.name || "ECDSA";
      }

      // Hash the document according to the curve type - similar to signing process
      let hashedDocument = '';
      try {
        // Get curve parameters if available
        let curveParameters = null;
        
        // Try to find the curve parameters in our data
        for (const algoKey in MOCK_CURVES) {
          const curves = MOCK_CURVES[algoKey];
          const curve = curves.find(c => c.name === curveName);
          if (curve && curve.parameters) {
            curveParameters = curve.parameters;
            break;
          }
        }
        
        // Dynamically import the crypto module
        const cryptoModule = await import('./crypto');
        hashedDocument = await cryptoModule.calculateDocumentHash(document, curveName, curveParameters, true);
        console.log('Document hashed as integer for verification:', hashedDocument);
      } catch (err) {
        console.error('Error hashing document for verification:', err);
        throw new Error('Failed to hash document for verification');
      }

      console.log(`Verifying document with algorithm: ${algorithmName}, curve: ${curveName}`);
      const response = await fetch(`${API_BASE_URL}/verify`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document: hashedDocument,
          signature: signature,
          public_key: publicKey,
          algorithm_name: algorithmName,
          curve_name: curveName
        }),
      });

      const data = await handleFetchResponse<any>(response);
      console.log('Verification response:', data);
      
      // Determine if the response matches our expected format
      // If it doesn't have the verification field, but has other fields, map it to our format
      if (data.verification === undefined && data.is_valid !== undefined) {
        return {
          verification: data.is_valid,
          meta_data: {
            document: data.document_hash || hashedDocument,
            public_key: publicKey,
            curve_name: curveName,
            bit_size: 256, // default
            verification_id: data.verification_id,
            verification_time: data.verification_time
          }
        };
      }

      // Return the data directly if it matches our interface
      return data;
    } catch (error) {
      console.error('Verify document API error:', error);
      throw error;
    }
  },
}; 