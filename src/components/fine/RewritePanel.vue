<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useFineModeStore } from '@/stores/fineMode'
import { useSettingsStore } from '@/stores/settings'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import { rewriteContent, saveToLibrary, type RewriteMeta } from '@/services/api'
import EmotionCurve from '@/components/fine/EmotionCurve.vue'
import { checkTokenRisk } from '@/utils/tokenEstimate'
import Button from '@/components/ui/Button.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Slider from '@/components/ui/Slider.vue'
import Separator from '@/components/ui/Separator.vue'

const fineModeStore = useFineModeStore()
const settingsStore = useSettingsStore()
const bookDefaultsStore = useBookDefaultsStore()

const isLoading = ref(false)
const referenceCount = ref(3)
const rewriteMode = ref<'rigid' | 'flexible'>('flexible')
const errorMsg = ref('')
const lastMeta = ref<RewriteMeta | null>(null)
const savingToLibrary = ref(false)
const libraryMsg = ref('')

watch(() => fineModeStore.state.bookName, (name) => {
  if (!name) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  if (bookDefaultsStore.defaults[name]) {
    referenceCount.value = cfg.referenceCount
    rewriteMode.value = cfg.rewriteMode
  }
})

const chineseCount = computed(() => {
  return fineModeStore.state.rewriteResult.match(/[\u4e00-\u9fff]/g)?.length ?? 0
})

// ── Token risk estimation ──
const tokenRisk = computed(() => {
  const provider = settingsStore.settings.llm.provider || 'DeepSeek'
  return checkTokenRisk(
    provider,
    fineModeStore.state.rawText,
    referenceCount.value,
  )
})

const riskLabel = computed(() => {
  const r = tokenRisk.value
  if (r.level === 'danger') {
    return `⚠ ${r.limitLabel} 上下文：预计使用 ${r.percentage}%，可能超限，请减少对标素材或缩短原文`
  }
  if (r.level === 'warning') {
    return `⚡ ${r.limitLabel} 上下文：预计使用 ${r.percentage}%，接近上限，建议减少对标素材`
  }
  return null
})

async function handleRewrite() {
  if (!fineModeStore.state.rawText.trim()) return
  isLoading.value = true
  errorMsg.value = ''
  lastMeta.value = null
  libraryMsg.value = ''
  try {
    const res = await rewriteContent({
      text: fineModeStore.state.rawText,
      book_name: fineModeStore.state.bookName,
      reference_count: referenceCount.value,
      originality: 30,
      target_chars: '3000-4500',
      rewrite_mode: rewriteMode.value,
    })
    fineModeStore.setRewriteResult(res.content || fineModeStore.state.rawText)
    lastMeta.value = res.meta
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : '洗稿失败，请确认 Python 后端已启动'
  } finally {
    isLoading.value = false
  }
}

/** 导出带溯源标记的文件 */
function handleExport() {
  const meta = lastMeta.value
  const content = fineModeStore.state.rewriteResult
  if (!content) return

  const header = [
    '# === 洗稿溯源标记 ===',
    `# 来源书籍: ${meta?.book_name || '未知'}`,
    `# 洗稿日期: ${meta?.date || '未知'}`,
    `# 洗稿模式: ${meta?.rewrite_mode === 'rigid' ? '锁骨架' : '首尾锁·中段自由'}`,
    `# 原创度: ${meta?.originality ?? '-'}%`,
    `# 对标素材数: ${meta?.reference_count ?? '-'}`,
    `# 原文SHA256: ${meta?.source_hash || '-'}`,
    `# 目标字数: ${meta?.target_chars || '-'}`,
    '# ====================',
    '',
  ].join('\n')

  const blob = new Blob([header + content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const safeName = (meta?.book_name || '未命名').replace(/[<>:"/\\|?*]/g, '_')
  a.download = `洗稿_${safeName}_${meta?.date?.replace(/[: ]/g, '_') || Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/** 手动加入素材库 */
async function handleSaveToLibrary() {
  const bookName = fineModeStore.state.bookName
  const content = fineModeStore.state.rewriteResult
  if (!bookName || !content) return
  savingToLibrary.value = true
  libraryMsg.value = ''
  try {
    const res = await saveToLibrary(bookName, content)
    libraryMsg.value = res.saved ? '✅ 已加入素材库' : '⚠ 已存在重复，跳过'
  } catch (e: unknown) {
    libraryMsg.value = '❌ 保存失败'
  } finally {
    savingToLibrary.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- 参数区 -->
    <div class="flex flex-col gap-0 flex-shrink-0">
      <div class="flex items-center gap-6 px-6 py-3 border-b bg-card">
        <div class="flex items-center gap-3 min-w-0">
          <label class="text-sm font-medium whitespace-nowrap">对标素材数量</label>
          <div class="w-32">
            <Slider
              :model-value="[referenceCount]"
              @update:model-value="referenceCount = $event[0]"
              :min="0"
              :max="10"
              :step="1"
            />
          </div>
          <span class="text-sm text-muted-foreground w-4 text-center">{{ referenceCount }}</span>
        </div>
        <Separator orientation="vertical" class="h-5" />
        <div class="flex items-center gap-2">
          <label class="text-sm font-medium whitespace-nowrap">洗稿模式</label>
          <select
            v-model="rewriteMode"
            class="h-8 px-2 text-sm border rounded-md bg-background"
          >
            <option value="flexible">首尾锁·中段自由</option>
            <option value="rigid">锁骨架</option>
          </select>
        </div>
      </div>

      <!-- Token risk warning -->
      <div
        v-if="riskLabel"
        :class="[
          'px-6 py-1.5 text-xs border-b flex-shrink-0',
          tokenRisk.level === 'danger'
            ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800'
            : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800',
        ]"
      >
        {{ riskLabel }}
      </div>

      <!-- 素材库操作消息 -->
      <div
        v-if="libraryMsg"
        class="px-6 py-1.5 text-xs text-muted-foreground border-b bg-muted/30 flex-shrink-0"
      >
        {{ libraryMsg }}
      </div>
    </div>

    <!-- 编辑区 -->
    <div class="flex flex-1 gap-0 overflow-hidden">
      <!-- 左侧：原文 -->
      <div class="flex flex-col flex-1 p-4 gap-2 min-w-0">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-muted-foreground">原文</span>
          <span class="text-xs text-muted-foreground">
            {{ fineModeStore.state.rawText.match(/[\u4e00-\u9fff]/g)?.length ?? 0 }} 字
          </span>
        </div>
        <Textarea
          v-model="fineModeStore.state.rawText"
          class="flex-1 resize-none font-mono text-sm h-full"
          placeholder="原文内容..."
        />
      </div>

      <Separator orientation="vertical" />

      <!-- 右侧：洗稿结果 -->
      <div class="flex flex-col flex-1 p-4 gap-2 min-w-0">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">洗稿结果</span>
          <span class="text-xs text-muted-foreground">{{ chineseCount }} 字</span>
        </div>
        <Textarea
          v-model="fineModeStore.state.rewriteResult"
          class="flex-1 resize-none font-mono text-sm h-full"
          placeholder="点击「开始洗稿」后结果将显示在此..."
        />
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="px-6 py-2 bg-destructive/10 text-destructive text-sm flex-shrink-0">
      {{ errorMsg }}
    </div>

    <!-- 底部操作栏 -->
    <div class="flex items-center justify-between px-6 py-3 border-t bg-card flex-shrink-0">
      <div class="flex items-center gap-2">
        <Button
          @click="handleRewrite"
          :disabled="isLoading || !fineModeStore.state.rawText"
        >
          {{ isLoading ? '洗稿中...' : '开始洗稿' }}
        </Button>

        <!-- 导出和入库按钮（洗稿完成后显示） -->
        <template v-if="fineModeStore.state.rewriteResult && lastMeta">
          <Button
            variant="outline"
            size="sm"
            @click="handleExport"
          >
            导出（带溯源标记）
          </Button>
          <Button
            variant="outline"
            size="sm"
            :disabled="savingToLibrary"
            @click="handleSaveToLibrary"
          >
            {{ savingToLibrary ? '保存中...' : '加入素材库' }}
          </Button>
        </template>
      </div>

      <EmotionCurve
        v-if="fineModeStore.state.rewriteResult"
        :text="fineModeStore.state.rewriteResult"
        :book-name="fineModeStore.state.bookName"
      />

      <Button
        variant="default"
        :disabled="!fineModeStore.state.rewriteResult"
        @click="fineModeStore.nextStep()"
      >
        下一步 →
      </Button>
    </div>
  </div>
</template>
