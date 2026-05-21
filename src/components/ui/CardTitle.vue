<script setup lang="ts">
import { cn } from "@/lib/utils";
import { type HTMLAttributes } from "vue";

interface CardTitleProps {
  class?: HTMLAttributes["class"];
}

const props = defineProps<CardTitleProps>();
</script>

<template>
  <h3 :class="cn('text-2xl font-semibold leading-none tracking-tight', props.class)">
    <slot />
  </h3>
</template>
