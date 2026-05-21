<template>
  <header class="flex h-14 shrink-0 items-center justify-between border-b border-border px-6">
    <h1 class="text-sm font-medium text-foreground">Pixelle-Video</h1>
    <div class="flex items-center gap-2">
      <span
        class="inline-block h-2.5 w-2.5 rounded-full"
        :class="connected ? 'bg-green-500' : 'bg-red-500'"
      />
      <span class="text-xs text-muted-foreground">
        {{ connected ? "Python 已连接" : "Python 未连接" }}
      </span>
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ connected?: boolean }>(), {
  connected: false,
});
</script>
