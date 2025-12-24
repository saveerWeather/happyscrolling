<template>
  <div>
    <div v-if="loading && items.length === 0" class="text-center py-12 text-gray-600">
      Loading feed...
    </div>
    
    <div v-else-if="items.length === 0" class="text-center py-12">
      <p class="text-gray-600 mb-4">No feed items yet.</p>
      <p class="text-sm text-gray-500">
        Add email addresses in <NuxtLink to="/settings" class="text-blue-600 hover:underline">Settings</NuxtLink> to see links sent from those addresses.
      </p>
    </div>
    
    <div v-else class="space-y-4">
      <FeedCard
        v-for="item in items"
        :key="item.id"
        :item="item"
      />
      
      <div v-if="hasMore" class="text-center py-8">
        <button
          @click="loadMore"
          :disabled="loading"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? 'Loading...' : 'Load More' }}
        </button>
      </div>
      
      <div v-else-if="items.length > 0" class="text-center py-8 text-gray-500 text-sm">
        No more items to load
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { items, loading, hasMore, fetchFeed, loadMore } = useFeed()

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

