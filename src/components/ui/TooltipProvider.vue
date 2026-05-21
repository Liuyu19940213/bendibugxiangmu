<script setup lang="ts">
import { TooltipProvider, type TooltipProviderProps } from "radix-vue";

interface Props extends TooltipProviderProps {
  delayDuration?: number;
}

const props = withDefaults(defineProps<Props>(), {
  delayDuration: 300,
});
</script>

<template>
  <TooltipProvider v-bind="props">
    <slot />
  </TooltipProvider>
</template>
