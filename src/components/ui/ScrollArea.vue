<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  ScrollAreaRoot,
  ScrollAreaViewport,
  type ScrollAreaRootProps,
} from "radix-vue";
import type { HTMLAttributes } from "vue";
import ScrollBar from "./ScrollBar.vue";

const props = withDefaults(
  defineProps<ScrollAreaRootProps & { class?: HTMLAttributes["class"] }>(),
  {
    type: "hover",
  },
);
</script>

<template>
  <ScrollAreaRoot
    v-bind="props"
    :class="cn('relative overflow-hidden', props.class)"
  >
    <ScrollAreaViewport class="h-full w-full rounded-[inherit]">
      <slot />
    </ScrollAreaViewport>
    <ScrollBar orientation="vertical" />
    <ScrollBar orientation="horizontal" />
  </ScrollAreaRoot>
</template>
