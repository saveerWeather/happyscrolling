<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading && items.length === 0" class="text-center py-16">
      <div class="inline-flex items-center gap-3 text-warm-600">
        <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="font-medium">Loading your Plate...</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="text-center py-20">
      <PlateIcon :size="80" class="mx-auto mb-4 opacity-20" />
      <h3 class="text-lg font-semibold text-warm-900 mb-2">Your Plate is empty!</h3>
      <p class="text-sm text-warm-500 mb-6 max-w-sm mx-auto">
        Forward links to your Busyplates email to save them for later.
      </p>
      <NuxtLink to="/account" class="btn-primary inline-block">
        View Email Addresses
      </NuxtLink>
    </div>

    <!-- Plate items -->
    <div v-else class="space-y-4">
      <PlateCard
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
        <div class="inline-flex items-center gap-2 text-sm text-warm-400">
          <div class="h-px w-8 bg-warm-300"></div>
          <span>You're all caught up!</span>
          <div class="h-px w-8 bg-warm-300"></div>
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
