<script setup lang="ts">
import { useBatchStore } from "@/stores/batch"
import Slider from "@/components/ui/Slider.vue"

const batchStore = useBatchStore()
</script>

<template>
  <div class="flex flex-wrap gap-4 p-4 border-b bg-card">
    <div class="flex flex-col gap-1">
      <span class="text-xs text-muted-foreground">配音引擎</span>
      <select
        :value="batchStore.globalConfig.voiceProvider"
        @change="batchStore.globalConfig.voiceProvider = ($event.target as HTMLSelectElement).value"
        class="flex h-9 w-[120px] rounded-md border border-input bg-background px-3 py-1 text-sm"
      >
        <option value="cosyvoice">CosyVoice2（本地）</option>
        <option value="indextts">IndexTTS（备用）</option>
        <option value="mimo">Mimo</option>
        <option value="minimax">MiniMax 海螺</option>
      </select>
    </div>

    <div class="flex flex-col gap-1">
      <span class="text-xs text-muted-foreground">BGM风格</span>
      <select
        :value="batchStore.globalConfig.bgmStyle"
        @change="batchStore.globalConfig.bgmStyle = ($event.target as HTMLSelectElement).value as any"
        class="flex h-9 w-[100px] rounded-md border border-input bg-background px-3 py-1 text-sm"
      >
        <option value="激昂">激昂</option>
        <option value="宁静">宁静</option>
      </select>
    </div>

    <div class="flex flex-col gap-1">
      <span class="text-xs text-muted-foreground">视频模式</span>
      <select
        :value="batchStore.globalConfig.videoMode"
        @change="batchStore.globalConfig.videoMode = ($event.target as HTMLSelectElement).value"
        class="flex h-9 w-[120px] rounded-md border border-input bg-background px-3 py-1 text-sm"
      >
        <option value="kenburns">Ken Burns</option>
        <option value="template">固定模板</option>
      </select>
    </div>

    <div class="flex flex-col gap-1">
      <span class="text-xs text-muted-foreground">洗稿模式</span>
      <select
        :value="batchStore.globalConfig.rewriteParams.rewriteMode"
        @change="batchStore.globalConfig.rewriteParams.rewriteMode = ($event.target as HTMLSelectElement).value as any"
        class="flex h-9 w-[160px] rounded-md border border-input bg-background px-3 py-1 text-sm"
      >
        <option value="flexible">首尾锁·中段自由</option>
        <option value="rigid">锁骨架换血肉</option>
      </select>
    </div>

    <div class="flex flex-col gap-1">
      <span class="text-xs text-muted-foreground">
        对标素材 {{ batchStore.globalConfig.rewriteParams.referenceCount }}
      </span>
      <div class="w-[140px]">
        <Slider
          :model-value="[batchStore.globalConfig.rewriteParams.referenceCount]"
          @update:model-value="(val: number[]) => batchStore.globalConfig.rewriteParams.referenceCount = val[0] ?? 0"
          :min="0" :max="10" :step="1"
        />
      </div>
    </div>
  </div>
</template>
