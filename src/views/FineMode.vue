<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useFineModeStore } from '@/stores/fineMode'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import { useSettingsStore } from '@/stores/settings'
import { BOOK_CATEGORIES } from '@/data/bookList'
import RewritePanel from '@/components/fine/RewritePanel.vue'
import VoicePanel from '@/components/fine/VoicePanel.vue'
import ImagePanel from '@/components/fine/ImagePanel.vue'
import VideoPanel from '@/components/fine/VideoPanel.vue'
import StepIndicator from '@/components/fine/StepIndicator.vue'
import Button from '@/components/ui/Button.vue'

const fineModeStore = useFineModeStore()
const bookDefaultsStore = useBookDefaultsStore()
const settingsStore = useSettingsStore()

const enableRewrite = ref(true)
const enableVoice = ref(true)
const enableImage = ref(true)
const enableVideo = ref(true)
const selectedBook = ref(fineModeStore.state.bookName || '')
const bookConfigLoaded = ref(false)
const showSwitchWarning = ref(false)

watch(enableVoice, (on) => { if (!on) { enableImage.value = false; enableVideo.value = false } })
watch(enableImage, (on) => { if (!on) enableVideo.value = false })
watch(enableVoice, (on) => { if (on) enableImage.value = true })
watch(enableImage, (on) => { if (on && enableVoice.value) enableVideo.value = true })

watch(selectedBook, (name) => {
  if (!name || bookConfigLoaded.value) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  if (!cfg || !bookDefaultsStore.defaults[name]) return
  fineModeStore.setVoiceConfig({ provider: cfg.voiceProvider as 'mimo' | 'indextts' | 'minimax' | 'cosyvoice' })
  fineModeStore.setImageConfig({ kenBurns: cfg.kenBurns, imageCount: cfg.imageCount, imageFolder: settingsStore.settings.image.imageFolder })
  fineModeStore.setBook(name, fineModeStore.state.rawText)
  bookConfigLoaded.value = true
})

const stepLabels = computed(() => {
  const labels: string[] = []
  if (enableRewrite.value) labels.push('洗稿')
  if (enableVoice.value) labels.push('配音')
  if (enableImage.value) labels.push('配图')
  if (enableVideo.value) labels.push('生成视频')
  return labels
})

const enabledSteps = computed(() => {
  const steps: string[] = []
  if (enableRewrite.value) steps.push('rewrite')
  if (enableVoice.value) steps.push('voice')
  if (enableImage.value) steps.push('image')
  if (enableVideo.value) steps.push('generate')
  return steps
})

const currentStep = computed(() => fineModeStore.state.currentStep)

const panelComponent = computed(() => {
  switch (currentStep.value) {
    case 'rewrite': return RewritePanel
    case 'voice': return VoicePanel
    case 'image': return ImagePanel
    case 'generate': return VideoPanel
    default: return RewritePanel
  }
})

const currentLabelIndex = computed(() => enabledSteps.value.indexOf(currentStep.value))

function handleGoToStep(index: number) {
  const step = enabledSteps.value[index]
  if (step) fineModeStore.setStep(step as any)
}

function toggleAllSwitch(label: string) {
  if (label === '洗稿') {
    enableRewrite.value = !enableRewrite.value
  } else if (label === '配音') {
    enableVoice.value = !enableVoice.value
  } else if (label === '配图') {
    enableImage.value = !enableImage.value
  } else if (label === '生成视频') {
    enableVideo.value = !enableVideo.value
  }
}

const flowTip = computed(() => {
  if (!enableRewrite.value && !enableVoice.value) return '跳过所有步骤，无流程可执行'
  if (!enableRewrite.value) return '跳过洗稿 → 直接使用原文'
  if (!enableVoice.value) return '只走洗稿流程'
  if (!enableImage.value) return '只走洗稿 + 配音'
  if (!enableVideo.value) return '只走洗稿 + 配音 + 配图'
  return '全流程：洗稿 → 配音 → 配图 → 生成视频'
})

const hasDefaults = computed(() => selectedBook.value && !!bookDefaultsStore.defaults[selectedBook.value])

const hasStarted = computed(() =>
  !!fineModeStore.state.rewriteResult ||
  !!fineModeStore.state.voiceResult ||
  fineModeStore.state.selectedImages.length > 0
)

function handleBookChange() {
  if (hasStarted.value) {
    showSwitchWarning.value = true
    return
  }
  applyBookChange()
}

function applyBookChange() {
  showSwitchWarning.value = false
  bookConfigLoaded.value = false
  fineModeStore.state.bookName = selectedBook.value
  if (!selectedBook.value || !bookDefaultsStore.defaults[selectedBook.value]) return
  const cfg = bookDefaultsStore.getBookConfig(selectedBook.value)
  fineModeStore.setVoiceConfig({ provider: cfg.voiceProvider as 'mimo' | 'indextts' | 'minimax' | 'cosyvoice' })
  fineModeStore.setImageConfig({ kenBurns: cfg.kenBurns, imageCount: cfg.imageCount, imageFolder: cfg.imageFolder || settingsStore.settings.image.imageFolder })
  bookConfigLoaded.value = true
}

function cancelSwitchBook() {
  selectedBook.value = fineModeStore.state.bookName
  showSwitchWarning.value = false
  bookConfigLoaded.value = true
}

function confirmSwitchBook() {
  fineModeStore.setBook(selectedBook.value, fineModeStore.state.rawText)
  applyBookChange()
}
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-shrink-0 border-b bg-card">
      <div class="flex items-center gap-4 px-6 py-2">
        <span class="text-sm font-medium text-muted-foreground shrink-0">📖 选择书籍</span>
        <select
          v-model="selectedBook"
          @change="handleBookChange"
          class="flex h-8 w-[200px] rounded-md border border-input bg-background px-2 py-0.5 text-sm"
        >
          <option value="">— 不指定书籍 —</option>
          <option v-for="book in BOOK_CATEGORIES" :key="book" :value="book">{{ book }}</option>
        </select>
        <span v-if="hasDefaults" class="text-xs text-green-600">✓ 已加载默认配置</span>
        <span v-else-if="selectedBook" class="text-xs text-muted-foreground">未设置默认配置，使用全局设置</span>
      </div>
      <div class="flex items-center gap-6 px-6 py-3 flex-wrap border-t">
        <span class="text-sm font-medium text-muted-foreground">创作流程</span>

        <label :class="['inline-flex items-center gap-1.5 cursor-pointer select-none', !enableRewrite && 'opacity-50']">
          <button role="switch" :aria-checked="enableRewrite" :class="['inline-flex h-5 w-9 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', enableRewrite ? 'bg-primary' : 'bg-input']" @click="toggleAllSwitch('洗稿')">
            <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', enableRewrite ? 'translate-x-4' : 'translate-x-0']" />
          </button>
          <span class="text-sm">📝 洗稿</span>
        </label>

        <label :class="['inline-flex items-center gap-1.5 cursor-pointer select-none', !enableVoice && 'opacity-50']">
          <button role="switch" :aria-checked="enableVoice" :class="['inline-flex h-5 w-9 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', enableVoice ? 'bg-primary' : 'bg-input']" @click="toggleAllSwitch('配音')">
            <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', enableVoice ? 'translate-x-4' : 'translate-x-0']" />
          </button>
          <span class="text-sm">🔊 配音</span>
        </label>

        <label :class="['inline-flex items-center gap-1.5 cursor-pointer select-none', (!enableImage || !enableVoice) && 'opacity-50']">
          <button role="switch" :aria-checked="enableImage" :disabled="!enableVoice" :class="['inline-flex h-5 w-9 items-center rounded-full border-2 border-transparent transition-colors', enableImage ? 'bg-primary' : 'bg-input']" @click="toggleAllSwitch('配图')">
            <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', enableImage ? 'translate-x-4' : 'translate-x-0']" />
          </button>
          <span class="text-sm">🖼️ 配图</span>
        </label>

        <label :class="['inline-flex items-center gap-1.5 cursor-pointer select-none', (!enableVideo || !enableImage) && 'opacity-50']">
          <button role="switch" :aria-checked="enableVideo" :disabled="!enableImage" :class="['inline-flex h-5 w-9 items-center rounded-full border-2 border-transparent transition-colors', enableVideo ? 'bg-primary' : 'bg-input']" @click="toggleAllSwitch('生成视频')">
            <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', enableVideo ? 'translate-x-4' : 'translate-x-0']" />
          </button>
          <span class="text-sm">🎬 视频</span>
        </label>

        <span class="text-xs text-muted-foreground ml-auto">{{ flowTip }}</span>
      </div>
    </div>

    <StepIndicator
      :steps="stepLabels"
      :current-index="currentLabelIndex >= 0 ? currentLabelIndex : 0"
      @go-to-step="handleGoToStep"
    />

    <div class="flex-1 overflow-hidden">
      <KeepAlive>
        <component :is="panelComponent" :key="currentStep" />
      </KeepAlive>
    </div>

    <div v-if="showSwitchWarning" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="cancelSwitchBook">
      <div class="bg-card rounded-lg border shadow-xl p-6 max-w-sm mx-4 space-y-4">
        <p class="text-sm font-medium">确定要切换书籍吗？</p>
        <p class="text-xs text-muted-foreground">你当前的洗稿结果、配音、图片选择将被清空，此操作不可撤销。</p>
        <div class="flex justify-end gap-2">
          <Button variant="outline" size="sm" @click="cancelSwitchBook">取消</Button>
          <Button variant="destructive" size="sm" @click="confirmSwitchBook">清空并切换</Button>
        </div>
      </div>
    </div>
  </div>
</template>
