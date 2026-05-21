import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MediaItem } from '@/types'
import type { MediaFilter, CooldownConfig } from '@/types/media'

export const useMediaStore = defineStore('media', () => {
  const items = ref<MediaItem[]>([])

  const filter = ref<MediaFilter>({
    type: 'all',
    source: 'all',
    category: 'all',
    bgmStyle: 'all',
    genre: 'all',
    tags: [],
    bookName: null,
    keyword: '',
    sortBy: 'createdAt',
    sortOrder: 'desc',
  })

  const cooldownConfig = ref<CooldownConfig>({
    days: 30,
    enabled: true,
  })

  const selectedIds = ref<Set<string>>(new Set())

  /** 判断素材是否在冷却期内 */
  function isInCooldown(item: MediaItem): boolean {
    if (!cooldownConfig.value.enabled || !item.lastUsedAt) return false
    const lastUsed = new Date(item.lastUsedAt).getTime()
    const cooldownEnd = lastUsed + cooldownConfig.value.days * 24 * 60 * 60 * 1000
    return Date.now() < cooldownEnd
  }

  /** 获取冷却期剩余天数 */
  function getCooldownRemaining(item: MediaItem): number {
    if (!item.lastUsedAt) return 0
    const lastUsed = new Date(item.lastUsedAt).getTime()
    const cooldownEnd = lastUsed + cooldownConfig.value.days * 24 * 60 * 60 * 1000
    const remaining = Math.ceil((cooldownEnd - Date.now()) / (24 * 60 * 60 * 1000))
    return Math.max(0, remaining)
  }

  const filteredItems = computed<MediaItem[]>(() => {
    let result = [...items.value]

    if (filter.value.type !== 'all') {
      result = result.filter((i) => i.type === filter.value.type)
    }
    if (filter.value.source !== 'all') {
      result = result.filter((i) => i.source === filter.value.source)
    }
    if (filter.value.category !== 'all') {
      result = result.filter((i) => i.category === filter.value.category)
    }
    if (filter.value.bgmStyle !== 'all') {
      result = result.filter((i) => i.bgmStyle === filter.value.bgmStyle)
    }
    if (filter.value.genre !== 'all') {
      result = result.filter((i) => i.genre === filter.value.genre)
    }
    if (filter.value.keyword) {
      const kw = filter.value.keyword.toLowerCase()
      result = result.filter(
        (i) =>
          i.name.toLowerCase().includes(kw) ||
          i.tags.some((t) => t.includes(kw)),
      )
    }
    if (filter.value.bookName) {
      result = result.filter((i) => i.bookName === filter.value.bookName)
    }

    result.sort((a, b) => {
      const aVal = a[filter.value.sortBy as keyof MediaItem]
      const bVal = b[filter.value.sortBy as keyof MediaItem]
      if (aVal == null || bVal == null) return 0
      const cmp = aVal > bVal ? 1 : -1
      return filter.value.sortOrder === 'desc' ? -cmp : cmp
    })

    return result
  })

  /** 获取可用的素材（不在冷却期内） */
  const availableItems = computed<MediaItem[]>(() =>
    filteredItems.value.filter((i) => !isInCooldown(i)),
  )

  function setFilter(f: Partial<MediaFilter>): void {
    Object.assign(filter.value, f)
  }

  function setCooldownConfig(config: Partial<CooldownConfig>): void {
    Object.assign(cooldownConfig.value, config)
  }

  function toggleSelect(id: string): void {
    const s = new Set(selectedIds.value)
    if (s.has(id)) {
      s.delete(id)
    } else {
      s.add(id)
    }
    selectedIds.value = s
  }

  function selectAll(): void {
    selectedIds.value = new Set(filteredItems.value.map((i) => i.id))
  }

  function clearSelection(): void {
    selectedIds.value = new Set()
  }

  function addItems(newItems: MediaItem[]): void {
    const existingIds = new Set(items.value.map((i) => i.id))
    const deduped = newItems.filter((item) => !existingIds.has(item.id))
    items.value.push(...deduped)
  }

  function updateItem(id: string, updates: Partial<MediaItem>): void {
    const index = items.value.findIndex((i) => i.id === id)
    if (index !== -1) {
      items.value[index] = { ...items.value[index], ...updates }
    }
  }

  function removeSelected(): void {
    items.value = items.value.filter((i) => !selectedIds.value.has(i.id))
    selectedIds.value = new Set()
  }

  /** 标记素材为已使用（更新 lastUsedAt） */
  function markAsUsed(id: string): void {
    const index = items.value.findIndex((i) => i.id === id)
    if (index !== -1) {
      items.value[index] = {
        ...items.value[index],
        lastUsedAt: new Date().toISOString(),
      }
    }
  }

  return {
    items,
    filter,
    cooldownConfig,
    selectedIds,
    filteredItems,
    availableItems,
    setFilter,
    setCooldownConfig,
    isInCooldown,
    getCooldownRemaining,
    toggleSelect,
    selectAll,
    clearSelection,
    addItems,
    updateItem,
    removeSelected,
    markAsUsed,
  }
})
