<script setup lang="ts">
import { cn } from "@/lib/utils";
import { Separator as SeparatorPrimitive, type SeparatorProps } from "radix-vue";
import { type HTMLAttributes } from "vue";

interface Props extends SeparatorProps {
  class?: HTMLAttributes["class"];
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  orientation: "horizontal",
  decorative: false,
});
</script>

<template>
  <SeparatorPrimitive
    :orientation="orientation"
    :decorative="decorative"
    :class="
      cn(
        'shrink-0 bg-border',
        orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
        props.class
      )
    "
  >
    <slot />
  </SeparatorPrimitive>
</template>
