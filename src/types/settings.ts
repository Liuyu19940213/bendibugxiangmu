export type { AppSettings, LlmConfig, VoiceConfig } from './'

export interface LlmTestResult {
  success: boolean
  latency: number
  error?: string
}

export interface TtsPreviewParams {
  text: string
  voiceConfig: import('./').VoiceConfig
}
