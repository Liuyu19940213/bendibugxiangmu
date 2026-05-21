<script setup lang="ts">
import { computed } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { MediaItem, BgmStyle } from '@/types'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'

const emit = defineEmits<{
  delete: [id: string]
  preview: [item: MediaItem]
}>()

const mediaStore = useMediaStore()

const bgmItems = computed(() =>
  mediaStore.filteredItems.filter((i) => i.type === 'bgm'),
)

const bgmStyleLabel: Record<BgmStyle, string> = {
  '激昂': '激昂',
  '宁静': '宁静',
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '—'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div v-if="bgmItems.length === 0" class="flex flex-col items-center justify-center py-16 text-muted-foreground">
    <p>暂无 BGM，点击上方按钮上传</p>
  </div>

  <div v-else class="flex flex-col gap-2">
    <div
      v-for="item in bgmItems"
      :key="item.id"
      class="flex items-center gap-3 rounded-lg border bg-card p-3 transition-shadow hover:shadow-sm"
    >
      <!-- 播放按钮 -->
      <button
        class="h-8 w-8 shrink-0 flex items-center justify-center rounded-full bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
        @click="emit('preview', item)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z" />
        </svg>
      </button>

      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <p class="text-sm font-medium truncate">{{ item.name }}</p>
          <Badge v-if="item.bgmStyle" variant="secondary" size="sm">
            {{ bgmStyleLabel[item.bgmStyle] || item.bgmStyle }}
          </Badge>
        </div>
        <div class="flex items-center gap-3 mt-0.5 text-xs text-muted-foreground">
          <span>{{ formatFileSize(item.fileSize) }}</span>
          <span v-if="item.fadeIn">淡入 {{ item.fadeIn }}s</span>
          <span v-if="item.fadeOut">淡出 {{ item.fadeOut }}s</span>
        </div>
      </div>

      <Button
        variant="ghost"
        size="icon"
        class="shrink-0 text-muted-foreground hover:text-destructive"
        @click="emit('delete', item.id)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
        </svg>
      </Button>
    </div>
  </div>
</template>
