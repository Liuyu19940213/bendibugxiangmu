<script setup lang="ts">
import { cn } from "@/lib/utils";

const model = defineModel<string>();

defineProps<{
  rows?: number | string;
  placeholder?: string;
  disabled?: boolean;
  class?: string;
}>();

defineOptions({ inheritAttrs: false });
</script>

<template>
  <textarea
    v-model="model"
    v-bind="$attrs"
    :rows="Number($props.rows) || undefined"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="
      cn(
        'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        $props.class,
      )
    "
  />
</template>
