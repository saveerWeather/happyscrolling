<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
// Restore user session on app load
const { fetchUser } = useAuth()

onMounted(async () => {
  await fetchUser()
})
</script>

