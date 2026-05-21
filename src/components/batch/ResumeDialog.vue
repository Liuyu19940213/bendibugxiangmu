<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'

const props = defineProps<{
  open: boolean
  completed: number
  failed: number
  total: number
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  clear: []
  resume: []
}>()

function handleClear() {
  emit('clear')
  emit('update:open', false)
}

function handleResume() {
  emit('resume')
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>发现未完成的任务</DialogTitle>
      </DialogHeader>

      <div class="py-4 space-y-3">
        <div class="bg-muted/50 rounded-lg p-4 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">总书籍数：</span>
            <span class="font-medium">{{ total }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">已完成：</span>
            <span class="font-medium text-green-600">{{ completed }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">失败：</span>
            <span class="font-medium text-red-600">{{ failed }}</span>
          </div>
        </div>
        <p class="text-sm text-muted-foreground">
          上一次批量运行未全部完成，是否恢复进度继续？
        </p>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleClear">
          清空重新开始
        </Button>
        <Button @click="handleResume">
          恢复进度
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
