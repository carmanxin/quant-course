<!-- components/StaticCodeBlock.vue -->
<template>
  <div class="scb" :class="{ 'scb--open': isOpen }">
    <div class="scb-bar">
      <span class="scb-tag">
        <span class="scb-lang">{{ langLabel }}</span>
        <span class="scb-len">{{ lineCount }} 行 · {{ sizeHint }}</span>
      </span>
      <div class="scb-actions">
        <button class="scb-btn" @click="copyCode" :title="copied ? '已复制' : '复制代码'">
          {{ copied ? '✓ 已复制' : '📋 复制' }}
        </button>
      </div>
    </div>

    <div class="scb-code">
      <slot />
    </div>

    <details class="scb-out" :open="defaultOpen" @toggle="onToggle">
      <summary class="scb-out-summary">
        <span class="scb-out-icon" :class="{ 'scb-out-icon--open': isOpen }">▶</span>
        点击展开可浏览运行结果
      </summary>
      <div class="scb-out-body">
        <div v-if="loading" class="scb-out-loading">加载结果中...</div>
        <template v-else-if="output">
          <pre v-if="output.text" class="scb-out-text">{{ output.text }}</pre>
          <div v-if="output.svgs && output.svgs.length" class="scb-out-svgs">
            <img
              v-for="(s, i) in output.svgs"
              :key="i"
              :src="s"
              :alt="`运行结果图 ${i + 1}`"
              loading="lazy"
            />
          </div>
          <div v-if="output.error" class="scb-out-error">⚠ {{ output.error }}</div>
        </template>
        <div v-else class="scb-out-empty">⚠ 暂无运行结果</div>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Output {
  text?: string
  svgs?: string[]
  error?: string
}

const props = withDefaults(defineProps<{
  codeB64?: string
  lang?: string
  defaultOpen?: boolean
}>(), {
  codeB64: '',
  lang: 'python',
  defaultOpen: false,
})

const isOpen = ref(false)
const copied = ref(false)
const loading = ref(false)
const output = ref<Output | null>(null)

const decodedCode = computed(() => {
  try {
    return decodeURIComponent(escape(atob(props.codeB64)))
  } catch (e) {
    return ''
  }
})

const rawLines = computed(() => decodedCode.value.split('\n'))
const lineCount = computed(() => Math.max(0, rawLines.value.length - 1))

const sizeHint = computed(() => {
  const bytes = new Blob([decodedCode.value]).size
  if (bytes > 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return bytes + ' B'
})

const langLabel = computed(() => props.lang?.toUpperCase() || 'PYTHON')

// 从源码首行提取 # @quantlab/output: <name>
const outputName = computed(() => {
  const first = rawLines.value[0] || ''
  const m = first.match(/^#\s*@quantlab\/output:\s*([\w.\-]+)/)
  return m ? m[1] : null
})

function onToggle(e: Event) {
  const t = e.target as HTMLDetailsElement
  isOpen.value = t.open
  if (t.open && !output.value && !loading.value && outputName.value) {
    loadOutput()
  }
}

async function loadOutput() {
  if (!outputName.value) return
  loading.value = true
  try {
    const res = await fetch(`/code/${outputName.value}.output.json`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    output.value = await res.json()
  } catch (e) {
    output.value = null
  } finally {
    loading.value = false
  }
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(decodedCode.value)
    copied.value = true
    setTimeout(() => copied.value = false, 1500)
  } catch (e) {
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
.scb {
  margin: 16px 0;
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  background: var(--vp-c-bg-soft, #f6f7f9);
  overflow: hidden;
  transition: border-color .2s, box-shadow .2s;
}
.scb:hover, .scb--open {
  border-color: var(--ft-brand, #00E5A0);
  box-shadow: 0 0 0 1px rgba(0, 229, 160, .15), 0 8px 24px rgba(0, 0, 0, .04);
}
.scb-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, rgba(0,229,160,.06), rgba(0,212,255,.04));
  border-bottom: 1px solid var(--vp-c-divider, #e2e8f0);
  gap: 8px;
}
.scb-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--vp-c-text-2, #5a6c8c);
  font-size: 12px;
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
}
.scb-lang {
  background: rgba(0,229,160,.18);
  color: #009e6e;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}
.scb-len { opacity: .8; }
.scb-actions { display: flex; gap: 6px; }
.scb-btn {
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
.scb-btn:hover {
  border-color: var(--ft-brand, #00E5A0);
  color: var(--ft-brand, #00E5A0);
}
.scb-code { position: relative; }
.scb-code :deep(pre.shiki),
.scb-code :deep(pre.vp-code-block) {
  margin: 0 !important;
  border-radius: 0 !important;
  border: none !important;
  background: var(--vp-code-block-bg, #fafbfc) !important;
}
.scb-out {
  border-top: 1px solid var(--ft-brand, #00E5A0);
  background: var(--vp-c-bg, white);
}
.scb-out-summary {
  cursor: pointer;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 500;
  color: var(--vp-c-text-1, #1f2937);
  background: linear-gradient(135deg, rgba(0,229,160,.06), rgba(0,212,255,.04));
  list-style: none;
  user-select: none;
}
.scb-out-summary::-webkit-details-marker { display: none; }
.scb-out-icon {
  display: inline-block;
  margin-right: 6px;
  transition: transform .2s;
  color: var(--ft-brand, #00E5A0);
}
.scb-out-icon--open { transform: rotate(90deg); }
.scb-out-body {
  padding: 14px;
  border-top: 1px solid var(--vp-c-divider, #e2e8f0);
}
.scb-out-loading,
.scb-out-empty {
  color: var(--vp-c-text-3, #94a3b8);
  font-size: 13px;
  font-style: italic;
}
.scb-out-text {
  margin: 0;
  padding: 12px;
  background: var(--vp-c-bg-soft, #f8fafc);
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  border-radius: 6px;
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
  font-size: 12.5px;
  line-height: 1.55;
  white-space: pre-wrap;
  overflow-x: auto;
  color: var(--vp-c-text-1, #1f2937);
}
.scb-out-svgs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 12px;
  margin-top: 12px;
}
.scb-out-svgs img {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  background: white;
}
.scb-out-error {
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(255, 69, 58, 0.08);
  border: 1px solid rgba(255, 69, 58, 0.3);
  color: #c0392b;
  font-size: 12.5px;
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
  white-space: pre-wrap;
}
:global(html.dark) .scb {
  background: var(--vp-c-bg-soft, #1a1a1a);
  border-color: var(--vp-c-divider, #2d3748);
}
:global(html.dark) .scb-btn {
  background: rgba(255,255,255,.06);
  color: #e7eaf6;
  border-color: rgba(255,255,255,.12);
}
:global(html.dark) .scb-out {
  background: var(--vp-c-bg, #0f1117);
}
:global(html.dark) .scb-out-text {
  background: #0a0a0a;
  border-color: rgba(255,255,255,.1);
  color: #e7eaf6;
}
:global(html.dark) .scb-out-svgs img {
  background: white;
  border-color: rgba(255,255,255,.12);
}
</style>