import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FineStep, FineModeState, VoiceConfig, GlobalConfig, ImageGenConfig } from '@/types'

export const useFineModeStore = defineStore('fineMode', () => {
  const state = ref<FineModeState>({
    bookName: '',
    rawText: '',
    currentStep: 'rewrite',
    rewriteResult: '',
    voiceConfig: {
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
    voiceResult: null,
    selectedImages: [],
    imageConfig: {
      mode: 'local',
      kenBurns: true,
      width: 1080,
      height: 1920,
      prompt: '',
      imagePaths: [],
      imageFolder: '',
      imageCount: 3,
    },
    generateConfig: {
      voiceId: '',
      voiceType: 'clone',
      voiceProvider: 'cosyvoice',
      bgmPath: '',
      bgmStyle: '宁静',
      durationMin: 10,
      durationMax: 60,
      videoMode: 'horizontal',
      rewriteParams: {
        referenceCount: 1,
        style: '默认',
        targetWordsMin: 100,
        targetWordsMax: 500,
        rewriteMode: 'rigid',
      },
    },
  })

  const currentStepName = computed<FineStep>(() => state.value.currentStep)
  const steps: FineStep[] = ['rewrite', 'voice', 'image', 'generate']
  const stepIndex = computed<number>(() => steps.indexOf(state.value.currentStep))

  function setBook(name: string, text: string): void {
    state.value.bookName = name
    state.value.rawText = text
    state.value.currentStep = 'rewrite'
    state.value.rewriteResult = ''
    state.value.selectedImages = []
  }

  function setStep(step: FineStep): void {
    state.value.currentStep = step
  }

  function nextStep(): void {
    const idx = stepIndex.value
    if (idx < steps.length - 1) state.value.currentStep = steps[idx + 1]
  }

  function prevStep(): void {
    const idx = stepIndex.value
    if (idx > 0) state.value.currentStep = steps[idx - 1]
  }

  function setRewriteResult(text: string): void {
    state.value.rewriteResult = text
  }

  function setVoiceConfig(c: Partial<VoiceConfig>): void {
    Object.assign(state.value.voiceConfig, c)
  }

  function setSelectedImages(images: string[]): void {
    state.value.selectedImages = images
  }

  function setVoiceResult(r: { path: string; duration: number } | null): void {
    state.value.voiceResult = r
  }

  function setImageConfig(c: Partial<ImageGenConfig>): void {
    Object.assign(state.value.imageConfig, c)
  }

  function setGenerateConfig(c: GlobalConfig): void {
    state.value.generateConfig = c
  }

  return {
    state,
    currentStepName,
    steps,
    stepIndex,
    setBook,
    setStep,
    nextStep,
    prevStep,
    setRewriteResult,
    setVoiceConfig,
    setVoiceResult,
    setImageConfig,
    setSelectedImages,
    setGenerateConfig,
  }
})
