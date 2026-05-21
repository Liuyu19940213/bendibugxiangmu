import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { GlobalConfig, BatchModule, BatchProgress, ModuleTemplate, ModuleTemplateModule } from '@/types'

const TEMPLATES_KEY = 'pixelle_batch_templates'
const PROGRESS_KEY = 'pixelle_batch_progress'

export const useBatchStore = defineStore('batch', () => {
  const globalConfig = ref<GlobalConfig>({
    voiceId: '',
    voiceType: 'clone',
    voiceProvider: 'mimo',
    bgmPath: 'default.mp3',
    bgmStyle: '宁静',
    durationMin: 480,
    durationMax: 780,
    videoMode: 'kenburns',
    rewriteParams: {
      referenceCount: 3,
      style: '沉稳大气',
      targetWordsMin: 3000,
      targetWordsMax: 4500,
      rewriteMode: 'flexible' as const,
    },
  })

  const modules = ref<BatchModule[]>([])
  const batchId = ref<string | null>(null)
  const isRunning = ref(false)
  const progress = ref<BatchProgress>({
    total: 0, completed: 0, failed: 0, skipped: 0,
    currentBook: null, percent: 0,
  })

  const enabledCount = computed<number>(() => modules.value.filter((m) => m.enabled).length)

  function addModule(bookName: string, rawText = '', configOverride?: Partial<GlobalConfig>): BatchModule {
    const m: BatchModule = {
      id: crypto.randomUUID(),
      bookName,
      rawText,
      enabled: true,
      status: 'idle',
      sortOrder: modules.value.length,
      resultText: undefined,
      configOverride,
    }
    modules.value.push(m)
    return m
  }

  function removeModule(id: string): void { modules.value = modules.value.filter((m) => m.id !== id) }
  function toggleModule(id: string): void {
    const m = modules.value.find((m) => m.id === id)
    if (m) m.enabled = !m.enabled
  }

  function syncByName(bookName: string, override: Partial<GlobalConfig>): void {
    modules.value.filter((m) => m.bookName === bookName).forEach((m) => {
      m.configOverride = { ...m.configOverride, ...override }
    })
  }

  function updateRawText(id: string, text: string): void {
    const m = modules.value.find((m) => m.id === id)
    if (m) m.rawText = text
  }

  function sortModules(): void { modules.value.sort((a, b) => a.bookName.localeCompare(b.bookName, 'zh')) }

  function resetProgress() {
    modules.value.forEach((m) => { m.status = 'idle'; m.errorMessage = undefined; m.resultText = undefined })
    progress.value = { total: 0, completed: 0, failed: 0, skipped: 0, currentBook: null, percent: 0 }
    batchId.value = null
    isRunning.value = false
    persistProgress()
  }

  function persistProgress() {
    try {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify({
        progress: progress.value,
        modules: modules.value.map((m) => ({ id: m.id, status: m.status, errorMessage: m.errorMessage, resultText: m.resultText })),
        isRunning: isRunning.value,
      }))
    } catch { /* ignore */ }
  }

  function restoreProgress(): boolean {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY)
      if (!raw) return false
      const data = JSON.parse(raw)
      if (!data.isRunning && data.progress.total === 0) return false
      if (Array.isArray(data.modules)) {
        for (const sm of data.modules) {
          const m = modules.value.find((x) => x.id === sm.id)
          if (m) { m.status = sm.status || 'idle'; m.errorMessage = sm.errorMessage; m.resultText = sm.resultText }
        }
      }
      if (data.progress) progress.value = data.progress
      isRunning.value = !!data.isRunning
      return true
    } catch { return false }
  }

  watch(() => modules.value.map((m) => ({ id: m.id, status: m.status })), () => {
    if (isRunning.value) persistProgress()
  }, { deep: true })

  const templates = ref<ModuleTemplate[]>([])

  function loadTemplates() {
    try { const raw = localStorage.getItem(TEMPLATES_KEY); if (raw) templates.value = JSON.parse(raw) } catch { templates.value = [] }
  }

  function persistTemplates() { localStorage.setItem(TEMPLATES_KEY, JSON.stringify(templates.value)) }

  function saveTemplate(name: string): ModuleTemplate {
    const tpl: ModuleTemplate = {
      id: crypto.randomUUID(), name, createdAt: new Date().toISOString(),
      globalConfig: JSON.parse(JSON.stringify(globalConfig.value)),
      modules: modules.value.filter((m) => m.enabled).map((m): ModuleTemplateModule => ({
        bookName: m.bookName, rawText: m.rawText, enabled: true, sortOrder: m.sortOrder,
      })),
    }
    templates.value.push(tpl)
    if (templates.value.length > 20) templates.value = templates.value.slice(-20)
    persistTemplates()
    return tpl
  }

  function deleteTemplate(id: string) { templates.value = templates.value.filter((t) => t.id !== id); persistTemplates() }

  function applyTemplate(id: string) {
    const tpl = templates.value.find((t) => t.id === id)
    if (!tpl) return
    globalConfig.value = JSON.parse(JSON.stringify(tpl.globalConfig))
    modules.value = tpl.modules.map((m, i): BatchModule => ({
      id: crypto.randomUUID(), bookName: m.bookName, rawText: m.rawText,
      enabled: true, sortOrder: i, status: 'idle', resultText: undefined,
    }))
  }

  loadTemplates()

  return {
    globalConfig, modules, batchId, isRunning, progress, enabledCount,
    addModule, removeModule, toggleModule, updateRawText, syncByName,
    sortModules, resetProgress, persistProgress, restoreProgress,
    templates, saveTemplate, deleteTemplate, applyTemplate, loadTemplates,
  }
})
