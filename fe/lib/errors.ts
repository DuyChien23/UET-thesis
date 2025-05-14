/**
 * Custom API error class
 */
export class ApiError extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Check if an error is an instance of ApiError
 */
export function isApiError(error: any): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Get a user-friendly error message from an API error
 */
export function getErrorMessage(error: any): string {
  if (isApiError(error)) {
    switch (error.status) {
      case 400:
        return error.data?.message || 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 422:
        return error.data?.message || 'Validation failed. Please check your input.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  }

  if (error instanceof Error) {
    // Check if it's a network error
    if (error.message === 'Failed to fetch' || error.message.includes('NetworkError')) {
      return 'Network error. Please check your connection.';
    }
    return error.message;
  }

  return 'An unexpected error occurred.';
}

/**
 * Transform fetch response errors into ApiError objects
 */
export async function handleFetchResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { message: 'An error occurred' };
    }
    
    throw new ApiError(
      errorData.message || `API error: ${response.status}`,
      response.status,
      errorData
    );
  }
  
  return await response.json() as T;
} 