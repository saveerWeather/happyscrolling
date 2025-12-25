<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <PlateIcon :size="80" class="mx-auto mb-4" />
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
          Set New Password
        </h1>
        <p class="text-warm-500 mt-2">Enter your new password below</p>
      </div>

      <!-- Reset Password Form -->
      <div class="card p-8">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="password" class="block text-sm font-medium text-warm-700 mb-2">
              New Password
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              minlength="6"
              class="input-field"
              placeholder="••••••••"
            />
            <p class="text-xs text-warm-500 mt-1">
              At least 6 characters
            </p>
          </div>

          <div>
            <label for="confirm-password" class="block text-sm font-medium text-warm-700 mb-2">
              Confirm Password
            </label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              type="password"
              required
              minlength="6"
              class="input-field"
              placeholder="••••••••"
            />
          </div>

          <div v-if="error" class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {{ error }}
          </div>

          <div v-if="success" class="text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg p-3">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full"
          >
            {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>
        </form>

        <div v-if="success" class="mt-4 text-center">
          <NuxtLink to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
            Go to Login
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const token = route.params.token as string

const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  error.value = ''
  success.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true

  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token: token,
        new_password: password.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to reset password' }))
      throw new Error(errorData.detail || 'Failed to reset password')
    }

    success.value = 'Password reset successfully! You can now log in.'
    password.value = ''
    confirmPassword.value = ''

    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.message || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>
