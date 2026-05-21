<script setup lang="ts">
import { ref } from 'vue'
import { useBatchStore } from '@/stores/batch'
import { useTxtParser } from '@/composables/useTxtParser'
import type { ParseResult } from '@/composables/useTxtParser'
import type { BatchModule } from '@/types'
import Button from '@/components/ui/Button.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogDescription from '@/components/ui/DialogDescription.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogClose from '@/components/ui/DialogClose.vue'
import { Upload } from 'lucide-vue-next'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  imported: []
}>()

const batchStore = useBatchStore()
const { parse } = useTxtParser()

const txtContent = ref('')
const parseResult = ref<ParseResult | null>(null)
const importing = ref(false)
const fileName = ref('')

/** 从本地文件读取 TXT 内容 */
function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  fileName.value = file.name
  const reader = new FileReader()
  reader.onload = () => {
    txtContent.value = reader.result as string
    input.value = ''
  }
  reader.onerror = () => {
    fileName.value = ''
    input.value = ''
  }
  reader.readAsText(file, 'utf-8')
}

function handleParse() {
  if (!txtContent.value.trim()) return
  parseResult.value = parse(txtContent.value)
}

function handleImportAll() {
  if (!parseResult.value || parseResult.value.modules.length === 0) return
  importing.value = true
  try {
    for (const m of parseResult.value.modules) {
      batchStore.addModule(m.bookName, m.rawText)
    }
    batchStore.sortModules()
    emit('imported')
    emit('update:open', false)
    txtContent.value = ''
    parseResult.value = null
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-2xl">
      <DialogHeader>
        <DialogTitle>导入 TXT 文案</DialogTitle>
        <DialogDescription>
          按空行切段，首行识别《书名》，其余行作为文案
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4 py-4">
        <!-- 文件选取 -->
        <div class="flex items-center gap-3">
          <label
            class="inline-flex items-center gap-2 px-3 py-2 rounded-md border cursor-pointer hover:bg-muted text-sm"
          >
            <Upload class="size-4" />
            选择 TXT 文件
            <input
              type="file"
              accept=".txt,.text/plain"
              class="hidden"
              @change="handleFileSelect"
            />
          </label>
          <span v-if="fileName" class="text-sm text-muted-foreground">{{ fileName }}</span>
        </div>

        <Textarea
          rows="10"
          v-model="txtContent"
          placeholder="在此粘贴 TXT 内容，或通过上方按钮选择文件..."
        />

        <Button variant="outline" @click="handleParse" :disabled="!txtContent.trim()">
          解析预览
        </Button>

        <!-- 预览表格 -->
        <div
          v-if="parseResult && parseResult.modules.length > 0"
          class="border rounded-md overflow-hidden"
        >
          <div class="grid grid-cols-[1fr_1fr_60px] gap-2 p-2 text-xs font-medium bg-muted">
            <div>书名</div>
            <div>文案</div>
            <div class="text-center">状态</div>
          </div>
          <div
            v-for="(m, idx) in parseResult.modules"
            :key="idx"
            class="grid grid-cols-[1fr_1fr_60px] gap-2 p-2 text-xs border-t"
          >
            <div class="truncate">{{ m.bookName }}</div>
            <div class="truncate text-muted-foreground">
              {{ m.rawText ? m.rawText.slice(0, 40) + '...' : '(无文案)' }}
            </div>
            <div class="text-center text-green-500">✓</div>
          </div>
        </div>

        <div
          v-if="parseResult && parseResult.unmatchedCount > 0"
          class="text-sm text-red-500"
        >
          ⚠ 有 {{ parseResult.unmatchedCount }} 段无法识别书名
        </div>
      </div>

      <DialogFooter>
        <DialogClose as-child>
          <Button variant="outline">取消</Button>
        </DialogClose>
        <Button
          @click="handleImportAll"
          :disabled="!parseResult || parseResult.modules.length === 0"
        >
          导入全部
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
