"use client"

import { useState, useCallback } from 'react';
import { apiService } from '@/lib/api';

/**
 * Custom hook for making API requests with automatic loading state management
 */
export function useApi() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Make a GET request to the specified endpoint
   */
  const get = useCallback(async <T>(endpoint: string): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchData(endpoint, { method: 'GET' });
      return response as T;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Make a POST request to the specified endpoint
   */
  const post = useCallback(async <T>(endpoint: string, data: any): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchData(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return response as T;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Make a PUT request to the specified endpoint
   */
  const put = useCallback(async <T>(endpoint: string, data: any): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchData(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return response as T;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Make a DELETE request to the specified endpoint
   */
  const del = useCallback(async <T>(endpoint: string): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchData(endpoint, { method: 'DELETE' });
      return response as T;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Make a PATCH request to the specified endpoint
   */
  const patch = useCallback(async <T>(endpoint: string, data: any): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchData(endpoint, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return response as T;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    get,
    post,
    put,
    del,
    patch,
  };
} 