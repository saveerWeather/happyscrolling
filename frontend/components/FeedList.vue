<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading && items.length === 0" class="text-center py-16">
      <div class="inline-flex items-center gap-3 text-slate-600">
        <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="font-medium">Loading your feed</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="text-center py-20">
      <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold text-slate-900 mb-2">No feed items yet</h3>
      <p class="text-sm text-slate-500 mb-6 max-w-sm mx-auto">
        Add email addresses in Settings to start seeing links sent from those addresses.
      </p>
      <NuxtLink to="/settings" class="btn-primary inline-block">
        Go to Settings
      </NuxtLink>
    </div>

    <!-- Feed items -->
    <div v-else class="space-y-4">
      <FeedCard
        v-for="item in items"
        :key="item.id"
        :item="item"
      />

      <!-- Load more button -->
      <div v-if="hasMore" class="text-center py-8">
        <button
          @click="loadMore"
          :disabled="loading"
          class="btn-primary"
        >
          <span v-if="loading" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
          </span>
          <span v-else>Load More</span>
        </button>
      </div>

      <!-- End of feed -->
      <div v-else-if="items.length > 0" class="text-center py-12">
        <div class="inline-flex items-center gap-2 text-sm text-slate-400">
          <div class="h-px w-8 bg-slate-300"></div>
          <span>You're all caught up!</span>
          <div class="h-px w-8 bg-slate-300"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { items, loading, loadingPreviews, hasMore, fetchFeed, loadMore } = useFeed()

onMounted(async () => {
  await fetchFeed(true)
})

// Infinite scroll (optional - can use intersection observer)
const handleScroll = () => {
  if (hasMore.value && !loading.value) {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const windowHeight = window.innerHeight
    const documentHeight = document.documentElement.scrollHeight
    
    if (scrollTop + windowHeight >= documentHeight - 200) {
      loadMore()
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

