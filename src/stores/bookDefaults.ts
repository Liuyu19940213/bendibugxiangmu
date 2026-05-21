import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BookDefaultConfig, BookDefaultsMap } from '@/types'

const STORAGE_KEY = 'pixelle-book-defaults'

export const DEFAULT_BOOK_CONFIG: BookDefaultConfig = {
  voiceProvider: 'cosyvoice',
  bgmStyle: '宁静',
  videoMode: 'kenburns',
  rewriteMode: 'flexible',
  referenceCount: 3,
  imageCount: 3,
  kenBurns: true,
  imageFolder: '',
}

function load(): BookDefaultsMap {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as BookDefaultsMap
  } catch { /* ignore */ }
  return {}
}

export const useBookDefaultsStore = defineStore('bookDefaults', () => {
  const defaults = ref<BookDefaultsMap>(load())

  function persist() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(defaults.value)) } catch { /* ignore */ }
  }

  function getBookConfig(bookName: string): BookDefaultConfig {
    return defaults.value[bookName] ?? { ...DEFAULT_BOOK_CONFIG }
  }

  function setBookConfig(bookName: string, config: Partial<BookDefaultConfig>): void {
    defaults.value[bookName] = { ...getBookConfig(bookName), ...config }
    persist()
  }

  function deleteBookConfig(bookName: string): void {
    delete defaults.value[bookName]
    persist()
  }

  function resetBookConfig(bookName: string): void {
    defaults.value[bookName] = { ...DEFAULT_BOOK_CONFIG }
    persist()
  }

  return { defaults, getBookConfig, setBookConfig, deleteBookConfig, resetBookConfig }
})
