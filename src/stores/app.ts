import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FineStep } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 侧边栏折叠状态
  const sidebarCollapsed = ref(false)

  // 当前视图
  const currentView = ref<'batch' | 'fine' | 'template' | 'media' | 'copy' | 'settings'>('batch')

  // 精细模式当前步骤
  const fineStep = ref<FineStep>('rewrite')

  /** 切换侧边栏折叠/展开 */
  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  /** 切换到指定视图 */
  function setView(view: typeof currentView.value): void {
    currentView.value = view
  }

  /** 设置精细模式当前步骤 */
  function setFineStep(step: FineStep): void {
    fineStep.value = step
  }

  return {
    sidebarCollapsed,
    currentView,
    fineStep,
    toggleSidebar,
    setView,
    setFineStep,
  }
})
