// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  app: {
    head: {
      title: 'Happy Scrolling',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }
      ]
    }
  },
  runtimeConfig: {
    // Server-side: can use internal Railway domain
    apiUrl: process.env.API_URL || process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000',
    // Client-side: must use public domain for CORS
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000'
    }
  },
  css: ['~/assets/css/main.css']
})

