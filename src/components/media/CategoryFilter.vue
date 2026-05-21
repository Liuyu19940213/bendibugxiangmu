<script setup lang="ts">
import { computed } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { ImageCategory, BgmStyle, CopyGenre } from '@/types'
import Button from '@/components/ui/Button.vue'

const mediaStore = useMediaStore()

const typeCategories = [
  { label: '全部', value: 'all' as const },
  { label: '图片', value: 'image' as const },
  { label: 'BGM', value: 'bgm' as const },
  { label: '文案', value: 'copy' as const },
]

const sourceCategories = [
  { label: '全部来源', value: 'all' as const },
  { label: '本地上传', value: 'upload' as const },
  { label: 'AI 生成', value: 'ai' as const },
  { label: '预设素材', value: 'preset' as const },
]

const imageCategories: Array<{ label: string; value: ImageCategory | 'all' }> = [
  { label: '全部分类', value: 'all' },
  { label: '自然风景', value: '自然风景' },
  { label: '演播室', value: '演播室' },
  { label: '书房', value: '书房' },
  { label: '抽象意境', value: '抽象意境' },
  { label: '未分类', value: '未分类' },
]

const bgmStyles: Array<{ label: string; value: BgmStyle | 'all' }> = [
  { label: '全部风格', value: 'all' },
  { label: '激昂', value: '激昂' },
  { label: '宁静', value: '宁静' },
]

const copyGenres: Array<{ label: string; value: CopyGenre | 'all' }> = [
  { label: '全部题材', value: 'all' },
  { label: '书籍', value: '书籍' },
  { label: '播客', value: '播客' },
  { label: '口播', value: '口播' },
  { label: '访谈', value: '访谈' },
  { label: '自定义', value: '自定义' },
]

const showImageCategory = computed(() => mediaStore.filter.type === 'all' || mediaStore.filter.type === 'image')
const showBgmStyle = computed(() => mediaStore.filter.type === 'all' || mediaStore.filter.type === 'bgm')
const showCopyGenre = computed(() => mediaStore.filter.type === 'all' || mediaStore.filter.type === 'copy')

function setType(type: 'all' | 'image' | 'bgm' | 'copy') {
  mediaStore.setFilter({ type })
}

function setSource(source: 'all' | 'upload' | 'ai' | 'preset') {
  mediaStore.setFilter({ source })
}

function setCategory(category: ImageCategory | 'all') {
  mediaStore.setFilter({ category })
}

function setBgmStyle(style: BgmStyle | 'all') {
  mediaStore.setFilter({ bgmStyle: style })
}

function setGenre(genre: CopyGenre | 'all') {
  mediaStore.setFilter({ genre })
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div>
      <p class="text-sm font-medium text-muted-foreground mb-2">素材类型</p>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="cat in typeCategories"
          :key="cat.value"
          :variant="mediaStore.filter.type === cat.value ? 'default' : 'outline'"
          size="sm"
          @click="setType(cat.value)"
        >
          {{ cat.label }}
        </Button>
      </div>
    </div>

    <div>
      <p class="text-sm font-medium text-muted-foreground mb-2">来源</p>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="cat in sourceCategories"
          :key="cat.value"
          :variant="mediaStore.filter.source === cat.value ? 'default' : 'outline'"
          size="sm"
          @click="setSource(cat.value)"
        >
          {{ cat.label }}
        </Button>
      </div>
    </div>

    <div v-if="showImageCategory">
      <p class="text-sm font-medium text-muted-foreground mb-2">图片分类</p>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="cat in imageCategories"
          :key="cat.value"
          :variant="mediaStore.filter.category === cat.value ? 'default' : 'outline'"
          size="sm"
          @click="setCategory(cat.value)"
        >
          {{ cat.label }}
        </Button>
      </div>
    </div>

    <div v-if="showBgmStyle">
      <p class="text-sm font-medium text-muted-foreground mb-2">BGM 风格</p>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="style in bgmStyles"
          :key="style.value"
          :variant="mediaStore.filter.bgmStyle === style.value ? 'default' : 'outline'"
          size="sm"
          @click="setBgmStyle(style.value)"
        >
          {{ style.label }}
        </Button>
      </div>
    </div>

    <div v-if="showCopyGenre">
      <p class="text-sm font-medium text-muted-foreground mb-2">文案题材</p>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="genre in copyGenres"
          :key="genre.value"
          :variant="mediaStore.filter.genre === genre.value ? 'default' : 'outline'"
          size="sm"
          @click="setGenre(genre.value)"
        >
          {{ genre.label }}
        </Button>
      </div>
    </div>
  </div>
</template>
