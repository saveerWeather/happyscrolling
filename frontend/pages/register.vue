<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <PlateIcon :size="80" class="mx-auto mb-4" />
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
          Join Busyplates
        </h1>
        <p class="text-warm-500 mt-2">Save it for later</p>
      </div>

      <!-- Register Form -->
      <div class="card p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-warm-700 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              class="input-field"
              placeholder="johndoe"
            />
          </div>

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
            <p class="text-xs text-warm-500 mt-1">
              We'll send you a verification email
            </p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-warm-700 mb-2">
              Password
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

          <div v-if="error" class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full"
          >
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-warm-600">
        Already have an account?
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

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const { register } = useAuth()
const router = useRouter()

const handleRegister = async () => {
  error.value = ''
  loading.value = true

  try {
    await register({
      username: username.value,
      email: email.value,
      password: password.value
    })
    router.push('/plate')
  } catch (err: any) {
    error.value = err.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}

// Redirect if already logged in
const { isAuthenticated } = useAuth()
if (isAuthenticated.value) {
  navigateTo('/plate')
}
</script>
