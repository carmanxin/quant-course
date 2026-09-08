<!-- components/QuizBlock.vue
     交互式小测验：选项可点选 → 即时判定对错 → 显示正确答案 → 解析默认折叠
     题面/选项/解析由 markdown-it 在构建期渲染成 HTML 后以 base64 传入，
     因此数学公式（MathJax）也能正常显示。
-->
<template>
  <div class="qz" :class="{ 'qz--answered': picked !== null }">
    <div class="qz-head">
      <span class="qz-badge">题目 {{ num }}</span>
      <div class="qz-q" v-html="questionHtml" />
    </div>

    <ul class="qz-opts">
      <li
        v-for="(opt, i) in optionHtmls"
        :key="i"
        class="qz-opt"
        :class="optClass(i)"
        @click="pick(i)"
      >
        <span class="qz-mark">{{ markFor(i) }}</span>
        <span class="qz-opt-body" v-html="opt" />
      </li>
    </ul>

    <div v-if="picked !== null" class="qz-verdict" :class="isRight ? 'qz-verdict--ok' : 'qz-verdict--bad'">
      <span v-if="isRight">✅ 回答正确！</span>
      <span v-else>❌ 回答错误，正确答案是 <b>{{ answer }}</b></span>
      <button class="qz-reset" @click="picked = null">重做</button>
    </div>

    <details class="qz-analysis">
      <summary>
        <span class="qz-analysis-icon">💡</span>
        <span v-if="picked === null">查看答案与解析</span>
        <span v-else>查看解析</span>
        <span class="qz-analysis-toggle">展开 ▼</span>
      </summary>
      <div class="qz-analysis-body">
        <div class="qz-answer-line">
          正确答案：<b>{{ answer }}</b>
        </div>
        <div class="qz-explain" v-html="explainHtml" />
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = withDefaults(defineProps<{
  num?: string
  question?: string      // base64(HTML)
  options?: string       // base64(JSON array of HTML strings)
  answer?: string        // 'A' | 'B' | 'C' | 'D'
  explain?: string       // base64(HTML)
}>(), {
  num: '',
  question: '',
  options: '',
  answer: '',
  explain: '',
})

function decodeB64(s: string): string {
  if (!s) return ''
  try {
    const binary = atob(s)
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0))
    return new TextDecoder().decode(bytes)
  } catch {
    return ''
  }
}

const questionHtml = computed(() => decodeB64(props.question))
const explainHtml = computed(() => decodeB64(props.explain))
const optionHtmls = computed<string[]>(() => {
  const raw = decodeB64(props.options)
  if (!raw) return []
  try {
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
})

const picked = ref<number | null>(null)
const answerIndex = computed(() => {
  const a = (props.answer || '').trim().toUpperCase()
  const i = 'ABCDEFGH'.indexOf(a)
  return i < 0 ? -1 : i
})
const isRight = computed(() => picked.value !== null && picked.value === answerIndex.value)

function pick(i: number) {
  picked.value = i
}
function markFor(i: number): string {
  if (picked.value === null) return String.fromCharCode(65 + i)
  if (i === answerIndex.value) return '✓'
  if (i === picked.value) return '✗'
  return String.fromCharCode(65 + i)
}
function optClass(i: number) {
  if (picked.value === null) return { 'qz-opt--idle': true }
  if (i === answerIndex.value) return { 'qz-opt--right': true }
  if (i === picked.value) return { 'qz-opt--wrong': true }
  return { 'qz-opt--dim': true }
}
</script>

<style scoped>
.qz {
  margin: 20px 0 26px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  border-radius: 12px;
  background: var(--vp-c-bg-soft, #f8fafc);
  overflow: hidden;
}
.qz--answered {
  border-color: var(--ft-brand, #00E5A0);
}
.qz-head {
  padding: 14px 18px 10px;
  border-bottom: 1px dashed var(--vp-c-divider, #e2e8f0);
}
.qz-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: #009e6e;
  background: rgba(0, 229, 160, .16);
  border-radius: 999px;
  padding: 3px 10px;
  margin-bottom: 8px;
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
}
.qz-q {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.7;
  color: var(--vp-c-text-1, #1f2937);
}
.qz-q :deep(p) { margin: 0; }

.qz-opts {
  list-style: none;
  margin: 0;
  padding: 12px 18px 4px;
}
.qz-opt {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 11px 14px;
  margin: 8px 0;
  border: 1.5px solid var(--vp-c-divider, #e2e8f0);
  border-radius: 10px;
  background: var(--vp-c-bg, #fff);
  cursor: pointer;
  transition: border-color .18s, background .18s, transform .12s, box-shadow .18s;
  font-size: 14px;
  line-height: 1.65;
}
.qz-opt:hover {
  border-color: var(--ft-brand, #00E5A0);
  transform: translateX(3px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, .05);
}
.qz-mark {
  flex: 0 0 22px;
  height: 22px;
  line-height: 20px;
  text-align: center;
  border-radius: 50%;
  border: 1.5px solid var(--vp-c-divider, #d5dbe4);
  font-size: 12px;
  font-weight: 700;
  color: var(--vp-c-text-2, #5a6c8c);
  background: var(--vp-c-bg, #fff);
}
.qz-opt-body { flex: 1; }
.qz-opt-body :deep(p) { margin: 0; }

.qz-opt--right {
  border-color: #10b981;
  background: rgba(16, 185, 129, .10);
}
.qz-opt--right .qz-mark {
  border-color: #10b981;
  background: #10b981;
  color: #fff;
}
.qz-opt--wrong {
  border-color: #ef4444;
  background: rgba(239, 68, 68, .09);
}
.qz-opt--wrong .qz-mark {
  border-color: #ef4444;
  background: #ef4444;
  color: #fff;
}
.qz-opt--dim { opacity: .5; }

.qz-verdict {
  margin: 6px 18px 0;
  padding: 9px 14px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}
.qz-verdict--ok {
  background: rgba(16, 185, 129, .12);
  border-left: 3px solid #10b981;
  color: #047857;
}
.qz-verdict--bad {
  background: rgba(239, 68, 68, .10);
  border-left: 3px solid #ef4444;
  color: #b91c1c;
}
.qz-reset {
  margin-left: auto;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border: 1px solid currentColor;
  border-radius: 6px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  opacity: .75;
}
.qz-reset:hover { opacity: 1; }

.qz-analysis {
  margin: 12px 18px 16px;
  border: 1px solid var(--vp-c-divider, #e2e8f0);
  border-radius: 9px;
  background: var(--vp-c-bg, #fff);
  overflow: hidden;
}
.qz-analysis > summary {
  cursor: pointer;
  list-style: none;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--vp-c-text-1, #1f2937);
  background: linear-gradient(135deg, rgba(0,229,160,.06), rgba(0,212,255,.04));
  user-select: none;
}
.qz-analysis > summary::-webkit-details-marker { display: none; }
.qz-analysis > summary:hover { background: rgba(0, 229, 160, .1); }
.qz-analysis-icon { margin-right: 6px; }
.qz-analysis-toggle {
  float: right;
  font-size: 12px;
  font-weight: 400;
  color: var(--vp-c-text-3, #94a3b8);
}
.qz-analysis[open] .qz-analysis-toggle { visibility: hidden; }
.qz-analysis-body {
  padding: 12px 16px 14px;
  border-top: 1px solid var(--vp-c-divider, #e2e8f0);
  font-size: 13.5px;
  line-height: 1.75;
  color: var(--vp-c-text-1, #1f2937);
}
.qz-answer-line {
  margin-bottom: 8px;
  font-weight: 600;
  color: #009e6e;
}
.qz-explain :deep(p) { margin: 0 0 6px; }
.qz-explain :deep(p:last-child) { margin-bottom: 0; }

:global(html.dark) .qz {
  background: var(--vp-c-bg-soft, #1a1a1a);
  border-color: var(--vp-c-divider, #2d3748);
}
:global(html.dark) .qz-opt,
:global(html.dark) .qz-analysis {
  background: var(--vp-c-bg, #0f1117);
  border-color: var(--vp-c-divider, #2d3748);
}
:global(html.dark) .qz-opt:hover { box-shadow: 0 2px 10px rgba(0,0,0,.4); }
:global(html.dark) .qz-q,
:global(html.dark) .qz-analysis-body { color: #e7eaf6; }
:global(html.dark) .qz-analysis > summary { color: #e7eaf6; }
:global(html.dark) .qz-opt--right { background: rgba(16,185,129,.16); }
:global(html.dark) .qz-opt--wrong { background: rgba(239,68,68,.14); }
</style>
