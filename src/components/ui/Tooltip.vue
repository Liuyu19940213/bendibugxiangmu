<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  type TooltipRootProps,
} from "radix-vue";
import { type HTMLAttributes } from "vue";

interface Props extends TooltipRootProps {
  class?: HTMLAttributes["class"];
  contentClass?: HTMLAttributes["class"];
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
}

const props = withDefaults(defineProps<Props>(), {
  side: "top",
  align: "center",
});
</script>

<template>
  <TooltipRoot v-bind="props">
    <TooltipTrigger as-child>
      <slot />
    </TooltipTrigger>
    <TooltipPortal>
      <TooltipContent
        :side="props.side"
        :align="props.align"
        :class="
          cn(
            'z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95',
            props.contentClass
          )
        "
      >
        <slot name="content" />
      </TooltipContent>
    </TooltipPortal>
  </TooltipRoot>
</template>
