/** Feed composable */
import { api } from '~/utils/api'

export interface FeedItem {
  id: number
  sender_email: string
  core_link: string
  received_date: string
  processed_date: string
  preview: {
    title?: string | null
    description?: string | null
    image_url?: string | null
    site_name?: string | null
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
  const page = ref(1)
  const hasMore = ref(true)
  const total = ref(0)

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
      
      const response = await api.get<FeedResponse>(`/api/feed?${params.toString()}`)
      
      if (reset) {
        items.value = response.items
      } else {
        items.value.push(...response.items)
      }
      
      hasMore.value = response.has_more
      total.value = response.total
      page.value += 1
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

  return {
    items,
    loading,
    hasMore,
    total,
    fetchFeed,
    loadMore,
  }
}

