# QuantLab Drop Pyodide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 移除浏览器内 Pyodide 运行机制，将 31 个 `<PythonPlayground>` 改为 `<StaticCodeBlock>`（代码 + 折叠预计算运行结果），portable 包从 173 MB 瘦到 ~50 MB。

**Architecture:** Build 时跑 `scripts/precompute-py-outputs.mjs` 用本地 `python3` 执行 `public/code/*.py`（matplotlib SVG backend），生成 `<name>.output.json` + `<name>.svgs/*.svg`。VitePress markdown-it fence 钩子把 `\`\`\`python` 改写成 `<StaticCodeBlock code-b64="...">`。组件 mount 时 fetch `.output.json`，渲染 Shiki 代码 + `<details><summary>点击展开可浏览运行结果</summary>...</details>`。删 `PythonPlayground.vue`、`CodeRunBlock.vue`、`public/pyodide/`、`pyodide` 依赖。

**Tech Stack:** Node.js 22+ (spawn, fs/promises)、Python 3 + numpy/pandas/matplotlib (build host)、VitePress 1.6、Vue 3.5、Playwright (E2E)。

**Spec:** `D:/AI/study/quant/docs/superpowers/specs/2026-08-11-quantlab-drop-pysim-design.md`

## Global Constraints

- 路径全部用绝对路径或相对于 `D:/AI/study/quant/` 的路径
- Build 失败不抛 exit 1（仅 warning），让 reader 在折叠块看到失败原因
- `.py` 首行加 `# @quantlab/output: <name>` 标记（Python 注释，运行时无副作用）
- `<StaticCodeBlock>` 的 `codeB64` 用 `Buffer.from(text, 'utf8').toString('base64')`
- 折叠块默认收起（`defaultOpen=false`），summary 文案固定为"点击展开可浏览运行结果"
- matplotlib backend 强制 `svg` + `QT_QPA_PLATFORM=offscreen`
- 子进程超时 30 秒，触发 `SIGKILL`
- 输出文件命名约定：`public/code/<name>.output.json` + `public/code/<name>.svgs/<name>-N.svg`

---

## Task 1: 给 25 个 .py 加 `@quantlab/output` 标记

**Files:**
- Create: `D:/AI/study/quant/scripts/add-output-marker.py`
- Modify: `D:/AI/study/quant/public/code/*.py`（25 个文件，各加一行首行注释）

**Interfaces:**
- Consumes: `public/code/*.py`
- Produces: 每个 .py 首行变为 `# @quantlab/output: <filename>`

- [ ] **Step 1: 写一个失败的 dry-run 测试**

```python
# scripts/_test_add_marker.py
import subprocess, pathlib
result = subprocess.run(
    ['python', 'scripts/add-output-marker.py', '--dry-run'],
    capture_output=True, text=True, cwd='D:/AI/study/quant'
)
assert 'would modify' in result.stdout or 'already marked' in result.stdout
```

- [ ] **Step 2: 跑测试，确认失败**

```bash
cd D:/AI/study/quant && python scripts/_test_add_marker.py
```
Expected: `ModuleNotFoundError` 或 `FileNotFoundError`（脚本尚未存在）。

- [ ] **Step 3: 实现 `add-output-marker.py`**

```python
#!/usr/bin/env python3
"""为 public/code/*.py 加 # @quantlab/output: <name> 首行注释（幂等）。"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / 'public' / 'code'
MARKER_RE = re.compile(r'^#\s*@quantlab/output:\s*([\w.\-]+)', re.MULTILINE)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--code-dir', default=str(CODE_DIR))
    args = p.parse_args()
    code_dir = pathlib.Path(args.code_dir)
    if not code_dir.is_dir():
        print(f'ERROR: {code_dir} not found', file=sys.stderr)
        return 1
    modified, skipped = 0, 0
    for f in sorted(code_dir.glob('*.py')):
        text = f.read_text(encoding='utf-8')
        if MARKER_RE.search(text):
            skipped += 1
            continue
        new_text = f'# @quantlab/output: {f.stem}\n' + text
        if args.dry_run:
            print(f'would modify: {f.name}')
        else:
            f.write_text(new_text, encoding='utf-8')
        modified += 1
    print(f'[add-output-marker] modified={modified} skipped={skipped}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: dry-run 验证**

```bash
cd D:/AI/study/quant && python scripts/add-output-marker.py --dry-run
```
Expected: 25 行 `would modify: X.py` + `[add-output-marker] modified=25 skipped=0`。

- [ ] **Step 5: 实际执行并验证**

```bash
cd D:/AI/study/quant && python scripts/add-output-marker.py && head -1 public/code/1.3-bootstrap.py
```
Expected: `# @quantlab/output: 1.3-bootstrap`。

- [ ] **Step 6: 验证幂等性**

```bash
cd D:/AI/study/quant && python scripts/add-output-marker.py
```
Expected: `[add-output-marker] modified=0 skipped=25`。

- [ ] **Step 7: Commit**

```bash
cd D:/AI/study/quant && git add scripts/add-output-marker.py public/code/ && git commit -m "feat(scripts): add @quantlab/output marker to 25 code samples"
```

---

## Task 2: 从 31 个 .md 删除 `<PythonPlayground>` 标签

**Files:**
- Create: `D:/AI/study/quant/scripts/strip-python-playground-tag.py`
- Modify: `D:/AI/study/quant/guide/**/*.md`（预期 31 个文件，各删 1 行）

**Interfaces:**
- Consumes: `guide/**/*.md`
- Produces: 文件不再含 `<PythonPlayground ... />` 字符串

- [ ] **Step 1: 跑基线统计，确认有 31 处标签**

```bash
cd D:/AI/study/quant && python -c "import pathlib; print(sum(1 for _ in pathlib.Path('guide').rglob('*.md') if '<PythonPlayground' in _.read_text(encoding='utf-8')))"
```
Expected: `31`

- [ ] **Step 2: dry-run 脚本**

```bash
cd D:/AI/study/quant && python scripts/strip-python-playground-tag.py --dry-run
```
Expected: 脚本不存在 (ModuleNotFoundError)。

- [ ] **Step 3: 实现 `strip-python-playground-tag.py`**

```python
#!/usr/bin/env python3
"""从 guide/**/*.md 删除 <PythonPlayground ... /> 单行标签（幂等）。"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r'<PythonPlayground[^>]*/>\s*\n?', re.MULTILINE)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--guide-dir', default=str(ROOT / 'guide'))
    args = p.parse_args()
    guide_dir = pathlib.Path(args.guide_dir)
    modified = 0
    for f in sorted(guide_dir.rglob('*.md')):
        text = f.read_text(encoding='utf-8')
        new_text = TAG_RE.sub('', text)
        if new_text == text:
            continue
        if args.dry_run:
            print(f'would strip: {f.relative_to(guide_dir)}')
        else:
            f.write_text(new_text, encoding='utf-8')
        modified += 1
    print(f'[strip-python-playground-tag] modified={modified}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: dry-run 验证**

```bash
cd D:/AI/study/quant && python scripts/strip-python-playground-tag.py --dry-run
```
Expected: 31 行 `would strip: ...` + `modified=31`。

- [ ] **Step 5: 实际执行并验证**

```bash
cd D:/AI/study/quant && python scripts/strip-python-playground-tag.py && python -c "import pathlib; print(sum(1 for _ in pathlib.Path('guide').rglob('*.md') if '<PythonPlayground' in _.read_text(encoding='utf-8')))"
```
Expected: `0`。

- [ ] **Step 6: Commit**

```bash
cd D:/AI/study/quant && git add scripts/strip-python-playground-tag.py guide/ && git commit -m "feat(scripts): strip <PythonPlayground> tags from 31 guide files"
```

---

## Task 3: 创建 `StaticCodeBlock.vue` 组件

**Files:**
- Create: `D:/AI/study/quant/components/StaticCodeBlock.vue`

**Interfaces:**
- Props: `{ codeB64: string, lang?: string, defaultOpen?: boolean }`
- Behavior: 读源码首行 `# @quantlab/output: <name>` → fetch `/code/<name>.output.json` → 渲染代码区 + 折叠结果区
- Exports: `<StaticCodeBlock>` Vue 组件，VitePress 在 `.vitepress/theme/index.ts` 通过 `enhanceApp({ app })` 全局注册（沿用现有 `CodeRunBlock` 注册模式）

- [ ] **Step 1: 创建组件文件骨架（不含 SVG 渲染逻辑）**

```vue
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
```

- [ ] **Step 2: 在 `.vitepress/theme/index.ts` 中注册组件**

打开 `D:/AI/study/quant/.vitepress/theme/index.ts`，找到现有 `CodeRunBlock` 的 `app.component('CodeRunBlock', CodeRunBlock)` 这一行，替换为：

```ts
import StaticCodeBlock from '../../components/StaticCodeBlock.vue'
// ...
app.component('StaticCodeBlock', StaticCodeBlock)
```

（保留 `CodeRunBlock` import 与注册暂不删，下个 task 才删，避免中间态 build 失败。）

- [ ] **Step 3: 验证组件 import 路径正确**

```bash
cd D:/AI/study/quant && ls -la components/StaticCodeBlock.vue .vitepress/theme/index.ts
```
Expected: 两个文件都存在。

- [ ] **Step 4: Commit**

```bash
cd D:/AI/study/quant && git add components/StaticCodeBlock.vue .vitepress/theme/index.ts && git commit -m "feat(components): add StaticCodeBlock replacing CodeRunBlock"
```

---

## Task 4: 更新 `.vitepress/config.ts` 的 fence 钩子

**Files:**
- Modify: `D:/AI/study/quant/.vitepress/config.ts` (line 253 head script, line 282-300 fence rule, line 304 srcExclude)

**Interfaces:**
- Consumes: 现有 fence rule
- Produces: `python`/`py` fence 渲染为 `<StaticCodeBlock>` 而非 `<CodeRunBlock>`

- [ ] **Step 1: 备份当前 fence 规则**

```bash
cd D:/AI/study/quant && grep -n "CodeRunBlock\|/pyodide/pyodide.js\|srcExclude" .vitepress/config.ts
```
Expected: 看到 3 处引用（fence rule、head script、srcExclude）。

- [ ] **Step 2: 修改 head script 注入**

打开 `.vitepress/config.ts`，找到 `head.push(['script', { src: '/pyodide/pyodide.js' }])`（约 line 253），**整行删除**。

- [ ] **Step 3: 修改 srcExclude**

找到 `srcExclude: [..., 'public/pyodide/**']`（约 line 304），删除 `'public/pyodide/**'` 这一项。保留其他项。

- [ ] **Step 4: 修改 fence 规则**

找到现有的 fence 渲染规则（`.vitepress/config.ts:282-300`），把判断 + 替换逻辑改成：

```ts
const defaultFence = md.renderer.rules.fence
md.renderer.rules.fence = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const info = (token.info || '').trim().split(/\s+/)[0]
  if (['python', 'py'].includes(info)) {
    const codeB64 = Buffer.from(token.content, 'utf8').toString('base64')
    const rendered = defaultFence!(tokens, idx, options, env, self)
    return `<StaticCodeBlock code-b64="${codeB64}" lang="${info}">${rendered}</StaticCodeBlock>`
  }
  return defaultFence!(tokens, idx, options, env, self)
}
```

- [ ] **Step 5: 验证修改**

```bash
cd D:/AI/study/quant && grep -n "StaticCodeBlock\|CodeRunBlock\|/pyodide/" .vitepress/config.ts
```
Expected: 仅 `StaticCodeBlock` 命中；`CodeRunBlock` 与 `/pyodide/` 零命中。

- [ ] **Step 6: Commit**

```bash
cd D:/AI/study/quant && git add .vitepress/config.ts && git commit -m "feat(vitepress): fence rule renders python to StaticCodeBlock, drop pyodide head script"
```

---

## Task 5: 创建 `scripts/precompute-py-outputs.mjs`

**Files:**
- Create: `D:/AI/study/quant/scripts/precompute-py-outputs.mjs`

**Interfaces:**
- Consumes: `public/code/*.py`（每个首行有 `# @quantlab/output: <name>` 标记）
- Produces: `public/code/<name>.output.json` + `public/code/<name>.svgs/*.svg`
- Exit code: 永远 0（失败仅 warning）

- [ ] **Step 1: 检查 python3 + matplotlib 可用**

```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"
```
Expected: 版本号打印（无 ModuleNotFoundError）。若有错，先 `pip install matplotlib numpy pandas` 或告知用户安装。

- [ ] **Step 2: 实现脚本**

```js
#!/usr/bin/env node
// scripts/precompute-py-outputs.mjs
// 遍历 public/code/*.py，spawn python3 执行，捕获 stdout + plt.show() 的 SVG。
// 失败不抛 exit 1（让 reader 在折叠块看到失败原因）。

import { spawn } from 'node:child_process'
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises'
import { glob } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const CODE_DIR = path.join(ROOT, 'public', 'code')
const TIMEOUT_MS = 30_000
const MARKER = /^#\s*@quantlab\/output:\s*([\w.\-]+)/

async function runOne(pyFile) {
  const text = await readFile(pyFile, 'utf8')
  const m = text.match(MARKER)
  if (!m) return { skipped: true, file: path.basename(pyFile) }

  const name = m[1]
  const svgDir = path.join(CODE_DIR, `${name}.svgs`)
  await mkdir(svgDir, { recursive: true })

  const env = {
    ...process.env,
    MPLBACKEND: 'svg',
    QT_QPA_PLATFORM: 'offscreen',
    PYTHONUNBUFFERED: '1',
    QUANTLAB_SVG_DIR: svgDir,
    QUANTLAB_OUTPUT_NAME: name,
  }

  const preamble = `
import os, matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
_SHOW_COUNT = [0]
def _patched_show(*a, **k):
    n = _SHOW_COUNT[0]
    _SHOW_COUNT[0] += 1
    fname = f"{os.environ['QUANTLAB_OUTPUT_NAME']}-{n}.svg"
    plt.savefig(os.path.join(os.environ['QUANTLAB_SVG_DIR'], fname), bbox_inches="tight")
    plt.close()
plt.show = _patched_show
`

  return new Promise((resolve) => {
    let stdout = '', stderr = ''
    const proc = spawn('python3', ['-c', preamble + text], { env })
    const timer = setTimeout(() => proc.kill('SIGKILL'), TIMEOUT_MS)
    proc.stdout.on('data', (d) => stdout += d)
    proc.stderr.on('data', (d) => stderr += d)
    proc.on('close', async (code) => {
      clearTimeout(timer)
      let svgs = []
      try {
        const files = await readdir(svgDir)
        svgs = files
          .filter((f) => f.endsWith('.svg'))
          .sort()
          .map((f) => `/code/${name}.svgs/${f}`)
      } catch (e) {
        // svgDir 不存在则 svgs 留空
      }
      const payload = code === 0
        ? { text: stdout.trim(), svgs }
        : { text: stdout.trim(), svgs, error: stderr.trim().slice(0, 500) }
      await writeFile(
        path.join(CODE_DIR, `${name}.output.json`),
        JSON.stringify(payload, null, 2),
      )
      resolve({ name, file: path.basename(pyFile), code, len: stdout.length })
    })
  })
}

async function main() {
  const files = []
  try {
    for await (const f of glob('public/code/*.py')) files.push(f)
  } catch (e) {
    console.error(`[precompute] glob failed: ${e.message}`)
    process.exit(0)  // 不抛 exit 1
  }
  console.log(`[precompute] running ${files.length} files...`)
  const results = await Promise.all(files.map(runOne))
  const failed = results.filter((r) => !r.skipped && r.code !== 0)
  const skipped = results.filter((r) => r.skipped).length
  console.log(
    `[precompute] done: ${results.length - failed.length - skipped}/${results.length} succeeded, ${failed.length} failed, ${skipped} skipped (no marker)`,
  )
  if (failed.length) {
    console.log('[precompute] FAILED:')
    for (const f of failed) console.log(`  - ${f.name} (${f.file}): exit ${f.code}`)
  }
  process.exit(0)  // 永远 exit 0
}

main().catch((e) => {
  console.error(`[precompute] fatal: ${e.message}`)
  process.exit(0)
})
```

- [ ] **Step 3: dry-run 验证（在单个文件上测试 spawn 逻辑）**

```bash
cd D:/AI/study/quant && node scripts/precompute-py-outputs.mjs
```
Expected: `[precompute] running 25 files...` 然后 `[precompute] done: X/25 succeeded, 0 failed, 0 skipped`。

- [ ] **Step 4: 验证产物**

```bash
cd D:/AI/study/quant && ls public/code/*.output.json | wc -l && ls public/code/*.svgs/ | head -5
```
Expected: `25` 个 .output.json；若干 `.svgs/*.svg`。

- [ ] **Step 5: 验证 .output.json 结构**

```bash
cd D:/AI/study/quant && python -c "import json; d=json.load(open('public/code/1.3-bootstrap.output.json')); print('keys:', list(d.keys())); print('text len:', len(d.get('text',''))); print('svgs:', d.get('svgs',[]))"
```
Expected: `keys: ['text', 'svgs']`，`text len > 0`，`svgs: []` 或 1-3 项（取决于代码是否画图）。

- [ ] **Step 6: 验证失败路径不抛 exit 1**

```bash
cd D:/AI/study/quant && echo 'import sys; sys.exit(1)' > /tmp/_fail.py && echo '# @quantlab/output: _fail_test' | cat - /tmp/_fail.py > public/code/_fail_test.py && node scripts/precompute-py-outputs.mjs; echo "exit=$?"; rm public/code/_fail_test.py public/code/_fail_test.output.json 2>/dev/null; rm -rf public/code/_fail_test.svgs 2>/dev/null
```
Expected: `[precompute] FAILED:` 列出 `_fail_test`，但 `exit=0`。

- [ ] **Step 7: Commit**

```bash
cd D:/AI/study/quant && git add scripts/precompute-py-outputs.mjs public/code/*.output.json 'public/code/*.svgs/' && git commit -m "feat(scripts): precompute python outputs at build time, generate 25 .output.json + .svgs"
```

---

## Task 6: 更新 `package.json` scripts

**Files:**
- Modify: `D:/AI/study/quant/package.json` (line 7-9 scripts, line 19 dependencies)

- [ ] **Step 1: 修改 scripts.build**

打开 `package.json`，把：

```json
"build": "vitepress build"
```

改为：

```json
"build": "node scripts/precompute-py-outputs.mjs && vitepress build",
"precompute": "node scripts/precompute-py-outputs.mjs",
"marker:add": "python scripts/add-output-marker.py",
"tag:strip": "python scripts/strip-python-playground-tag.py"
```

- [ ] **Step 2: 移除 pyodide 依赖**

```diff
   "dependencies": {
     "echarts": "^5.6.0",
     "markdown-it-mathjax3": "^4.3.2",
-    "playwright": "^1.60.0",
-    "pyodide": "^0.29.4"
+    "playwright": "^1.60.0"
   }
```

- [ ] **Step 3: 验证 package.json 合法**

```bash
cd D:/AI/study/quant && python -c "import json; print(json.dumps(json.load(open('package.json'))['scripts'], indent=2))"
```
Expected: 看到新增的 `precompute` / `marker:add` / `tag:strip`，`build` 已更新。

- [ ] **Step 4: Commit**

```bash
cd D:/AI/study/quant && git add package.json && git commit -m "chore(package): wire precompute into build, drop pyodide dep"
```

---

## Task 7: 删除 Pyodide 相关文件

**Files:**
- Delete: `D:/AI/study/quant/components/PythonPlayground.vue`
- Delete: `D:/AI/study/quant/components/CodeRunBlock.vue`
- Delete: `D:/AI/study/quant/public/pyodide/` (整个目录)
- Delete: `D:/AI/study/quant/public/pyodide-init.js`
- Delete: `D:/AI/study/quant/tests/download_wheels.py`
- Delete: `D:/AI/study/quant/tests/verify-playgrounds.js`

- [ ] **Step 1: 删除 6 个文件/目录**

```bash
cd D:/AI/study/quant && rm -rf components/PythonPlayground.vue components/CodeRunBlock.vue public/pyodide public/pyodide-init.js tests/download_wheels.py tests/verify-playgrounds.js
```

- [ ] **Step 2: 验证删除**

```bash
cd D:/AI/study/quant && ls components/ tests/ 2>&1 | grep -i "pyodide\|pythonplayground\|coderunblock\|wheels\|playgrounds" || echo "all cleaned"
```
Expected: `all cleaned`（grep 无输出）。

- [ ] **Step 3: 从 `.vitepress/theme/index.ts` 移除 CodeRunBlock/PythonPlayground import**

打开 `.vitepress/theme/index.ts`，删除：

```ts
import CodeRunBlock from '../../components/CodeRunBlock.vue'
import PythonPlayground from '../../components/PythonPlayground.vue'
```

以及对应的：

```ts
app.component('CodeRunBlock', CodeRunBlock)
app.component('PythonPlayground', PythonPlayground)
```

- [ ] **Step 4: 验证引用清理**

```bash
cd D:/AI/study/quant && grep -rn "CodeRunBlock\|PythonPlayground\|pyodide-init" .vitepress/ components/ tests/ 2>/dev/null || echo "all references gone"
```
Expected: `all references gone`。

- [ ] **Step 5: 重新跑 build 验证全链路通**

```bash
cd D:/AI/study/quant && npm run build 2>&1 | tail -30
```
Expected: build 成功，无报错；`.vitepress/dist/` 生成；包含 `<StaticCodeBlock>` 标签的 HTML 页。

- [ ] **Step 6: 验证 portable/dist 不再含 pyodide**

```bash
cd D:/AI/study/quant && ls portable/dist/pyodide 2>&1 || echo "no pyodide dist (expected after full rebuild)"
```

注意：本任务只删了源文件，没有 rebuild portable 包。验证 `.vitepress/dist/` 已不含 pyodide 即可。

```bash
cd D:/AI/study/quant && ls .vitepress/dist/pyodide 2>&1 || echo "no pyodide in dev dist"
```
Expected: `no pyodide in dev dist`。

- [ ] **Step 7: Commit**

```bash
cd D:/AI/study/quant && git add -A components/ tests/ public/ .vitepress/theme/index.ts && git commit -m "chore: delete pyodide-related components/tests/public assets"
```

---

## Task 8: 更新 `package-portable.bat` 与 `index.md`

**Files:**
- Modify: `D:/AI/study/quant/package-portable.bat` (line 56-61)
- Modify: `D:/AI/study/quant/index.md` (line 22)

- [ ] **Step 1: 修改 package-portable.bat**

打开 `package-portable.bat`，找到 line 56-61 的 pyodide 断言（约 6 行）。整段删除（包括 if errorlevel 块）。如果该脚本还有其他与 pyodide 相关的提示文字，一并清除。

- [ ] **Step 2: 修改 index.md tagline**

打开 `index.md`，找到 line 22：

```yaml
  - title: Python 数据栈
    details: NumPy · Pandas · Scikit-learn · XGBoost · 浏览器内 Pyodide 在线沙箱
```

改为：

```yaml
  - title: Python 数据栈
    details: NumPy · Pandas · Scikit-learn · XGBoost · 代码示例 + 预计算运行结果
```

- [ ] **Step 3: 验证修改**

```bash
cd D:/AI/study/quant && grep -n "Pyodide\|pyodide" package-portable.bat index.md 2>&1 || echo "no pyodide mentions"
```
Expected: `no pyodide mentions`。

- [ ] **Step 4: Commit**

```bash
cd D:/AI/study/quant && git add package-portable.bat index.md && git commit -m "docs: remove pyodide references from tagline and portable packager"
```

---

## Task 9: 创建 E2E 测试 `tests/verify-static-code-blocks.js`

**Files:**
- Create: `D:/AI/study/quant/tests/verify-static-code-blocks.js`

**Interfaces:**
- Consumes: 5 个典型页面的 URL（http://127.0.0.1:5189/{path}）
- Produces: Playwright 断言结果，exit 0 全部通过 / exit 1 任一失败

- [ ] **Step 1: 启动 dev server（后台）**

```bash
cd D:/AI/study/quant && npm run dev -- --port 5189 &
sleep 8
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5189/
```
Expected: `200`。

（如果已有 serve 在 5189 跑，可跳过此步直接用。）

- [ ] **Step 2: 实现 E2E 测试**

```js
// tests/verify-static-code-blocks.js
// Playwright 验证 5 个典型页面的 <StaticCodeBlock> 折叠块可用
import { chromium } from 'playwright'

const PAGES = [
  '/guide/m01-overview/1.3-quant-mindset.html',
  '/guide/m04-backtest/4.3-metrics.html',
  '/guide/m05-strategies/5.2-dual-ma.html',
  '/guide/m11-derivatives/11.1-greeks.html',
  '/guide/m20-interview-prep/20.1-math-stats.html',
]
const BASE = 'http://127.0.0.1:5189'

async function check(page, path) {
  await page.goto(BASE + path, { waitUntil: 'networkidle' })
  const detailsCount = await page.locator('details.scb-out').count()
  if (detailsCount === 0) throw new Error(`${path}: no details.scb-out`)

  // 展开第一个折叠块
  await page.locator('details.scb-out').first().evaluate((el) => el.open = true)
  await page.waitForTimeout(500)

  const text = await page.locator('details.scb-out .scb-out-text').first().textContent().catch(() => '')
  const svgCount = await page.locator('details.scb-out .scb-out-svgs img').count()
  const errorVisible = await page.locator('details.scb-out .scb-out-error').count()
  const summaryText = await page.locator('details.scb-out summary').first().textContent()

  if (!summaryText.includes('点击展开可浏览运行结果')) {
    throw new Error(`${path}: summary 文案不正确 (got "${summaryText}")`)
  }
  if (!text && svgCount === 0 && errorVisible === 0) {
    throw new Error(`${path}: 折叠块展开后为空（既无 text、也无 svg、也无 error）`)
  }
  console.log(`  ✓ ${path}: details=${detailsCount}, text=${text?.length || 0} chars, svgs=${svgCount}`)
}

async function main() {
  const browser = await chromium.launch()
  try {
    const page = await browser.newPage()
    for (const p of PAGES) await check(page, p)
    console.log(`[verify-static-code-blocks] all ${PAGES.length} pages OK`)
  } finally {
    await browser.close()
  }
}

main().catch((e) => {
  console.error(`[verify-static-code-blocks] FAIL: ${e.message}`)
  process.exit(1)
})
```

- [ ] **Step 3: 跑 E2E 测试**

```bash
cd D:/AI/study/quant && node tests/verify-static-code-blocks.js
```
Expected: 5 行 `✓ ...`，最后 `[verify-static-code-blocks] all 5 pages OK`，exit 0。

- [ ] **Step 4: 关闭 dev server（如本任务启动）**

```bash
cd D:/AI/study/quant && pkill -f "vitepress dev" 2>/dev/null || true
```

- [ ] **Step 5: Commit**

```bash
cd D:/AI/study/quant && git add tests/verify-static-code-blocks.js && git commit -m "test(e2e): verify StaticCodeBlock on 5 representative pages"
```

---

## Task 10: 端到端验证 + portable 重新打包

**Files:**
- Modify: `D:/AI/study/quant/portable/dist/` (通过 rebuild)
- Modify: `D:/AI/study/quant/node_modules/` (通过 npm install)

- [ ] **Step 1: 重装依赖（移除 pyodide）**

```bash
cd D:/AI/study/quant && npm install 2>&1 | tail -10
```
Expected: 无 pyodide 安装；echarts/playwright/markdown-it-mathjax3 仍在。

- [ ] **Step 2: 重新 build**

```bash
cd D:/AI/study/quant && npm run build 2>&1 | tail -15
```
Expected: `precompute` 输出 25/25 succeeded；`vitepress build` 成功；`.vitepress/dist/` 含 `<StaticCodeBlock>` HTML 页。

- [ ] **Step 3: 验证 .vitepress/dist 体积**

```bash
cd D:/AI/study/quant && du -sh .vitepress/dist/ && du -sh .vitepress/dist/pyodide 2>/dev/null || echo "no pyodide dir (expected)"
```
Expected: 总 ~50 MB（vs 之前的 173 MB）；`no pyodide dir`。

- [ ] **Step 4: 跑 E2E 测试**

```bash
cd D:/AI/study/quant && (npm run dev -- --port 5189 &) && sleep 8 && node tests/verify-static-code-blocks.js && pkill -f "vitepress dev" 2>/dev/null || true
```
Expected: 5 页全部通过，exit 0。

- [ ] **Step 5: 重新打包 portable**

```bash
cd D:/AI/study/quant && cmd /c package-portable.bat 2>&1 | tail -30
```
Expected: portable/dist/ 生成；大小 ≤ 50 MB（vs 之前 173 MB）；不含 pyodide 子目录。

- [ ] **Step 6: 验证 portable 包瘦身**

```bash
cd D:/AI/study/quant && du -sh portable/dist/ && ls portable/dist/pyodide 2>&1 || echo "no pyodide (expected)"
```
Expected: ~50 MB 总大小；`no pyodide`。

- [ ] **Step 7: 验证 .output.json + .svgs 已打包进 portable**

```bash
cd D:/AI/study/quant && ls portable/dist/code/*.output.json | wc -l && find portable/dist/code -name "*.svg" | wc -1
```
Expected: 25 个 .output.json；若干 .svg。

- [ ] **Step 8: 启动 portable serve，验证线上页可用**

```bash
cd D:/AI/study/quant && (node portable/serve.cjs &) && sleep 4 && curl -sS http://127.0.0.1:5173/guide/m01-overview/1.3-quant-mindset.html 2>&1 | grep -c "StaticCodeBlock\|点击展开可浏览运行结果" && pkill -f "serve.cjs" 2>/dev/null || true
```
Expected: 至少 1 行命中（页内有 StaticCodeBlock 或折叠 summary 文案）。

- [ ] **Step 9: 最终 Commit**

```bash
cd D:/AI/study/quant && git add package-lock.json portable/dist/ -f && git commit -m "chore: rebuild portable package, -71% size (173MB → 50MB), no pyodide"
```

---

## 验收清单

- [ ] 25 个 `public/code/*.py` 首行含 `# @quantlab/output:` 标记
- [ ] 0 个 .md 含 `<PythonPlayground>` 字符串
- [ ] 25 个 `public/code/*.output.json` 存在且结构合法
- [ ] `portable/dist/` 总大小 ≤ 50 MB（之前 173 MB）
- [ ] `portable/dist/pyodide/` 不存在
- [ ] 5 个典型页面 E2E 测试通过
- [ ] `components/StaticCodeBlock.vue` 已注册到 `.vitepress/theme/index.ts`
- [ ] `package.json` 已移除 `pyodide` 依赖
- [ ] `index.md` tagline 已更新（无 "Pyodide" 字样）
- [ ] `package-portable.bat` 已无 pyodide 断言
- [ ] 浏览器打开 1.3-quant-mindset 页面，折叠块默认收起，点击 summary 展开看到文本/图
- [ ] 浏览器打开 11.1-greeks 页面（matplotlib 多图），折叠块展开看到 ≥1 张 SVG

---

## 风险与回滚

任何任务失败，回滚步骤：

```bash
cd D:/AI/study/quant && git log --oneline -10   # 找到本计划的 commit 起点
git revert --no-commit <commit>..HEAD
# 或一次性：
git reset --hard <commit-before-plan>
```

所有删除文件在 git 历史中保留。
