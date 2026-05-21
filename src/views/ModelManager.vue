<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getModelStatus, downloadModel, downloadAllModels } from '@/services/api'
import type { ModelStatusResponse, ModelInfo, EnvironmentInfo } from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import { Cpu, Monitor, Download, CheckCircle2, XCircle, AlertTriangle, RefreshCw } from 'lucide-vue-next'

const loading = ref(true)
const models = ref<ModelInfo[]>([])
const environment = ref<EnvironmentInfo | null>(null)
const downloading = ref<Set<string>>(new Set())
const downloadAllLoading = ref(false)
const downloadMsg = ref<Record<string, string>>({})

async function loadStatus() {
  loading.value = true
  try {
    const res: ModelStatusResponse = await getModelStatus()
    models.value = res.models
    environment.value = res.environment
  } catch (e: unknown) {
    console.error('获取模型状态失败:', e)
  } finally {
    loading.value = false
  }
}

async function handleDownload(key: string) {
  if (downloading.value.has(key)) return
  downloading.value = new Set(downloading.value).add(key)
  downloadMsg.value[key] = ''
  try {
    const res = await downloadModel(key)
    downloadMsg.value[key] = res.message
    if (res.success) {
      await loadStatus()
    }
  } catch (e: unknown) {
    downloadMsg.value[key] = `下载失败: ${(e as Error)?.message || e}`
  } finally {
    const next = new Set(downloading.value)
    next.delete(key)
    downloading.value = next
  }
}

async function handleDownloadAll() {
  downloadAllLoading.value = true
  try {
    await downloadAllModels()
    await loadStatus()
  } catch (e: unknown) {
    console.error('一键下载失败:', e)
  } finally {
    downloadAllLoading.value = false
  }
}

function categoryLabel(c: string): string {
  const m: Record<string, string> = { asr: '语音转文字', tts: '语音合成', image: 'AI 生图', emotion: '情绪分析' }
  return m[c] ?? c
}

function categoryBadgeVariant(c: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  const m: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
    asr: 'default', tts: 'secondary', image: 'outline', emotion: 'destructive',
  }
  return m[c] ?? 'outline'
}

function formatSize(mb: number): string {
  if (mb >= 1000) return `${(mb / 1000).toFixed(1)} GB`
  return `${mb} MB`
}

const missingCount = ref(0)

function refreshCount() {
  missingCount.value = models.value.filter((m) => !m.downloaded).length
}

onMounted(async () => {
  await loadStatus()
  refreshCount()
})

const totalSize = ref(0)
function calcTotal() {
  totalSize.value = models.value.reduce((s, m) => s + m.size_mb, 0)
}
onMounted(() => { calcTotal() })
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-4xl mx-auto p-6 space-y-6">

      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-semibold">📦 模型与依赖管理</h1>
          <p class="text-xs text-muted-foreground mt-1">管理本地 AI 模型的下载状态、环境检测、一键下载</p>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" @click="loadStatus" :disabled="loading">
            <RefreshCw :class="['h-4 w-4 mr-1', loading && 'animate-spin']" />刷新
          </Button>
          <Button
            size="sm"
            :disabled="missingCount === 0 || downloadAllLoading"
            @click="handleDownloadAll"
          >
            <Download class="h-4 w-4 mr-1" />
            {{ downloadAllLoading ? '下载中...' : `一键下载 (${missingCount})` }}
          </Button>
        </div>
      </div>

      <!-- 环境信息 -->
      <Card v-if="environment">
        <CardHeader>
          <CardTitle class="flex items-center gap-2 text-base">
            <Cpu class="h-4 w-4" />环境检测
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">GPU</p>
              <p class="text-sm font-medium">{{ environment.gpu_name || '未检测到' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">显存</p>
              <p class="text-sm font-medium">{{ environment.vram_total_mb > 0 ? `${environment.vram_total_mb / 1024} GB` : '—' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">CUDA</p>
              <div class="flex items-center gap-1.5">
                <CheckCircle2 v-if="environment.cuda_available" class="h-3.5 w-3.5 text-green-500" />
                <XCircle v-else class="h-3.5 w-3.5 text-red-500" />
                <span class="text-sm">{{ environment.cuda_available ? `v${environment.cuda_version}` : '不可用' }}</span>
              </div>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">PyTorch</p>
              <p class="text-sm font-medium">{{ environment.torch_version || '—' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">Python</p>
              <p class="text-sm font-medium">{{ environment.python_version }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">FFmpeg</p>
              <div class="flex items-center gap-1.5">
                <CheckCircle2 v-if="environment.ffmpeg_available" class="h-3.5 w-3.5 text-green-500" />
                <XCircle v-else class="h-3.5 w-3.5 text-red-500" />
                <span class="text-sm">{{ environment.ffmpeg_available ? '可用' : '未安装' }}</span>
              </div>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">可用显存</p>
              <p class="text-sm font-medium">{{ environment.vram_free_mb > 0 ? `${(environment.vram_free_mb / 1024).toFixed(1)} GB` : '—' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-muted-foreground">模型总数</p>
              <p class="text-sm font-medium">
                {{ models.filter((m) => m.downloaded).length }} / {{ models.length }} 已就绪
              </p>
            </div>
          </div>

          <div v-if="!environment.cuda_available" class="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 flex items-start gap-2">
            <AlertTriangle class="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-medium text-amber-700">CUDA 不可用</p>
              <p class="text-xs text-amber-600 mt-0.5">请确保已安装 NVIDIA 驱动 ≥525 版本，并安装 PyTorch CUDA 版</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 模型列表 -->
      <div class="space-y-3">
        <div class="flex items-center gap-2">
          <Monitor class="h-4 w-4 text-muted-foreground" />
          <h2 class="text-sm font-semibold">模型清单</h2>
          <span class="text-xs text-muted-foreground">（合计约 {{ totalSize >= 1000 ? `${(totalSize / 1000).toFixed(0)} GB` : `${totalSize} MB` }}）</span>
        </div>

        <div v-if="loading" class="text-center py-16 text-sm text-muted-foreground">
          <RefreshCw class="h-6 w-6 mx-auto mb-2 animate-spin opacity-30" />
          查询模型状态中...
        </div>

        <Card v-for="model in models" :key="model.key" :class="[model.downloaded ? 'border-green-200 bg-green-50/30' : '']">
          <CardContent class="p-4">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-sm">{{ model.name }}</span>
                  <Badge :variant="categoryBadgeVariant(model.category)" size="sm">
                    {{ categoryLabel(model.category) }}
                  </Badge>
                  <Badge :variant="model.downloaded ? 'default' : 'outline'" size="sm">
                    {{ model.downloaded ? '✓ 已就绪' : '未下载' }}
                  </Badge>
                </div>
                <div class="text-xs text-muted-foreground space-y-0.5">
                  <p>大小：{{ formatSize(model.size_mb) }}</p>
                  <p v-if="model.required_by.length">用途：{{ model.required_by.join(' · ') }}</p>
                  <p v-if="model.local_path" class="truncate">路径：{{ model.local_path }}</p>
                </div>

                <div v-if="downloadMsg[model.key]" :class="['text-xs mt-2', downloadMsg[model.key].includes('失败') ? 'text-red-600' : 'text-green-600']">
                  {{ downloadMsg[model.key] }}
                </div>
              </div>

              <div class="shrink-0">
                <Button
                  v-if="!model.downloaded"
                  variant="outline"
                  size="sm"
                  :disabled="downloading.has(model.key)"
                  @click="handleDownload(model.key)"
                >
                  <Download v-if="!downloading.has(model.key)" class="h-3.5 w-3.5 mr-1" />
                  <RefreshCw v-else class="h-3.5 w-3.5 mr-1 animate-spin" />
                  {{ downloading.has(model.key) ? '下载中...' : '下载' }}
                </Button>
                <CheckCircle2 v-else class="h-5 w-5 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="h-8" />
    </div>
  </div>
</template>
