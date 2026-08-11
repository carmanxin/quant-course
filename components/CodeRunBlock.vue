<template>
  <div class="crb" :class="{ 'crb--open': isOpen }">
    <!-- 代码区(默认只读 Shiki 高亮) -->
    <div class="crb-code">
      <div class="crb-bar">
        <span class="crb-tag">
          <span class="crb-lang">{{ langLabel }}</span>
          <span class="crb-len">{{ lineCount }} 行 · {{ sizeHint }}</span>
        </span>
        <div class="crb-actions">
          <button class="crb-btn" @click="copyCode" :title="copied ? '已复制' : '复制代码'">
            {{ copied ? '✓ 已复制' : '📋 复制' }}
          </button>
          <button class="crb-btn crb-btn--primary" @click="toggleRun" :disabled="opening">
            <template v-if="opening">⏳ 准备中...</template>
            <template v-else-if="isOpen">▼ 收起</template>
            <template v-else>▶ 一键运行</template>
          </button>
        </div>
      </div>
      <div class="crb-rendered">
        <slot />
      </div>
    </div>

    <!-- 运行区(展开) -->
    <Transition name="crb-slide">
      <div v-if="isOpen" class="crb-runner">
        <PythonPlayground :code="decodedCode" :height="180" />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import PythonPlayground from './PythonPlayground.vue'

const props = withDefaults(defineProps<{
  codeB64?: string
  lang?: string
}>(), {
  codeB64: '',
  lang: 'python',
})

const isOpen = ref(false)
const opening = ref(false)
const copied = ref(false)

const decodedCode = computed(() => {
  try {
    return decodeURIComponent(escape(atob(props.codeB64)))
  } catch (e) {
    return ''
  }
})

const rawLines = computed(() => decodedCode.value.split('\n'))
const lineCount = computed(() => rawLines.value.length - 1)

const sizeHint = computed(() => {
  const bytes = new Blob([decodedCode.value]).size
  if (bytes > 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return bytes + ' B'
})

const langLabel = computed(() => props.lang?.toUpperCase() || 'PYTHON')

async function toggleRun() {
  if (isOpen.value) {
    isOpen.value = false
    return
  }
  opening.value = true
  isOpen.value = true
  await nextTick()
  // 等几帧让过渡开始渲染
  setTimeout(() => {
    opening.value = false
  }, 200)
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(decodedCode.value)
    copied.value = true
    setTimeout(() => copied.value = false, 1500)
  } catch (e) {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = decodedCode.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => copied.value = false, 1500)
  }
}
</script>

<style scoped>
.crb {
  margin: 16px 0;
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  background: var(--vp-c-bg-soft, #f6f7f9);
  overflow: hidden;
  transition: border-color .2s, box-shadow .2s;
}
.crb:hover, .crb--open {
  border-color: var(--ft-brand, #00E5A0);
  box-shadow: 0 0 0 1px rgba(0, 229, 160, .15), 0 8px 24px rgba(0, 0, 0, .04);
}
.crb-code {
  position: relative;
}
.crb-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, rgba(0,229,160,.06), rgba(0,212,255,.04));
  border-bottom: 1px solid var(--vp-c-divider, #e2e8f0);
  gap: 8px;
}
.crb-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--vp-c-text-2, #5a6c8c);
  font-size: 12px;
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
}
.crb-lang {
  background: rgba(0,229,160,.18);
  color: #009e6e;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}
.crb-len { opacity: .8; }

.crb-actions {
  display: flex;
  gap: 6px;
}
.crb-btn {
  font-size: 12px;
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  border-radius: 6px;
  background: white;
  color: var(--vp-c-text-1, #1f2937);
  cursor: pointer;
  transition: all .15s;
  font-family: inherit;
  font-weight: 500;
}
.crb-btn:hover {
  border-color: var(--ft-brand, #00E5A0);
  color: var(--ft-brand, #00E5A0);
}
.crb-btn:disabled {
  opacity: .5;
  cursor: not-allowed;
}
.crb-btn--primary {
  background: linear-gradient(135deg, var(--ft-brand, #00E5A0), var(--ft-brand-2, #00D4FF));
  color: #052e1d;
  border-color: transparent;
  font-weight: 600;
}
.crb-btn--primary:hover {
  color: #052e1d;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 229, 160, .35);
}

.crb-rendered {
  position: relative;
}
.crb-rendered :deep(pre.shiki),
.crb-rendered :deep(pre.vp-code-block) {
  margin: 0 !important;
  border-radius: 0 !important;
  border: none !important;
  background: var(--vp-code-block-bg, #fafbfc) !important;
}

.crb-rendered :deep(.code-block) {
  margin: 0 !important;
  border: none !important;
  border-radius: 0 !important;
  background: var(--vp-code-block-bg, #fafbfc) !important;
}

/* Dark mode适配 */
:global(html.dark) .crb {
  background: var(--vp-c-bg-soft, #1a1a1a);
  border-color: var(--vp-c-divider, #2d3748);
}
:global(html.dark) .crb-btn {
  background: rgba(255,255,255,.06);
  color: #e7eaf6;
  border-color: rgba(255,255,255,.12);
}
:global(html.dark) .crb-btn:hover {
  border-color: var(--ft-brand, #00E5A0);
}

.crb-runner {
  background: var(--vp-c-bg, white);
  border-top: 1px solid var(--ft-brand, #00E5A0);
}
:global(html.dark) .crb-runner {
  background: var(--vp-c-bg, #0f1117);
}

.crb-slide-enter-active, .crb-slide-leave-active {
  transition: max-height .35s ease, opacity .25s ease;
  overflow: hidden;
}
.crb-slide-enter-from, .crb-slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.crb-slide-enter-to, .crb-slide-leave-from {
  max-height: 700px;
  opacity: 1;
}
</style>
