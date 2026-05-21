<script setup lang="ts">
import Separator from '@/components/ui/Separator.vue'

const props = defineProps<{
  steps: string[]
  currentIndex: number
}>()

const emit = defineEmits<{
  'go-to-step': [index: number]
}>()

function handleClick(index: number) {
  emit('go-to-step', index)
}
</script>

<template>
  <div class="flex items-center px-6 py-4 bg-card border-b">
    <template v-for="(step, i) in steps" :key="i">
      <!-- Step node -->
      <div
        class="flex flex-col items-center gap-1 cursor-pointer select-none hover:opacity-80 transition-opacity"
        @click="handleClick(i)"
      >
        <!-- Circle indicator -->
        <div
          class="h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors"
          :class="{
            'bg-primary text-primary-foreground': i === currentIndex,
            'bg-primary/20 text-primary': i < currentIndex,
            'bg-muted text-muted-foreground': i > currentIndex,
          }"
        >
          <span v-if="i < currentIndex">✓</span>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <!-- Label -->
        <span
          class="text-xs font-medium transition-colors"
          :class="{
            'text-primary': i === currentIndex,
            'text-primary/70': i < currentIndex,
            'text-muted-foreground': i > currentIndex,
          }"
        >
          {{ step }}
        </span>
      </div>

      <!-- Connector line between steps -->
      <div v-if="i < steps.length - 1" class="flex-1 mx-2 mb-4">
        <Separator
          orientation="horizontal"
          :class="{
            'bg-primary/40': i < currentIndex,
            'bg-muted': i >= currentIndex,
          }"
        />
      </div>
    </template>
  </div>
</template>
