<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    :class="className"
  >
    <!-- Outer rim -->
    <circle cx="12" cy="12" r="10" fill="url(#plateGradient)" stroke="#b55533" stroke-width="0.5"/>
    <!-- Inner plate surface -->
    <circle cx="12" cy="12" r="7.5" fill="#faf8f3" opacity="0.9"/>
    <!-- Rim highlight -->
    <path d="M 12 2 A 10 10 0 0 1 22 12" stroke="#d97556" stroke-width="1" fill="none" opacity="0.5"/>

    <defs>
      <linearGradient id="plateGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#d97556;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#b55533;stop-opacity:1" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
interface Props {
  size?: number
  className?: string
}

withDefaults(defineProps<Props>(), {
  size: 24,
  className: ''
})
</script>
