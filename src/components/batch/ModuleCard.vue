<script setup lang="ts">
import type { BatchModule, GlobalConfig } from "@/types";
import { useBatchStore } from "@/stores/batch";
import Button from "@/components/ui/Button.vue";
import Badge from "@/components/ui/Badge.vue";
import Textarea from "@/components/ui/Textarea.vue";
import CardHeader from "@/components/ui/CardHeader.vue";
import CardTitle from "@/components/ui/CardTitle.vue";
import CardContent from "@/components/ui/CardContent.vue";
import { Trash2, ChevronDown, ChevronUp } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  module: BatchModule;
}>();

const emit = defineEmits<{
  remove: [id: string];
  "update:override": [override: Partial<GlobalConfig>];
}>();

const batchStore = useBatchStore();
const showOverride = ref(false);
const useCustomConfig = ref(!!props.module.configOverride && Object.keys(props.module.configOverride).length > 0)

const override = ref<Partial<GlobalConfig>>({ ...props.module.configOverride })

watch(override, (val) => { emit("update:override", { ...val }) }, { deep: true })

function toggleCustomConfig(val: boolean) {
  useCustomConfig.value = val
  if (!val) emit("update:override", {})
}

function getStatusBadge(status: string) {
  const map: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
    idle: { label: "待处理", variant: "secondary" },
    pending: { label: "排队中", variant: "outline" },
    running: { label: "运行中", variant: "default" },
    completed: { label: "已完成", variant: "default" },
    failed: { label: "失败", variant: "destructive" },
    skipped: { label: "已跳过", variant: "outline" },
  };
  return map[status] ?? { label: status, variant: "outline" };
}
</script>

<template>
  <div class="border rounded-lg bg-card">
    <CardHeader class="pb-2">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-2 min-w-0">
          <CardTitle class="text-base truncate">{{ module.bookName }}</CardTitle>
          <Badge :variant="getStatusBadge(module.status).variant">
            {{ getStatusBadge(module.status).label }}
          </Badge>
        </div>
        <div class="flex items-center gap-1 shrink-0">
          <span class="text-xs text-muted-foreground">{{ useCustomConfig ? '自定义' : '全局' }}</span>
          <button
            role="switch"
            :aria-checked="useCustomConfig"
            :class="['inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', useCustomConfig ? 'bg-primary' : 'bg-input']"
            @click="toggleCustomConfig(!useCustomConfig)"
          >
            <span :class="['pointer-events-none block h-4 w-4 rounded-full bg-background shadow-sm ring-0 transition-transform', useCustomConfig ? 'translate-x-4' : 'translate-x-0']" />
          </button>
          <Button variant="ghost" size="sm" @click="showOverride = !showOverride">
            <ChevronDown v-if="!showOverride" class="h-4 w-4" />
            <ChevronUp v-else class="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" :disabled="module.status === 'running'" @click="emit('remove', module.id)">
            <Trash2 class="h-4 w-4 text-muted-foreground hover:text-destructive" />
          </Button>
        </div>
      </div>
    </CardHeader>

    <CardContent class="space-y-3 pb-4">
      <div v-if="module.errorMessage" class="text-sm text-destructive">{{ module.errorMessage }}</div>

      <div>
        <label class="text-xs text-muted-foreground">文案内容</label>
        <Textarea
          :model-value="module.rawText"
          @update:model-value="batchStore.updateRawText(props.module.id, $event ?? '')"
          rows="4"
          :disabled="module.status === 'running'"
          class="mt-1 text-sm"
          placeholder="输入文案内容..."
        />
      </div>

      <div v-if="module.resultText" class="space-y-1">
        <p class="text-xs text-muted-foreground">洗稿结果</p>
        <p class="text-sm leading-relaxed border-l-2 border-primary/40 pl-3 max-h-[200px] overflow-y-auto">
          {{ module.resultText }}
        </p>
      </div>

      <div v-if="showOverride && useCustomConfig" class="space-y-3 pl-3 border-l-2 border-muted">
        <p class="text-xs text-muted-foreground">模块独立配置（覆盖全局）</p>

        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="text-xs text-muted-foreground">配音引擎</label>
            <select
              :value="override.voiceProvider"
              @change="override.voiceProvider = ($event.target as HTMLSelectElement).value"
              class="flex h-8 w-full rounded-md border border-input bg-background px-2 py-0.5 text-xs"
            >
              <option value="">继承全局</option>
              <option value="cosyvoice">CosyVoice2（本地）</option>
              <option value="indextts">IndexTTS（备用）</option>
              <option value="mimo">Mimo</option>
              <option value="minimax">MiniMax 海螺</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-muted-foreground">BGM风格</label>
            <select
              :value="override.bgmStyle"
              @change="(override.bgmStyle as any) = ($event.target as HTMLSelectElement).value"
              class="flex h-8 w-full rounded-md border border-input bg-background px-2 py-0.5 text-xs"
            >
              <option value="">继承全局</option>
              <option value="激昂">激昂</option>
              <option value="宁静">宁静</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-muted-foreground">视频模式</label>
            <select
              :value="override.videoMode"
              @change="override.videoMode = ($event.target as HTMLSelectElement).value"
              class="flex h-8 w-full rounded-md border border-input bg-background px-2 py-0.5 text-xs"
            >
              <option value="">继承全局</option>
              <option value="kenburns">Ken Burns</option>
              <option value="template">固定模板</option>
            </select>
          </div>
        </div>
      </div>
    </CardContent>
  </div>
</template>
