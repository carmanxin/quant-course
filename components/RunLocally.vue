<template>
  <div class="run-locally">
    <span class="run-locally-icon">💡</span>
    <span class="run-locally-text">
      此代码依赖 <strong>{{ packages }}</strong>，浏览器环境不支持。
      <a :href="colabUrl" target="_blank" rel="noopener" class="run-locally-link">在 Colab 打开 ↗</a>
      <span class="run-locally-divider">|</span>
      <span class="run-locally-local">本地运行：<code>bash setup.sh</code> → <code>jupyter lab</code></span>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  packages?: string
  colabUrl?: string
}>(), {
  packages: '',
  colabUrl: 'https://colab.research.google.com/drive/1-placeholder',
})
</script>

<style scoped>
.run-locally {
  margin: 12px 0;
  padding: 10px 16px;
  border-radius: 10px;
  background: var(--vp-c-bg-alt);
  border: 1px solid var(--vp-c-border);
  font-size: 0.88em;
  line-height: 1.6;
}

:root .run-locally {
  background: #fff9e6;
  border-color: #ffdf80;
}

.dark .run-locally {
  background: rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.2);
}

.run-locally-icon {
  margin-right: 6px;
}

.run-locally-text {
  color: var(--vp-c-text-2);
}

.run-locally-link {
  color: #007AFF;
  font-weight: 600;
  text-decoration: none;
}

.run-locally-link:hover {
  text-decoration: underline;
}

.run-locally-divider {
  margin: 0 8px;
  color: var(--vp-c-text-3);
}

.run-locally-local {
  color: var(--vp-c-text-3);
}

.run-locally-local code {
  background: var(--vp-c-bg);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.92em;
}
</style>
