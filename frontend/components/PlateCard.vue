<template>
  <article class="plate-card bg-white border border-warm-200/60 overflow-hidden hover:shadow-xl hover:shadow-warm-200/50 hover:border-warm-300/60 transition-all duration-300 hover:-translate-y-0.5">
    <!-- Card Header: Source/Author -->
    <div class="card-header px-4 py-3 flex items-center justify-between border-b border-warm-100">
      <div class="flex items-center gap-3">
        <!-- Avatar -->
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-cream-50 font-bold text-xs">
          {{ getInitials(getPosterName()) }}
        </div>

        <!-- Source info -->
        <div class="flex items-center gap-2 text-sm">
          <span class="font-semibold text-warm-900">{{ getPosterName() }}</span>
          <span
            v-if="item.preview?.platform"
            class="platform-badge-mini"
            :class="platformBadgeClass"
          >
            {{ getPlatformLabel(item.preview.platform) }}
          </span>
          <span class="text-warm-400">·</span>
          <span class="text-warm-500">{{ formatDate(item.received_date) }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- External link icon -->
        <a
          :href="item.core_link"
          target="_blank"
          rel="noopener noreferrer"
          class="text-warm-400 hover:text-warm-600 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>

        <!-- Delete button -->
        <button
          @click="handleDelete"
          class="text-warm-400 hover:text-red-600 transition-colors"
          title="Delete from Plate"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Card Content -->
    <a
      :href="item.core_link"
      target="_blank"
      rel="noopener noreferrer"
      class="block group"
    >
      <!-- Twitter/Reddit: Text first, then image -->
      <template v-if="item.preview?.platform === 'twitter' || item.preview?.platform === 'reddit'">
        <div v-if="item.preview?.text_content || item.preview?.title" class="px-4 py-3">
          <p class="text-[15px] text-warm-900 leading-relaxed">
            {{ item.preview.text_content || item.preview.title }}
          </p>
        </div>

        <div v-if="displayImage" class="w-full overflow-hidden">
          <img
            :src="displayImage"
            :alt="'Post image'"
            class="w-full h-auto max-h-[500px] object-cover"
            @error="handleImageError"
          />
        </div>
      </template>

      <!-- YouTube/Vimeo: Video embed + title -->
      <template v-else-if="(item.preview?.platform === 'youtube' || item.preview?.platform === 'vimeo') && item.preview?.embed_html">
        <div class="aspect-video bg-black" v-html="item.preview.embed_html"></div>
        <div v-if="item.preview?.title" class="px-4 py-3">
          <h3 class="font-semibold text-warm-900">{{ item.preview.title }}</h3>
          <p v-if="item.preview?.description" class="text-sm text-warm-600 mt-1 line-clamp-2">
            {{ item.preview.description }}
          </p>
        </div>
      </template>

      <!-- Articles: Image + title/description -->
      <template v-else-if="item.preview?.title || item.preview?.description || displayImage">
        <div v-if="displayImage" class="w-full overflow-hidden">
          <img
            :src="displayImage"
            :alt="item.preview?.title || 'Article image'"
            class="w-full h-auto max-h-[400px] object-cover group-hover:scale-[1.02] transition-transform duration-500"
            @error="handleImageError"
          />
        </div>

        <div class="px-4 py-3">
          <h3 v-if="item.preview?.title" class="text-lg font-bold text-warm-900 leading-snug line-clamp-3">
            {{ item.preview.title }}
          </h3>
          <p v-if="item.preview?.description" class="text-sm text-warm-600 mt-2 line-clamp-2">
            {{ item.preview.description }}
          </p>
        </div>
      </template>

      <!-- No preview: Show the full link -->
      <template v-else>
        <div class="px-4 py-3">
          <p class="text-sm text-warm-600 break-all">
            {{ item.core_link }}
          </p>
        </div>
      </template>
    </a>

    <!-- Notes section -->
    <div class="px-4 py-3 border-t border-warm-100">
      <textarea
        v-model="localNotes"
        @input="handleNotesChange"
        placeholder="Add notes..."
        class="w-full px-3 py-2 text-sm border border-warm-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all resize-none bg-warm-100 focus:bg-white"
        rows="2"
      ></textarea>
      <div v-if="saveStatus" class="text-xs text-warm-400 mt-1">
        {{ saveStatus }}
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { FeedItem } from '~/composables/useFeed'

interface Props {
  item: FeedItem
}

const props = defineProps<Props>()
const { deleteFeedItem, updateNotes } = useFeed()
const imageErrors = ref<Set<string>>(new Set())
const localNotes = ref(props.item.notes || '')
const saveStatus = ref('')
let saveTimeout: NodeJS.Timeout | null = null

const hasPreviewData = computed(() => {
  const preview = props.item.preview
  if (!preview) return false
  return !!(
    preview.title ||
    preview.description ||
    preview.image_url ||
    preview.images?.length ||
    preview.text_content
  )
})

const getPosterName = () => {
  // Priority 1: Author (Twitter user, Reddit user, etc.)
  if (props.item.preview?.author) {
    return props.item.preview.author
  }

  // Priority 2: Site name (Washington Post, NYT, etc.)
  if (props.item.preview?.site_name) {
    return props.item.preview.site_name
  }

  // Priority 3: Hostname from URL
  return getHostname(props.item.core_link)
}

const getInitials = (name: string) => {
  if (name.includes('@')) {
    return name.split('@')[0].slice(0, 2).toUpperCase()
  }

  const words = name.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

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
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } else if (days > 0) {
    return `${days}d`
  } else if (hours > 0) {
    return `${hours}h`
  } else if (minutes > 0) {
    return `${minutes}m`
  } else {
    return 'now'
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img.src) {
    imageErrors.value.add(img.src)
  }
}

const displayImage = computed(() => {
  const preview = props.item.preview
  if (!preview) return null

  if (preview.images && preview.images.length > 0) {
    return preview.images[0]
  }

  if (preview.image_url && !imageErrors.value.has(preview.image_url)) {
    return preview.image_url
  }

  return null
})

const platformBadgeClass = computed(() => {
  const platform = props.item.preview?.platform
  switch (platform) {
    case 'twitter':
      return 'bg-sky-100 text-sky-700'
    case 'youtube':
      return 'bg-red-100 text-red-700'
    case 'reddit':
      return 'bg-orange-100 text-orange-700'
    case 'instagram':
      return 'bg-pink-100 text-pink-700'
    case 'tiktok':
      return 'bg-warm-900 text-white'
    default:
      return 'bg-warm-100 text-warm-600'
  }
})

const getPlatformLabel = (platform: string | null | undefined) => {
  if (!platform) return ''
  const labels: Record<string, string> = {
    twitter: '𝕏',
    youtube: 'YT',
    reddit: 'Reddit',
    instagram: 'IG',
    tiktok: 'TikTok',
    article: 'Article'
  }
  return labels[platform] || ''
}

const handleDelete = async () => {
  if (confirm('Remove this from your Plate?')) {
    try {
      await deleteFeedItem(props.item.id)
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Failed to remove. Please try again.')
    }
  }
}

const handleNotesChange = () => {
  saveStatus.value = 'Saving...'

  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }

  saveTimeout = setTimeout(async () => {
    try {
      await updateNotes(props.item.id, localNotes.value)
      saveStatus.value = 'Saved'
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    } catch (error) {
      console.error('Failed to save notes:', error)
      saveStatus.value = 'Failed to save'
    }
  }, 1000) // Debounce for 1 second
}

// Watch for prop changes
watch(() => props.item.notes, (newNotes) => {
  if (newNotes !== localNotes.value) {
    localNotes.value = newNotes || ''
  }
})
</script>

<style scoped>
.plate-card {
  @apply rounded-xl shadow-sm;
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.platform-badge-mini {
  @apply inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold tracking-wide;
}

:deep(iframe) {
  @apply w-full rounded-lg;
}

/* Smooth image loading */
.plate-card img {
  @apply bg-warm-100;
}
</style>
