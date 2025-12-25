<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50">
    <!-- Header -->
    <header class="border-b border-warm-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <NuxtLink to="/plate" class="flex items-center gap-3">
          <PlateIcon :size="40" />
          <h1 class="text-2xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
            Busyplates
          </h1>
        </NuxtLink>
        <button
          @click="logout"
          class="px-4 py-2 text-warm-700 font-medium hover:text-red-600 transition-colors"
        >
          Logout
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-2xl mx-auto px-4 py-12">
      <div class="text-center mb-8">
        <h2 class="text-4xl font-bold text-warm-900 mb-2">Account Settings</h2>
        <p class="text-warm-600">Manage your Busyplates account</p>
      </div>

      <!-- Profile Section -->
      <div class="card p-8 mb-6">
        <h3 class="text-xl font-bold text-warm-900 mb-6">Profile Information</h3>

        <form @submit.prevent="updateProfile" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-warm-700 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="profileForm.username"
              type="text"
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
              v-model="profileForm.email"
              type="email"
              class="input-field"
              placeholder="your@email.com"
            />
            <p class="text-xs text-warm-500 mt-1">
              Changing your email will require verification
            </p>
          </div>

          <div>
            <label for="display-name" class="block text-sm font-medium text-warm-700 mb-2">
              Display Name <span class="text-warm-400">(Optional)</span>
            </label>
            <input
              id="display-name"
              v-model="profileForm.display_name"
              type="text"
              class="input-field"
              placeholder="John Doe"
            />
          </div>

          <div v-if="profileError" class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {{ profileError }}
          </div>

          <div v-if="profileSuccess" class="text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg p-3">
            {{ profileSuccess }}
          </div>

          <button
            type="submit"
            :disabled="profileLoading"
            class="btn-primary w-full"
          >
            {{ profileLoading ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- Change Password Section -->
      <div class="card p-8 mb-6">
        <h3 class="text-xl font-bold text-warm-900 mb-6">Change Password</h3>

        <form @submit.prevent="changePassword" class="space-y-6">
          <div>
            <label for="current-password" class="block text-sm font-medium text-warm-700 mb-2">
              Current Password
            </label>
            <input
              id="current-password"
              v-model="passwordForm.currentPassword"
              type="password"
              class="input-field"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label for="new-password" class="block text-sm font-medium text-warm-700 mb-2">
              New Password
            </label>
            <input
              id="new-password"
              v-model="passwordForm.newPassword"
              type="password"
              class="input-field"
              placeholder="••••••••"
            />
            <p class="text-xs text-warm-500 mt-1">
              At least 6 characters
            </p>
          </div>

          <div v-if="passwordError" class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {{ passwordError }}
          </div>

          <div v-if="passwordSuccess" class="text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg p-3">
            {{ passwordSuccess }}
          </div>

          <button
            type="submit"
            :disabled="passwordLoading"
            class="btn-primary w-full"
          >
            {{ passwordLoading ? 'Changing...' : 'Change Password' }}
          </button>
        </form>
      </div>

      <!-- Danger Zone -->
      <div class="bg-white border-2 border-red-200 rounded-xl shadow-sm p-8">
        <h3 class="text-xl font-bold text-red-600 mb-4">Danger Zone</h3>
        <p class="text-warm-600 mb-6">
          Once you delete your account, there is no going back. This action cannot be undone.
        </p>

        <button
          @click="showDeleteConfirm = true"
          class="px-6 py-2.5 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-all shadow-md"
        >
          Delete Account
        </button>
      </div>

      <!-- Delete Confirmation Modal -->
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click="showDeleteConfirm = false"
      >
        <div
          class="card p-8 max-w-md w-full"
          @click.stop
        >
          <h3 class="text-2xl font-bold text-red-600 mb-4">Delete Account</h3>
          <p class="text-warm-600 mb-6">
            Are you absolutely sure? This action cannot be undone. All your saved items will be permanently deleted.
          </p>

          <form @submit.prevent="deleteAccount" class="space-y-6">
            <div>
              <label for="delete-password" class="block text-sm font-medium text-warm-700 mb-2">
                Enter your password to confirm
              </label>
              <input
                id="delete-password"
                v-model="deleteForm.password"
                type="password"
                class="input-field"
                placeholder="••••••••"
                required
              />
            </div>

            <div v-if="deleteError" class="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
              {{ deleteError }}
            </div>

            <div class="flex gap-3">
              <button
                type="button"
                @click="showDeleteConfirm = false"
                class="flex-1 px-6 py-2.5 bg-white text-warm-700 border border-warm-300 rounded-xl font-semibold hover:bg-warm-100 transition-all shadow-sm"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="deleteLoading"
                class="flex-1 px-6 py-2.5 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-all disabled:opacity-50 shadow-md"
              >
                {{ deleteLoading ? 'Deleting...' : 'Delete Forever' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { user, logout, fetchUser } = useAuth()
const router = useRouter()
const config = useRuntimeConfig()

// Profile form
const profileForm = ref({
  username: '',
  email: '',
  display_name: ''
})
const profileLoading = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

// Password form
const passwordForm = ref({
  currentPassword: '',
  newPassword: ''
})
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// Delete account
const showDeleteConfirm = ref(false)
const deleteForm = ref({
  password: ''
})
const deleteLoading = ref(false)
const deleteError = ref('')

// Load user data
onMounted(async () => {
  await fetchUser()
  if (user.value) {
    profileForm.value = {
      username: user.value.username,
      email: user.value.email,
      display_name: user.value.display_name || ''
    }
  }
})

// Update profile
const updateProfile = async () => {
  profileError.value = ''
  profileSuccess.value = ''
  profileLoading.value = true

  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        username: profileForm.value.username,
        email: profileForm.value.email,
        display_name: profileForm.value.display_name || null
      })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update profile' }))
      throw new Error(error.detail || 'Failed to update profile')
    }

    await fetchUser()
    profileSuccess.value = 'Profile updated successfully!'
    setTimeout(() => {
      profileSuccess.value = ''
    }, 3000)
  } catch (err: any) {
    profileError.value = err.message || 'Failed to update profile'
  } finally {
    profileLoading.value = false
  }
}

// Change password
const changePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  passwordLoading.value = true

  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword
      })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to change password' }))
      throw new Error(error.detail || 'Failed to change password')
    }

    passwordSuccess.value = 'Password changed successfully!'
    passwordForm.value = { currentPassword: '', newPassword: '' }
    setTimeout(() => {
      passwordSuccess.value = ''
    }, 3000)
  } catch (err: any) {
    passwordError.value = err.message || 'Failed to change password'
  } finally {
    passwordLoading.value = false
  }
}

// Delete account
const deleteAccount = async () => {
  deleteError.value = ''
  deleteLoading.value = true

  try {
    const response = await fetch(`${config.public.apiUrl}/api/account/delete`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        password: deleteForm.value.password
      })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete account' }))
      throw new Error(error.detail || 'Failed to delete account')
    }

    // Account deleted, redirect to landing page
    await logout()
    router.push('/')
  } catch (err: any) {
    deleteError.value = err.message || 'Failed to delete account'
  } finally {
    deleteLoading.value = false
  }
}
</script>
