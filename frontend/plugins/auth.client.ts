/** Auth plugin - restore session on page load (client-side only) */
export default defineNuxtPlugin(async () => {
  const { fetchUser } = useAuth()

  // Try to restore session from cookie on every page load
  await fetchUser()
})
