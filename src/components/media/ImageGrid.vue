<script setup lang="ts">
import { computed } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { MediaItem } from '@/types'
import Badge from '@/components/ui/Badge.vue'

const emit = defineEmits<{
  preview: [item: MediaItem]
}>()

const mediaStore = useMediaStore()

const imageItems = computed(() =>
  mediaStore.filteredItems.filter((i) => i.type === 'image'),
)

function getSourceLabel(source: string): string {
  switch (source) {
    case 'ai': return 'AI'
    case 'preset': return '预设'
    case 'upload': return '上传'
    default: return source
  }
}

function getCooldownLabel(item: MediaItem): string | null {
  if (!item.lastUsedAt) return null
  const remaining = mediaStore.getCooldownRemaining(item)
  if (remaining > 0) return `冷却 ${remaining}天`
  return null
}
</script>

<template>
  <div v-if="imageItems.length === 0" class="flex flex-col items-center justify-center py-16 text-muted-foreground">
    <p>暂无图片，点击上方按钮上传</p>
  </div>

  <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <div
      v-for="item in imageItems"
      :key="item.id"
      class="group relative rounded-lg border bg-card overflow-hidden cursor-pointer transition-shadow hover:shadow-md"
      :class="{ 'opacity-60': mediaStore.isInCooldown(item) }"
      @click="emit('preview', item)"
    >
      <div class="aspect-square bg-muted">
        <img
          :src="item.path"
          :alt="item.name"
          class="h-full w-full object-cover"
        />
      </div>

      <!-- 来源标签 -->
      <Badge
        :variant="item.source === 'ai' ? 'default' : 'secondary'"
        class="absolute top-2 left-2 text-xs"
      >
        {{ getSourceLabel(item.source) }}
      </Badge>

      <!-- 冷却期标签 -->
      <Badge
        v-if="getCooldownLabel(item)"
        variant="destructive"
        class="absolute top-2 right-8 text-xs"
      >
        {{ getCooldownLabel(item) }}
      </Badge>

      <div class="p-2">
        <p class="text-sm truncate">{{ item.name }}</p>
        <div class="flex items-center gap-1 mt-1">
          <span class="text-xs text-muted-foreground">{{ item.category }}</span>
          <span v-if="item.kenBurns" class="text-xs px-1 bg-muted rounded">KB</span>
        </div>
      </div>

      <div class="absolute top-2 right-2" @click.stop>
        <input
          type="checkbox"
          :checked="mediaStore.selectedIds.has(item.id)"
          class="h-4 w-4 rounded border-gray-300"
          @change="mediaStore.toggleSelect(item.id)"
        />
      </div>
    </div>
  </div>
</template>
