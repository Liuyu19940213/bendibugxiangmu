<script setup lang="ts">
import { ref, computed, onUnmounted, onMounted } from 'vue'
import { useFineModeStore } from '@/stores/fineMode'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import { generateVideoAsync, getTask } from '@/services/api'
import type { VideoResponse } from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Progress from '@/components/ui/Progress.vue'

const fineModeStore = useFineModeStore()
const bookDefaultsStore = useBookDefaultsStore()

const BGM_OPTIONS = [
  { label: '激昂 — 进取', value: 'default.mp3' },
  { label: '无 BGM', value: '' },
]

const TEMPLATE_OPTIONS = [
  { label: '1080×1920 图片默认', value: '1080x1920/image_default.html' },
  { label: '1080×1920 图片全屏', value: '1080x1920/image_full.html' },
  { label: '1080×1920 优雅卡片', value: '1080x1920/image_elegant.html' },
  { label: '1080×1920 书籍展示', value: '1080x1920/image_book.html' },
  { label: '1080×1920 治愈风景', value: '1080x1920/image_healing.html' },
]

const VIDEO_MODES = [
  { label: 'Ken Burns 默认（缓慢缩放/平移）', value: 'kenburns' },
  { label: '固定模板', value: 'template' },
]

const selectedBgm = ref('default.mp3')
const bgmVolume = ref(0.3)
const selectedTemplate = ref('1080x1920/image_default.html')
const selectedVideoMode = ref('kenburns')
const nScenes = ref(6)

const isGenerating = ref(false)
const taskProgress = ref(0)
const taskStatus = ref('')
const result = ref<VideoResponse | null>(null)
const errorMsg = ref('')
const showImageWarning = ref(false)
const imageWarningMsg = ref('')
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  const name = fineModeStore.state.bookName
  if (!name || !bookDefaultsStore.defaults[name]) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  selectedBgm.value = cfg.bgmStyle === '激昂' ? 'default.mp3' : ''
  selectedVideoMode.value = cfg.videoMode
})

const textCharCount = computed(() => {
  return (fineModeStore.state.rewriteResult || fineModeStore.state.rawText)
    .match(/[\u4e00-\u9fff]/g)?.length ?? 0
})

const suggestedScenes = computed(() => {
  const chars = textCharCount.value
  const byChars = Math.max(3, Math.ceil(chars / 450))
  return Math.min(15, byChars)
})

const isReady = computed(() => {
  return !!fineModeStore.state.rewriteResult && textCharCount.value >= 50
})

function checkImageFolder() {
  const need = fineModeStore.state.imageConfig.imageCount
  const selected = fineModeStore.state.selectedImages.length
  if (selected < need) {
    imageWarningMsg.value = `当前已选 ${selected} 张图片，需要 ${need} 张。请前往「配图」步骤选取更多图片。`
    showImageWarning.value = true
    return false
  }
  return true
}

async function handleGenerate() {
  if (isGenerating.value || !isReady.value) return
  if (!checkImageFolder()) return
  isGenerating.value = true
  taskProgress.value = 0
  taskStatus.value = '提交任务...'
  result.value = null
  errorMsg.value = ''

  try {
    const { voiceConfig, rewriteResult, selectedImages } = fineModeStore.state

    const { task_id } = await generateVideoAsync({
      text: rewriteResult,
      mode: 'fixed',
      n_scenes: nScenes.value,
      tts_speed: voiceConfig.speed,
      frame_template: selectedTemplate.value,
      bgm_path: selectedBgm.value || undefined,
      bgm_volume: bgmVolume.value,
      image_paths: selectedImages.length > 0 ? selectedImages : undefined,
    })

    pollTimer = setInterval(async () => {
      try {
        const task = await getTask(task_id)
        taskStatus.value = task.status
        if (task.progress !== undefined) taskProgress.value = task.progress
        if (task.status === 'completed' && task.result) {
          result.value = task.result
          isGenerating.value = false
          stopPolling()
        } else if (task.status === 'failed') {
          errorMsg.value = task.error ?? '视频生成失败'
          isGenerating.value = false
          stopPolling()
        }
      } catch { /* ignore poll errors */ }
    }, 2000)
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : '提交失败，请确认后端已启动'
    isGenerating.value = false
  }
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onUnmounted(() => stopPolling())
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 overflow-y-auto px-6 py-6">
      <div class="max-w-lg mx-auto space-y-5">

        <div class="rounded-lg border bg-muted/40 p-4 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">书名</span>
            <span class="font-medium">{{ fineModeStore.state.bookName || '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">文案字数</span>
            <span class="font-medium">{{ textCharCount }} 字</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">配音引擎</span>
            <span class="font-medium">{{ fineModeStore.state.voiceConfig.provider }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">图片数量</span>
            <span class="font-medium">{{ fineModeStore.state.selectedImages.length || 0 }} 张</span>
          </div>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium">视频模式</label>
          <select
            v-model="selectedVideoMode"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          >
            <option v-for="m in VIDEO_MODES" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium">背景音乐</label>
          <select
            v-model="selectedBgm"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          >
            <option v-for="bgm in BGM_OPTIONS" :key="bgm.value" :value="bgm.value">{{ bgm.label }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium">帧模板</label>
          <select
            v-model="selectedTemplate"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          >
            <option v-for="t in TEMPLATE_OPTIONS" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">场景数</label>
            <span class="text-xs text-muted-foreground">建议 {{ suggestedScenes }} 个</span>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" :disabled="nScenes <= 3" @click="nScenes--">−</Button>
            <span class="w-10 text-center font-mono text-sm">{{ nScenes }}</span>
            <Button variant="outline" size="sm" :disabled="nScenes >= 15" @click="nScenes++">+</Button>
            <Button variant="ghost" size="sm" class="ml-2 text-xs" @click="nScenes = suggestedScenes">使用建议</Button>
          </div>
        </div>

        <Button class="w-full h-12 text-base" :disabled="isGenerating || !isReady" @click="handleGenerate">
          {{ isGenerating ? '生成中...' : '开始生成视频' }}
        </Button>

        <p v-if="!isReady" class="text-xs text-center text-muted-foreground">
          {{ !fineModeStore.state.rewriteResult ? '请先在「洗稿」步骤生成文案' : '文案太短，至少需要 50 个中文字' }}
        </p>

        <div v-if="isGenerating" class="space-y-2">
          <Progress :model-value="taskProgress" class="h-2" />
          <p class="text-xs text-center text-muted-foreground">{{ taskStatus }} — {{ taskProgress }}%</p>
        </div>

        <div v-if="errorMsg" class="text-sm text-destructive">{{ errorMsg }}</div>

        <div v-if="result" class="rounded-lg border bg-muted/50 p-4 space-y-2">
          <p class="text-sm font-medium text-primary">视频已生成</p>
          <p class="text-xs text-muted-foreground">时长: {{ result.duration.toFixed(1) }} 秒</p>
          <p class="text-xs text-muted-foreground">大小: {{ (result.file_size / 1024 / 1024).toFixed(1) }} MB</p>
          <p class="text-xs text-muted-foreground truncate">{{ result.video_url }}</p>
        </div>

        <div v-if="showImageWarning" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showImageWarning = false">
          <div class="bg-card rounded-lg border shadow-xl p-6 max-w-sm mx-4 space-y-4">
            <p class="text-sm font-medium">⚠️ 图片数量不足</p>
            <p class="text-xs text-muted-foreground">{{ imageWarningMsg }}</p>
            <div class="flex justify-end">
              <Button variant="outline" size="sm" @click="showImageWarning = false">知道了</Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center px-6 py-3 border-t bg-card flex-shrink-0">
      <Button variant="outline" @click="fineModeStore.prevStep()">← 上一步</Button>
    </div>
  </div>
</template>
