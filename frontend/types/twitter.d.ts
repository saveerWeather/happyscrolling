// Type declarations for Twitter widgets
declare global {
  interface Window {
    twttr?: {
      widgets: {
        load: () => void
        createTweet: (id: string, element: HTMLElement, options?: any) => Promise<any>
      }
    }
  }
}

export {}

