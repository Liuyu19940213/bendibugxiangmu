<script setup lang="ts">
import { cn } from "@/lib/utils";
import { type HTMLAttributes } from "vue";

interface CardDescriptionProps {
  class?: HTMLAttributes["class"];
}

const props = defineProps<CardDescriptionProps>();
</script>

<template>
  <p :class="cn('text-sm text-muted-foreground', props.class)">
    <slot />
  </p>
</template>
