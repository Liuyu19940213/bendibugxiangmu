<script setup lang="ts">
import { ref, onUnmounted, onMounted } from 'vue'
import { useBatchStore } from '@/stores/batch'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import { rewriteContent } from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Progress from '@/components/ui/Progress.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogDescription from '@/components/ui/DialogDescription.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import { Play, Square } from 'lucide-vue-next'

import type { BatchModule } from '@/types'

const batchStore = useBatchStore()
const bookDefaultsStore = useBookDefaultsStore()

const showSummary = ref(false)
const showImageWarning = ref(false)
const imageWarningBooks = ref<string[]>([])
const summaryData = ref({
  completed: 0,
  failed: 0,
  skipped: 0,
  failedBooks: [] as { name: string; reason: string }[],
})

// 取消标志
let cancelled = false

function updateProgress() {
  const mods = batchStore.modules
  const runnable = mods.filter((m) => m.enabled && m.rawText.trim() !== '')
  const total = runnable.length
  const completed = runnable.filter((m) => m.status === 'completed').length
  const failed = runnable.filter((m) => m.status === 'failed').length
  const skipped = runnable.filter((m) => m.status === 'skipped').length
  batchStore.progress = {
    total,
    completed,
    failed,
    skipped,
    currentBook: batchStore.progress.currentBook,
    percent: total > 0 ? Math.round(((completed + failed + skipped) / total) * 100) : 0,
  }
}

async function runModule(mod: BatchModule) {
  if (cancelled) return

  // 跳过已禁用的和空文案的（不参与进度统计，updateProgress 只统计 runnable 模块）
  if (!mod.enabled || !mod.rawText.trim()) {
    mod.status = 'skipped'
    updateProgress()
    batchStore.persistProgress()
    return
  }

  mod.status = 'running'
  batchStore.progress.currentBook = mod.bookName
  updateProgress()
  batchStore.persistProgress()

  // 计算目标字数范围
  const override = mod.configOverride
  const rewriteParams = {
    ...batchStore.globalConfig.rewriteParams,
    ...(override?.rewriteParams || {}),
  }

  try {
    const resp = await rewriteContent({
      text: mod.rawText,
      book_name: mod.bookName,
      reference_count: rewriteParams.referenceCount,
      originality: 30,
      target_chars: `${rewriteParams.targetWordsMin}-${rewriteParams.targetWordsMax}`,
      rewrite_mode: rewriteParams.rewriteMode,
    })

    if (resp.success) {
      mod.status = 'completed'
      mod.resultText = resp.content
      mod.errorMessage = undefined
    } else {
      mod.status = 'failed'
      mod.errorMessage = resp.message || '洗稿返回失败'
    }
  } catch (err: unknown) {
    mod.status = 'failed'
    const msg = err instanceof Error ? err.message : '网络或服务异常'
    mod.errorMessage = msg
  }

  updateProgress()
  batchStore.persistProgress()
}

async function handleStart() {
  cancelled = false

  const booksWithFolder: string[] = []
  for (const mod of batchStore.modules) {
    if (!mod.enabled) continue
    const def = bookDefaultsStore.defaults[mod.bookName]
    if (def?.imageFolder) booksWithFolder.push(mod.bookName)
  }
  if (booksWithFolder.length > 0) {
    imageWarningBooks.value = booksWithFolder
    showImageWarning.value = true
    return
  }

  doStartBatch()
}

async function confirmStartBatch() {
  showImageWarning.value = false
  await doStartBatch()
}

async function doStartBatch() {
  batchStore.isRunning = true
  const enabledMods = batchStore.modules.filter((m) => m.enabled)

  // 先重置所有状态（保留 rawText）
  enabledMods.forEach((m) => {
    m.status = 'idle'
    m.errorMessage = undefined
    m.resultText = undefined
  })
  batchStore.progress = {
    total: 0,
    completed: 0,
    failed: 0,
    skipped: 0,
    currentBook: null,
    percent: 0,
  }
  updateProgress()
  batchStore.persistProgress()

  // 串行执行每个模块
  for (const mod of batchStore.modules) {
    if (cancelled) break
    await runModule(mod)
  }

  // 完成
  batchStore.isRunning = false
  batchStore.progress.currentBook = null
  batchStore.persistProgress()

  const failedBooks = batchStore.modules
    .filter((m) => m.status === 'failed')
    .map((m) => ({
      name: m.bookName,
      reason: m.errorMessage || '未知错误',
    }))
  summaryData.value = {
    completed: batchStore.progress.completed,
    failed: batchStore.progress.failed,
    skipped: batchStore.progress.skipped,
    failedBooks,
  }
  showSummary.value = true
}

function handleCancel() {
  cancelled = true
  batchStore.isRunning = false
  batchStore.progress.currentBook = null
  updateProgress()
  batchStore.persistProgress()
}

function handleCloseSummary() {
  showSummary.value = false
}

function handleReset() {
  batchStore.resetProgress()
}

onMounted(() => {
  batchStore.restoreProgress()
})

onUnmounted(() => {
  cancelled = true
})
</script>

<template>
  <div class="sticky bottom-0 bg-background/95 backdrop-blur border-t p-4">
    <!-- 运行前 + 运行完成 -->
    <div
      v-if="!batchStore.isRunning && batchStore.progress.total === 0"
      class="flex items-center justify-between"
    >
      <span class="text-sm text-muted-foreground">
        共 {{ batchStore.enabledCount }} 本书待处理
      </span>
      <Button @click="handleStart" :disabled="batchStore.enabledCount === 0">
        <Play class="h-4 w-4 mr-1" />开始批量运行
      </Button>
    </div>

    <!-- 运行中 -->
    <div v-else-if="batchStore.isRunning" class="space-y-2">
      <div class="flex items-center gap-4">
        <Progress
          class="flex-1"
          :model-value="batchStore.progress.percent"
        />
        <Button variant="outline" size="sm" @click="handleCancel">
          <Square class="h-4 w-4 mr-1" />取消
        </Button>
      </div>
      <div class="text-sm text-muted-foreground">
        <template v-if="batchStore.progress.currentBook">
          正在处理：《{{ batchStore.progress.currentBook }}》
        </template>
        <span class="ml-4">
          {{ batchStore.progress.completed }}/{{ batchStore.progress.total }} 完成，
          {{ batchStore.progress.failed }} 失败
        </span>
      </div>
    </div>

    <!-- 全部完成 -->
    <div v-else class="flex items-center justify-between">
      <span class="text-sm">
        ✅ {{ batchStore.progress.completed }} / ❌ {{ batchStore.progress.failed }} / ⏭ {{ batchStore.progress.skipped }}
      </span>
      <Button variant="outline" size="sm" @click="handleReset">
        重置
      </Button>
    </div>
  </div>

  <!-- 完成汇总弹窗 -->
  <Dialog :open="showSummary" @update:open="showSummary = $event">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>批量运行完成</DialogTitle>
        <DialogDescription>
          运行已完成，以下是执行结果汇总
        </DialogDescription>
      </DialogHeader>
      <div class="py-4 space-y-3">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-green-600">{{ summaryData.completed }}</div>
            <div class="text-sm text-muted-foreground">成功</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-red-600">{{ summaryData.failed }}</div>
            <div class="text-sm text-muted-foreground">失败</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-yellow-600">{{ summaryData.skipped }}</div>
            <div class="text-sm text-muted-foreground">跳过</div>
          </div>
        </div>

        <div v-if="summaryData.failedBooks.length > 0" class="mt-4">
          <div class="text-sm font-medium mb-2">失败书籍：</div>
          <div class="space-y-2 max-h-60 overflow-y-auto">
            <div
              v-for="(book, index) in summaryData.failedBooks"
              :key="index"
              class="p-3 bg-red-50 border border-red-200 rounded text-sm"
            >
              <div class="font-medium text-red-800">{{ book.name }}</div>
              <div class="text-red-600 text-xs mt-1">{{ book.reason }}</div>
            </div>
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button @click="handleCloseSummary">关闭</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <div v-if="showImageWarning" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showImageWarning = false">
    <div class="bg-card rounded-lg border shadow-xl p-6 max-w-sm mx-4 space-y-4">
      <p class="text-sm font-medium">⚠️ 图片文件夹提醒</p>
      <div class="text-xs text-muted-foreground space-y-2">
        <p>以下书籍已配置专用图片文件夹，请确保文件夹内有足够的图片：</p>
        <ul class="list-disc list-inside space-y-0.5">
          <li v-for="book in imageWarningBooks" :key="book">{{ book }}</li>
        </ul>
        <p class="text-amber-600">建议先在「洗稿和二创」页面为这些书籍选取图片，再运行批量任务。</p>
      </div>
      <div class="flex justify-end gap-2">
        <Button variant="outline" size="sm" @click="showImageWarning = false">取消</Button>
        <Button size="sm" @click="confirmStartBatch">仍然开始</Button>
      </div>
    </div>
  </div>
</template>
