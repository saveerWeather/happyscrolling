<template>
  <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
    <a
      :href="item.core_link"
      target="_blank"
      rel="noopener noreferrer"
      class="block"
    >
      <div v-if="item.preview?.image_url" class="w-full h-48 overflow-hidden bg-gray-200">
        <img
          :src="item.preview.image_url"
          :alt="item.preview.title || 'Link preview'"
          class="w-full h-full object-cover"
          @error="imageError = true"
        />
      </div>
      
      <div class="p-6">
        <div class="flex items-start justify-between mb-2">
          <div class="flex-1">
            <h3 class="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
              {{ item.preview?.title || item.core_link }}
            </h3>
            <p v-if="item.preview?.description" class="text-gray-600 text-sm mb-3 line-clamp-2">
              {{ item.preview.description }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center justify-between text-sm text-gray-500">
          <div class="flex items-center gap-2">
            <span v-if="item.preview?.site_name" class="font-medium">
              {{ item.preview.site_name }}
            </span>
            <span v-else class="truncate max-w-xs">
              {{ getHostname(item.core_link) }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs">{{ item.sender_email }}</span>
            <span>{{ formatDate(item.received_date) }}</span>
          </div>
        </div>
      </div>
    </a>
  </article>
</template>

<script setup lang="ts">
import type { FeedItem } from '~/composables/useFeed'

interface Props {
  item: FeedItem
}

const props = defineProps<Props>()
const imageError = ref(false)

const getHostname = (url: string) => {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 7) {
    return date.toLocaleDateString()
  } else if (days > 0) {
    return `${days}d ago`
  } else if (hours > 0) {
    return `${hours}h ago`
  } else if (minutes > 0) {
    return `${minutes}m ago`
  } else {
    return 'Just now'
  }
}
</script>

