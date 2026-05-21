<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  SliderRoot,
  SliderTrack,
  SliderRange,
  SliderThumb,
} from "radix-vue";

const model = defineModel<number[]>({ required: true });

defineProps<{
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  orientation?: "horizontal" | "vertical";
  dir?: "ltr" | "rtl";
  inverted?: boolean;
  class?: string;
}>();
</script>

<template>
  <SliderRoot
    v-model="model"
    :min="min"
    :max="max"
    :step="step"
    :disabled="disabled"
    :orientation="orientation"
    :dir="dir"
    :inverted="inverted"
    :class="
      cn(
        'relative flex w-full select-none items-center',
        $props.class,
      )
    "
  >
    <SliderTrack class="relative h-2 w-full grow overflow-hidden rounded-full bg-secondary">
      <SliderRange class="absolute h-full bg-primary" />
    </SliderTrack>
    <SliderThumb
      class="block h-5 w-5 rounded-full border-2 border-primary bg-background ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    />
  </SliderRoot>
</template>
