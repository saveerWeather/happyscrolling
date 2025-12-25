<template>
  <div class="min-h-screen bg-gradient-to-b from-cream-50 to-cream-100">
    <!-- Modern Header -->
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-warm-200/60 shadow-sm">
      <div class="max-w-5xl mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <!-- Logo/Brand -->
          <div class="flex items-center gap-3">
            <PlateIcon :size="40" />
            <div>
              <h1 class="text-xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
                Busyplates
              </h1>
              <p class="text-xs text-warm-500">Your Plate</p>
            </div>
          </div>

          <!-- Navigation -->
          <nav class="flex items-center gap-2">
            <NuxtLink
              to="/account"
              class="px-4 py-2 text-sm font-medium text-warm-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all"
            >
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Account
              </div>
            </NuxtLink>
            <button
              @click="logout"
              class="px-4 py-2 text-sm font-medium text-warm-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
            >
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </div>
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Plate Container -->
    <main class="max-w-2xl mx-auto px-4 py-4">
      <PlateList />
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { logout, fetchUser } = useAuth()

onMounted(async () => {
  await fetchUser()
})
</script>

<style scoped>
/* Custom scrollbar for modern look */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: var(--neutral-300);
  border-radius: 4px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: var(--neutral-500);
}
</style>
