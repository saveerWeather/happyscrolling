/** API client utilities */
export interface ApiResponse<T> {
  success?: boolean
  data?: T
  message?: string
}

function getApiUrl(): string {
  const config = useRuntimeConfig()
  if (import.meta.server) {
    // Server-side: can use internal Railway domain (backend.railway.internal)
    // This is faster and doesn't go through the public internet
    return config.apiUrl || config.public.apiUrl
  } else {
    // Client-side: MUST use public domain for CORS to work
    // Browser can't access Railway internal domains
    return config.public.apiUrl
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const API_URL = getApiUrl()
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Important for sessions
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || error.message || 'Request failed')
  }
  
  return response.json()
}

export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, data?: any) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    }),
  patch: <T>(endpoint: string, data?: any) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    }),
  delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
}

