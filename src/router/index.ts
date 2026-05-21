import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AppLayout,
      children: [
        { path: "", redirect: "/batch" },
        { path: "batch", name: "batch", component: () => import("@/views/BatchCreation.vue") },
        { path: "fine", name: "fine", component: () => import("@/views/FineMode.vue") },
        { path: "template", name: "template", component: () => import("@/views/TemplateCanvas.vue") },
        { path: "media", name: "media", component: () => import("@/views/MediaLibrary.vue") },
        { path: "copy", name: "copy", component: () => import("@/views/CopyLibrary.vue") },
        { path: "history", name: "history", component: () => import("@/views/HistoryView.vue") },
        { path: "settings", name: "settings", component: () => import("@/views/Settings.vue") },
        { path: "book-defaults", name: "book-defaults", component: () => import("@/views/BookDefaults.vue") },
        { path: "models", name: "models", component: () => import("@/views/ModelManager.vue") },
        { path: "test", name: "test", component: () => import("@/views/TestComponents.vue") },
      ],
    },
  ],
});

export default router;
