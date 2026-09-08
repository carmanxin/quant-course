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

    <details class="scb-code-wrap" :open="codeOpen" @toggle="onCodeToggle">
      <summary class="scb-code-summary">
        <span class="scb-code-icon">📄</span>
        <span class="scb-code-title">此处有展示代码</span>
        <span class="scb-code-meta">{{ lineCount }} 行 · {{ sizeHint }}</span>
        <span class="scb-code-toggle">{{ codeOpen ? '收起 ▲' : '展开 ▼' }}</span>
      </summary>
      <div class="scb-code">
        <slot />
      </div>
    </details>

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
          <div v-if="output.note" class="scb-out-note">{{ noteText }}</div>
          <div v-if="output.error" class="scb-out-error">⚠ {{ output.error }}</div>
        </template>
        <div v-else class="scb-out-empty">⚠ 暂无运行结果</div>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Output {
  text?: string
  svgs?: string[]
  error?: string
  note?: string
}

const props = withDefaults(defineProps<{
  codeB64?: string
  lang?: string
  defaultOpen?: boolean
  /** 构建期内联的运行结果 JSON 的 base64（来自 fence 钩子），优先于运行时 fetch */
  outputB64?: string
}>(), {
  codeB64: '',
  lang: 'python',
  // 代码区与运行结果区都默认折叠，读者按需展开
  defaultOpen: false,
  outputB64: '',
})

const isOpen = ref(false)
const codeOpen = ref(false)
const copied = ref(false)
const loading = ref(false)

// 内联输出优先：构建期已写死，无需 fetch（file:// 也能显示）
const inlineOutput = computed<Output | null>(() => {
  if (!props.outputB64) return null
  try {
    const binary = atob(props.outputB64)
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0))
    const json = new TextDecoder().decode(bytes)
    return JSON.parse(json) as Output
  } catch (e) {
    return null
  }
})
// 运行时 fetch 的 fallback（仅当无内联输出时触发）
const fetchedOutput = ref<Output | null>(null)
const output = computed(() => inlineOutput.value || fetchedOutput.value)

const decodedCode = computed(() => {
  try {
    return decodeURIComponent(escape(atob(props.codeB64)))
  } catch (e) {
    return ''
  }
})

// ---- "代码片段" note 的智能阐释 ----
// 当输出是"本段为代码片段（仅展示函数/类定义）"时，根据代码内容生成目的说明，
// 而不是生硬地只显示"仅为片段"。
const FRAGMENT_NOTE = '本段为代码片段（仅展示函数/类定义，未提供运行入口，无需运行）'

function extractDoc(lines: string[], i: number): string {
  for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
    const t = lines[j].trim()
    if (t === '') continue
    if (t.startsWith('"""') || t.startsWith("'''")) {
      let content = t.slice(3)
      let k = j
      while (!/(["']{3})$/.test(content) && k < Math.min(i + 10, lines.length - 1)) {
        k++
        content += '\n' + lines[k].trim()
        if (/(["']{3})$/.test(lines[k].trim())) break
      }
      content = content.replace(/^(["']{3})\s*/, '').replace(/\s*(["']{3})$/, '').trim()
      const firstLine = content.split('\n')[0].trim().split('。')[0]
      if (/^(Parameters|Args|Arguments|Returns|Return|Note|Examples|Notes|Attributes|属性|参数|返回|示例|注意|说明|:param|:type|:return|:raises)/i.test(firstLine)) return ''
      return firstLine.length > 60 ? firstLine.slice(0, 60) + '…' : firstLine
    }
    if (t.startsWith('#')) {
      const c = t.replace(/^#+\s*/, '').trim()
      return c.length > 60 ? c.slice(0, 60) + '…' : c
    }
    // def 跨行签名/函数体其他行：跳过继续找 docstring/注释
  }
  return ''
}

function describeFragment(code: string): string {
  const lines = code.split('\n')
  const items: { name: string; kind: string; desc: string }[] = []
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(?:def|class)\s+([A-Za-z_]\w*)/)
    if (m) {
      const kind = lines[i].startsWith('class') ? '类' : '函数'
      const desc = extractDoc(lines, i)
      items.push({ name: m[1], kind, desc })
    }
  }
  if (!items.length) return ''
  const described = items.filter((x) => x.desc).map((x) => `${x.kind} \`${x.name}\`（${x.desc}）`)
  const undescribed = items.filter((x) => !x.desc).map((x) => `${x.kind} \`${x.name}\``)
  let explain = `本段代码定义了 ${items.length} 个函数/类：`
  if (described.length) explain += described.join('、')
  if (undescribed.length) {
    if (described.length) explain += '，以及 ' + undescribed.join('、')
    else explain += undescribed.join('、')
  }
  explain += '。该片段为教学展示（未包含独立运行的输入数据），可在实战练习中结合真实数据调用。'
  return explain
}

// 展开结果区时展示的 note 文本：fragment note → 智能阐释；其余原样
const noteText = computed(() => {
  const note = output.value?.note
  if (!note) return ''
  if (note === FRAGMENT_NOTE) {
    const explain = describeFragment(decodedCode.value)
    if (explain) return '📘 ' + explain
  }
  return '📘 ' + note
})

const rawLines = computed(() => decodedCode.value.split('\n'))
const lineCount = computed(() => Math.max(0, rawLines.value.length - 1))

const sizeHint = computed(() => {
  const bytes = new Blob([decodedCode.value]).size
  if (bytes > 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return bytes + ' B'
})

const langLabel = computed(() => props.lang?.toUpperCase() || 'PYTHON')

// FNV-1a 32-bit hash（与 scripts/precompute-py-outputs.mjs 保持一致）
function fnv1a(str: string): string {
  let h = 0x811c9dc5
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}

// 归一化：去掉 marker、统一换行、去行尾空格、去首尾空白（与 precompute 一致）
function normalizeCode(raw: string): string {
  return raw
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+$/gm, '')
    .trim()
}

// 内容 hash 作为查询键（fence 代码与 public/code/*.py 匹配的基础）
const codeHash = computed(() => {
  const code = decodedCode.value
  return code ? fnv1a(normalizeCode(code)) : null
})

// _index.json 缓存：codeHash -> name
let indexCache: Record<string, string> | null = null
async function resolveOutputName(): Promise<string | null> {
  if (!codeHash.value) return null
  if (!indexCache) {
    try {
      const res = await fetch('/code/_index.json')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      indexCache = await res.json()
    } catch (e) {
      indexCache = {}
    }
  }
  return indexCache[codeHash.value] || null
}

function onToggle(e: Event) {
  const t = e.target as HTMLDetailsElement
  isOpen.value = t.open
  // 已有内联输出则无需 fetch；否则在展开时尝试运行时加载（fallback）
  if (t.open && !output.value && !inlineOutput.value && !loading.value) {
    loadOutput()
  }
}

function onCodeToggle(e: Event) {
  codeOpen.value = (e.target as HTMLDetailsElement).open
}

async function loadOutput() {
  loading.value = true
  try {
    const name = await resolveOutputName()
    if (!name) {
      fetchedOutput.value = null
      return
    }
    const res = await fetch(`/code/${name}.output.json`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    fetchedOutput.value = await res.json()
  } catch (e) {
    fetchedOutput.value = null
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
.scb-code-wrap {
  border-bottom: 1px solid var(--vp-c-divider, #e2e8f0);
}
.scb-code-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  list-style: none;
  user-select: none;
  background: var(--vp-c-bg, white);
  color: var(--vp-c-text-1, #1f2937);
  font-size: 13px;
  font-weight: 500;
  transition: background .15s;
}
.scb-code-summary:hover {
  background: rgba(0, 229, 160, .05);
}
.scb-code-summary::-webkit-details-marker { display: none; }
.scb-code-icon { font-size: 14px; }
.scb-code-title { color: var(--ft-brand, #00E5A0); font-weight: 700; }
.scb-code-meta {
  font-size: 12px;
  color: var(--vp-c-text-3, #94a3b8);
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
  margin-left: auto;
}
.scb-code-toggle {
  font-size: 12px;
  color: var(--vp-c-text-2, #5a6c8c);
  white-space: nowrap;
}
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
.scb-out-note {
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(56, 142, 230, 0.08);
  border: 1px solid rgba(56, 142, 230, 0.3);
  color: #2c5d8f;
  font-size: 12.5px;
  line-height: 1.6;
}
:global(html.dark) .scb {
  background: var(--vp-c-bg-soft, #1a1a1a);
  border-color: var(--vp-c-divider, #2d3748);
}
:global(html.dark) .scb-code-summary {
  background: var(--vp-c-bg, #0f1117);
  color: #e7eaf6;
}
:global(html.dark) .scb-code-summary:hover {
  background: rgba(0, 229, 160, .08);
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