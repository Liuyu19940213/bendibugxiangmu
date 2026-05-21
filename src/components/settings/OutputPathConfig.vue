<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

const settingsStore = useSettingsStore()

function selectFolder() {
  alert('文件夹选择将通过 Tauri 原生对话框实现')
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>输出路径配置</CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div>
        <label class="text-sm font-medium">视频输出目录</label>
        <div class="flex gap-2 mt-1">
          <Input
            :model-value="settingsStore.settings.outputPath"
            readonly
            placeholder="未设置输出路径"
            class="flex-1"
          />
          <Button @click="selectFolder">选择文件夹</Button>
        </div>
      </div>

      <p class="text-xs text-muted-foreground">
        输出格式：{输出路径}/{日期}/{书名}/final.mp4
      </p>
    </CardContent>
  </Card>
</template>
