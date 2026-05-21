// ===== 批量创作 =====

export type ModuleStatus = 'idle' | 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

export interface RewriteParams {
  referenceCount: number
  style: string
  targetWordsMin: number
  targetWordsMax: number
  rewriteMode: 'rigid' | 'flexible'
}

export interface GlobalConfig {
  voiceId: string
  voiceType: 'clone'
  voiceProvider: string
  bgmPath: string
  bgmStyle: '激昂' | '宁静'
  durationMin: number
  durationMax: number
  videoMode: string
  rewriteParams: RewriteParams
}

export interface BatchModule {
  id: string
  bookName: string
  rawText: string
  enabled: boolean
  status: ModuleStatus
  errorMessage?: string
  resultText?: string
  configOverride?: Partial<GlobalConfig>
  sortOrder: number
}

export interface BatchProgress {
  total: number
  completed: number
  failed: number
  skipped: number
  currentBook: string | null
  percent: number
}

// ===== 精细模式 =====

export type FineStep = 'rewrite' | 'voice' | 'image' | 'generate'

export interface FineModeState {
  bookName: string
  rawText: string
  currentStep: FineStep
  rewriteResult: string
  voiceConfig: VoiceConfig
  voiceResult: { path: string; duration: number } | null
  selectedImages: string[]
  imageConfig: ImageGenConfig
  generateConfig: GlobalConfig
}

export interface ImageGenConfig {
  mode: 'local'
  kenBurns: boolean
  width: number
  height: number
  prompt: string
  imagePaths: string[]
  imageFolder: string
  imageCount: number
}

// ===== 配音 =====

export interface VoiceConfig {
  provider: 'mimo' | 'indextts' | 'minimax' | 'cosyvoice'
  voiceId: string
  speed: number
  pitch: number
  volume: number
  referenceAudioPath: string
  mimoApiKey: string
  mimoBaseUrl: string
  minimaxApiKey: string
  minimaxVoiceId: string
}

// ===== 素材库 =====

export type MediaType = 'image' | 'bgm' | 'copy'
export type ImageSource = 'ai' | 'preset' | 'upload'
export type ImageCategory = '自然风景' | '演播室' | '书房' | '抽象意境' | '未分类'
export type BgmStyle = '激昂' | '宁静'
export type CopyGenre = '书籍' | '播客' | '口播' | '访谈' | '自定义'

export interface MediaItem {
  id: string
  type: MediaType
  name: string
  path: string
  source: ImageSource
  category: ImageCategory
  tags: string[]
  bookName?: string
  createdAt: string
  lastUsedAt?: string
  fileSize: number
  kenBurns: boolean
  bgmStyle?: BgmStyle
  fadeIn?: number
  fadeOut?: number
  rawText?: string
  emotionRhythm?: string
  genre?: CopyGenre
}

// ===== 模块模板 =====

export interface ModuleTemplateModule {
  bookName: string
  rawText: string
  enabled: boolean
  sortOrder: number
}

export interface ModuleTemplate {
  id: string
  name: string
  createdAt: string
  globalConfig: GlobalConfig
  modules: ModuleTemplateModule[]
}

// ===== API 通用 =====

export interface ApiResponse<T = unknown> {
  code: number
  data: T | null
  message: string
}

// ===== LLM 配置 =====

export interface LlmConfig {
  provider: string
  apiKey: string
  apiBase: string
  model: string
  temperature: number
  maxTokens: number
}

// ===== 设置 =====

export interface AppSettings {
  llm: LlmConfig
  tts: VoiceConfig
  image: ImageGenSettings
  outputPath: string
  pythonPort: number
}

export interface ImageGenSettings {
  imageFolder: string
  imageCount: number
  width: number
  height: number
  kenBurns: boolean
}

export interface BookDefaultConfig {
  voiceProvider: string
  bgmStyle: '激昂' | '宁静'
  videoMode: string
  rewriteMode: 'rigid' | 'flexible'
  referenceCount: number
  imageCount: number
  kenBurns: boolean
  imageFolder: string
}

export type BookDefaultsMap = Record<string, BookDefaultConfig>
