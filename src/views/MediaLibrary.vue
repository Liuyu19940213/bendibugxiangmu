<script setup lang="ts">
import { ref } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { MediaItem } from '@/types'
import Tabs from '@/components/ui/Tabs.vue'
import TabsList from '@/components/ui/TabsList.vue'
import TabsTrigger from '@/components/ui/TabsTrigger.vue'
import TabsContent from '@/components/ui/TabsContent.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import CategoryFilter from '@/components/media/CategoryFilter.vue'
import ImageGrid from '@/components/media/ImageGrid.vue'
import ImageUploader from '@/components/media/ImageUploader.vue'
import ImageDetail from '@/components/media/ImageDetail.vue'
import BgmList from '@/components/media/BgmList.vue'
import BgmUploader from '@/components/media/BgmUploader.vue'
import { Image, Music } from 'lucide-vue-next'

const mediaStore = useMediaStore()

const activeTab = ref('image')
const searchKeyword = ref('')
const previewItem = ref<MediaItem | null>(null)
const detailOpen = ref(false)

function onSearchInput(value: string) {
  searchKeyword.value = value
  mediaStore.setFilter({ keyword: value })
}

function onPreview(item: MediaItem) {
  previewItem.value = item
  detailOpen.value = true
}

function onSaveDetail(item: MediaItem) {
  mediaStore.updateItem(item.id, item)
}

function onImageFilesSelected(files: File[]) {
  console.log('Image files selected:', files.map((f) => f.name))
}

function onBgmFilesSelected(files: File[]) {
  console.log('BGM files selected:', files.map((f) => f.name))
}

function onBgmDelete(id: string) {
  mediaStore.removeSelected()
}

function onBgmPreview(item: MediaItem) {
  console.log('Preview BGM:', item.name)
}
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- 顶部工具栏 -->
    <div class="flex items-center gap-3 border-b px-6 py-3">
      <Button variant="outline" size="sm" @click="mediaStore.selectAll()">
        全选
      </Button>
      <span class="text-sm text-muted-foreground">
        已选 {{ mediaStore.selectedIds.size }} 个
      </span>
      <Button
        variant="destructive"
        size="sm"
        :disabled="mediaStore.selectedIds.size === 0"
        @click="mediaStore.removeSelected()"
      >
        删除选中
      </Button>
      <div class="flex-1" />
      <span class="text-sm text-muted-foreground">
        共 {{ mediaStore.filteredItems.length }} 项
      </span>
    </div>

    <!-- 主体 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧分类筛选 -->
      <aside class="w-52 shrink-0 border-r p-4">
        <CategoryFilter />
        <div class="mt-4">
          <Input
            :model-value="searchKeyword"
            placeholder="搜索素材..."
            @update:model-value="onSearchInput"
          />
        </div>
      </aside>

      <!-- 右侧内容 -->
      <main class="flex-1 overflow-auto p-6">
        <Tabs v-model="activeTab" class="w-full">
          <TabsList class="mb-4">
            <TabsTrigger value="image" class="gap-2">
              <Image class="h-4 w-4" />
              图片库
            </TabsTrigger>
            <TabsTrigger value="bgm" class="gap-2">
              <Music class="h-4 w-4" />
              BGM 库
            </TabsTrigger>
          </TabsList>

          <TabsContent value="image">
            <div class="flex flex-col gap-4">
              <ImageUploader @files-selected="onImageFilesSelected" />
              <ImageGrid @preview="onPreview" />
            </div>
          </TabsContent>

          <TabsContent value="bgm">
            <div class="flex flex-col gap-4">
              <BgmUploader @files-selected="onBgmFilesSelected" />
              <BgmList @delete="onBgmDelete" @preview="onBgmPreview" />
            </div>
          </TabsContent>

        </Tabs>
      </main>
    </div>

    <!-- 素材详情弹窗 -->
    <ImageDetail
      :item="previewItem"
      :open="detailOpen"
      @save="onSaveDetail"
      @update:open="detailOpen = $event"
    />
  </div>
</template>
