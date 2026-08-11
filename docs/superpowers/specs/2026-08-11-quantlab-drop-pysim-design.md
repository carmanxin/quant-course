# QuantLab — 移除浏览器内 Python 运行机制设计

- **Date**: 2026-08-11
- **Status**: Design (待用户复核)
- **Owner**: QuantLab 维护者
- **Scope**: 移除浏览器内 Pyodide 运行，将 31 个 `<PythonPlayground>` 改为"代码 + 预计算运行结果（折叠）"

## 背景与动机

QuantLab 当前用 **Pyodide (CPython 编译为 WebAssembly)** 在浏览器内执行 Python 代码，让读者点击"一键运行"按钮即可看到 print 输出和 matplotlib 图表。

**问题**：
1. **包体积过大** — `portable/dist/pyodide/` 占 123 MB / 173 MB（71%），其中 scipy 44.9 MB、pandas 22.7 MB、matplotlib 15 MB、numpy 11.4 MB 是主因。
2. **首次加载慢** — wasm + 5 个 wheels 拉取约 10–30 秒，4 镜像 fallback 仍可能超时。
3. **环境脆弱** — 网络受限或 wasm MIME 配置错误都会让交互失效；CI 上 E2E 测试 (`tests/verify-playgrounds.js`) 容易 flake。
4. **与"展示代码与代码运行后的结果"诉求不符** — 当前是"运行"而非"展示结果"。

**目标**：
- 不在浏览器执行 Python；
- 保留所有 Python 代码示例的可读性（Shiki 高亮、复制按钮、源码可下载）；
- 把每个示例的"运行结果"（stdout 文本 + matplotlib SVG 图）作为**预计算产物**嵌入；
- 折叠收起运行结果，避免首屏视觉噪音；
- 包体积瘦 71%。

## 设计原则

1. **零本地运行时** — 浏览器不依赖 Python / WASM / wheels。
2. **零运行时网络** — 输出产物在 build 时生成，打包后是纯静态文件。
3. **build 时一次性** — 改 .py 后重跑 build 自动刷新结果。
4. **优雅降级** — 任何环节失败都不阻塞 build，读者看到失败原因。
5. **可回滚** — 改动可由 `git revert` 一键回退。

## 架构

### 数据流

```
public/code/1.3-bootstrap.py
        │
        │  [build time] scripts/precompute-py-outputs.mjs
        │     spawn('python3', [...], {MPLBACKEND:'svg', QT_QPA_PLATFORM:'offscreen'})
        │     preamble: monkey-patch plt.show() → savefig to <name>.svgs/<name>-N.svg
        │     capture stdout + scan *.svg → write <name>.output.json
        ▼
public/code/
  ├─ 1.3-bootstrap.py
  ├─ 1.3-bootstrap.output.json     { text, svgs }
  └─ 1.3-bootstrap.svgs/
       └─ 1.3-bootstrap-0.svg
        │
        │  [build time] .vitepress/config.ts fence renderer
        │     ```python ... ```  →  <StaticCodeBlock code-b64="...">...</StaticCodeBlock>
        ▼
portable/dist/
  ├─ code/*.py + *.output.json + *.svgs/*.svg
  └─ guide/m01-overview/1.3-quant-mindset.html  (含 <StaticCodeBlock>)
        │
        │  [runtime, browser]
        │     <StaticCodeBlock> mount
        │     fetch /code/1.3-bootstrap.output.json
        │     render: <Shiki code> + <details><summary>...</summary><pre>text</pre><img src=svg></details>
        ▼
读者看到：代码高亮 + 「点击展开可浏览运行结果」折叠块
```

### src 推断策略

`<PythonPlayground>` 旧写法把代码块与 `src` 解耦（代码块后跟独立标签）。新方案在 .py **首行注释**加约定标记：

```python
# @quantlab/output: 1.3-bootstrap
import numpy as np
...
```

脚本扫到 `# @quantlab/output: <name>` 标记 → 把输出写到 `public/code/<name>.output.json` + `public/code/<name>.svgs/*.svg`。组件读源码首行拿这个标记。

一次性脚本 `scripts/add-output-marker.py` 给 25 个 .py 补这个首行注释（已存在标记则跳过）。

### 走法 B（hash 映射）的弃用理由

任何微小改动（空格、注释、版本号）都换 hash → 输出引用全失效。可维护性差。

## 改动清单

### 新增（5 个）

| 路径 | 大小估计 | 作用 |
|---|---|---|
| `components/StaticCodeBlock.vue` | ~6 KB | 替代 CodeRunBlock + PythonPlayground |
| `scripts/precompute-py-outputs.mjs` | ~5 KB | build-time 执行所有 .py |
| `scripts/add-output-marker.py` | ~1 KB | 一次性，给 25 个 .py 加首行标记 |
| `scripts/strip-python-playground-tag.py` | ~1 KB | 一次性，从 31 个 .md 删除 `<PythonPlayground>` 标签 |
| `tests/verify-static-code-blocks.js` | ~3 KB | Playwright 端到端验证 5 个典型页面 |

### 删除（6 类）

| 路径 | 大小 | 备注 |
|---|---|---|
| `components/PythonPlayground.vue` | 27 KB | 全部被 StaticCodeBlock 替代 |
| `components/CodeRunBlock.vue` | 5.8 KB | 全部被 StaticCodeBlock 替代 |
| `public/pyodide/`（整个目录） | ~123 MB | wheels + wasm |
| `public/pyodide-init.js` | 1.1 KB | 引导脚本 |
| `tests/download_wheels.py` | 2.7 KB | wheels 下载工具 |
| `tests/verify-playgrounds.js` | 5.2 KB | E2E 测的是 PythonPlayground |

### 修改（5 个）

| 路径 | 修改内容 |
|---|---|
| `.vitepress/config.ts` | (a) fence 规则 `python/py` 分支改为渲染 `<StaticCodeBlock>`；(b) 移除 `head` 中 `<script src="/pyodide/pyodide.js">`；(c) 移除 `srcExclude` 中的 `public/pyodide/**`；(d) 移除 `public/pyodide-init.js` 引用 |
| `package.json` | (a) `dependencies` 移除 `pyodide`（line 19）；(b) `scripts.build` 改为 `node scripts/precompute-py-outputs.mjs && vitepress build` |
| `package-portable.bat` | 移除 line 56-61 的 pyodide 存在性断言；不再提示 `npm install pyodide@0.26.4 --no-save` |
| `index.md` | line 22 "浏览器内 Pyodide 在线沙箱" → "代码示例 + 预计算结果" |
| 31 个 .md | 移除 `<PythonPlayground src="..." :height="..." />` 单行（`scripts/strip-python-playground-tag.py` 一次性处理） |

### 保留

- `components/RunLocally.vue`（11 个 .md 继续指向 Colab / setup.sh）
- 253 个 `::: details` + 21 个 `<details>`（教学用折叠：名词解释、案例答案等）
- 117 个 .md 的纯 markdown 主体内容
- `public/code/*.py`（25 个源文件，仅首行加 `# @quantlab/output:` 注释）

## StaticCodeBlock 组件 API

### Props

```ts
interface Props {
  /** Base64 编码的源码（fence 渲染规则直接传，避开转义） */
  codeB64: string
  /** fence 语言标签（默认 'python'） */
  lang?: string
  /** 是否默认展开（默认 false） */
  defaultOpen?: boolean
}
```

源码首行 `# @quantlab/output: <name>` 决定 fetch 哪个 `/code/<name>.output.json`。

### 模板结构

```vue
<template>
  <div class="scb">
    <div class="scb-bar">
      <span class="scb-tag">
        <span class="scb-lang">{{ langLabel }}</span>
        <span class="scb-len">{{ lineCount }} 行 · {{ sizeHint }}</span>
      </span>
      <button class="scb-btn" @click="copyCode">📋 复制</button>
    </div>

    <div class="scb-code"><slot /></div>

    <details class="scb-out" :open="defaultOpen">
      <summary class="scb-out-summary">
        <span class="scb-out-icon">▶</span>
        点击展开可浏览运行结果
      </summary>
      <div class="scb-out-body">
        <div v-if="loading" class="scb-out-loading">加载结果中...</div>
        <template v-else-if="output">
          <pre v-if="output.text" class="scb-out-text">{{ output.text }}</pre>
          <div v-if="output.svgs?.length" class="scb-out-svgs">
            <img v-for="(s, i) in output.svgs" :key="i" :src="s" :alt="`运行结果图 ${i+1}`" />
          </div>
          <div v-if="output.error" class="scb-out-error">⚠ {{ output.error }}</div>
        </template>
        <div v-else class="scb-out-empty">⚠ 暂无运行结果</div>
      </div>
    </details>
  </div>
</template>
```

### 行为

| 场景 | 行为 |
|---|---|
| 首次 mount | `fetch(/code/<name>.output.json)`，失败显示「⚠ 暂无运行结果」 |
| 点击 summary | 原生 `<details>` 切换；CSS `summary::marker { display: none }` + `.scb-out-icon` 旋转 90° |
| 点击「复制」 | `navigator.clipboard.writeText(decodedCode)`，1.5s 后回退提示 |
| 深色模式 | `:global(html.dark) .scb-out-text { background: #1a1a1a }` |
| `codeB64` 解析失败 | decodeURIComponent(escape(atob(...))) try/catch → 显示空代码区，不报错 |
| SVG 加载失败 | `<img onerror>` fallback 到占位 SVG |
| 无 `codeB64` 或无 src 标记 | 跳过 fetch；折叠块显示「⚠ 暂无运行结果」 |

### 视觉规范

- CSS 变量复用 `--ft-brand` (Electric Mint)、`--vp-c-divider`、`--vp-c-bg-soft`，class 前缀从 `crb-` 改为 `scb-`。
- summary 背景：`linear-gradient(135deg, rgba(0,229,160,.06), rgba(0,212,255,.04))` 与 `<RunLocally>` 同款。
- SVG `<img>`：`max-width: 100%; border-radius: 8px;`，多张用 CSS Grid `repeat(auto-fit, minmax(360px, 1fr))`。

## 构建脚本

### `scripts/precompute-py-outputs.mjs`

```js
// 伪代码骨架
import { spawn } from 'node:child_process'
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises'
import path from 'node:path'

const CODE_DIR = 'public/code'
const TIMEOUT_MS = 30_000
const MARKER = /^#\s*@quantlab\/output:\s*([\w.\-]+)/

async function runOne(pyFile) {
  const text = await readFile(pyFile, 'utf8')
  const m = text.match(MARKER)
  if (!m) return { skipped: true }

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
    n = _SHOW_COUNT[0]; _SHOW_COUNT[0] += 1
    fname = f"{os.environ['QUANTLAB_OUTPUT_NAME']}-{n}.svg"
    plt.savefig(os.path.join(os.environ['QUANTLAB_SVG_DIR'], fname), bbox_inches="tight")
    plt.close()
plt.show = _patched_show
`
  return new Promise((resolve) => {
    let stdout = '', stderr = ''
    const proc = spawn('python3', ['-c', preamble + text], { env })
    const timer = setTimeout(() => proc.kill('SIGKILL'), TIMEOUT_MS)
    proc.stdout.on('data', d => stdout += d)
    proc.stderr.on('data', d => stderr += d)
    proc.on('close', async (code) => {
      clearTimeout(timer)
      const svgs = (await readdir(svgDir).catch(() => []))
        .filter(f => f.endsWith('.svg'))
        .sort()
        .map(f => `/code/${name}.svgs/${f}`)
      const payload = code === 0
        ? { text: stdout.trim(), svgs }
        : { text: stdout.trim(), svgs, error: stderr.trim().slice(0, 500) }
      await writeFile(path.join(CODE_DIR, `${name}.output.json`), JSON.stringify(payload, null, 2))
      resolve({ name, code })
    })
  })
}

async function main() {
  const files = []
  for await (const f of glob('public/code/*.py')) files.push(f)
  const results = await Promise.all(files.map(runOne))
  const failed = results.filter(r => r.code !== 0)
  console.log(`[precompute] ${results.length - failed.length}/${results.length} succeeded`)
  if (failed.length) for (const f of failed) console.log(`  FAILED ${f.name}`)
}
main()
```

**并发**：25 个 .py × 平均 3s ≈ 3–10s 总耗时。

**CI 缓存**：基于 .py 的 mtime + sha256 hash；命中缓存则跳过 spawn。

### `package.json` scripts

```diff
- "build": "vitepress build"
+ "build": "node scripts/precompute-py-outputs.mjs && vitepress build"
+ "precompute": "node scripts/precompute-py-outputs.mjs"
+ "marker:add": "python scripts/add-output-marker.py"
+ "tag:strip": "python scripts/strip-python-playground-tag.py"
```

## markdown-it fence 钩子

### `.vitepress/config.ts` 新规则

```ts
const fenceRender: any = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const info = (token.info || '').trim().split(/\s+/)[0]
  if (['python', 'py'].includes(info)) {
    const codeB64 = Buffer.from(token.content, 'utf8').toString('base64')
    return `<StaticCodeBlock code-b64="${codeB64}" lang="${info}">${defaultFenceRender(tokens, idx)}</StaticCodeBlock>`
  }
  return defaultFenceRender(tokens, idx)
}
md.renderer.rules.fence = fenceRender
```

### 旧规则移除

`.vitepress/config.ts:253` head 中的 `<script src="/pyodide/pyodide.js">` 移除。`.vitepress/config.ts:304` `srcExclude` 中的 `'public/pyodide/**'` 移除（目录已删）。

## 错误处理

| 失败场景 | 处理位置 | 用户看到 |
|---|---|---|
| `python3` 不在 PATH | spawn EACCES → catch 写空 .output.json | build warning + 折叠块「⚠ 暂无运行结果」 |
| .py 抛 ModuleNotFoundError | 子进程 stderr → `output.error` | 折叠块红色文本「⚠ ModuleNotFoundError: xxx」 |
| .py 死循环 / 超时 | `proc.kill('SIGKILL')` 30s | 折叠块「⚠ 执行超时（30s）」 |
| .output.json 缺失 | 组件 fetch 404 | 折叠块「⚠ 暂无运行结果」 |
| SVG 0 个 | 正常 — 无 plt 调用 | 折叠块仅显示 stdout 文本 |
| SVG 文件 >500KB | 脚本 warning，不阻止 | 文档 img 自动 `max-width: 100%` |

**build 不中断原则**：任何 precompute 失败仅 warning，最终 build exit 0；让读者在折叠块看到失败原因，而非整站空白。

## 测试

| 层 | 工具 | 覆盖 |
|---|---|---|
| 单元 | `node --test scripts/precompute-py-outputs.mjs` | spawn、超时、SVG 注入 |
| 组件 | 暂不写 vitest（项目当前无 vitest 配置） | 跳过 |
| 端到端 | `playwright` (已装) | `tests/verify-static-code-blocks.js` 跑 5 页：1.3、4.3、5.2、11.1、20.1 |
| 构建 | `npm run build && test -f portable/dist/code/1.3-bootstrap.output.json` | build 完整性 |

### `tests/verify-static-code-blocks.js` 断言

- 5 个页面 HTTP 200
- 每个页面至少 1 个 `details.scb-out`
- 展开后 `.scb-out-text` 非空 或 `.scb-out-svgs img` 非空
- 至少 1 个 `<img>` 实际加载成功（`naturalWidth > 0`）

## 风险与回滚

| 风险 | 缓解 |
|---|---|
| .py 加首行注释后某些脚本依赖精确首行 | `add-output-marker.py` 用 `#` 注释，Python 解析忽略；且仅当无标记时加 |
| precompute 失败未发现 | build warning 输出失败列表；CI 步骤 fail 不应通过 |
| SVG 主题与站点浅色背景对比弱 | matplotlib 默认主题；如读者反馈差，加 `plt.style.use('seaborn-v0_8-whitegrid')` 到 preamble |
| 25 个 .py 的 plt 输出体积膨胀 | 单 SVG 一般 30–100KB；25 个共 ~3MB，比 Pyodide 123MB 仍省 120MB |
| Pyodide 删了但 .md 还有 `<PythonPlayground>` 残留 | `scripts/strip-python-playground-tag.py` 一次性扫除；git diff 应为 31 文件 × -1 行 |
| 用户在浏览器断网 | output.json 是站点静态文件，离线可访问；fetch 仅在站点 origin 内 |

**回滚**：`git revert <commit>` 一键回退。所有删除文件都在 git 历史中。

## 验收标准

- `npm run build` 成功，exit 0
- `portable/dist/code/*.output.json` 共 25 个文件
- `portable/dist/guide/m01-overview/1.3-quant-mindset.html` 等 31 个页面包含 `<StaticCodeBlock>` 标签
- `portable/` 总大小从 173 MB 降到 ~50 MB（-71%）
- 5 个 E2E 测试页面 playwright 通过
- 浏览器打开 5 个页面，折叠块默认收起，点击 summary 展开后看到 stdout 文本和/或 SVG 图
- 复制按钮正常工作

## 不在范围内（YAGNI）

- ❌ 在浏览器重新实现 Python 解释器
- ❌ 把 .py 转成 JavaScript 运行（Pyodide 的轻量替代品）
- ❌ 交互式 matplotlib（缩放、平移）
- ❌ 实时刷新输出（用户改代码后重跑）
- ❌ 把 253 个 `::: details` 全部迁移到新组件（它们是教学用，不是代码输出）

## 开放问题

无。所有架构决策已确认。

## 实施前置

1. 用户复核本设计文档 ✓ (待)
2. 调用 `writing-plans` skill 生成实施计划
3. 按计划逐项实现 + 验证
