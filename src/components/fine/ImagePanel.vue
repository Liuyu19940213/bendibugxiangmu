<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useFineModeStore } from '@/stores/fineMode'
import { useSettingsStore } from '@/stores/settings'
import { useBookDefaultsStore } from '@/stores/bookDefaults'
import Button from '@/components/ui/Button.vue'
import { FolderOpen, Image, X } from 'lucide-vue-next'

const fineModeStore = useFineModeStore()
const settingsStore = useSettingsStore()
const bookDefaultsStore = useBookDefaultsStore()

const imageFolder = ref(fineModeStore.state.imageConfig.imageFolder || settingsStore.settings.image.imageFolder || '')
const imageCount = ref(fineModeStore.state.imageConfig.imageCount || settingsStore.settings.image.imageCount || 3)
const kenBurns = ref(true)
const imagePaths = ref<string[]>([])
const folderFiles = ref<string[]>([])

const folderInputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  const name = fineModeStore.state.bookName
  if (!name) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  if (bookDefaultsStore.defaults[name]) {
    imageCount.value = cfg.imageCount
    kenBurns.value = cfg.kenBurns
    if (cfg.imageFolder) imageFolder.value = cfg.imageFolder
  }
})

watch(() => fineModeStore.state.bookName, (name) => {
  if (!name) return
  const cfg = bookDefaultsStore.getBookConfig(name)
  if (bookDefaultsStore.defaults[name]) {
    imageCount.value = cfg.imageCount
    kenBurns.value = cfg.kenBurns
    if (cfg.imageFolder) imageFolder.value = cfg.imageFolder
  }
})

watch([imageFolder, imageCount, kenBurns, imagePaths], () => {
  fineModeStore.setImageConfig({
    mode: 'local',
    imageFolder: imageFolder.value,
    imageCount: imageCount.value,
    kenBurns: kenBurns.value,
    imagePaths: imagePaths.value,
    width: 1080,
    height: 1920,
  })
  fineModeStore.setSelectedImages(imagePaths.value)
}, { immediate: true })

function handleSelectFolder() {
  folderInputRef.value?.click()
}

function handleFolderSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return
  const firstPath = (files[0] as any).path || (files[0] as any).webkitRelativePath
  if (firstPath) {
    imageFolder.value = firstPath.replace(/[/\\][^/\\]+$/, '')
    folderFiles.value = []
    for (let i = 0; i < files.length; i++) {
      const f = files[i]
      if (f.type.startsWith('image/')) {
        const path = (f as any).path || (f as any).webkitRelativePath
        if (path) folderFiles.value.push(path)
      }
    }
  }
  input.value = ''
}

function pickRandomImages() {
  if (folderFiles.value.length === 0) return
  const count = Math.min(imageCount.value, folderFiles.value.length)
  const shuffled = [...folderFiles.value].sort(() => Math.random() - 0.5)
  imagePaths.value = shuffled.slice(0, count)
}

function removeImage(index: number) {
  imagePaths.value.splice(index, 1)
}

const folderName = computed(() => {
  if (!imageFolder.value) return ''
  return imageFolder.value.replace(/\\/g, '/').split('/').pop() || imageFolder.value
})

const displayPaths = computed(() =>
  imagePaths.value.map((p) => {
    const parts = p.replace(/\\/g, '/').split('/')
    return parts.slice(-2).join('/')
  })
)

const imageCountLabel = computed(() => imagePaths.value.length)
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 overflow-y-auto px-6 py-6">
      <div class="max-w-lg mx-auto space-y-6">

        <div class="space-y-2">
          <label class="text-sm font-medium">图片文件夹</label>
          <input ref="folderInputRef" type="file" webkitdirectory directory multiple accept="image/*" class="hidden" @change="handleFolderSelected" />
          <div v-if="imageFolder" class="space-y-3">
            <div class="flex items-center gap-2 p-2 rounded-md border bg-muted/30">
              <FolderOpen class="w-4 h-4 text-muted-foreground shrink-0" />
              <span class="text-sm truncate flex-1">{{ folderName || imageFolder }}</span>
              <span class="text-xs text-muted-foreground">{{ folderFiles.length }} 张</span>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="handleSelectFolder">更换文件夹</Button>
              <Button variant="outline" size="sm" :disabled="folderFiles.length === 0" @click="pickRandomImages">
                随机选取 {{ imageCount }} 张
              </Button>
            </div>
          </div>
          <Button v-else variant="outline" class="w-full" @click="handleSelectFolder">
            <FolderOpen class="w-4 h-4 mr-2" />
            选择图库文件夹
          </Button>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium">每次使用数量</label>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" :disabled="imageCount <= 1" @click="imageCount = Math.max(1, imageCount - 1)">−</Button>
            <span class="w-8 text-center text-sm">{{ imageCount }}</span>
            <Button variant="outline" size="sm" :disabled="imageCount >= 20" @click="imageCount = Math.min(20, imageCount + 1)">+</Button>
          </div>
        </div>

        <div v-if="imageCountLabel > 0" class="space-y-2">
          <p class="text-xs text-muted-foreground">
            已选 <span class="font-medium text-foreground">{{ imageCountLabel }}</span> 张图片
            <span v-if="imageCountLabel < imageCount" class="text-amber-500">（不足 {{ imageCount }} 张，将全部使用）</span>
          </p>
          <div class="space-y-1 max-h-[320px] overflow-y-auto">
            <div
              v-for="(path, i) in displayPaths"
              :key="i"
              class="flex items-center gap-2 rounded-md border bg-muted/30 px-3 py-2 group"
            >
              <Image class="w-4 h-4 text-muted-foreground shrink-0" />
              <span class="text-sm truncate flex-1">{{ path }}</span>
              <button class="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" @click="removeImage(i)">
                <X class="w-4 h-4 text-muted-foreground hover:text-destructive" />
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium">Ken Burns 效果</label>
            <p class="text-xs text-muted-foreground">视频播放时自动缓慢缩放/平移图片</p>
          </div>
          <button
            role="switch"
            :aria-checked="kenBurns"
            :class="['inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors', kenBurns ? 'bg-primary' : 'bg-input']"
            @click="kenBurns = !kenBurns"
          >
            <span :class="['pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg transition-transform', kenBurns ? 'translate-x-5' : 'translate-x-0']" />
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between px-6 py-3 border-t bg-card flex-shrink-0">
      <Button variant="outline" @click="fineModeStore.prevStep()">← 上一步</Button>
      <Button @click="fineModeStore.nextStep()">下一步 →</Button>
    </div>
  </div>
</template>
