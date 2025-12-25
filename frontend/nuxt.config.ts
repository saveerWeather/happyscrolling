// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  app: {
    head: {
      title: 'Busyplates - Save it for later',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Too much on your plate? Save it for later with Busyplates.'
        }
      ],
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

