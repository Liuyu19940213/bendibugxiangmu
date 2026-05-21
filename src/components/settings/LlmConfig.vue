<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { testLlmConnection } from '@/services/api'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Slider from '@/components/ui/Slider.vue'

const settingsStore = useSettingsStore()

const form = reactive({
  provider: settingsStore.settings.llm.provider,
  apiBase: settingsStore.settings.llm.apiBase,
  apiKey: settingsStore.settings.llm.apiKey,
  model: settingsStore.settings.llm.model,
  temperature: settingsStore.settings.llm.temperature,
})

const showApiKey = ref(false)
const isLocked = ref(!!settingsStore.settings.llm.apiKey)
const isTesting = ref(false)
const testMsg = ref('')
const testOk = ref(false)

const providers = [
  { label: 'DeepSeek', value: 'DeepSeek', apiBase: 'https://api.deepseek.com', model: 'deepseek-chat' },
  { label: '通义千问', value: '通义千问', apiBase: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus' },
  { label: '豆包', value: '豆包', apiBase: 'https://ark.cn-beijing.volces.com/api/v3', model: 'doubao-pro-32k' },
]

watch(() => form.provider, (val) => {
  if (isLocked.value) return
  const preset = providers.find(p => p.value === val)
  if (preset) {
    form.apiBase = preset.apiBase
    form.model = preset.model
  }
})

function saveConfig() {
  settingsStore.updateLlmConfig({
    provider: form.provider,
    apiBase: form.apiBase,
    apiKey: form.apiKey,
    model: form.model,
    temperature: form.temperature,
  })
}

async function handleTest() {
  isTesting.value = true
  testMsg.value = ''
  testOk.value = false

  try {
    const res = await testLlmConnection({
      provider: form.provider,
      api_base: form.apiBase,
      api_key: form.apiKey,
      model: form.model,
    })

    testOk.value = res.ok
    testMsg.value = res.detail

    if (res.ok) {
      saveConfig()
      isLocked.value = true
    }
  } catch (e: unknown) {
    testOk.value = false
    testMsg.value = e instanceof Error ? e.message : '测试请求失败'
  } finally {
    isTesting.value = false
  }
}

function handleReset() {
  form.apiKey = ''
  isLocked.value = false
  testMsg.value = ''
  testOk.value = false
  settingsStore.updateLlmConfig({
    provider: form.provider,
    apiBase: form.apiBase,
    apiKey: '',
    model: form.model,
    temperature: form.temperature,
  })
}

onMounted(() => {
  if (settingsStore.settings.llm.apiKey) {
    isLocked.value = true
  }
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>
        LLM API 配置
        <span v-if="isLocked" class="ml-2 text-xs font-normal text-green-600 dark:text-green-400">
          ✓ 已通过测试
        </span>
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- 测试结果消息 -->
      <div
        v-if="testMsg"
        :class="[
          'px-3 py-2 rounded text-sm',
          testOk
            ? 'bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300'
            : 'bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300',
        ]"
      >
        {{ testMsg }}
      </div>

      <div>
        <label class="text-sm font-medium">提供商</label>
        <select
          v-model="form.provider"
          :disabled="isLocked"
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm mt-1 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <option v-for="p in providers" :key="p.value" :value="p.value">{{ p.label }}</option>
        </select>
      </div>

      <div>
        <label class="text-sm font-medium">API Base</label>
        <Input v-model="form.apiBase" :disabled="isLocked" class="mt-1" />
      </div>

      <div>
        <label class="text-sm font-medium">API Key</label>
        <div class="relative mt-1">
          <Input
            :type="showApiKey ? 'text' : 'password'"
            v-model="form.apiKey"
            :disabled="isLocked"
            placeholder="sk-..."
          />
          <button
            v-if="!isLocked"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-muted-foreground hover:text-foreground"
            @click="showApiKey = !showApiKey"
          >
            {{ showApiKey ? '隐藏' : '显示' }}
          </button>
        </div>
      </div>

      <div>
        <label class="text-sm font-medium">模型名称</label>
        <Input v-model="form.model" :disabled="isLocked" class="mt-1" />
      </div>

      <div>
        <label class="text-sm font-medium">Temperature: {{ form.temperature.toFixed(1) }}</label>
        <Slider
          :model-value="[form.temperature]"
          @update:model-value="form.temperature = Number($event[0])"
          :min="0.1"
          :max="2.0"
          :step="0.1"
          :disabled="isLocked"
          class="mt-2"
        />
      </div>

      <div class="flex gap-2 pt-2">
        <template v-if="!isLocked">
          <Button
            :disabled="!form.apiKey || !form.apiBase || !form.model || isTesting"
            @click="handleTest"
          >
            {{ isTesting ? '测试中...' : '测试连接' }}
          </Button>
        </template>
        <template v-else>
          <Button variant="outline" @click="handleReset">重置</Button>
        </template>
      </div>
    </CardContent>
  </Card>
</template>
