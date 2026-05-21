<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useBookDefaultsStore, DEFAULT_BOOK_CONFIG } from '@/stores/bookDefaults'
import { BOOK_CATEGORIES } from '@/data/bookList'
import type { BookDefaultConfig } from '@/types'
import Button from '@/components/ui/Button.vue'
import Slider from '@/components/ui/Slider.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogClose from '@/components/ui/DialogClose.vue'
import { Plus, Trash2, Settings2, FolderOpen } from 'lucide-vue-next'

const store = useBookDefaultsStore()

const showDialog = ref(false)
const editingBookName = ref('')
const form = reactive<BookDefaultConfig>({ ...DEFAULT_BOOK_CONFIG })

const configuredList = computed(() =>
  Object.entries(store.defaults).map(([bookName, config]) => ({ bookName, config }))
)

const availableBooks = computed(() =>
  BOOK_CATEGORIES.filter((b) => !store.defaults[b])
)

const dialogTitle = computed(() =>
  editingBookName.value ? `编辑：${editingBookName.value}` : '添加书籍默认配置'
)

function openAdd() {
  editingBookName.value = ''
  _bookSelect.value = ''
  Object.assign(form, DEFAULT_BOOK_CONFIG)
  showDialog.value = true
}

function openEdit(bookName: string) {
  editingBookName.value = bookName
  Object.assign(form, store.getBookConfig(bookName))
  showDialog.value = true
}

function handleSave() {
  const name = editingBookName.value || _bookSelect.value
  if (!name) return
  const cfg: BookDefaultConfig = {
    voiceProvider: form.voiceProvider,
    bgmStyle: form.bgmStyle,
    videoMode: form.videoMode,
    rewriteMode: form.rewriteMode,
    referenceCount: form.referenceCount,
    imageCount: form.imageCount,
    kenBurns: form.kenBurns,
    imageFolder: form.imageFolder,
  }
  store.setBookConfig(name, cfg)
  showDialog.value = false
}

function handleSelectDefaultFolder() {
  defaultFolderInputRef.value?.click()
}

function handleDefaultFolderSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return
  const firstPath = (files[0] as any).path || (files[0] as any).webkitRelativePath
  if (firstPath) {
    form.imageFolder = firstPath.replace(/[/\\][^/\\]+$/, '')
  }
  input.value = ''
}

function handleDelete(bookName: string) {
  store.deleteBookConfig(bookName)
}

const _bookSelect = ref('')
const defaultFolderInputRef = ref<HTMLInputElement | null>(null)
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-3xl mx-auto p-6 space-y-5">

      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-semibold">📖 书籍默认配置</h1>
          <p class="text-xs text-muted-foreground mt-1">为每本书预设默认参数，选书时自动加载</p>
        </div>
        <Button :disabled="availableBooks.length === 0" @click="openAdd">
          <Plus class="h-4 w-4 mr-1" />
          添加配置
        </Button>
      </div>

      <div v-if="configuredList.length === 0" class="text-center py-16 text-sm text-muted-foreground space-y-2">
        <Settings2 class="h-10 w-10 mx-auto opacity-20" />
        <p>尚未为任何书籍设置默认配置</p>
        <p>点击「添加配置」开始</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="item in configuredList"
          :key="item.bookName"
          class="flex items-center justify-between rounded-lg border bg-card p-4 hover:border-primary/30 transition-colors"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-medium text-sm">{{ item.bookName }}</span>
            </div>
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span>配音：{{ item.config.voiceProvider === 'cosyvoice' ? 'CosyVoice2' : item.config.voiceProvider === 'mimo' ? 'Mimo' : item.config.voiceProvider === 'minimax' ? 'MiniMax 海螺' : 'IndexTTS' }}</span>
              <span>BGM：{{ item.config.bgmStyle }}</span>
              <span>视频：{{ item.config.videoMode === 'kenburns' ? 'Ken Burns' : '固定模板' }}</span>
              <span>洗稿：{{ item.config.rewriteMode === 'flexible' ? '首尾锁·中段自由' : '锁骨架换血肉' }}</span>
              <span>素材：{{ item.config.referenceCount }} 个</span>
              <span>图片：{{ item.config.imageCount }} 张</span>
              <span>Ken Burns：{{ item.config.kenBurns ? '开' : '关' }}</span>
              <span v-if="item.config.imageFolder" class="truncate max-w-[180px]">📁 {{ item.config.imageFolder.replace(/\\/g, '/').split('/').pop() || item.config.imageFolder }}</span>
            </div>
          </div>
          <div class="flex items-center gap-1 ml-3 shrink-0">
            <Button variant="ghost" size="sm" @click="openEdit(item.bookName)">编辑</Button>
            <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="handleDelete(item.bookName)">
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div class="h-12" />
    </div>

    <Dialog :open="showDialog" @update:open="showDialog = $event">
      <DialogContent class="max-w-md max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{{ dialogTitle }}</DialogTitle>
        </DialogHeader>

        <div class="space-y-5 py-4">
          <div v-if="!editingBookName">
            <label class="text-sm font-medium">选择书籍</label>
            <select
              v-model="_bookSelect"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1"
            >
              <option value="" disabled>— 请选择 —</option>
              <option v-for="book in availableBooks" :key="book" :value="book">{{ book }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs text-muted-foreground">配音引擎</label>
              <select v-model="form.voiceProvider" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1">
                <option value="cosyvoice">CosyVoice2（本地·推荐）</option>
                <option value="indextts">IndexTTS（本地·备用）</option>
                <option value="mimo">Mimo</option>
                <option value="minimax">MiniMax 海螺</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-muted-foreground">BGM 风格</label>
              <select v-model="form.bgmStyle" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1">
                <option value="激昂">激昂</option>
                <option value="宁静">宁静</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs text-muted-foreground">视频模式</label>
              <select v-model="form.videoMode" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1">
                <option value="kenburns">Ken Burns</option>
                <option value="template">固定模板</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-muted-foreground">洗稿模式</label>
              <select v-model="form.rewriteMode" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1">
                <option value="flexible">首尾锁·中段自由</option>
                <option value="rigid">锁骨架换血肉</option>
              </select>
            </div>
          </div>

          <div>
            <div class="flex justify-between">
              <label class="text-xs text-muted-foreground">对标素材数量</label>
              <span class="text-xs">{{ form.referenceCount }}</span>
            </div>
            <Slider :model-value="[form.referenceCount]" @update:model-value="form.referenceCount = Number($event[0])" :min="0" :max="10" :step="1" class="mt-1" />
          </div>

          <div>
            <div class="flex justify-between">
              <label class="text-xs text-muted-foreground">每次使用图片数量</label>
              <span class="text-xs">{{ form.imageCount }}</span>
            </div>
            <div class="flex items-center gap-2 mt-1">
              <Button variant="outline" size="sm" :disabled="form.imageCount <= 1" @click="form.imageCount = Math.max(1, form.imageCount - 1)">−</Button>
              <span class="w-8 text-center text-sm">{{ form.imageCount }}</span>
              <Button variant="outline" size="sm" :disabled="form.imageCount >= 20" @click="form.imageCount = Math.min(20, form.imageCount + 1)">+</Button>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <label class="text-sm">Ken Burns 效果</label>
              <p class="text-xs text-muted-foreground">视频播放时自动缓慢缩放/平移</p>
            </div>
            <button role="switch" :aria-checked="form.kenBurns" :class="['inline-flex h-5 w-9 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', form.kenBurns ? 'bg-primary' : 'bg-input']" @click="form.kenBurns = !form.kenBurns">
              <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', form.kenBurns ? 'translate-x-4' : 'translate-x-0']" />
            </button>
          </div>

          <div>
            <label class="text-sm font-medium">图片文件夹</label>
            <p class="text-xs text-muted-foreground mt-0.5">为此书指定专用的图片文件夹</p>
            <input ref="defaultFolderInputRef" type="file" webkitdirectory directory multiple accept="image/*" class="hidden" @change="handleDefaultFolderSelected" />
            <div v-if="form.imageFolder" class="flex items-center gap-2 mt-2">
              <div class="flex items-center gap-1.5 px-2 py-1 rounded border bg-muted/30 text-xs flex-1 min-w-0">
                <FolderOpen class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <span class="truncate">{{ form.imageFolder.replace(/\\/g, '/').split('/').pop() || form.imageFolder }}</span>
              </div>
              <Button variant="outline" size="sm" @click="handleSelectDefaultFolder">更换</Button>
              <Button variant="ghost" size="sm" class="text-destructive" @click="form.imageFolder = ''">清空</Button>
            </div>
            <Button v-else variant="outline" size="sm" class="w-full mt-2" @click="handleSelectDefaultFolder">
              <FolderOpen class="h-4 w-4 mr-1" />选择文件夹（可选）
            </Button>
          </div>
        </div>

        <DialogFooter>
          <DialogClose as-child>
            <Button variant="outline">取消</Button>
          </DialogClose>
          <Button :disabled="!editingBookName && !_bookSelect" @click="handleSave">
            保存默认配置
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
