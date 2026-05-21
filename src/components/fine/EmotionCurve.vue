<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  analyzeRhythm,
  updateRhythmSegment,
  type EmotionRhythmResult,
  type EmotionSegment,
} from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { Sparkles, Edit3, Save } from 'lucide-vue-next'

const props = defineProps<{
  text: string
  bookName?: string
}>()

const emit = defineEmits<{
  save: [result: EmotionRhythmResult]
}>()

const loading = ref(false)
const result = ref<EmotionRhythmResult | null>(null)
const analysisId = ref<string | null>(null)
const editingIndex = ref<number | null>(null)

const emotionColors: Record<string, string> = {
  '激昂': 'bg-red-500',
  '平静': 'bg-blue-500',
  '疑问': 'bg-yellow-500',
  '感叹': 'bg-orange-500',
  '悲伤': 'bg-purple-500',
}

const emotionLabels: Record<string, string> = {
  '激昂': '激昂',
  '平静': '平静',
  '疑问': '疑问',
  '感叹': '感叹',
  '悲伤': '悲伤',
}

const maxDuration = computed(() => result.value?.total_duration || 1)

function barWidth(seg: EmotionSegment): string {
  return ((seg.duration / maxDuration.value) * 100).toFixed(1) + '%'
}

async function handleAnalyze() {
  if (!props.text.trim()) return
  loading.value = true
  try {
    const res = await analyzeRhythm(props.text, props.bookName || '')
    result.value = res.result
    analysisId.value = res.analysis_id
  } finally {
    loading.value = false
  }
}

async function handleUpdateEmotion(index: number, emotion: string) {
  if (!result.value || !analysisId.value) return
  const seg = result.value.segments[index]
  if (!seg) return
  await updateRhythmSegment(analysisId.value, index, emotion, seg.text)
  seg.emotion = emotion
  editingIndex.value = null
}

function handleSave() {
  if (result.value) emit('save', result.value)
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <Button size="sm" @click="handleAnalyze" :disabled="loading || !text.trim()">
        <Sparkles class="h-4 w-4 mr-1" />
        {{ loading ? '分析中...' : result ? '重新分析' : '分析情绪节奏' }}
      </Button>
      <Button v-if="result" size="sm" variant="outline" @click="handleSave">
        <Save class="h-4 w-4 mr-1" />保存到文案库
      </Button>
    </div>

    <div v-if="result" class="rounded-lg border p-4 space-y-3">
      <div class="flex items-center gap-2 text-sm text-muted-foreground">
        <span>{{ result.segments.length }} 段</span>
        <span>·</span>
        <span>总时长约 {{ result.total_duration.toFixed(0) }} 秒</span>
      </div>

      <!-- 情绪条形图 -->
      <div class="flex h-6 rounded-lg overflow-hidden">
        <div
          v-for="seg in result.segments"
          :key="seg.index"
          :class="[
            emotionColors[seg.emotion] || 'bg-gray-300',
            'transition-all first:rounded-l-lg last:rounded-r-lg',
          ]"
          :style="{ width: barWidth(seg) }"
          :title="`${seg.emotion} ${seg.confidence.toFixed(0)}: ${seg.text.slice(0, 20)}`"
        ></div>
      </div>

      <!-- 图例 -->
      <div class="flex flex-wrap gap-2">
        <Badge
          v-for="(label, key) in emotionLabels"
          :key="key"
          variant="secondary"
          class="text-xs"
        >
          <span :class="['inline-block h-2 w-2 rounded-full mr-1', emotionColors[key] || 'bg-gray-300']"></span>
          {{ label }}
        </Badge>
      </div>

      <!-- 片段详情列表 -->
      <div class="space-y-1 max-h-64 overflow-y-auto">
        <div
          v-for="seg in result.segments"
          :key="seg.index"
          class="flex items-center gap-2 text-xs py-1.5 border-b border-border/50 last:border-0"
        >
          <Badge
            :class="[emotionColors[seg.emotion] || 'bg-gray-500', 'text-white shrink-0']"
            size="sm"
          >
            {{ emotionLabels[seg.emotion] || seg.emotion }}
          </Badge>
          <span class="truncate flex-1">{{ seg.text }}</span>

          <div v-if="editingIndex === seg.index" class="flex items-center gap-1 shrink-0">
            <button
              v-for="e in Object.keys(emotionLabels)"
              :key="e"
              :class="[
                'px-1.5 py-0.5 rounded text-[10px] transition-colors',
                seg.emotion === e ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80',
              ]"
              @click="handleUpdateEmotion(seg.index, e)"
            >
              {{ e }}
            </button>
          </div>

          <button
            v-else
            class="p-0.5 rounded hover:bg-muted shrink-0"
            @click="editingIndex = seg.index"
          >
            <Edit3 class="h-3 w-3 text-muted-foreground" />
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="text-sm text-muted-foreground py-4 text-center">
      点击上方按钮分析文案情绪节奏
    </div>
  </div>
</template>
