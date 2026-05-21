import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { AppSettings } from '@/types'

const STORAGE_KEY = 'pixelle-video-settings'

function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as AppSettings
  } catch { /* ignore */ }
  return {
    llm: {
      provider: 'DeepSeek',
      apiKey: '',
      apiBase: 'https://api.deepseek.com',
      model: 'deepseek-chat',
      temperature: 0.7,
      maxTokens: 4096,
    },
    tts: {
      provider: 'cosyvoice',
      voiceId: '',
      speed: 1.0,
      pitch: 0,
      volume: 80,
      referenceAudioPath: '',
      mimoApiKey: '',
      mimoBaseUrl: '',
      minimaxApiKey: '',
      minimaxVoiceId: '',
    },
    image: {
      imageFolder: '',
      imageCount: 3,
      width: 1080,
      height: 1920,
      kenBurns: true,
    },
    outputPath: '',
    pythonPort: 19876,
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>(loadSettings())

  watch(
    settings,
    (val) => {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(val)) } catch { /* ignore */ }
    },
    { deep: true },
  )

  function updateLlmConfig(c: Partial<AppSettings['llm']>): void {
    Object.assign(settings.value.llm, c)
  }

  function updateTtsConfig(c: Partial<AppSettings['tts']>): void {
    Object.assign(settings.value.tts, c)
  }

  function updateImageConfig(c: Partial<AppSettings['image']>): void {
    Object.assign(settings.value.image, c)
  }

  function setOutputPath(path: string): void {
    settings.value.outputPath = path
  }

  return {
    settings,
    updateLlmConfig,
    updateTtsConfig,
    updateImageConfig,
    setOutputPath,
  }
})
