<script setup lang="ts">
import { useBatchStore } from '@/stores/batch'
import { computed } from 'vue'
import type { GlobalConfig } from '@/types'
import ModuleCard from '@/components/batch/ModuleCard.vue'
import { Library } from 'lucide-vue-next'

const batchStore = useBatchStore()

const sortedModules = computed(() =>
  [...batchStore.modules].sort((a, b) => a.bookName.localeCompare(b.bookName, 'zh')),
)
</script>

<template>
  <!-- 空状态 -->
  <div
    v-if="batchStore.modules.length === 0"
    class="flex flex-col items-center justify-center py-20 text-muted-foreground"
  >
    <Library class="h-16 w-16 mb-4" />
    <p class="text-lg">还没有添加任何书籍</p>
    <p class="text-sm mt-1">导入 TXT 或点击下方按钮手动添加</p>
  </div>

  <!-- 卡片网格 -->
  <div
    v-else
    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4"
  >
    <ModuleCard
      v-for="m in sortedModules"
      :key="m.id"
      :module="m"
      @remove="batchStore.removeModule"
      @update:override="(override: Partial<GlobalConfig>) => batchStore.syncByName(m.bookName, override)" />
  </div>
</template>
