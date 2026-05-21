<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useBatchStore } from '@/stores/batch'
import {
  buildExportPayload,
  downloadJsonFile,
  readJsonFile,
  validateImportPayload,
  applyImportedSettings,
  type ExportSchema,
} from '@/services/configIO'
import { listTemplates, getTemplateContent, type TemplateInfo } from '@/services/api'
import type { AppSettings, GlobalConfig } from '@/types'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Separator from '@/components/ui/Separator.vue'
import Tabs from '@/components/ui/Tabs.vue'
import TabsContent from '@/components/ui/TabsContent.vue'
import TabsList from '@/components/ui/TabsList.vue'
import TabsTrigger from '@/components/ui/TabsTrigger.vue'

import Slider from '@/components/ui/Slider.vue'
import { Upload, Download, AlertTriangle, CheckCircle, Eye, Palette, Type, Sparkles, Trash2 } from 'lucide-vue-next'

const settingsStore = useSettingsStore()
const batchStore = useBatchStore()

const templateName = ref('我的模板')
const importMessage = ref<{ type: 'success' | 'error'; text: string } | null>(null)
const importWarnApiKey = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const activeTab = ref('text')
const selectedTemplate = ref('1080x1920/image_default.html')
const previewText = ref('生活就像一杯茶，不会苦一辈子，但总会苦一阵子。')
const fontSize = ref(24)
const lineHeight = ref(1.6)
const letterSpacing = ref(2)
const textColor = ref('#ffffff')
const backgroundColor = ref('#667eea')
const opacity = ref(85)
const fontFamily = ref('"PingFang SC", "Microsoft YaHei", sans-serif')
const textAlign = ref<'left' | 'center' | 'right'>('center')
const textShadowColor = ref('#000000')
const textShadowBlur = ref(4)
const textShadowOffsetX = ref(2)
const textShadowOffsetY = ref(2)
const textPosX = ref(50)
const textPosY = ref([50])
const bgScale = ref(1.0)

const isDraggingText = ref(false)
const isResizing = ref(false)
const previewContainerRef = ref<HTMLElement | null>(null)

function onTextMouseDown(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.resize-handle')) return
  isDraggingText.value = true
  document.addEventListener('mousemove', onTextDragMove)
  document.addEventListener('mouseup', onTextDragUp)
  e.preventDefault()
}

function onTextDragMove(e: MouseEvent) {
  if (!isDraggingText.value || !previewContainerRef.value) return
  const rect = previewContainerRef.value.getBoundingClientRect()
  const y = e.clientY - rect.top
  const pct = Math.max(0, Math.min(100, Math.round((y / rect.height) * 100)))
  textPosY.value = [pct]
}

function onTextDragUp() {
  isDraggingText.value = false
  document.removeEventListener('mousemove', onTextDragMove)
  document.removeEventListener('mouseup', onTextDragUp)
}

function onResizeMouseDown(e: MouseEvent) {
  isResizing.value = true
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeUp)
  e.preventDefault()
  e.stopPropagation()
}

function onResizeMove(e: MouseEvent) {
  if (!isResizing.value) return
  const delta = e.movementY
  const newSize = Math.max(24, Math.min(80, fontSize.value + Math.round(delta * 0.5)))
  fontSize.value = newSize
}

function onResizeUp() {
  isResizing.value = false
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeUp)
}

function onBgWheel(e: WheelEvent) {
  if (!previewContainerRef.value) return
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.05 : 0.05
  bgScale.value = Math.max(0.5, Math.min(3.0, Math.round((bgScale.value + delta) * 100) / 100))
}

const PRESETS_KEY = 'pixelle_template_presets'
interface TemplatePreset {
  id: string
  name: string
  createdAt: string
  template: string
  fontSize: number
  lineHeight: number
  letterSpacing: number
  textColor: string
  backgroundColor: string
  opacity: number
  fontFamily: string
  textAlign: 'left' | 'center' | 'right'
  textShadowColor: string
  textShadowBlur: number
  textShadowOffsetX: number
  textShadowOffsetY: number
  textPosX: number
  textPosY: number
  bgScale: number
}
const presets = ref<TemplatePreset[]>([])
const presetName = ref('')
const showSavePreset = ref(false)
const presetNameError = ref('')

const templates = ref<TemplateInfo[]>([])
const groupedTemplates = computed(() => {
  const groups: Record<string, TemplateInfo[]> = {}
  templates.value.forEach(t => {
    if (!groups[t.size]) groups[t.size] = []
    groups[t.size].push(t)
  })
  return groups
})

const sizeOptions = computed(() => Object.keys(groupedTemplates.value))

const fontOptions = [
  { label: '系统默认', value: 'sans-serif' },
  { label: '苹方+雅黑', value: '"PingFang SC", "Microsoft YaHei", sans-serif' },
  { label: '苹方', value: '"PingFang SC", sans-serif' },
  { label: '微软雅黑', value: '"Microsoft YaHei", sans-serif' },
  { label: '宋体', value: '"SimSun", serif' },
  { label: '楷体', value: '"KaiTi", serif' },
  { label: '黑体', value: '"SimHei", sans-serif' },
  { label: '仿宋', value: '"FangSong", serif' },
]

const textShadowStyle = computed(() => {
  if (textShadowBlur.value === 0 && textShadowOffsetX.value === 0 && textShadowOffsetY.value === 0) return 'none'
  return `${textShadowOffsetX.value}px ${textShadowOffsetY.value}px ${textShadowBlur.value}px ${textShadowColor.value}`
})

const selectedSize = ref('1080x1920')

watch(selectedSize, (newSize) => {
  const firstTemplate = groupedTemplates.value[newSize]?.[0]
  if (firstTemplate) {
    selectedTemplate.value = firstTemplate.key
  }
})

watch(selectedTemplate, (newPath) => {
  const parts = newPath.split('/')
  if (parts[0] !== selectedSize.value) {
    selectedSize.value = parts[0]
  }
})

function getTemplateType(name: string): 'static' | 'image' | 'video' {
  if (name.startsWith('static_')) return 'static'
  if (name.startsWith('video_')) return 'video'
  return 'image'
}

const TEMPLATE_CN_NAMES: Record<string, string> = {
  'image_minimal_framed.html': '极简边框风格',
  'image_blur_card.html': '模糊背景卡片',
  'image_book.html': '图书解读',
  'image_cartoon.html': '卡通风格',
  'image_default.html': '图片默认',
  'image_elegant.html': '优雅风格',
  'image_excerpt.html': '图书摘抄',
  'image_fashion_vintage.html': '时尚复古风格',
  'image_full.html': '全屏图片',
  'image_healing.html': '疗愈风格',
  'image_health_preservation.html': '养生习惯',
  'image_life_insights.html': '人生感悟',
  'image_life_insights_light.html': '人生感悟·亮色',
  'image_long_text.html': '长文本',
  'image_modern.html': '现代风格',
  'image_neon.html': '霓虹风格',
  'image_psychology_card.html': '心理卡片风',
  'image_purple.html': '紫色梦幻',
  'image_satirical_cartoon.html': '讽刺漫画风格',
  'image_simple_black.html': '黑白简单风格',
  'image_simple_line_drawing.html': '简笔画小人',
  'static_default.html': '静态默认',
  'static_excerpt.html': '图书摘抄·静态',
  'video_default.html': '视频默认',
  'video_healing.html': '疗愈·动态',
  'image_film.html': '电影风格',
  'image_ultrawide_minimal.html': '极简风格·横屏',
  'image_wide_darktech.html': '横屏科技风格',
  'asset_default.html': '素材模版',
}

function getTemplateDisplayName(name: string): string {
  return TEMPLATE_CN_NAMES[name] || name.replace(/\.(html|htm)$/, '').replace(/^(static_|image_|video_)/, '')
}

function loadPresets() {
  try {
    const raw = localStorage.getItem(PRESETS_KEY)
    if (raw) presets.value = JSON.parse(raw)
  } catch { presets.value = [] }
}

function savePreset() {
  const name = presetName.value.trim()
  if (!name) {
    presetNameError.value = '请输入预设名称'
    return
  }
  presetNameError.value = ''
  const preset: TemplatePreset = {
    id: crypto.randomUUID(),
    name,
    createdAt: new Date().toISOString(),
    template: selectedTemplate.value,
    fontSize: fontSize.value,
    lineHeight: lineHeight.value,
    letterSpacing: letterSpacing.value,
    textColor: textColor.value,
    backgroundColor: backgroundColor.value,
    opacity: opacity.value,
    fontFamily: fontFamily.value,
    textAlign: textAlign.value,
    textShadowColor: textShadowColor.value,
    textShadowBlur: textShadowBlur.value,
    textShadowOffsetX: textShadowOffsetX.value,
    textShadowOffsetY: textShadowOffsetY.value,
    textPosX: textPosX.value,
    textPosY: textPosY.value[0],
    bgScale: bgScale.value,
  }
  presets.value.push(preset)
  localStorage.setItem(PRESETS_KEY, JSON.stringify(presets.value))
  presetName.value = ''
  showSavePreset.value = false
  importMessage.value = { type: 'success', text: `预设"${name}"已保存` }
}

function applyPreset(preset: TemplatePreset) {
  selectedTemplate.value = preset.template
  fontSize.value = preset.fontSize
  lineHeight.value = preset.lineHeight
  letterSpacing.value = preset.letterSpacing
  textColor.value = preset.textColor
  backgroundColor.value = preset.backgroundColor
  opacity.value = preset.opacity
  fontFamily.value = preset.fontFamily
  textAlign.value = preset.textAlign
  textShadowColor.value = preset.textShadowColor
  textShadowBlur.value = preset.textShadowBlur
  textShadowOffsetX.value = preset.textShadowOffsetX
  textShadowOffsetY.value = preset.textShadowOffsetY
  textPosX.value = preset.textPosX ?? 50
  textPosY.value = [preset.textPosY ?? 50]
  bgScale.value = preset.bgScale ?? 1.0
}

function deletePreset(id: string) {
  presets.value = presets.value.filter(p => p.id !== id)
  localStorage.setItem(PRESETS_KEY, JSON.stringify(presets.value))
}

const deletingPresetId = ref<string | null>(null)

function applyToBatch() {
  const existingIdx = presets.value.findIndex(p => p.name === '批量默认')
  const preset: TemplatePreset = {
    id: existingIdx >= 0 ? presets.value[existingIdx].id : crypto.randomUUID(),
    name: '批量默认',
    createdAt: new Date().toISOString(),
    template: selectedTemplate.value,
    fontSize: fontSize.value,
    lineHeight: lineHeight.value,
    letterSpacing: letterSpacing.value,
    textColor: textColor.value,
    backgroundColor: backgroundColor.value,
    opacity: opacity.value,
    fontFamily: fontFamily.value,
    textAlign: textAlign.value,
    textShadowColor: textShadowColor.value,
    textShadowBlur: textShadowBlur.value,
    textShadowOffsetX: textShadowOffsetX.value,
    textShadowOffsetY: textShadowOffsetY.value,
    textPosX: textPosX.value,
    textPosY: textPosY.value[0],
    bgScale: bgScale.value,
  }
  if (existingIdx >= 0) {
    presets.value[existingIdx] = preset
  } else {
    presets.value.push(preset)
  }
  localStorage.setItem(PRESETS_KEY, JSON.stringify(presets.value))
}

async function loadTemplates() {
  try {
    templates.value = await listTemplates()
    if (!selectedTemplate.value && templates.value.length > 0) {
      selectedTemplate.value = templates.value[0].key
    }
  } catch (e: unknown) {
    console.warn('加载模板列表失败：', e instanceof Error ? e.message : String(e))
  }
}

function handleExport() {
  try {
    const payload = buildExportPayload({
      name: templateName.value || '未命名',
      settings: settingsStore.settings,
      batchConfig: batchStore.globalConfig,
      template: {
        path: selectedTemplate.value,
        fontSize: fontSize.value,
        lineHeight: lineHeight.value,
        letterSpacing: letterSpacing.value,
        textColor: textColor.value,
        backgroundColor: backgroundColor.value,
        opacity: opacity.value,
        fontFamily: fontFamily.value,
        textAlign: textAlign.value,
        textShadowColor: textShadowColor.value,
        textShadowBlur: textShadowBlur.value,
        textShadowOffsetX: textShadowOffsetX.value,
        textShadowOffsetY: textShadowOffsetY.value,
        textPosX: textPosX.value,
        textPosY: textPosY.value[0],
        bgScale: bgScale.value,
      }
    })
    downloadJsonFile(payload)
  } catch {
    importMessage.value = { type: 'error', text: '导出失败，请检查配置数据' }
  }
}

function triggerImport() {
  fileInputRef.value?.click()
}

async function handleFileChange(e: Event) {
  importMessage.value = null
  importWarnApiKey.value = false

  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const raw = await readJsonFile(file)
    let parsed: unknown
    try {
      parsed = JSON.parse(raw)
    } catch {
      importMessage.value = { type: 'error', text: '文件格式错误：不是有效的 JSON' }
      return
    }

    const validated = validateImportPayload(parsed)
    if (!validated.ok) {
      importMessage.value = { type: 'error', text: validated.error }
      return
    }

    const data = validated.data
    applyImport(data)
    importMessage.value = {
      type: 'success',
      text: `成功导入"${data.name || '未命名'}"`,
    }
    importWarnApiKey.value = !!data.settings.llm?.apiKey
  } catch (err) {
    importMessage.value = { type: 'error', text: `导入失败：${err instanceof Error ? err.message : '未知错误'}` }
  } finally {
    target.value = ''
  }
}

function applyImport(data: ExportSchema) {
  const s = data.settings
  const b = data.batchConfig

  templateName.value = data.name || '导入的模板'

  if (data.template) {
    selectedTemplate.value = data.template.path || selectedTemplate.value
    fontSize.value = data.template.fontSize || fontSize.value
    lineHeight.value = data.template.lineHeight || lineHeight.value
    letterSpacing.value = data.template.letterSpacing || letterSpacing.value
    textColor.value = data.template.textColor || textColor.value
    backgroundColor.value = data.template.backgroundColor || backgroundColor.value
    opacity.value = data.template.opacity ?? opacity.value
    fontFamily.value = data.template.fontFamily || fontFamily.value
    textAlign.value = data.template.textAlign || textAlign.value
    textShadowColor.value = data.template.textShadowColor || textShadowColor.value
    textShadowBlur.value = data.template.textShadowBlur ?? textShadowBlur.value
    textShadowOffsetX.value = data.template.textShadowOffsetX ?? textShadowOffsetX.value
    textShadowOffsetY.value = data.template.textShadowOffsetY ?? textShadowOffsetY.value
    textPosX.value = (data.template as Record<string, unknown>).textPosX as number ?? textPosX.value
    textPosY.value = [(data.template as Record<string, unknown>).textPosY as number ?? textPosY.value[0]]
    bgScale.value = (data.template as Record<string, unknown>).bgScale as number ?? bgScale.value
  }

  applyImportedSettings(
    { settings: s, batchConfig: b },
    {
      updateLlmConfig: (c) => settingsStore.updateLlmConfig(c),
      updateTtsConfig: (c) => settingsStore.updateTtsConfig(c),
      updateImageConfig: (c) => settingsStore.updateImageConfig(c),
      setOutputPath: (p) => settingsStore.setOutputPath(p),
      setGlobalConfig: (c) => Object.assign(batchStore.globalConfig, c),
    },
  )
}

const configSummary = computed(() => [
  { label: 'LLM 模型', value: `${settingsStore.settings.llm.provider} / ${settingsStore.settings.llm.model}` },
  { label: 'LLM 地址', value: settingsStore.settings.llm.apiBase || '—' },
  { label: '配音方式', value: settingsStore.settings.tts.provider },
  { label: '语速', value: `${settingsStore.settings.tts.speed.toFixed(1)}x` },
  { label: '输出目录', value: settingsStore.settings.outputPath || '默认 output/' },
  { label: 'BGM 风格', value: batchStore.globalConfig.bgmStyle },
  { label: '视频时长', value: `${batchStore.globalConfig.durationMin / 60}～${batchStore.globalConfig.durationMax / 60} 分钟` },
  { label: '洗稿风格', value: batchStore.globalConfig.rewriteParams.style },
])

onMounted(() => {
  loadTemplates()
  loadPresets()
})

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onTextDragMove)
  document.removeEventListener('mouseup', onTextDragUp)
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeUp)
})
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 flex overflow-hidden">
      <div class="w-1/2 flex flex-col border-r border-border">
        <div class="p-4 border-b border-border">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="font-medium">模板配置</h2>
              <p class="text-xs text-muted-foreground mt-1">调整参数实时预览效果</p>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm flex items-center gap-2">
                <Sparkles class="h-4 w-4" />
                选择模板
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-3">
                <select
                  v-model="selectedSize"
                  class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option v-for="size in sizeOptions" :key="size" :value="size">
                    {{ size }}
                  </option>
                </select>

                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="template in groupedTemplates[selectedSize]"
                    :key="template.key"
                    @click="selectedTemplate = template.key"
                    :class="[
                      'p-2 rounded-lg text-left text-sm transition-all',
                      selectedTemplate === template.key
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted hover:bg-muted/80',
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-xs px-1.5 py-0.5 rounded" :class="{
                        'bg-green-500/20 text-green-600': template.name.startsWith('static_'),
                        'bg-blue-500/20 text-blue-600': template.name.startsWith('image_'),
                        'bg-purple-500/20 text-purple-600': template.name.startsWith('video_'),
                      }">
                        {{ template.name.startsWith('static_') ? '静态' : template.name.startsWith('image_') ? '图片' : '视频' }}
                      </span>
                    </div>
                    <div class="mt-1 truncate">{{ getTemplateDisplayName(template.name) }}</div>
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Tabs v-model="activeTab">
            <TabsList class="w-full">
              <TabsTrigger value="text" class="flex-1 flex items-center justify-center gap-2">
                <Type class="h-4 w-4" />
                文字
              </TabsTrigger>
              <TabsTrigger value="style" class="flex-1 flex items-center justify-center gap-2">
                <Palette class="h-4 w-4" />
                样式
              </TabsTrigger>
            </TabsList>

            <TabsContent value="text" class="mt-4 space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">预览文本</label>
                <textarea
                  v-model="previewText"
                  placeholder="输入预览文本..."
                  rows="4"
                  class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                ></textarea>
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">字体大小</label>
                  <span class="text-sm text-muted-foreground">{{ fontSize }}px</span>
                </div>
                <Slider
                  :model-value="[fontSize]"
                  @update:model-value="fontSize = Number($event[0])"
                  :min="24"
                  :max="80"
                  :step="1"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">字体</label>
                <select
                  v-model="fontFamily"
                  class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option v-for="f in fontOptions" :key="f.value" :value="f.value">
                    {{ f.label }}
                  </option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">对齐</label>
                <div class="flex gap-2">
                  <Button
                    size="sm"
                    :variant="textAlign === 'left' ? 'default' : 'outline'"
                    @click="textAlign = 'left'"
                  >左对齐</Button>
                  <Button
                    size="sm"
                    :variant="textAlign === 'center' ? 'default' : 'outline'"
                    @click="textAlign = 'center'"
                  >居中</Button>
                  <Button
                    size="sm"
                    :variant="textAlign === 'right' ? 'default' : 'outline'"
                    @click="textAlign = 'right'"
                  >右对齐</Button>
                </div>
              </div>
              <div class="space-y-2">
                 <div class="flex items-center justify-between">
                   <label class="text-sm font-medium">垂直位置</label>
                   <span class="text-sm text-muted-foreground">{{ textPosY }}%</span>
                 </div>
                 <Slider
                   v-model="textPosY"
                   :min="0"
                   :max="100"
                   :step="1"
                 />
               </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">行高</label>
                  <span class="text-sm text-muted-foreground">{{ lineHeight.toFixed(1) }}</span>
                </div>
                <Slider
                  :model-value="[lineHeight]"
                  @update:model-value="lineHeight = Number($event[0])"
                  :min="1.2"
                  :max="2.5"
                  :step="0.1"
                />
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">字间距</label>
                  <span class="text-sm text-muted-foreground">{{ letterSpacing }}px</span>
                </div>
                <Slider
                  :model-value="[letterSpacing]"
                  @update:model-value="letterSpacing = Number($event[0])"
                  :min="0"
                  :max="10"
                  :step="1"
                />
              </div>
            </TabsContent>

            <TabsContent value="style" class="mt-4 space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-sm font-medium">文字颜色</label>
                  <div class="flex items-center gap-2">
                    <input
                      v-model="textColor"
                      type="color"
                      class="w-10 h-10 rounded-lg cursor-pointer border border-input"
                    />
                    <Input v-model="textColor" class="flex-1" />
                  </div>
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium">背景颜色</label>
                  <div class="flex items-center gap-2">
                    <input
                      v-model="backgroundColor"
                      type="color"
                      class="w-10 h-10 rounded-lg cursor-pointer border border-input"
                    />
                    <Input v-model="backgroundColor" class="flex-1" />
                  </div>
                </div>
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">背景透明度</label>
                  <span class="text-sm text-muted-foreground">{{ opacity }}%</span>
                </div>
                <Slider
                  :model-value="[opacity]"
                  @update:model-value="opacity = Number($event[0])"
                  :min="50"
                  :max="100"
                  :step="1"
                />
              </div>
              
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">背景缩放</label>
                  <span class="text-sm text-muted-foreground">{{ (bgScale * 100).toFixed(0) }}%</span>
                </div>
                <Slider
                  :model-value="[bgScale]"
                  @update:model-value="bgScale = Number($event[0])"
                  :min="0.5"
                  :max="3.0"
                  :step="0.05"
                />
                <p class="text-xs text-muted-foreground">鼠标滚轮在预览区也可缩放背景</p>
              </div>
              
              <Separator />
              <div class="space-y-3">
                <label class="text-sm font-medium">文字阴影</label>
                <div class="grid grid-cols-2 gap-3">
                  <div class="space-y-1.5">
                    <label class="text-xs text-muted-foreground">阴影颜色</label>
                    <div class="flex items-center gap-2">
                      <input v-model="textShadowColor" type="color" class="w-8 h-8 rounded cursor-pointer border border-input" />
                      <Input v-model="textShadowColor" class="flex-1" />
                    </div>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs text-muted-foreground">模糊半径</label>
                    <div class="flex items-center gap-2">
                      <Slider
                        :model-value="[textShadowBlur]"
                        @update:model-value="textShadowBlur = Number($event[0])"
                        :min="0"
                        :max="20"
                        :step="1"
                      />
                      <span class="text-xs w-8 text-right">{{ textShadowBlur }}</span>
                    </div>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs text-muted-foreground">水平偏移</label>
                    <div class="flex items-center gap-2">
                      <Slider
                        :model-value="[textShadowOffsetX]"
                        @update:model-value="textShadowOffsetX = Number($event[0])"
                        :min="-10"
                        :max="10"
                        :step="1"
                      />
                      <span class="text-xs w-8 text-right">{{ textShadowOffsetX }}</span>
                    </div>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs text-muted-foreground">垂直偏移</label>
                    <div class="flex items-center gap-2">
                      <Slider
                        :model-value="[textShadowOffsetY]"
                        @update:model-value="textShadowOffsetY = Number($event[0])"
                        :min="-10"
                        :max="10"
                        :step="1"
                      />
                      <span class="text-xs w-8 text-right">{{ textShadowOffsetY }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm">导入/导出模板</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-2 mb-4">
                <label class="text-sm font-medium">模板名称</label>
                <Input v-model="templateName" placeholder="例如：书单号-沉稳风" />
              </div>

              <div
                v-if="importMessage"
                :class="[
                  'flex items-start gap-3 rounded-lg border p-3 mb-4',
                  importMessage.type === 'success'
                    ? 'border-green-500/30 bg-green-500/10'
                    : 'border-destructive/30 bg-destructive/10',
                ]"
              >
                <CheckCircle v-if="importMessage.type === 'success'" class="h-4 w-4 text-green-500 mt-0.5" />
                <AlertTriangle v-else class="h-4 w-4 text-destructive mt-0.5" />
                <div>
                  <p
                    :class="[
                      'text-sm font-medium',
                      importMessage.type === 'success' ? 'text-green-600' : 'text-destructive',
                    ]"
                  >
                    {{ importMessage.type === 'success' ? '导入成功' : '导入失败' }}
                  </p>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ importMessage.text }}</p>
                  <p
                    v-if="importWarnApiKey && importMessage.type === 'success'"
                    class="text-xs text-muted-foreground mt-1"
                  >
                    注意：导入文件包含 API Key，已写入配置。
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <Button class="gap-2 flex-1" @click="handleExport">
                  <Download class="h-4 w-4" />
                  导出模板
                </Button>
                <Button variant="outline" class="gap-2 flex-1" @click="triggerImport">
                  <Upload class="h-4 w-4" />
                  导入模板
                </Button>
              </div>

              <input
                ref="fileInputRef"
                type="file"
                accept=".json"
                class="hidden"
                @change="handleFileChange"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm flex items-center gap-2">
                <Sparkles class="h-4 w-4" />
                我的预设
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-2">
                <div v-if="showSavePreset" class="space-y-2">
                  <div class="flex items-center gap-2">
                    <Input v-model="presetName" placeholder="预设名称，如：书单号-沉稳风" class="flex-1" />
                    <Button size="sm" @click="savePreset">保存</Button>
                    <Button size="sm" variant="ghost" @click="showSavePreset = false; presetName = ''; presetNameError = ''">取消</Button>
                  </div>
                  <p v-if="presetNameError" class="text-xs text-destructive">{{ presetNameError }}</p>
                </div>
                <Button v-else variant="outline" size="sm" class="w-full gap-2" @click="showSavePreset = true; presetName = ''; presetNameError = ''">
                  + 保存当前参数为预设
                </Button>
                <div v-if="presets.length > 0" class="space-y-1.5 max-h-[200px] overflow-y-auto">
                  <div
                    v-for="preset in presets"
                    :key="preset.id"
                    class="flex items-center justify-between rounded-md px-3 py-2 bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <button
                      class="text-left flex-1 min-w-0"
                      @click="applyPreset(preset)"
                    >
                      <div class="text-sm font-medium truncate">{{ preset.name }}</div>
                      <div class="text-xs text-muted-foreground">{{ preset.template }}</div>
                    </button>
                    <Button
                      size="sm"
                      variant="ghost"
                      class="h-7 w-7 text-muted-foreground hover:text-destructive shrink-0"
                      @click="deletingPresetId = preset.id"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
                <div
                  v-if="deletingPresetId"
                  class="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2"
                >
                  <AlertTriangle class="h-4 w-4 text-destructive shrink-0" />
                  <span class="text-sm flex-1">确认删除该预设？</span>
                  <Button size="sm" variant="destructive" @click="deletePreset(deletingPresetId!); deletingPresetId = null">
                    删除
                  </Button>
                  <Button size="sm" variant="ghost" @click="deletingPresetId = null">取消</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-4">
              <Button class="w-full gap-2" @click="applyToBatch">
                <Sparkles class="h-4 w-4" />
                应用当前模板参数到批量创作
              </Button>
              <p class="text-xs text-muted-foreground mt-2 text-center">
                将模板样式同步为批量创作全局画面风格
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm">当前配置概览</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div v-for="row in configSummary" :key="row.label" class="flex flex-col gap-0.5">
                  <span class="text-muted-foreground">{{ row.label }}</span>
                  <span class="font-medium truncate">{{ row.value }}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div class="w-1/2 flex flex-col overflow-hidden">
        <div class="p-4 border-b border-border">
          <div class="flex items-center gap-2">
            <Eye class="h-5 w-5 text-muted-foreground" />
            <h2 class="font-medium">视频预览</h2>
          </div>
          <p class="text-xs text-muted-foreground mt-1">拖拽文字改位置 · 滚轮缩放背景 · 文字右下角拖拽改大小</p>
        </div>
        
        <div class="flex-1 flex items-center justify-center p-8 bg-muted/20">
          <div
            ref="previewContainerRef"
            class="relative shadow-2xl overflow-hidden"
            :class="{
              'w-[324px] h-[576px]': selectedSize === '1080x1920',
              'w-[576px] h-[324px]': selectedSize === '1920x1080',
              'w-[324px] h-[324px]': selectedSize === '1080x1080',
            }"
            :style="{
              background: backgroundColor,
              opacity: opacity / 100,
            }"
            @wheel.prevent="onBgWheel"
          >
            <div
              class="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/50 transition-transform duration-200"
              :style="{ transform: `scale(${bgScale})` }"
            ></div>
            
            <div class="absolute inset-0 flex justify-center p-8" :class="{ 'cursor-grab': !isDraggingText, 'cursor-grabbing': isDraggingText }">
              <div
                @mousedown="onTextMouseDown"
                :style="{
                  position: 'absolute',
                  top: `${textPosY[0]}%`,
                  transform: 'translateY(-50%)',
                  cursor: isDraggingText ? 'grabbing' : 'grab',
                  userSelect: 'none',
                  transition: isDraggingText ? 'none' : 'top 0.15s ease',
                }"
              >
                <div
                  v-if="!isDraggingText"
                  class="absolute -left-6 top-1/2 -translate-y-1/2 text-white/20 text-xs pointer-events-none select-none"
                  title="拖拽调整垂直位置"
                >⋮⋮</div>
                <p
                  class="leading-relaxed transition-colors"
                  :class="{ 'ring-2 ring-white/30 rounded': isDraggingText }"
                  :style="{
                    fontSize: `${fontSize}px`,
                    lineHeight: lineHeight,
                    letterSpacing: `${letterSpacing}px`,
                    color: textColor,
                    fontFamily: fontFamily,
                    textAlign: textAlign,
                    textShadow: textShadowStyle,
                    padding: isDraggingText ? '4px' : '0px',
                  }"
                >
                  {{ previewText }}
                </p>
                <div
                  class="resize-handle absolute -bottom-1 -right-1 w-4 h-4 border-2 border-white/40 rounded-sm cursor-nwse-resize hover:border-white/80 transition-colors"
                  :class="{ 'border-white/80 scale-125': isResizing }"
                  @mousedown="onResizeMouseDown"
                  title="拖拽调整字体大小"
                ></div>
              </div>
            </div>
            
            <div class="absolute bottom-2 right-2 px-2 py-1 bg-black/50 rounded text-xs text-white">
              {{ selectedSize }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
