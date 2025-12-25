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
    const apiUrl = config.public.apiUrl
    
    try {
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(credentials)
      })
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }))
        throw new Error(error.detail || 'Login failed')
      }
      
      const user = await response.json()
      authStore.setUser(user)
      
      return user
    } catch (error) {
      throw error
    }
  }

  const register = async (data: RegisterData) => {
    const user = await api.post<User>('/api/auth/register', data)
    authStore.setUser(user)
    return user
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/logout', {})
    } catch (error) {
      console.error('Logout error:', error)
    }
    authStore.setUser(null)
    navigateTo('/login')
  }

  const fetchUser = async () => {
    try {
      const user = await api.get<User>('/api/auth/me')
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

