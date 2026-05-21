<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  DialogTitle,
  type DialogTitleProps,
  useForwardProps,
} from "radix-vue";
import { type HTMLAttributes } from "vue";

const props = defineProps<
  DialogTitleProps & { class?: HTMLAttributes["class"] }
>();
const forwarded = useForwardProps(props);
</script>

<template>
  <DialogTitle
    v-bind="forwarded"
    :class="
      cn('text-lg font-semibold leading-none tracking-tight', props.class)
    "
  >
    <slot />
  </DialogTitle>
</template>
