<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { testLlmConnection } from '@/services/api'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Slider from '@/components/ui/Slider.vue'

const settingsStore = useSettingsStore()

const llm = reactive({ ...settingsStore.settings.llm })
const showLlmKey = ref(false)
const isLlmTesting = ref(false)
const llmTestMsg = ref('')
const llmTestOk = ref(false)
const llmLocked = ref(!!settingsStore.settings.llm.apiKey)
const showApiSection = ref(true)

async function handleLlmTest() {
  isLlmTesting.value = true
  llmTestMsg.value = ''
  try {
    const res = await testLlmConnection({ provider: llm.provider, api_base: llm.apiBase, api_key: llm.apiKey, model: llm.model })
    llmTestOk.value = res.ok
    llmTestMsg.value = res.detail
    if (res.ok) {
      settingsStore.updateLlmConfig({ apiKey: llm.apiKey, apiBase: llm.apiBase, model: llm.model, provider: llm.provider, temperature: llm.temperature })
      llmLocked.value = true
    }
  } catch (e: unknown) {
    llmTestOk.value = false
    llmTestMsg.value = e instanceof Error ? e.message : '测试失败'
  } finally {
    isLlmTesting.value = false
  }
}

function handleLlmReset() {
  llm.apiKey = ''
  llmLocked.value = false
  llmTestMsg.value = ''
  settingsStore.updateLlmConfig({ apiKey: '' })
}

const tts = reactive({ ...settingsStore.settings.tts })
const refAudioName = ref(tts.referenceAudioPath ? tts.referenceAudioPath.replace(/\\/g, '/').split('/').pop() || '' : '')
const fileInputRef = ref<HTMLInputElement | null>(null)

function handleSelectAudio() { fileInputRef.value?.click() }
function handleAudioFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const path = (file as any).path
  if (path) {
    tts.referenceAudioPath = path
    refAudioName.value = file.name
    saveTts()
  }
  input.value = ''
}
function clearAudio() { tts.referenceAudioPath = ''; refAudioName.value = ''; saveTts() }
function saveTts() { settingsStore.updateTtsConfig({ ...tts }) }

const img = reactive({ ...settingsStore.settings.image })
function saveImg() { settingsStore.updateImageConfig({ ...img }) }

const folderInputRef = ref<HTMLInputElement | null>(null)
function handleSelectFolder() { folderInputRef.value?.click() }
function handleFolderSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return
  const firstPath = (files[0] as any).path || (files[0] as any).webkitRelativePath
  if (firstPath) {
    const dir = firstPath.replace(/[/\\][^/\\]+$/, '')
    img.imageFolder = dir
    saveImg()
  }
  input.value = ''
}

const outputPath = ref(settingsStore.settings.outputPath)
function saveOutput() { settingsStore.setOutputPath(outputPath.value) }
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-xl mx-auto p-6 space-y-5">

      <h1 class="text-lg font-semibold">⚙️ 设置</h1>

      <Card>
        <CardHeader class="cursor-pointer select-none" @click="showApiSection = !showApiSection">
          <CardTitle class="flex items-center gap-2 text-base">
            <span>{{ showApiSection ? '▾' : '▸' }}</span>
            📝 洗稿 API
            <span v-if="llmLocked" class="text-xs font-normal text-green-600 ml-2">🔒 已锁定</span>
          </CardTitle>
        </CardHeader>
        <CardContent v-if="showApiSection" class="space-y-3">
          <div v-if="llmTestMsg" :class="['px-3 py-2 rounded text-sm', llmTestOk ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700']">
            {{ llmTestMsg }}
          </div>

          <div>
            <label class="text-xs text-muted-foreground">提供商</label>
            <select v-model="llm.provider" :disabled="llmLocked" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1 disabled:opacity-60">
              <option value="DeepSeek">DeepSeek</option>
              <option value="通义千问">通义千问</option>
              <option value="豆包">豆包</option>
              <option value="OpenAI">OpenAI</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-muted-foreground">API Base</label>
            <Input v-model="llm.apiBase" :disabled="llmLocked" class="mt-1" />
          </div>
          <div>
            <label class="text-xs text-muted-foreground">API Key</label>
            <div class="relative mt-1">
              <Input :type="showLlmKey ? 'text' : 'password'" v-model="llm.apiKey" :disabled="llmLocked" placeholder="sk-..." />
              <button v-if="!llmLocked" class="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground" @click="showLlmKey = !showLlmKey">{{ showLlmKey ? '隐藏' : '显示' }}</button>
            </div>
          </div>
          <div>
            <label class="text-xs text-muted-foreground">模型名称</label>
            <Input v-model="llm.model" :disabled="llmLocked" class="mt-1" />
          </div>
          <div class="flex gap-2">
            <Button v-if="!llmLocked" :disabled="!llm.apiKey || isLlmTesting" @click="handleLlmTest">{{ isLlmTesting ? '检测中...' : '检测连接' }}</Button>
            <Button v-else variant="outline" @click="handleLlmReset">修改配置</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-base">🔊 语音合成</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div>
            <label class="text-xs text-muted-foreground">配音引擎</label>
            <select v-model="tts.provider" @change="saveTts" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1">
              <option value="cosyvoice">CosyVoice2（本地·推荐）</option>
              <option value="indextts">IndexTTS（本地·备用）</option>
              <option value="mimo">Mimo</option>
              <option value="minimax">MiniMax 海螺</option>
            </select>
          </div>

          <template v-if="tts.provider === 'mimo'">
            <div>
              <label class="text-xs text-muted-foreground">Mimo API Key</label>
              <Input v-model="tts.mimoApiKey" @change="saveTts" placeholder="sk-..." class="mt-1" />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">Mimo Base URL</label>
              <Input v-model="tts.mimoBaseUrl" @change="saveTts" placeholder="https://api.mimo.com/v1" class="mt-1" />
            </div>
          </template>

          <template v-if="tts.provider === 'minimax'">
            <div>
              <label class="text-xs text-muted-foreground">MiniMax API Key</label>
              <Input v-model="tts.minimaxApiKey" @change="saveTts" placeholder="eyJ..." class="mt-1" />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">海螺 voice_id（可选）</label>
              <Input v-model="tts.minimaxVoiceId" @change="saveTts" placeholder="留空使用默认音色，填克隆音色ID则用自定义" class="mt-1" />
            </div>
          </template>

          <div>
            <label class="text-xs text-muted-foreground">参考音频（声音克隆 · 5~8 秒最佳）</label>
            <input ref="fileInputRef" type="file" accept="audio/*" class="hidden" @change="handleAudioFile" />
            <div v-if="refAudioName" class="flex items-center gap-2 mt-1">
              <span class="text-sm text-muted-foreground truncate flex-1">{{ refAudioName }}</span>
              <Button variant="ghost" size="sm" class="text-destructive" @click="clearAudio">删除</Button>
            </div>
            <Button v-else variant="outline" class="w-full mt-1 text-sm" @click="handleSelectAudio">选择音频文件</Button>
          </div>

          <div>
            <div class="flex justify-between"><label class="text-xs text-muted-foreground">语速</label><span class="text-xs">{{ tts.speed.toFixed(1) }}</span></div>
            <Slider :model-value="[tts.speed]" @update:model-value="tts.speed = Number($event[0]); saveTts()" :min="0.5" :max="2" :step="0.1" class="mt-1" />
          </div>
          <div>
            <div class="flex justify-between"><label class="text-xs text-muted-foreground">音量</label><span class="text-xs">{{ tts.volume }}</span></div>
            <Slider :model-value="[tts.volume]" @update:model-value="tts.volume = Number($event[0]); saveTts()" :min="0" :max="100" :step="5" class="mt-1" />
          </div>
          <div>
            <div class="flex justify-between"><label class="text-xs text-muted-foreground">音调</label><span class="text-xs">{{ tts.pitch > 0 ? '+' : '' }}{{ tts.pitch }}</span></div>
            <Slider :model-value="[tts.pitch]" @update:model-value="tts.pitch = Number($event[0]); saveTts()" :min="-20" :max="20" :step="1" class="mt-1" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-base">🖼️ 图片</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div>
            <label class="text-xs text-muted-foreground">图片文件夹</label>
            <input ref="folderInputRef" type="file" webkitdirectory directory multiple class="hidden" @change="handleFolderSelected" />
            <div v-if="img.imageFolder" class="flex items-center gap-2 mt-1">
              <span class="text-sm text-muted-foreground truncate flex-1">{{ img.imageFolder }}</span>
              <Button variant="ghost" size="sm" class="text-destructive" @click="img.imageFolder = ''; saveImg()">清空</Button>
            </div>
            <Button v-else variant="outline" class="w-full mt-1 text-sm" @click="handleSelectFolder">选择图库文件夹</Button>
          </div>

          <div>
            <div class="flex justify-between"><label class="text-xs text-muted-foreground">每次使用图片数量</label><span class="text-xs">{{ img.imageCount }}</span></div>
            <div class="flex items-center gap-2 mt-1">
              <Button variant="outline" size="sm" :disabled="img.imageCount <= 1" @click="img.imageCount--; saveImg()">−</Button>
              <span class="w-8 text-center text-sm">{{ img.imageCount }}</span>
              <Button variant="outline" size="sm" :disabled="img.imageCount >= 20" @click="img.imageCount++; saveImg()">+</Button>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <label class="text-sm">Ken Burns 效果</label>
              <p class="text-xs text-muted-foreground">视频播放时自动缓慢缩放/平移</p>
            </div>
            <button role="switch" :aria-checked="img.kenBurns" :class="['inline-flex h-5 w-9 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', img.kenBurns ? 'bg-primary' : 'bg-input']" @click="img.kenBurns = !img.kenBurns; saveImg()">
              <span :class="['block h-4 w-4 rounded-full bg-background shadow-sm transition-transform', img.kenBurns ? 'translate-x-4' : 'translate-x-0']" />
            </button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-base">📂 视频输出目录</CardTitle>
        </CardHeader>
        <CardContent class="space-y-3">
          <div>
            <label class="text-xs text-muted-foreground">默认自动生成（output/时间戳），可手动指定</label>
            <Input v-model="outputPath" placeholder="留空则自动生成" class="mt-1" />
          </div>
          <Button @click="saveOutput">保存</Button>
        </CardContent>
      </Card>

      <div class="h-12" />
    </div>
  </div>
</template>
