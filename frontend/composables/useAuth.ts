/** Authentication composable */
import { api } from '~/utils/api'

export interface User {
  id: number
  username: string
  email: string
  email_verified: boolean
  created_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export const useAuth = () => {
  const authStore = useAuthStore()

  const login = async (credentials: LoginCredentials) => {
    const config = useRuntimeConfig()
    
    const response = await fetch(`${config.public.apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // Important for sessions
      body: JSON.stringify(credentials)
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Login failed')
    }
    
    const user = await response.json()
    authStore.setUser(user)
    
    return user
  }

  const register = async (data: RegisterData) => {
    const user = await api.post<User>('/api/auth/register', data)
    // Auto-login after registration
    await login({ email: data.email, password: data.password })
    return user
  }

  const logout = async () => {
    const config = useRuntimeConfig()
    try {
      await fetch(`${config.public.apiUrl}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch (error) {
      console.error('Logout error:', error)
    }
    authStore.setUser(null)
    navigateTo('/login')
  }

  const fetchUser = async () => {
    try {
      const config = useRuntimeConfig()
      const response = await fetch(`${config.public.apiUrl}/api/auth/me`, {
        method: 'GET',
        credentials: 'include' // Important for sessions
      })
      
      if (!response.ok) {
        throw new Error('Not authenticated')
      }
      
      const user = await response.json()
      authStore.setUser(user)
      return user
    } catch (error) {
      authStore.setUser(null)
      return null
    }
  }

  const isAuthenticated = computed(() => !!authStore.user)

  return {
    login,
    register,
    logout,
    fetchUser,
    isAuthenticated,
    user: computed(() => authStore.user)
  }
}

