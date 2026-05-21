<script setup lang="ts">
import { ref } from "vue";
import Slider from "@/components/ui/Slider.vue";
import Select from "@/components/ui/Select.vue";
import SelectTrigger from "@/components/ui/SelectTrigger.vue";
import SelectValue from "@/components/ui/SelectValue.vue";
import SelectContent from "@/components/ui/SelectContent.vue";
import SelectGroup from "@/components/ui/SelectGroup.vue";
import SelectItem from "@/components/ui/SelectItem.vue";

const sliderValue = ref([3]);
const selectValue = ref("clone");

const testResults = ref<string[]>([]);

function log(msg: string) {
  testResults.value.push(`[${new Date().toLocaleTimeString()}] ${msg}`);
}

function onSliderChange(val: number[]) {
  sliderValue.value = val;
  log(`Slider 拖拽 → ${val[0]}`);
}

function onSelectChange(val: string) {
  selectValue.value = val;
  log(`Select 选中 → ${val}`);
}
</script>

<template>
  <div class="max-w-xl mx-auto p-8 space-y-8">
    <h1 class="text-2xl font-bold">组件功能测试页</h1>

    <!-- Slider 测试 -->
    <section class="space-y-3 p-6 border rounded-lg">
      <h2 class="text-lg font-semibold">1. Slider 滑块测试</h2>
      <p class="text-sm text-muted-foreground">拖拽滑块，下方的值应该实时变化</p>
      <div class="flex items-center gap-4">
        <div class="w-[200px]">
          <Slider
            :model-value="sliderValue"
            @update:model-value="onSliderChange"
            :min="0"
            :max="10"
            :step="1"
          />
        </div>
        <span class="text-xl font-mono bg-muted px-3 py-1 rounded">{{ sliderValue[0] }}</span>
      </div>
    </section>

    <!-- Select 测试 -->
    <section class="space-y-3 p-6 border rounded-lg">
      <h2 class="text-lg font-semibold">2. Select 下拉框测试</h2>
      <p class="text-sm text-muted-foreground">点击下拉框，选择不同选项，下方应显示选中的值</p>
      <div class="flex items-center gap-4">
        <Select :model-value="selectValue" @update:model-value="(v: string) => onSelectChange(v)">
          <SelectTrigger class="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="clone">克隆男声</SelectItem>
              <SelectItem value="tts">TTS合成</SelectItem>
              <SelectItem value="female">女声</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <span class="text-xl font-mono bg-muted px-3 py-1 rounded">{{ selectValue }}</span>
      </div>
    </section>

    <!-- 原生 range 对照组 -->
    <section class="space-y-3 p-6 border rounded-lg">
      <h2 class="text-lg font-semibold">3. 原生 range 对照组</h2>
      <p class="text-sm text-muted-foreground">系统自带滑块，排除浏览器环境问题</p>
      <div class="flex items-center gap-4">
        <input
          type="range"
          :min="0"
          :max="10"
          :step="1"
          :value="sliderValue[0]"
          @input="onSliderChange([Number(($event.target as HTMLInputElement).value)])"
          class="w-[200px]"
        />
        <span class="text-xl font-mono bg-muted px-3 py-1 rounded">{{ sliderValue[0] }}</span>
      </div>
    </section>

    <!-- 原生 Select 对比测试 -->
    <section class="space-y-3 p-6 border rounded-lg">
      <h2 class="text-lg font-semibold">4. 原生 Select 对比测试</h2>
      <p class="text-sm text-muted-foreground">原生 select 作为对照组，确保基本环境正常</p>
      <select
        class="flex h-9 w-[180px] rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
      >
        <option>选项A</option>
        <option>选项B</option>
        <option>选项C</option>
      </select>
    </section>

    <!-- 测试日志 -->
    <section class="space-y-3 p-6 border rounded-lg">
      <h2 class="text-lg font-semibold">5. 交互日志</h2>
      <div class="bg-muted rounded-md p-3 max-h-40 overflow-y-auto font-mono text-xs space-y-1">
        <div v-if="testResults.length === 0" class="text-muted-foreground">等待交互...</div>
        <div v-for="(msg, i) in testResults" :key="i">{{ msg }}</div>
      </div>
    </section>
  </div>
</template>
