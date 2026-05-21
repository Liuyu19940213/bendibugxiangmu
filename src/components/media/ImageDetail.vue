<script setup lang="ts">
import { ref } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { MediaItem, ImageCategory } from '@/types'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Select from '@/components/ui/Select.vue'
import SelectTrigger from '@/components/ui/SelectTrigger.vue'
import SelectContent from '@/components/ui/SelectContent.vue'
import SelectGroup from '@/components/ui/SelectGroup.vue'
import SelectItem from '@/components/ui/SelectItem.vue'
import SelectValue from '@/components/ui/SelectValue.vue'
import Switch from '@/components/ui/Switch.vue'

const props = defineProps<{
  item: MediaItem | null
  open: boolean
}>()

const emit = defineEmits<{
  save: [item: MediaItem]
  'update:open': [boolean]
}>()

const mediaStore = useMediaStore()
const newTag = ref('')

const presetCategories: ImageCategory[] = ['自然风景', '演播室', '书房', '抽象意境', '未分类']

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function removeTag(tag: string) {
  if (!props.item) return
  const updated = { ...props.item, tags: props.item.tags.filter((t) => t !== tag) }
  emit('save', updated)
}

function addTag() {
  if (!props.item || !newTag.value.trim()) return
  if (props.item.tags.includes(newTag.value.trim())) {
    newTag.value = ''
    return
  }
  const updated = { ...props.item, tags: [...props.item.tags, newTag.value.trim()] }
  newTag.value = ''
  emit('save', updated)
}

function onCategoryChange(category: ImageCategory) {
  if (!props.item) return
  const updated = { ...props.item, category }
  emit('save', updated)
}

function onKenBurnsChange(enabled: boolean) {
  if (!props.item) return
  const updated = { ...props.item, kenBurns: enabled }
  emit('save', updated)
}

const cooldownRemaining = ref(0)
const inCooldown = ref(false)

function refreshCooldown() {
  if (props.item) {
    inCooldown.value = mediaStore.isInCooldown(props.item)
    cooldownRemaining.value = mediaStore.getCooldownRemaining(props.item)
  }
}

// watch for item changes
import { watch } from 'vue'
watch(() => props.item, () => {
  refreshCooldown()
}, { immediate: true })
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-lg">
      <DialogHeader>
        <DialogTitle>素材详情</DialogTitle>
      </DialogHeader>

      <div v-if="item" class="space-y-4">
        <div v-if="item.type === 'image'" class="rounded-lg overflow-hidden bg-muted">
          <img :src="item.path" :alt="item.name" class="w-full object-contain max-h-64" />
        </div>

        <div class="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span class="text-muted-foreground">名称：</span>{{ item.name }}
          </div>
          <div v-if="item.fileSize">
            <span class="text-muted-foreground">大小：</span>{{ formatFileSize(item.fileSize) }}
          </div>
          <div>
            <span class="text-muted-foreground">来源：</span>
            <Badge variant="secondary" size="sm">
              {{ item.source === 'ai' ? 'AI 生成' : item.source === 'preset' ? '预设' : '上传' }}
            </Badge>
          </div>
          <div v-if="item.createdAt">
            <span class="text-muted-foreground">添加：</span>{{ new Date(item.createdAt).toLocaleDateString() }}
          </div>
        </div>

        <!-- 冷却期状态 -->
        <div v-if="item.lastUsedAt" class="rounded-lg border p-3 text-sm">
          <p class="text-muted-foreground">
            上次使用：{{ new Date(item.lastUsedAt).toLocaleString() }}
          </p>
          <p v-if="inCooldown" class="text-orange-500 font-medium mt-1">
            冷却中 · 剩余 {{ cooldownRemaining }} 天
          </p>
          <p v-else class="text-green-500 font-medium mt-1">
            已冷却完毕，可使用
          </p>
        </div>

        <!-- 分类（仅图片） -->
        <div v-if="item.type === 'image'">
          <p class="text-sm font-medium text-muted-foreground mb-1">分类</p>
          <Select :model-value="item.category" @update:model-value="(v: string) => onCategoryChange(v as ImageCategory)">
            <SelectTrigger>
              <SelectValue placeholder="选择分类" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="cat in presetCategories" :key="cat" :value="cat">
                  {{ cat }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        <!-- Ken Burns（仅图片） -->
        <div v-if="item.type === 'image'" class="flex items-center justify-between rounded-lg border p-3">
          <div>
            <p class="text-sm font-medium">Ken Burns 效果</p>
            <p class="text-xs text-muted-foreground">缓慢缩放平移，增加画面动感</p>
          </div>
          <Switch :model-value="item.kenBurns" @update:model-value="onKenBurnsChange" />
        </div>

        <!-- 标签 -->
        <div>
          <p class="text-sm font-medium text-muted-foreground mb-1">标签</p>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <Badge
              v-for="tag in item.tags.filter((t) => !presetCategories.includes(t as ImageCategory))"
              :key="tag"
              variant="secondary"
              class="gap-1"
            >
              {{ tag }}
              <button
                class="ml-0.5 text-muted-foreground hover:text-foreground"
                @click="removeTag(tag)"
              >
                ×
              </button>
            </Badge>
            <span v-if="item.tags.filter((t) => !presetCategories.includes(t as ImageCategory)).length === 0" class="text-xs text-muted-foreground">
              暂无标签
            </span>
          </div>
          <div class="flex gap-2">
            <Input
              v-model="newTag"
              placeholder="输入新标签"
              class="flex-1"
              @keydown.enter="addTag"
            />
            <Button size="sm" @click="addTag">添加</Button>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">关闭</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
