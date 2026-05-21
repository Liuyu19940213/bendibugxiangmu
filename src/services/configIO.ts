import type { AppSettings, GlobalConfig } from '@/types'

export interface TemplateConfig {
  path: string
  fontSize: number
  lineHeight: number
  letterSpacing: number
  textColor: string
  backgroundColor: string
  opacity: number
  fontFamily: string
  textAlign: 'left' | 'center' | 'right'
  textShadowColor: string
  textShadowBlur: number
  textShadowOffsetX: number
  textShadowOffsetY: number
}

export interface ExportSchema {
  version: 1
  name: string
  exportedAt: string
  settings: Omit<AppSettings, 'pythonPort'>
  batchConfig: GlobalConfig
  template?: TemplateConfig
}

export interface ImportResult {
  success: boolean
  summary: string
  warnApiKey: boolean
}

interface ExportInput {
  name: string
  settings: AppSettings
  batchConfig: GlobalConfig
  template?: TemplateConfig
}

export function buildExportPayload(input: ExportInput): ExportSchema {
  const now = new Date().toISOString()
  return {
    version: 1,
    name: input.name,
    exportedAt: now,
    settings: {
      llm: { ...input.settings.llm },
      tts: { ...input.settings.tts },
      image: { ...input.settings.image },
      outputPath: input.settings.outputPath,
    },
    batchConfig: JSON.parse(JSON.stringify(input.batchConfig)),
    template: input.template ? JSON.parse(JSON.stringify(input.template)) : undefined,
  }
}

export function downloadJsonFile(data: ExportSchema): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const safeName = data.name.replace(/[<>:"/\\|?*]/g, '_')
  a.download = `pixelle-video-template-${safeName}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function readJsonFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsText(file, 'utf-8')
  })
}

export function validateImportPayload(raw: unknown): { ok: true; data: ExportSchema } | { ok: false; error: string } {
  if (typeof raw !== 'object' || raw === null) {
    return { ok: false, error: '文件内容不是有效的 JSON 对象' }
  }
  const obj = raw as Record<string, unknown>
  if (obj.version !== 1) {
    return { ok: false, error: `不支持的版本: ${obj.version}（仅支持版本 1）` }
  }
  if (!obj.settings || typeof obj.settings !== 'object') {
    return { ok: false, error: '缺少 settings 字段' }
  }
  if (!obj.batchConfig || typeof obj.batchConfig !== 'object') {
    return { ok: false, error: '缺少 batchConfig 字段' }
  }
  return { ok: true, data: obj as unknown as ExportSchema }
}

export interface ApplyImportInput {
  settings: ExportSchema['settings']
  batchConfig: ExportSchema['batchConfig']
}

export function applyImportedSettings(
  input: ApplyImportInput,
  setters: {
    updateLlmConfig: (c: Partial<AppSettings['llm']>) => void
    updateTtsConfig: (c: Partial<AppSettings['tts']>) => void
    updateImageConfig: (c: Partial<AppSettings['image']>) => void
    setOutputPath: (p: string) => void
    setGlobalConfig: (c: Partial<GlobalConfig>) => void
  },
): ImportResult {
  const s = input.settings
  const b = input.batchConfig
  const warnApiKey = !!(s.llm?.apiKey)

  setters.updateLlmConfig({
    provider: s.llm?.provider,
    apiBase: s.llm?.apiBase,
    model: s.llm?.model,
    temperature: s.llm?.temperature,
    maxTokens: s.llm?.maxTokens,
    ...(s.llm?.apiKey ? { apiKey: s.llm.apiKey } : {}),
  })

  setters.updateTtsConfig({
    provider: s.tts?.provider,
    voiceId: s.tts?.voiceId,
    speed: s.tts?.speed,
    pitch: s.tts?.pitch,
    volume: s.tts?.volume,
    referenceAudioPath: s.tts?.referenceAudioPath,
    mimoApiKey: (s.tts as any)?.mimoApiKey,
    mimoBaseUrl: (s.tts as any)?.mimoBaseUrl,
    minimaxApiKey: (s.tts as any)?.minimaxApiKey,
    minimaxVoiceId: (s.tts as any)?.minimaxVoiceId,
  })

  setters.updateImageConfig({
    imageFolder: (s.image as any)?.imageFolder,
    imageCount: (s.image as any)?.imageCount,
    width: (s.image as any)?.width,
    height: (s.image as any)?.height,
    kenBurns: (s.image as any)?.kenBurns,
  })

  setters.setOutputPath(s.outputPath || '')

  setters.setGlobalConfig({
    voiceId: b.voiceId,
    voiceType: b.voiceType,
    voiceProvider: b.voiceProvider,
    bgmPath: b.bgmPath,
    bgmStyle: b.bgmStyle,
    durationMin: b.durationMin,
    durationMax: b.durationMax,
    videoMode: b.videoMode,
    rewriteParams: b.rewriteParams,
  })

  return {
    success: true,
    summary: `设置已导入：LLM(${s.llm?.provider || '—'}) · TTS(${s.tts?.provider || '—'}) · 配音(${b.voiceType || '—'})`,
    warnApiKey,
  }
}
