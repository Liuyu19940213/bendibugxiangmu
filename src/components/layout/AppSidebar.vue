<template>
  <aside class="flex w-40 shrink-0 flex-col border-r border-border bg-card">
    <!-- Logo / Brand -->
    <div class="flex h-14 items-center justify-center border-b border-border">
      <span class="text-lg font-semibold tracking-tight text-foreground">
        Pixelle
      </span>
    </div>

    <!-- Navigation -->
    <nav class="flex flex-1 flex-col gap-1 p-3">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        active-class="bg-accent text-accent-foreground"
      >
        <component :is="item.icon" class="h-4 w-4" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Settings at bottom -->
    <div class="border-t border-border p-3">
      <router-link
        :to="historyItem.to"
        class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        active-class="bg-accent text-accent-foreground"
      >
        <component :is="historyItem.icon" class="h-4 w-4" />
        <span>{{ historyItem.label }}</span>
      </router-link>
      <router-link
        :to="settingsItem.to"
        class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground mt-1"
        active-class="bg-accent text-accent-foreground"
      >
        <component :is="settingsItem.icon" class="h-4 w-4" />
        <span>{{ settingsItem.label }}</span>
      </router-link>
    </div>
  </aside>
</template>

<script setup lang="ts">
import {
  Library,
  Crosshair,
  Palette,
  Package,
  FileText,
  BookOpen,
  History,
  Settings,
  Boxes,
  type Component,
} from "lucide-vue-next";

interface NavItem {
  to: string;
  label: string;
  icon: Component;
}

const navItems: NavItem[] = [
  { to: "/fine", label: "洗稿和二创", icon: Crosshair },
  { to: "/batch", label: "批量创作", icon: Library },
  { to: "/template", label: "模板画布", icon: Palette },
  { to: "/media", label: "素材库", icon: Package },
  { to: "/copy", label: "文案库", icon: FileText },
  { to: "/book-defaults", label: "书籍默认配置", icon: BookOpen },
  { to: "/models", label: "模型管理", icon: Boxes },
];

const settingsItem: NavItem = {
  to: "/settings",
  label: "设置",
  icon: Settings,
};

const historyItem: NavItem = {
  to: "/history",
  label: "运行历史",
  icon: History,
};
</script>
