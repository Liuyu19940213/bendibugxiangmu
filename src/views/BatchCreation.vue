<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useBatchStore } from '@/stores/batch'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import { BOOK_CATEGORIES } from '@/data/bookList'
import GlobalConfigBar from '@/components/batch/GlobalConfigBar.vue'
import ModuleList from '@/components/batch/ModuleList.vue'
import BatchRunPanel from '@/components/batch/BatchRunPanel.vue'
import TxtImportDialog from '@/components/batch/TxtImportDialog.vue'
import ResumeDialog from '@/components/batch/ResumeDialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Separator from '@/components/ui/Separator.vue'
import Slider from '@/components/ui/Slider.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogClose from '@/components/ui/DialogClose.vue'
import { Plus, Upload, Save } from 'lucide-vue-next'

const batchStore = useBatchStore()
const bookDefaultsStore = useBookDefaultsStore()
const showAddDialog = ref(false)
const showImport = ref(false)
const showResume = ref(false)
const showSaveTpl = ref(false)
const newBookName = ref('')
const newBookText = ref('')
const newBgmStyle = ref<'激昂' | '宁静'>('宁静')
const newRewriteMode = ref<'rigid' | 'flexible'>('flexible')
const newReferenceCount = ref(3)
const newImageFolder = ref('')
const useCustomConfig = ref(false)
const templateName = ref('')

watch(newBookName, (name) => {
  if (!name || !bookDefaultsStore.defaults[name] || useCustomConfig.value) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  newBgmStyle.value = cfg.bgmStyle as '激昂' | '宁静'
  newRewriteMode.value = cfg.rewriteMode
  newReferenceCount.value = cfg.referenceCount
  newImageFolder.value = cfg.imageFolder || ''
})

const restoredProgress = ref<{ completed: number; failed: number; total: number } | null>(null)

onMounted(() => {
  try {
    const raw = localStorage.getItem('pixelle_batch_progress')
    if (raw) {
      const data = JSON.parse(raw)
      if (data.progress && data.progress.total > 0) {
        restoredProgress.value = {
          completed: data.progress.completed || 0,
          failed: data.progress.failed || 0,
          total: data.progress.total || 0,
        }
        showResume.value = true
      }
    }
  } catch { /* ignore */ }
})

function handleAdd() {
  if (!newBookName.value.trim()) return
  const override = useCustomConfig.value
    ? {
        bgmStyle: newBgmStyle.value,
        rewriteParams: {
          referenceCount: newReferenceCount.value,
          style: '沉稳大气',
          targetWordsMin: 3000,
          targetWordsMax: 4500,
          rewriteMode: newRewriteMode.value,
        },
        ...(newImageFolder.value ? { imageFolder: newImageFolder.value } as any : {}),
      }
    : (newImageFolder.value ? { imageFolder: newImageFolder.value } as any : undefined)
  batchStore.addModule(newBookName.value.trim(), newBookText.value, override)
  batchStore.sortModules()
  newBookName.value = ''
  newBookText.value = ''
  newBgmStyle.value = '宁静'
  newRewriteMode.value = 'flexible'
  newReferenceCount.value = 3
  newImageFolder.value = ''
  useCustomConfig.value = false
  showAddDialog.value = false
}

function handleSaveTemplate() {
  if (!templateName.value.trim()) return
  batchStore.saveTemplate(templateName.value.trim())
  templateName.value = ''
  showSaveTpl.value = false
}

function handleApplyTemplate(id: string) {
  if (!id) return
  batchStore.applyTemplate(id)
}

function handleResumeClear() {
  batchStore.resetProgress()
  restoredProgress.value = null
  localStorage.removeItem('pixelle_batch_progress')
}

function handleResumeContinue() {
  batchStore.restoreProgress()
  restoredProgress.value = null
  showResume.value = false
}
</script>

<template>
  <div class="flex flex-col h-full">
    <GlobalConfigBar />
    <Separator />
    <div class="flex-1 overflow-y-auto">
      <ModuleList />
    </div>
    <div class="flex items-center gap-3 px-4 py-3 border-t bg-card">
      <Button variant="outline" size="sm" @click="showAddDialog = true">
        <Plus class="h-4 w-4 mr-1" />手动添加
      </Button>
      <Button variant="outline" size="sm" @click="showImport = true">
        <Upload class="h-4 w-4 mr-1" />导入 TXT
      </Button>

      <div class="flex-1" />

      <div v-if="batchStore.templates.length > 0" class="flex items-center gap-2">
        <select
          class="flex h-9 w-40 rounded-md border border-input bg-background px-3 py-1 text-sm"
          @change="handleApplyTemplate(($event.target as HTMLSelectElement).value)"
        >
          <option value="" disabled selected>载入模板</option>
          <option v-for="t in batchStore.templates" :key="t.id" :value="t.id">
            {{ t.name }}（{{ t.modules.length }}本）
          </option>
        </select>
      </div>

      <Button variant="outline" size="sm" :disabled="batchStore.enabledCount === 0" @click="showSaveTpl = true">
        <Save class="h-4 w-4 mr-1" />保存模板
      </Button>
    </div>
    <BatchRunPanel />

    <Dialog :open="showAddDialog" @update:open="showAddDialog = $event">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>手动添加书籍</DialogTitle>
        </DialogHeader>
        <div class="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
          <div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
            <div>
              <p class="text-sm font-medium">是否自定义</p>
              <p class="text-xs text-muted-foreground">开启后按模块选择设置，关闭则遵循全局默认</p>
            </div>
            <button
              role="switch"
              :aria-checked="useCustomConfig"
              :class="['inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', useCustomConfig ? 'bg-primary' : 'bg-input']"
              @click="useCustomConfig = !useCustomConfig"
            >
              <span :class="['pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform', useCustomConfig ? 'translate-x-5' : 'translate-x-0']" />
            </button>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">书名</label>
            <select v-model="newBookName" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm">
              <option value="" disabled>— 请选择 —</option>
              <option v-for="cat in BOOK_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <template v-if="useCustomConfig">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">BGM风格</label>
              <select v-model="newBgmStyle" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm">
                <option value="激昂">激昂</option>
                <option value="宁静">宁静</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">洗稿模式</label>
              <select v-model="newRewriteMode" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm">
                <option value="flexible">首尾锁·中段自由</option>
                <option value="rigid">锁骨架换血肉</option>
              </select>
            </div>
          </div>
          </template>

          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium">对标素材 {{ newReferenceCount }}</label>
            </div>
            <Slider
              :model-value="[newReferenceCount]"
              @update:model-value="(val: number[]) => (newReferenceCount = val[0] ?? 3)"
              :min="0" :max="10" :step="1"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">预置文案（可选）</label>
            <Textarea v-model="newBookText" rows="6" placeholder="可留空，后续再编辑..." />
          </div>
        </div>
        <DialogFooter>
          <DialogClose as-child>
            <Button variant="outline">取消</Button>
          </DialogClose>
          <Button @click="handleAdd" :disabled="!newBookName.trim()">确认添加</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog :open="showSaveTpl" @update:open="showSaveTpl = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>保存模块模板</DialogTitle>
        </DialogHeader>
        <div class="py-4">
          <p class="text-sm text-muted-foreground mb-3">
            将当前 {{ batchStore.enabledCount }} 本书的模块配置保存为模板
          </p>
          <div class="space-y-2">
            <label class="text-sm font-medium">模板名称</label>
            <Input v-model="templateName" placeholder="如：书单号-沉稳风" @keydown.enter="handleSaveTemplate" />
          </div>
        </div>
        <DialogFooter>
          <DialogClose as-child>
            <Button variant="outline">取消</Button>
          </DialogClose>
          <Button @click="handleSaveTemplate" :disabled="!templateName.trim()">保存</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <TxtImportDialog v-model:open="showImport" @imported="showImport = false" />
    <ResumeDialog
      v-model:open="showResume"
      :completed="restoredProgress?.completed || 0"
      :failed="restoredProgress?.failed || 0"
      :total="restoredProgress?.total || 0"
      @clear="handleResumeClear"
      @resume="handleResumeContinue"
    />
  </div>
</template>
