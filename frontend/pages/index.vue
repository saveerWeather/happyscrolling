<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Happy Scrolling</h1>
        <div class="flex gap-4 items-center">
          <NuxtLink to="/settings" class="text-gray-600 hover:text-gray-900">
            Settings
          </NuxtLink>
          <button 
            @click="logout" 
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <FeedList />
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { logout, fetchUser } = useAuth()

// Fetch user on page load to restore session
onMounted(async () => {
  await fetchUser()
})
</script>

