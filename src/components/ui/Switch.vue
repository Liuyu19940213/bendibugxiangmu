<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  SwitchRoot,
  SwitchThumb,
  type SwitchRootProps,
} from "radix-vue";
import { type HTMLAttributes } from "vue";

interface SwitchProps extends SwitchRootProps {
  class?: HTMLAttributes["class"];
}

const props = defineProps<SwitchProps>();
</script>

<template>
  <SwitchRoot
    :default-checked="defaultChecked"
    :checked="checked"
    :disabled="disabled"
    :required="required"
    :name="name"
    :value="value"
    :class="
      cn(
        'peer inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input',
        props.class
      )
    "
  >
    <SwitchThumb
      class="pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0"
    />
  </SwitchRoot>
</template>
