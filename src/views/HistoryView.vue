<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getBatchHistory,
  getBatchHistoryDetail,
  type BatchHistoryItem,
  type BatchHistoryDetail,
  type ModuleTraceMeta,
} from '@/services/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Badge from '@/components/ui/Badge.vue'
import Separator from '@/components/ui/Separator.vue'
import { History, Hash, Eye, BookOpen, X } from 'lucide-vue-next'

const loading = ref(false)
const items = ref<BatchHistoryItem[]>([])
const selectedDetail = ref<BatchHistoryDetail | null>(null)
const detailOpen = ref(false)

async function loadHistory() {
  loading.value = true
  try {
    items.value = await getBatchHistory()
  } finally {
    loading.value = false
  }
}

async function openDetail(item: BatchHistoryItem) {
  try {
    selectedDetail.value = await getBatchHistoryDetail(item.batch_id)
    detailOpen.value = true
  } catch {
    selectedDetail.value = null
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'completed': return '已完成'
    case 'failed': return '失败'
    case 'cancelled': return '已取消'
    default: return status
  }
}

function statusVariant(status: string): 'default' | 'destructive' | 'secondary' {
  switch (status) {
    case 'completed': return 'default'
    case 'failed': return 'destructive'
    case 'cancelled': return 'secondary'
    default: return 'secondary'
  }
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('zh-CN')
}

function formatHash(hash: string): string {
  if (!hash) return '—'
  return hash.slice(0, 10) + '…'
}

function fmtOrig(orig: number | null): string {
  if (orig == null) return '—'
  return (orig * 100).toFixed(0) + '%'
}

onMounted(loadHistory)
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-2 border-b px-6 py-3">
      <History class="h-5 w-5 text-muted-foreground" />
      <h2 class="font-medium">运行历史</h2>
      <div class="flex-1" />
      <Button size="sm" variant="ghost" @click="loadHistory" :disabled="loading">
        {{ loading ? '加载中…' : '刷新' }}
      </Button>
    </div>

    <div class="flex-1 overflow-auto p-6">
      <div v-if="loading" class="text-center py-16 text-muted-foreground">加载中…</div>

      <div v-else-if="items.length === 0" class="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <History class="h-16 w-16 mb-4 opacity-20" />
        <p class="text-lg font-medium">暂无运行历史</p>
        <p class="text-sm mt-1">完成批量任务后，记录会自动出现在这里</p>
      </div>

      <div v-else class="space-y-3">
        <p class="text-sm text-muted-foreground">共 {{ items.length }} 条记录</p>

        <div
          v-for="item in items"
          :key="item.batch_id"
          class="flex items-center gap-4 rounded-lg border bg-card p-4 cursor-pointer transition-shadow hover:shadow-sm"
          @click="openDetail(item)"
        >
          <Badge :variant="statusVariant(item.status)">
            {{ statusLabel(item.status) }}
          </Badge>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-sm font-medium truncate">{{ item.batch_id.slice(0, 8) }}</p>
            </div>
            <p class="text-xs text-muted-foreground">{{ formatDate(item.created_at) }}</p>
          </div>

          <div class="hidden sm:flex items-center gap-4 text-sm">
            <span class="text-green-600">{{ item.completed_modules }} 成功</span>
            <span v-if="item.failed_modules > 0" class="text-red-500">{{ item.failed_modules }} 失败</span>
            <span class="text-muted-foreground">共 {{ item.total_modules }} 本</span>
          </div>

          <Eye class="h-4 w-4 text-muted-foreground" />
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div
      v-if="detailOpen && selectedDetail"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="detailOpen = false"
    >
      <div class="bg-card rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col m-4">
        <div class="flex items-center gap-2 px-6 py-4 border-b">
          <BookOpen class="h-5 w-5" />
          <h3 class="font-medium flex-1">运行详情 · {{ selectedDetail.batch_id.slice(0, 8) }}</h3>
          <Button variant="ghost" size="icon" @click="detailOpen = false">
            <X class="h-4 w-4" />
          </Button>
        </div>

        <div class="px-6 py-3 text-sm text-muted-foreground border-b">
          创建：{{ formatDate(selectedDetail.created_at) }} ·
          完成：{{ formatDate(selectedDetail.completed_at) }} ·
          状态：{{ statusLabel(selectedDetail.status) }} ·
          共 {{ selectedDetail.modules.length }} 本书
        </div>

        <div class="flex-1 overflow-auto p-6 space-y-3">
          <div
            v-for="(m, idx) in selectedDetail.modules"
            :key="idx"
            class="rounded-lg border p-3"
          >
            <div class="flex items-start justify-between mb-2">
              <p class="text-sm font-medium">{{ m.book_name || `第 ${idx + 1} 本书` }}</p>
              <Badge variant="secondary" class="text-xs">
                {{ m.char_count }} 字
              </Badge>
            </div>

            <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <div class="flex items-center gap-1">
                <Hash class="h-3 w-3" />
                原文：{{ formatHash(m.source_hash) }}
              </div>
              <div>原创度：{{ fmtOrig(m.originality) }}</div>
              <div>对标素材：{{ m.reference_count }} 篇</div>
              <div v-if="m.rewrite_date">洗稿时间：{{ formatDate(m.rewrite_date) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
