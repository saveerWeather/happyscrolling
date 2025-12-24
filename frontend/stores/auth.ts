/** Pinia auth store */
import { defineStore } from 'pinia'

export interface User {
  id: number
  username: string
  email: string
  email_verified: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.user,
  },
  
  actions: {
    setUser(user: User | null) {
      this.user = user
    },
  },
})

