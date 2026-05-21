<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMediaStore } from '@/stores/media'
import type { MediaItem } from '@/types'
import { extractTextFromVideo } from '@/services/api'
import { BOOK_CATEGORIES } from '@/data/bookList'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Badge from '@/components/ui/Badge.vue'
import Separator from '@/components/ui/Separator.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogClose from '@/components/ui/DialogClose.vue'
import { FileText, Search, Download, BookOpen, Zap, Plus, Video, Loader2 } from 'lucide-vue-next'

const mediaStore = useMediaStore()

const searchKeyword = ref('')
const showAddDialog = ref(false)
const addMode = ref<'paste' | 'video'>('paste')

const selectedBook = ref('')
const textName = ref('')
const textContent = ref('')
const videoFile = ref<File | null>(null)
const videoModelSize = ref('medium')
const isExtracting = ref(false)
const extractResult = ref('')
const extractProgress = ref('')
const extractEmotion = ref(false)

const emotionColors: Record<string, string> = {
  '激昂': 'bg-red-500',
  '平静': 'bg-blue-500',
  '疑问': 'bg-yellow-500',
  '感叹': 'bg-orange-500',
  '悲伤': 'bg-purple-500',
}

function parseRhythm(emotionRhythm?: string): string[] {
  if (!emotionRhythm) return []
  try {
    const parsed = JSON.parse(emotionRhythm)
    return (parsed.emotions || []) as string[]
  } catch {
    return []
  }
}

const matchingItems = computed<MediaItem[]>(() => {
  return mediaStore.items.filter(
    (i) => i.type === 'copy' && i.bookName && i.emotionRhythm,
  )
})

const filteredItems = computed<MediaItem[]>(() => {
  let result = mediaStore.items.filter((i) => i.type === 'copy')

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(
      (i) =>
        i.name.toLowerCase().includes(kw) ||
        (i.rawText && i.rawText.toLowerCase().includes(kw)) ||
        (i.bookName && i.bookName.toLowerCase().includes(kw)) ||
        i.tags.some((t) => t.includes(kw)),
    )
  }

  return result
})

function truncateText(text: string | undefined, maxLen: number = 120): string {
  if (!text) return '（无内容）'
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen) + '…'
}

function countChars(text: string | undefined): number {
  if (!text) return 0
  return text.replace(/[^\u4e00-\u9fff]/g, '').length
}

function formatDate(isoStr: string | undefined): string {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleDateString('zh-CN')
}

function openAddDialog(mode: 'paste' | 'video') {
  addMode.value = mode
  selectedBook.value = BOOK_CATEGORIES[0]
  textName.value = ''
  textContent.value = ''
  videoFile.value = null
  extractResult.value = ''
  extractProgress.value = ''
  showAddDialog.value = true
}

function handleSaveText() {
  if (!selectedBook.value || !textName.value.trim() || !textContent.value.trim()) return
  const now = new Date().toISOString()
  mediaStore.addItems([{
    id: crypto.randomUUID(),
    type: 'copy',
    name: textName.value.trim(),
    path: '',
    source: 'upload',
    category: '未分类',
    tags: [],
    bookName: selectedBook.value,
    createdAt: now,
    fileSize: 0,
    kenBurns: false,
    rawText: textContent.value.trim(),
  }])
  showAddDialog.value = false
}

function handleVideoSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  videoFile.value = file
  if (!textName.value.trim()) {
    textName.value = file.name.replace(/\.[^.]+$/, '')
  }
  input.value = ''
}

async function handleExtractText() {
  if (!videoFile.value) return
  isExtracting.value = true
  extractProgress.value = '正在提取音频...'
  extractResult.value = ''
  try {
    extractProgress.value = '正在语音转文字...'
    const res = await extractTextFromVideo(videoFile.value, videoModelSize.value)
    extractResult.value = res.text
    if (!textName.value.trim()) {
      textName.value = `视频转写_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}`
    }
    extractProgress.value = '转写完成'
  } catch (e: unknown) {
    extractResult.value = ''
    extractProgress.value = ''
    alert('转写失败：' + (e instanceof Error ? e.message : '未知错误'))
  } finally {
    isExtracting.value = false
  }
}

function handleSaveExtracted() {
  if (!selectedBook.value || !extractResult.value.trim()) return
  const now = new Date().toISOString()
  mediaStore.addItems([{
    id: crypto.randomUUID(),
    type: 'copy',
    name: (textName.value || '视频转写').trim(),
    path: '',
    source: 'upload',
    category: '未分类',
    tags: ['视频转写'],
    bookName: selectedBook.value,
    createdAt: now,
    fileSize: 0,
    kenBurns: false,
    rawText: extractResult.value.trim(),
  }])
  showAddDialog.value = false
}
</script>

<template>
  <div class="flex h-full flex-col">

    <div class="flex items-center gap-3 border-b px-6 py-3">
      <div class="relative flex-1 max-w-sm">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          v-model="searchKeyword"
          placeholder="搜索文案名称、书籍或内容..."
          class="pl-9"
        />
      </div>

      <Separator orientation="vertical" class="h-6" />

      <Button variant="outline" size="sm" class="gap-2" @click="openAddDialog('paste')">
        <Plus class="h-4 w-4" />
        粘贴文案
      </Button>
      <Button variant="default" size="sm" class="gap-2" @click="openAddDialog('video')">
        <Video class="h-4 w-4" />
        视频转文案
      </Button>
      <Button variant="outline" size="sm" class="gap-2" :disabled="filteredItems.length === 0">
        <Download class="h-4 w-4" />
        导出
      </Button>
    </div>

    <div class="flex-1 overflow-auto p-6">
      <div v-if="filteredItems.length === 0" class="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <FileText class="h-16 w-16 mb-4 opacity-20" />
        <p class="text-lg font-medium">暂无文案</p>
        <p class="text-sm mt-1">点击「粘贴文案」直接输入，或「视频转文案」从视频中提取</p>
        <div class="flex gap-3 mt-4">
          <Button variant="outline" size="sm" @click="openAddDialog('paste')">
            <Plus class="h-4 w-4 mr-1" />粘贴文案
          </Button>
          <Button variant="default" size="sm" @click="openAddDialog('video')">
            <Video class="h-4 w-4 mr-1" />视频转文案
          </Button>
        </div>
      </div>

      <div v-else class="space-y-4">
        <div v-if="matchingItems.length > 0" class="rounded-lg border p-3 bg-muted/30">
          <p class="text-sm font-medium flex items-center gap-1 mb-2">
            <Zap class="h-4 w-4 text-yellow-500" />同书籍情绪节奏参考
          </p>
          <div class="flex flex-wrap gap-2">
            <Badge
              v-for="mi in matchingItems.slice(0, 5)"
              :key="mi.id"
              variant="secondary"
              size="sm"
            >
              {{ mi.name }}
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground mt-1">
            共 {{ matchingItems.length }} 条可参考节奏 · 点击上方卡片查看详情
          </p>
        </div>

        <div class="flex items-center gap-4 text-sm text-muted-foreground">
          <span>共 {{ filteredItems.length }} 条</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card
            v-for="item in filteredItems"
            :key="item.id"
            class="group cursor-pointer transition-shadow hover:shadow-md"
          >
            <CardHeader class="pb-2">
              <div class="flex items-start justify-between">
                <CardTitle class="text-base flex items-center gap-2">
                  <BookOpen class="h-4 w-4 text-muted-foreground" />
                  {{ item.name }}
                </CardTitle>
                <Badge v-if="item.bookName" variant="secondary" size="sm">
                  {{ item.bookName }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p class="text-sm text-muted-foreground line-clamp-3">
                {{ truncateText(item.rawText) }}
              </p>
              <div class="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                <span>中文字数：{{ countChars(item.rawText) }}</span>
                <span v-if="item.createdAt">创建：{{ formatDate(item.createdAt) }}</span>
              </div>
              <div v-if="item.tags.length > 0" class="flex flex-wrap gap-1 mt-2">
                <Badge
                  v-for="tag in item.tags"
                  :key="tag"
                  variant="secondary"
                  size="sm"
                >
                  {{ tag }}
                </Badge>
              </div>

              <div v-if="item.emotionRhythm" class="mt-3 pt-3 border-t border-border/50">
                <p class="text-xs text-muted-foreground flex items-center gap-1 mb-1">
                  <Zap class="h-3 w-3" />情绪节奏
                </p>
                <div class="flex h-2.5 rounded-full overflow-hidden">
                  <div
                    v-for="(emotion, ei) in parseRhythm(item.emotionRhythm).slice(0, 20)"
                    :key="ei"
                    :class="[emotionColors[emotion] || 'bg-gray-300', 'flex-1']"
                  ></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>

    <Dialog :open="showAddDialog" @update:open="showAddDialog = $event">
      <DialogContent class="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {{ addMode === 'paste' ? '📝 粘贴文案' : '🎬 视频转文案' }}
          </DialogTitle>
        </DialogHeader>

        <div class="space-y-4 py-4">

          <div class="space-y-2">
            <label class="text-sm font-medium">选择书籍</label>
            <select
              v-model="selectedBook"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            >
              <option v-for="book in BOOK_CATEGORIES" :key="book" :value="book">{{ book }}</option>
            </select>
          </div>

          <div v-if="selectedBook" class="space-y-2">
            <label class="text-sm font-medium">文案名称</label>
            <Input v-model="textName" placeholder="给这段文案起个名字..." />
          </div>

          <template v-if="addMode === 'paste'">
            <div class="space-y-2">
              <label class="text-sm font-medium">文案内容</label>
              <Textarea v-model="textContent" rows="10" placeholder="直接粘贴文案内容..." />
            </div>
            <Button class="w-full" :disabled="!selectedBook || !textName.trim() || !textContent.trim()" @click="handleSaveText">
              保存到文案库
            </Button>
          </template>

          <template v-if="addMode === 'video'">
            <div class="space-y-2">
              <label class="text-sm font-medium">选择视频文件</label>
              <div class="flex items-center gap-2">
                <input
                  type="file"
                  accept="video/*"
                  class="hidden"
                  id="video-file-input"
                  @change="handleVideoSelect"
                />
                <Button variant="outline" size="sm" @click="(document.getElementById('video-file-input') as HTMLInputElement)?.click()">
                  <Video class="h-4 w-4 mr-1" />选择视频
                </Button>
                <span v-if="videoFile" class="text-sm text-muted-foreground truncate">{{ videoFile.name }}</span>
                <span v-else class="text-xs text-muted-foreground">未选择文件</span>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">转录模型</label>
              <select
                v-model="videoModelSize"
                class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="tiny">tiny — 最快（~150MB，适合短视频）</option>
                <option value="base">base — 快速（~280MB）</option>
                <option value="small">small — 均衡（~920MB）</option>
                <option value="medium">medium — 精准（~1.5GB，推荐）</option>
              </select>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <label class="text-sm font-medium">同时提取情绪节奏</label>
                <p class="text-xs text-muted-foreground">分析音频情绪变化，用于后续配音参考</p>
              </div>
              <button
                role="switch"
                :aria-checked="extractEmotion"
                :class="['inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', extractEmotion ? 'bg-primary' : 'bg-input']"
                @click="extractEmotion = !extractEmotion"
              >
                <span :class="['pointer-events-none block h-4 w-4 rounded-full bg-background shadow-sm ring-0 transition-transform', extractEmotion ? 'translate-x-4' : 'translate-x-0']" />
              </button>
            </div>

            <Button
              class="w-full"
              :disabled="!selectedBook || !videoFile || isExtracting"
              @click="handleExtractText"
            >
              <Loader2 v-if="isExtracting" class="h-4 w-4 mr-1 animate-spin" />
              {{ isExtracting ? extractProgress : '开始语音转文字' }}
            </Button>

            <div
              v-if="extractResult"
              class="rounded-lg border bg-muted/30 p-4 space-y-2"
            >
              <p class="text-xs text-muted-foreground">转写结果（{{ countChars(extractResult) }} 中文字）</p>
              <p class="text-sm leading-relaxed max-h-[200px] overflow-y-auto whitespace-pre-wrap">{{ extractResult }}</p>
              <Button
                class="w-full mt-2"
                :disabled="!selectedBook || !textName.trim()"
                @click="handleSaveExtracted"
              >
                保存到文案库
              </Button>
            </div>
          </template>
        </div>

        <DialogFooter>
          <DialogClose as-child>
            <Button variant="outline">取消</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
