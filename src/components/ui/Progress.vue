<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/lib/utils";
import {
  ProgressRoot,
  ProgressIndicator,
  type ProgressRootProps,
} from "radix-vue";
import { type HTMLAttributes } from "vue";

interface Props extends ProgressRootProps {
  class?: HTMLAttributes["class"];
}

const props = defineProps<Props>();

const progressModelValue = computed(() => (props.modelValue as number) ?? 0);
</script>

<template>
  <ProgressRoot
    :class="
      cn(
        'relative h-4 w-full overflow-hidden rounded-full bg-secondary',
        props.class
      )
    "
    v-bind="props"
  >
    <ProgressIndicator
      class="h-full w-full flex-1 bg-primary transition-all"
      :style="`transform: translateX(-${100 - progressModelValue}%)`"
    />
  </ProgressRoot>
</template>
