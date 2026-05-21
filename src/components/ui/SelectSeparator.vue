<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  SelectSeparator,
  type SelectSeparatorProps,
  useForwardProps,
} from "radix-vue";
import { type HTMLAttributes } from "vue";

const props = defineProps<
  SelectSeparatorProps & { class?: HTMLAttributes["class"] }
>();
const forwarded = useForwardProps(props);
</script>

<template>
  <SelectSeparator
    v-bind="forwarded"
    :class="cn('-mx-1 my-1 h-px bg-muted', props.class)"
  />
</template>
