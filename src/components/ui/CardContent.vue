<script setup lang="ts">
import { cn } from "@/lib/utils";
import { type HTMLAttributes } from "vue";

interface CardContentProps {
  class?: HTMLAttributes["class"];
}

const props = defineProps<CardContentProps>();
</script>

<template>
  <div :class="cn('p-6 pt-0', props.class)">
    <slot />
  </div>
</template>
