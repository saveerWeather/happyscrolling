<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <PlateIcon :size="80" class="mx-auto mb-4" />
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
          Reset Password
        </h1>
        <p class="text-warm-500 mt-2">Enter your email to receive a reset link</p>
      </div>

      <!-- Forgot Password Form -->
      <div class="card p-8">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-warm-700 mb-2">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="input-field"
              placeholder="your@email.com"
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
            {{ loading ? 'Sending...' : 'Send Reset Link' }}
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-warm-600">
        Remember your password?
        <NuxtLink to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
          Log in
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const email = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const config = useRuntimeConfig()

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/request-password-reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email.value })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to send reset link' }))
      throw new Error(errorData.detail || 'Failed to send reset link')
    }

    success.value = 'Password reset link sent! Check your email.'
    email.value = ''
  } catch (err: any) {
    error.value = err.message || 'Failed to send reset link'
  } finally {
    loading.value = false
  }
}
</script>
