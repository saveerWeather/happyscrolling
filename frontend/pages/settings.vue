<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <NuxtLink to="/" class="text-gray-600 hover:text-gray-900">
          Back to Feed
        </NuxtLink>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-6 text-gray-900">Linked Email Addresses</h2>
        
        <p class="text-sm text-gray-600 mb-4">
          Add email addresses to see links sent from those addresses in your feed.
        </p>

        <form @submit.prevent="handleAddEmail" class="mb-6">
          <div class="flex gap-2">
            <input
              v-model="newEmail"
              type="email"
              required
              placeholder="email@example.com"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              :disabled="adding"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {{ adding ? 'Adding...' : 'Add Email' }}
            </button>
          </div>
          <div v-if="addError" class="mt-2 text-red-600 text-sm">
            {{ addError }}
          </div>
        </form>

        <div v-if="loading" class="text-gray-600">Loading...</div>
        <div v-else-if="emails.length === 0" class="text-gray-500 text-sm">
          No linked emails yet. Add one above to get started.
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="email in emails"
            :key="email.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div>
              <p class="font-medium text-gray-900">{{ email.email_address }}</p>
              <p class="text-sm text-gray-500">
                {{ email.verified ? 'Verified' : 'Not verified' }}
              </p>
            </div>
            <button
              @click="removeEmail(email.id)"
              :disabled="removing === email.id"
              class="px-4 py-2 text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
            >
              {{ removing === email.id ? 'Removing...' : 'Remove' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

interface UserEmail {
  id: number
  email_address: string
  verified: boolean
  created_at: string
}

const emails = ref<UserEmail[]>([])
const loading = ref(true)
const newEmail = ref('')
const adding = ref(false)
const addError = ref('')
const removing = ref<number | null>(null)

import { api } from '~/utils/api'

const fetchEmails = async () => {
  loading.value = true
  try {
    emails.value = await api.get<UserEmail[]>('/api/settings/emails')
  } catch (error) {
    console.error('Error fetching emails:', error)
  } finally {
    loading.value = false
  }
}

const handleAddEmail = async () => {
  addError.value = ''
  adding.value = true
  
  try {
    const newEmailData = await api.post<UserEmail>('/api/settings/emails', {
      email_address: newEmail.value
    })
    emails.value.push(newEmailData)
    newEmail.value = ''
  } catch (error: any) {
    addError.value = error.message || 'Failed to add email'
  } finally {
    adding.value = false
  }
}

const removeEmail = async (id: number) => {
  if (!confirm('Are you sure you want to remove this email?')) return
  
  removing.value = id
  try {
    await api.delete(`/api/settings/emails/${id}`)
    emails.value = emails.value.filter(e => e.id !== id)
  } catch (error) {
    console.error('Error removing email:', error)
    alert('Failed to remove email')
  } finally {
    removing.value = null
  }
}

onMounted(() => {
  fetchEmails()
})
</script>

