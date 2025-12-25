<template>
  <div class="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-sage-50">
    <!-- Header -->
    <header class="border-b border-warm-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <PlateIcon :size="40" />
          <h1 class="text-2xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
            Busyplates
          </h1>
        </div>
        <div class="flex items-center gap-3">
          <NuxtLink to="/login" class="px-4 py-2 text-warm-700 font-medium hover:text-primary-600 transition-colors">
            Log in
          </NuxtLink>
          <NuxtLink to="/register" class="btn-primary">
            Sign up
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="max-w-6xl mx-auto px-4 py-20">
      <div class="text-center mb-16">
        <div class="flex justify-center mb-8">
          <PlateIcon :size="120" />
        </div>

        <h2 class="text-5xl md:text-6xl font-bold text-warm-900 mb-6">
          Too much on your plate?
        </h2>

        <p class="text-xl md:text-2xl text-warm-600 mb-4">
          Save it for later.
        </p>

        <p class="text-lg text-warm-500 max-w-2xl mx-auto mb-12">
          Forward links to your Busyplates inbox. We'll organize them into a clean,
          distraction-free feed you can browse when you're ready.
        </p>

        <NuxtLink to="/register" class="btn-primary text-lg px-8 py-4 inline-block">
          Get Started - It's Free
        </NuxtLink>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-3 gap-8 mt-20">
        <div class="card p-8 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
            <svg class="w-8 h-8 text-cream-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-warm-900 mb-3">Email to Save</h3>
          <p class="text-warm-600">
            Forward any link to your Busyplates email address. No app switching required.
          </p>
        </div>

        <div class="card p-8 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-warm-900 mb-3">Your Plate</h3>
          <p class="text-warm-600">
            All your links in one beautiful, ad-free feed. Add notes, stay organized.
          </p>
        </div>

        <div class="card p-8 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-primary-600 to-sage-500 flex items-center justify-center">
            <svg class="w-8 h-8 text-cream-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-warm-900 mb-3">Read Later</h3>
          <p class="text-warm-600">
            Browse at your own pace. Your plate will be waiting when you're ready.
          </p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-warm-200 mt-20 py-8">
      <div class="max-w-6xl mx-auto px-4 text-center text-warm-500">
        <p>&copy; 2025 Busyplates. Save it for later.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

// Redirect if already logged in
const { isAuthenticated } = useAuth()
if (isAuthenticated.value) {
  navigateTo('/plate')
}
</script>
