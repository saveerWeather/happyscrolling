/** Feed composable */
import { api } from '~/utils/api'

export interface FeedItem {
  id: number
  sender_email: string
  core_link: string
  received_date: string
  processed_date: string
  notes?: string | null
  preview: {
    title?: string | null
    description?: string | null
    image_url?: string | null
    site_name?: string | null
    text_content?: string | null
    images?: string[] | null
    author?: string | null
    platform?: string | null
    subreddit?: string | null
    published_time?: string | null
    embed_html?: string | null
    embeddable?: boolean | null
  } | null
}

export interface FeedResponse {
  items: FeedItem[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

export const useFeed = () => {
  const items = ref<FeedItem[]>([])
  const loading = ref(false)
  const loadingPreviews = ref(false)
  const page = ref(1)
  const hasMore = ref(true)
  const total = ref(0)
  const previewCache = new Map<string, FeedItem['preview']>()

  const fetchPreview = async (url: string, itemId: number): Promise<void> => {
    try {
      // Check cache first
      if (previewCache.has(url)) {
        const cachedPreview = previewCache.get(url)
        const item = items.value.find(i => i.id === itemId)
        if (item) {
          item.preview = cachedPreview
        }
        return
      }

      // Fetch preview
      const preview = await api.get<FeedItem['preview']>(
        `/api/feed/preview?url=${encodeURIComponent(url)}`
      )
      
      // Cache it
      previewCache.set(url, preview)
      
      // Update the item
      const item = items.value.find(i => i.id === itemId)
      if (item) {
        item.preview = preview
      }
    } catch (error) {
      console.error(`Error fetching preview for ${url}:`, error)
      // Don't throw - just log the error, item will show without preview
    }
  }

  const fetchPreviewsForItems = async (newItems: FeedItem[]) => {
    loadingPreviews.value = true
    
    try {
      // Fetch all previews in parallel (but limit concurrency to avoid overwhelming the server)
      const BATCH_SIZE = 5
      for (let i = 0; i < newItems.length; i += BATCH_SIZE) {
        const batch = newItems.slice(i, i + BATCH_SIZE)
        await Promise.allSettled(
          batch.map(item => fetchPreview(item.core_link, item.id))
        )
        // Small delay between batches to avoid rate limiting
        if (i + BATCH_SIZE < newItems.length) {
          await new Promise(resolve => setTimeout(resolve, 100))
        }
      }
    } finally {
      loadingPreviews.value = false
    }
  }

  const fetchFeed = async (reset = false, emailFilter?: string) => {
    if (loading.value) return
    
    loading.value = true
    
    try {
      if (reset) {
        page.value = 1
        items.value = []
      }
      
      const params = new URLSearchParams({
        page: page.value.toString(),
        limit: '20',
      })
      
      if (emailFilter) {
        params.append('email', emailFilter)
      }
      
      // Fetch items immediately (without waiting for previews)
      const response = await api.get<FeedResponse>(`/api/feed?${params.toString()}`)
      
      const newItems = reset ? response.items : [...items.value, ...response.items]
      
      if (reset) {
        items.value = response.items
      } else {
        items.value.push(...response.items)
      }
      
      hasMore.value = response.has_more
      total.value = response.total
      page.value += 1
      
      // Fetch previews asynchronously after items are loaded
      // Don't await - let it run in background
      fetchPreviewsForItems(response.items).catch(err => {
        console.error('Error fetching previews:', err)
      })
    } catch (error) {
      console.error('Error fetching feed:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadMore = () => {
    if (hasMore.value && !loading.value) {
      fetchFeed(false)
    }
  }

  const deleteFeedItem = async (itemId: number) => {
    try {
      await api.delete(`/api/feed/${itemId}`)

      // Remove from local state
      items.value = items.value.filter(item => item.id !== itemId)
      total.value -= 1
    } catch (error) {
      console.error('Error deleting feed item:', error)
      throw error
    }
  }

  const updateNotes = async (itemId: number, notes: string) => {
    try {
      const response = await api.patch<FeedItem>(
        `/api/feed/${itemId}`,
        { notes }
      )

      // Update local state
      const item = items.value.find(i => i.id === itemId)
      if (item) {
        item.notes = response.notes
      }
    } catch (error) {
      console.error('Error updating notes:', error)
      throw error
    }
  }

  return {
    items,
    loading,
    loadingPreviews,
    hasMore,
    total,
    fetchFeed,
    loadMore,
    deleteFeedItem,
    updateNotes,
  }
}

