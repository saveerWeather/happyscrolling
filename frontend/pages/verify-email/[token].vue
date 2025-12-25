<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <PlateIcon :size="80" class="mx-auto mb-4" />
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
          Email Verification
        </h1>
      </div>

      <!-- Verification Status -->
      <div class="card p-8 text-center">
        <!-- Loading State -->
        <div v-if="loading" class="space-y-4">
          <div class="w-16 h-16 mx-auto rounded-full bg-primary-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-primary-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <p class="text-warm-600">Verifying your email...</p>
        </div>

        <!-- Success State -->
        <div v-else-if="success" class="space-y-4">
          <div class="w-16 h-16 mx-auto rounded-full bg-green-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-warm-900">Email Verified!</h2>
          <p class="text-warm-600">Your email has been successfully verified.</p>
          <NuxtLink to="/plate" class="btn-primary inline-block mt-4">
            Go to Your Plate
          </NuxtLink>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="space-y-4">
          <div class="w-16 h-16 mx-auto rounded-full bg-red-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-warm-900">Verification Failed</h2>
          <div class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {{ error }}
          </div>
          <p class="text-warm-500 text-sm">
            The verification link may have expired or is invalid.
          </p>
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
const config = useRuntimeConfig()

const token = route.params.token as string

const loading = ref(true)
const success = ref(false)
const error = ref('')

// Automatically verify on mount
onMounted(async () => {
  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/verify-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Verification failed' }))
      throw new Error(errorData.detail || 'Verification failed')
    }

    success.value = true
  } catch (err: any) {
    error.value = err.message || 'Failed to verify email'
  } finally {
    loading.value = false
  }
})
</script>
