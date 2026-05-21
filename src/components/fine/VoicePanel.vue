<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFineModeStore } from '@/stores/fineMode'
import { useSettingsStore } from '@/stores/settings'
import { synthesizeTTS } from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Slider from '@/components/ui/Slider.vue'

const fineModeStore = useFineModeStore()
const settingsStore = useSettingsStore()
const voiceConfig = fineModeStore.state.voiceConfig

const isSynthesizing = ref(false)
const audioResult = ref<{ path: string; duration: number } | null>(null)
const errorMsg = ref('')

const customRefAudio = computed(() => settingsStore.settings.tts.referenceAudioPath)

const hasCustomVoice = computed(() => !!customRefAudio.value)

function handleProviderChange(val: string) {
  fineModeStore.setVoiceConfig({ provider: val as 'mimo' | 'indextts' | 'minimax' | 'cosyvoice' })
}

async function handleGenerateVoice() {
  const text = fineModeStore.state.rewriteResult
  if (!text.trim()) {
    errorMsg.value = '请先在「洗稿」步骤生成文案'
    return
  }
  if (!customRefAudio.value) {
    errorMsg.value = '请在设置页上传参考音频以使用克隆音色'
    return
  }
  isSynthesizing.value = true
  errorMsg.value = ''
  audioResult.value = null
  try {
    const res = await synthesizeTTS({ text })
    audioResult.value = { path: res.audio_path, duration: res.duration }
    fineModeStore.setVoiceResult({ path: res.audio_path, duration: res.duration })
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : '配音失败，请确认后端已启动'
  } finally {
    isSynthesizing.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 overflow-y-auto px-6 py-6">
      <div class="max-w-lg mx-auto space-y-6">

        <div v-if="!hasCustomVoice" class="rounded-lg border border-amber-200 bg-amber-50 p-4 space-y-2">
          <p class="text-sm font-medium text-amber-700">尚未上传参考音频</p>
          <p class="text-xs text-amber-600">请先在 <router-link to="/settings" class="underline font-medium">设置页 → 语音合成</router-link> 上传参考音频以使用克隆音色</p>
        </div>

        <div v-else class="rounded-lg border bg-muted/50 p-4 space-y-2">
          <p class="text-sm font-medium">🎤 我的克隆音色</p>
          <p class="text-xs text-muted-foreground">参考音频：{{ customRefAudio.split('/').pop() || customRefAudio.split('\\').pop() }}</p>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium">配音引擎</label>
          <select
            :model-value="voiceConfig.provider"
            @change="handleProviderChange(($event.target as HTMLSelectElement).value)"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          >
            <option value="cosyvoice">CosyVoice2（本地）</option>
            <option value="indextts">IndexTTS（本地·备用）</option>
            <option value="mimo">Mimo</option>
            <option value="minimax">MiniMax 海螺</option>
          </select>
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">语速</label>
            <span class="text-sm text-muted-foreground">{{ voiceConfig.speed.toFixed(1) }}</span>
          </div>
          <Slider
            :model-value="[voiceConfig.speed]"
            @update:model-value="fineModeStore.setVoiceConfig({ speed: Number($event[0]) })"
            :min="0.5" :max="2.0" :step="0.1"
          />
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">音量</label>
            <span class="text-sm text-muted-foreground">{{ voiceConfig.volume }}</span>
          </div>
          <Slider
            :model-value="[voiceConfig.volume]"
            @update:model-value="fineModeStore.setVoiceConfig({ volume: Number($event[0]) })"
            :min="0" :max="100" :step="5"
          />
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">音调</label>
            <span class="text-sm text-muted-foreground">{{ voiceConfig.pitch > 0 ? '+' : '' }}{{ voiceConfig.pitch }}</span>
          </div>
          <Slider
            :model-value="[voiceConfig.pitch]"
            @update:model-value="fineModeStore.setVoiceConfig({ pitch: Number($event[0]) })"
            :min="-20" :max="20" :step="1"
          />
        </div>

        <Button
          variant="outline"
          class="w-full"
          :disabled="isSynthesizing || !hasCustomVoice"
          @click="handleGenerateVoice"
        >
          {{ isSynthesizing ? '合成中...' : '生成配音' }}
        </Button>

        <div v-if="errorMsg" class="text-sm text-destructive">{{ errorMsg }}</div>

        <div v-if="audioResult" class="rounded-lg border bg-muted/50 p-4 space-y-2">
          <p class="text-sm font-medium text-primary">配音已生成</p>
          <p class="text-xs text-muted-foreground">文件: {{ audioResult.path }}</p>
          <p class="text-xs text-muted-foreground">时长: {{ audioResult.duration.toFixed(1) }} 秒</p>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between px-6 py-3 border-t bg-card flex-shrink-0">
      <Button variant="outline" @click="fineModeStore.prevStep()">← 上一步</Button>
      <Button @click="fineModeStore.nextStep()">下一步 →</Button>
    </div>
  </div>
</template>
