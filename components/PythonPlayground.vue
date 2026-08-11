<template>
  <div class="py-playground" :class="{ 'py-loading': loading }">
    <div class="py-header">
      <span class="py-label">
        🐍 Python {{ pyVersion || '' }}
        <span class="py-pkgs" v-if="pyodideLoaded">| numpy, pandas, scipy, matplotlib{{ extraPkgs }}</span>
        <span v-else-if="isPreloading" class="py-pkgs py-pkgs--loading">| ⏳ 后台预装中…</span>
      </span>
      <div class="py-header-right">
        <span v-if="hasUnsupported" class="py-warn" :title="warnTitle">⚠️ 部分包不可用</span>
        <button class="py-run-btn" :disabled="(loading && !pyodideLoaded) || running" @click="runCode">
          {{ pyodideLoaded ? (running ? '⚡ 运行中...' : '▶ 运行') : (isPreloading ? '⏳ 准备中...' : '▶ 运行') }}
        </button>
      </div>
    </div>
    <pre ref="slotRef" class="py-slot-source"><slot /></pre>
    <textarea
      ref="editorRef"
      class="py-editor"
      :value="code"
      @input="code = ($event.target as HTMLTextAreaElement).value"
      spellcheck="false"
      :style="{ minHeight: editorHeight + 'px' }"
    ></textarea>
    <div v-if="output !== null" class="py-output" :class="{ 'py-error': isError }">
      <div v-for="(seg, i) in outputSegments" :key="i" class="py-seg">
        <pre v-if="seg.type === 'text'" v-html="seg.text"></pre>
        <img v-else-if="seg.type === 'image'"
             :src="seg.src"
             :alt="seg.alt || '图表'"
             class="py-img"
             @load="onImgLoad" />
      </div>
    </div>
    <div v-if="isPreloading || loading" class="py-output py-placeholder py-preloading">
      <div class="py-spinner"></div>
      <div class="py-preload-text">⏳ <strong>Python 运行环境准备中...</strong></div>
      <div class="py-preload-detail">{{ preloadingProgress || '初始化中...' }}</div>
      <div class="py-preload-hint">
        💡 浏览器后台正在下载 numpy / pandas / scipy。<br/>
        完成后本页面所有代码框直接可运行,无需再次下载。
      </div>
    </div>
    <div v-else-if="pyodideLoaded && output === null" class="py-output py-placeholder py-ready">
      <span style="color: var(--mdb-bull, #00E5A0)">✓</span> Python 环境已就绪。点击「▶ 运行」执行上方代码。
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  src?: string
  code?: string
  height?: number
}>(), {
  src: '',
  code: '',
  height: 200,
})

// Read slot content from hidden DOM element (preserves newlines)
const slotRef = ref<HTMLElement | null>(null)
const code = ref('print("Hello, Quant!")')
let codeLoaded = false

async function loadCode() {
  if (codeLoaded) return
  // Priority: src (fetch .py file) > slot content > code prop
  if (props.src) {
    try {
      const resp = await fetch(props.src)
      if (resp.ok) {
        code.value = await resp.text()
        codeLoaded = true
        return
      }
    } catch (e) { /* fall through */ }
  }
  // Try slot content from hidden DOM
  if (slotRef.value) {
    const text = slotRef.value.textContent || ''
    const trimmed = text.trim()
    if (trimmed.length > 10) {
      code.value = trimmed
      codeLoaded = true
      return
    }
  }
  // Fallback to code prop
  if (props.code) {
    code.value = props.code
    codeLoaded = true
  }
}

const editorRef = ref<HTMLTextAreaElement | null>(null)
const editorHeight = ref(props.height)
const output = ref<string | null>(null)
const isError = ref(false)

// Split output into text segments and image segments (for matplotlib base64 PNG)
interface OutputSeg { type: 'text' | 'image'; text?: string; src?: string; alt?: string }
const outputSegments = computed<OutputSeg[]>(() => {
  if (output.value === null) return []
  const text = output.value
  // Regex to find __MATPLOTLIB_PNG__<base64>__END_MATPLOTLIB_PNG__ blocks
  const re = /__MATPLOTLIB_PNG__([A-Za-z0-9+/=]+)__END_MATPLOTLIB_PNG__/g
  const segs: OutputSeg[] = []
  let lastIdx = 0
  let m: RegExpExecArray | null
  let imgCount = 0
  while ((m = re.exec(text)) !== null) {
    if (m.index > lastIdx) {
      const t = text.slice(lastIdx, m.index).replace(/__MATPLOTLIB_READY__\s*/g, '')
      if (t.trim()) segs.push({ type: 'text', text: t })
    }
    segs.push({ type: 'image', src: `data:image/png;base64,${m[1]}`, alt: `图表 ${++imgCount}` })
    lastIdx = m.index + m[0].length
  }
  if (lastIdx < text.length) {
    const t = text.slice(lastIdx).replace(/__MATPLOTLIB_READY__\s*/g, '')
    if (t.trim()) segs.push({ type: 'text', text: t })
  }
  return segs
})

function onImgLoad() {
  // After images load, scroll output area to bottom
  nextTick(() => {
    const el = document.querySelector('.py-output')
    if (el) (el as HTMLElement).scrollTop = (el as HTMLElement).scrollHeight
  })
}
const loading = ref(false)
const running = ref(false)
const pyVersion = ref('')
const pyodideLoaded = ref(false)
const extraPkgs = ref('')
const hasUnsupported = ref(false)
const warnTitle = ref('')
const preloadingProgress = ref('')  // 后台预加载的进度描述
const isPreloading = ref(false)

// 同步全局阶段到本地 ref,UI 自动响应
function syncFromGlobal() {
  const g = getGlobal()
  if (g.phase === 'loaded') {
    pyodideLoaded.value = true
    loading.value = false
    isPreloading.value = false
  } else if (g.phase === 'loading') {
    isPreloading.value = true
    loading.value = true
    preloadingProgress.value = g.progress
  } else if (g.phase === 'failed') {
    isPreloading.value = false
    loading.value = false
  }
}

// ============ 全局 Pyodide 单例(后台预加载) ============
// 所有 PythonPlayground 共享一个 Pyodide 实例,避免重复下载/初始化
// 利用 window 全局挂载,跨页面导航不丢失
interface GlobalPyodideState {
  pyodide: any | null
  promise: Promise<any> | null
  loadedPkgs: Set<string>
  phase: 'idle' | 'loading' | 'loaded' | 'failed'
  progress: string  // 用户可见的进度描述
}
const GLOBAL_KEY = '__QUANTLAB_PYODIDE__'
function getGlobal(): GlobalPyodideState {
  const w = window as any
  if (!w[GLOBAL_KEY]) {
    w[GLOBAL_KEY] = {
      pyodide: null,
      promise: null,
      loadedPkgs: new Set<string>(),
      phase: 'idle',
      progress: '',
    }
  }
  return w[GLOBAL_KEY] as GlobalPyodideState
}

// Known package availability in Pyodide
const BUILTIN = new Set([
  'numpy', 'pandas', 'scipy', 'matplotlib', 'pyplot',
  'json', 'time', 'math', 'random', 're', 'sys', 'os',
  'itertools', 'collections', 'functools', 'datetime',
  'typing', 'dataclasses', 'enum', 'abc', 'pathlib',
  'hashlib', 'warnings', 'logging', 'threading', 'asyncio',
  'heapq', 'decimal', 'copy', 'io', 'textwrap', 'csv',
  'statistics', 'struct', 'inspect', 'operator',
])

const MICROPIP = new Set([
  'sklearn', 'scikit-learn', 'scikit_learn',
  'pyarrow',
  'networkx',
  'statsmodels',
])

// Packages that work via pyfetch shim (browser HTTP)
const PYFETCH_SHIM = new Set([
  'requests',
])

// Packages that use pyfetch fallback with CORS warning
const PYFETCH_WARN = new Set([
  'akshare',
  'yfinance',
])

const UNSUPPORTED: Record<string, string> = {
  'xgboost': 'XGBoost 依赖 C++ 编译，浏览器环境不支持',
  'lightgbm': 'LightGBM 依赖 C++ 编译，浏览器环境不支持',
  'transformers': 'HuggingFace transformers 体积过大，浏览器环境不支持',
  'torch': 'PyTorch 无 WebAssembly 版本',
  'kafka': 'Kafka 需要连接外部消息队列服务',
  'ibapi': 'IB API 需要连接盈透 TWS/Gateway',
  'prometheus_client': 'Prometheus 需要连接外部监控服务',
  'websocket': '浏览器不支持原生 WebSocket 服务端',
  'websockets': '浏览器不支持原生 WebSocket 服务端',
  'redis': 'Redis 需要连接外部 Redis 服务',
  'gym': 'OpenAI Gym 依赖渲染引擎，浏览器环境不支持',
  'numba': 'Numba LLVM JIT 不支持 WebAssembly',
  'hmmlearn': 'hmmlearn 依赖 C 扩展，浏览器环境不支持',
  'seaborn': 'seaborn 依赖链较复杂，可能不完全支持',
}

function detectImports(src: string): { micropip: string[], pyfetchShim: string[], pyfetchWarn: string[], unsupported: string[] } {
  const needMicropip: string[] = []
  const needPyfetchShim: string[] = []
  const needPyfetchWarn: string[] = []
  const needUnsupported: string[] = []
  const importRe = /(?:^|\n)(?:import\s+(\w+)|from\s+(\w+)(?:\.\w+)*\s+import)/g
  let m: RegExpExecArray | null
  const globalLoadedPkgs = getGlobal().loadedPkgs
  while ((m = importRe.exec(src)) !== null) {
    const pkg = (m[1] || m[2]).split('.')[0].toLowerCase()
    if (globalLoadedPkgs.has(pkg)) continue
    if (UNSUPPORTED[pkg]) {
      needUnsupported.push(pkg)
    } else if (PYFETCH_SHIM.has(pkg)) {
      needPyfetchShim.push(pkg)
    } else if (PYFETCH_WARN.has(pkg)) {
      needPyfetchWarn.push(pkg)
    } else if (MICROPIP.has(pkg)) {
      needMicropip.push(pkg)
    }
  }
  return {
    micropip: [...new Set(needMicropip)],
    pyfetchShim: [...new Set(needPyfetchShim)],
    pyfetchWarn: [...new Set(needPyfetchWarn)],
    unsupported: [...new Set(needUnsupported)],
  }
}

// Python preamble for requests pyfetch shim
const PYFETCH_REQUESTS_SHIM = `
import sys
import json as _json

class _RequestsResponse:
    def __init__(self, status, body, headers):
        self.status_code = status
        self.text = body
        self._body = body
        self.headers = headers
    def json(self):
        return _json.loads(self._body)

class _RequestsModule:
    """requests API shim backed by pyodide.http.pyfetch"""
    @staticmethod
    async def _fetch(method, url, **kwargs):
        from pyodide.http import pyfetch
        resp = await pyfetch(url, method=method, **kwargs)
        body = await resp.string()
        headers = dict(resp.headers)
        return _RequestsResponse(resp.status, body, headers)

def _install_requests_shim():
    import importlib
    if 'requests' not in sys.modules:
        m = type(sys)('requests')
        m.get = lambda url, **kw: _RequestsModule._fetch('GET', url, **kw)
        m.post = lambda url, **kw: _RequestsModule._fetch('POST', url, **kw)
        m.put = lambda url, **kw: _RequestsModule._fetch('PUT', url, **kw)
        m.Response = _RequestsResponse
        sys.modules['requests'] = m
_install_requests_shim()
`

// Python preamble for akshare/yfinance pyfetch-based mock
const PYFETCH_DATA_SHIM = `
import sys as _sys
import json as _json

class _DataFrameBuilder:
    @staticmethod
    def from_dict(data):
        import pandas as pd
        return pd.DataFrame(data)

class _FetchModule:
    """Browser-compatible data fetch with CORS fallback"""
    @staticmethod
    async def _get_json(url, params=None):
        from pyodide.http import pyfetch
        if params:
            qs = '&'.join(f'{k}={v}' for k,v in params.items())
            url = f'{url}?{qs}'
        try:
            resp = await pyfetch(url)
            body = await resp.string()
            return _json.loads(body)
        except Exception as e:
            raise RuntimeError(
                f'数据获取失败: {e}\\n'
                f'目标 API ({url[:60]}...) 可能受 CORS 跨域限制，'
                f'浏览器环境无法直接访问外部数据源。'
            )

_AK_FETCH = _FetchModule()
_YF_FETCH = _FetchModule()
`

function buildPreamble(pyfetchShim: string[], pyfetchWarn: string[]): string {
  const parts: string[] = []
  if (pyfetchShim.length) parts.push(PYFETCH_REQUESTS_SHIM)
  if (pyfetchWarn.length) parts.push(PYFETCH_DATA_SHIM)
  parts.push(DEMO_DATA_PREAMBLE)
  return parts.join('\n')
}

// ============ 教学 Demo Data Preamble ============
// 常见教学片段会引用未定义的 df / prices / returns / nav_no_cost / trades 等
// 这里预填一组示例数据,使教学片段开箱即用,无需用户感知
const DEMO_DATA_PREAMBLE = `
import numpy as _np
import pandas as _pd

_np.random.seed(42)
_n = 60  # 默认 60 个交易日
# 价格序列(几何布朗运动)
_close = 100 * _np.exp(_np.cumsum(_np.random.normal(0.0005, 0.02, _n)))
_high  = _close * (1 + _np.abs(_np.random.normal(0, 0.008, _n)))
_low   = _close * (1 - _np.abs(_np.random.normal(0, 0.008, _n)))
_open  = _close + _np.random.normal(0, 0.5, _n)
_vol   = _np.random.randint(1_000_000, 5_000_000, _n)

# 组合/持仓/收益变量(常见教学片段引用) - 先定义
position           = _np.sign(_np.random.normal(0, 1, _n)).copy()
signal             = _np.random.choice([-1, 0, 1], _n, p=[0.45, 0.1, 0.45])
trades             = _np.diff(_np.concatenate([[0], signal]), prepend=0)
prices             = _close
returns            = _pd.Series(_close).pct_change().fillna(0).values
strategy_returns   = signal[:-1] * returns
capital            = 1_000_000.0
nav_no_cost        = _np.cumprod(1 + strategy_returns) * capital
nav_with_cost      = nav_no_cost.copy()

# 常用 DataFrame(含教学片段需要的 position/signal/returns 列)
df = _pd.DataFrame({
    'Date':     _pd.date_range('2025-01-01', periods=_n, freq='B'),
    'Open':     _open, 'High': _high, 'Low': _low, 'Close': _close, 'Volume': _vol,
    'returns':  returns,
    'signal':   signal,
    'position': position,
}).set_index('Date')

# Backtesting context
results   = {'sharpe': 1.34, 'maxdd': -0.082, 'winrate': 0.56, 'trades': 247}
portfolio = {'AAPL': 0.30, 'NVDA': 0.25, 'MSFT': 0.20, 'GOOG': 0.15, 'CASH': 0.10}
factors   = _pd.DataFrame({
    'momentum':    _np.random.normal(0.001, 0.02, _n),
    'value':       _np.random.normal(0.0005, 0.015, _n),
    'quality':     _np.random.normal(0.0008, 0.012, _n),
    'lowvol':     -_np.abs(_np.random.normal(0, 0.018, _n)),
})
`

// Pyodide is pre-loaded via VitePress head script tag — global loadPyodide() is available
declare global { interface Window { loadPyodide?: (opts: any) => Promise<any> } }

const CDN_MIRRORS = [
  // 本地 Pyodide（便携版 / 离线包）—— 优先使用
  './pyodide/',
  '/pyodide/',
  // 在线镜像（在线时回退使用）
  'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/',
  'https://unpkg.com/pyodide@0.26.4/full/',
  'https://pyodide-cdn2.iodide.io/v0.26.4/full/',
]

async function loadPyodideCDN(): Promise<any> {
  const g = getGlobal()
  // 如果实例已就绪,直接返回
  if (g.phase === 'loaded' && g.pyodide) {
    return g.pyodide
  }
  // 另一个实例正在加载中,等待它完成
  if (g.promise) {
    return g.promise
  }
  // 首次调用才真正启动加载
  g.phase = 'loading'
  g.progress = '初始化 Pyodide ...'
  loading.value = true
  isPreloading.value = true
  preloadingProgress.value = g.progress

  g.promise = (async () => {
    try {
      if (typeof window.loadPyodide !== 'function') {
        throw new Error('Pyodide 脚本未加载，请刷新页面')
      }

      let lastError: Error | null = null
      for (const indexURL of CDN_MIRRORS) {
        try {
          g.progress = `从 ${indexURL.startsWith('./') || indexURL.startsWith('/') ? '本地便携包' : 'CDN'} 加载运行时 (~6MB)...`
          syncFromGlobal()
          const pyodideInstance = await window.loadPyodide!({ indexURL })

          // 列出本地便携包里已预装的 wheels(wheels/ 与 indexURL 同级)
          const prebundled = ['numpy', 'pandas', 'scipy', 'matplotlib', 'micropip']
          const toLoad = prebundled.filter(p => !g.loadedPkgs.has(p))
          if (toLoad.length) {
            g.progress = `预装包 ${toLoad.join(' / ')} ...`
            syncFromGlobal()
            await pyodideInstance.loadPackage(toLoad, {
              messageCallback: (msg: string) => {
                if (msg) g.progress = msg
                syncFromGlobal()
              }
            })
            toLoad.forEach(p => g.loadedPkgs.add(p))
          }

          const micropip = pyodideInstance.pyimport('micropip')
          g.pyodide = pyodideInstance
          pyodideInstance._micropip = micropip
          pyVersion.value = pyodideInstance.runPython('import sys; sys.version.split()[0]')
          g.phase = 'loaded'
          g.progress = '已就绪'
          syncFromGlobal()
          return pyodideInstance
        } catch (e: any) {
          lastError = e
          continue
        }
      }
      throw lastError || new Error('所有 CDN 镜像均加载失败')
    } catch (e: any) {
      g.phase = 'failed'
      g.progress = ''
      loading.value = false
      isPreloading.value = false
      throw new Error(`Python 环境加载失败（网络较慢时可能超时）。\n${e.message}\n\n💡 方案1: 刷新页面重试\n💡 方案2: bash setup.sh → jupyter lab 本地运行`)
    }
  })()

  return g.promise
}

// 后台预加载触发器 — 任何 PythonPlayground 挂载时立即调用一次
// 后续 Page 切换 / 多个 PythonPlayground 共享同一个加载结果
function ensurePreloadStarted() {
  const g = getGlobal()
  if (g.phase === 'idle') {
    // 异步启动,不阻塞挂载
    loadPyodideCDN().catch(() => { /* 错误已在函数内处理 */ })
  } else {
    // 已经在加载中或已加载,同步本地状态
    syncFromGlobal()
  }
}

async function installPackages(packages: string[]) {
  const pyodide = getGlobal().pyodide
  if (!pyodide || !packages.length) return
  const globalLoadedPkgs = getGlobal().loadedPkgs
  const toInstall = packages.filter(p => !globalLoadedPkgs.has(p))
  if (!toInstall.length) return

  const labelParts: string[] = []
  for (const pkg of toInstall) {
    try {
      const pypiName = pkg === 'sklearn' ? 'scikit-learn' : pkg
      await pyodide._micropip.install(pypiName)
      globalLoadedPkgs.add(pkg)
      labelParts.push(pkg)
    } catch (e) {
      console.warn(`Failed to install ${pkg}:`, e)
    }
  }
  if (labelParts.length) {
    extraPkgs.value = ', ' + labelParts.join(', ')
  }
}

async function runCode() {
  if (running.value) return

  running.value = true
  output.value = null
  isError.value = false
  hasUnsupported.value = false

  let pyodide: any = null
  try {
    // 优先复用全局已加载的 Pyodide,无则等待启动
    if (!getGlobal().pyodide) {
      // 显示加载状态
      loading.value = true
    }
    pyodide = await loadPyodideCDN()
  } catch (loadErr: any) {
    output.value = loadErr.message || String(loadErr)
    isError.value = true
    running.value = false
    loading.value = false
    return
  }

  const src = code.value

  try {
    // Detect imports
    const { micropip: needPip, pyfetchShim, pyfetchWarn, unsupported } = detectImports(src)

    // Build warnings
    const allWarnings: string[] = []
    if (unsupported.length) {
      hasUnsupported.value = true
      warnTitle.value = unsupported.map(p => `${p}: ${UNSUPPORTED[p]}`).join('\n')
      allWarnings.push(...unsupported.map(p => `⚠ ${p}: ${UNSUPPORTED[p]}`))
    }
    if (pyfetchWarn.length) {
      allWarnings.push(`⚠ ${pyfetchWarn.join(', ')}: 使用浏览器 HTTP 适配，部分数据源可能受 CORS 限制`)
    }

    // Install micropip packages
    await installPackages(needPip)

    // Run preamble (pyfetch shims + demo data)
    const preamble = buildPreamble(pyfetchShim, pyfetchWarn)
    if (preamble) {
      try { await pyodide.runPythonAsync(preamble) } catch(e) { /* shim errors are non-fatal */ }
    }

    // Capture stdout/stderr
    const capturedOutput: string[] = []
    pyodide.setStdout({ batched: (text: string) => { capturedOutput.push(text) } })
    pyodide.setStderr({ batched: (text: string) => { capturedOutput.push(text) } })

    // Force matplotlib AGG backend so plt.savefig() always works regardless of env
    try {
      await pyodide.runPythonAsync(`
import io as _io_q
import base64 as _b64_q
import matplotlib
try:
    matplotlib.use('Agg')
except Exception:
    pass
import matplotlib.pyplot as _plt_q
_orig_show = _plt_q.show
def _patched_show(*args, **kwargs):
    try:
        fig = _plt_q.gcf()
        _buf = _io_q.BytesIO()
        fig.savefig(_buf, format='png', bbox_inches='tight', dpi=90)
        _b64 = _b64_q.b64encode(_buf.getvalue()).decode('ascii')
        print(f"__MATPLOTLIB_PNG__{_b64}__END_MATPLOTLIB_PNG__")
        _plt_q.close(fig)
    except Exception as _e:
        print(f"⚠️ 图表渲染失败: {_e}")
_plt_q.show = _patched_show
print("__MATPLOTLIB_READY__")
`)
    } catch (e) {
      // matplotlib not available, silently skip the patch
    }

    await pyodide.runPythonAsync(src)

    let out = capturedOutput.join('')
    if (allWarnings.length && !out.includes('⚠')) {
      out = '[运行环境提示]\n' + allWarnings.join('\n') + '\n\n' + out
    }
    output.value = out
    isError.value = false
  } catch (err: any) {
    let msg = err.message || String(err)
    if (msg.includes('ModuleNotFoundError') || msg.includes('No module named')) {
      const mod = msg.match(/No module named '(\w+)'/)?.[1] || msg.match(/ModuleNotFoundError.*'(\w+)'/)?.[1] || ''
      if (mod && UNSUPPORTED[mod.toLowerCase()]) {
        msg = `${msg}\n\n💡 ${mod} 在浏览器中不可用：${UNSUPPORTED[mod.toLowerCase()]}`
      }
    } else if (msg.includes('NameError') && msg.includes('is not defined')) {
      // 友好提示:引用了未定义变量(常见于教学片段)
      const m = msg.match(/name '(\w+)' is not defined/)
      const varName = m ? m[1] : ''
      msg = `${msg}\n\n💡 这是教学代码片段,引用了 \`${varName}\` 等教学变量。
工作区已自动准备常用的 demo 数据: df / prices / returns / nav_no_cost
/ trades / strategy_returns / capital 等。如仍报错,请查阅本章节完整示例。`
    } else if (msg.includes('IndentationError') || msg.includes('SyntaxError')) {
      msg = `${msg}\n\n💡 代码缩进/语法有误。Markdown 渲染时可能丢缩进,请用 Tab 键重排或直接复制源文件代码。`
    }
    output.value = msg
    isError.value = true
  } finally {
    running.value = false
  }

  await nextTick()
  if (editorRef.value) {
    editorRef.value.style.height = 'auto'
    editorRef.value.style.height = Math.max(props.height, editorRef.value.scrollHeight) + 'px'
  }
}

onMounted(async () => {
  await loadCode()
  if (editorRef.value) {
    editorRef.value.style.height = 'auto'
    editorRef.value.style.height = Math.max(props.height, editorRef.value.scrollHeight) + 'px'
  }
  // ★ 后台预加载 Pyodide + numpy/pandas/scipy/matplotlib
  // 用户读了几秒钟章节后,Python 环境已经准备好了
  ensurePreloadStarted()
})
</script>

<style scoped>
.py-playground {
  background: var(--py-bg, #2c2c2e);
  border: 1px solid var(--py-border, #3a3a3c);
  border-radius: 10px;
  overflow: hidden;
  margin: 16px 0;
  transition: border-color 0.2s;
}

.py-playground:hover {
  border-color: #545458;
}

.py-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--py-header-bg, rgba(0, 0, 0, 0.2));
  border-bottom: 1px solid var(--py-border, #3a3a3c);
  gap: 8px;
  flex-wrap: wrap;
}

.py-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.py-label {
  font-size: 0.8em;
  font-weight: 600;
  color: var(--vp-c-text-2);
  font-family: var(--vp-font-family-mono);
}

.py-pkgs {
  font-weight: 400;
  color: var(--vp-c-text-3);
  font-size: 0.9em;
}

.py-warn {
  font-size: 0.75em;
  color: #FF9F0A;
  cursor: help;
  white-space: nowrap;
}

.py-run-btn {
  background: #007AFF;
  border: none;
  color: white;
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 500;
  font-family: var(--vp-font-family-base);
  transition: all 0.15s ease;
  margin: 0;
  white-space: nowrap;
}

.py-run-btn:hover:not(:disabled) {
  background: #0066d6;
  transform: translateY(-1px);
}

.py-run-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.py-editor {
  width: 100%;
  padding: 16px;
  border: none;
  background: var(--py-editor-bg, #1c1c1e);
  color: var(--vp-c-text-1);
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.88em;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  tab-size: 4;
}

.py-editor:focus {
  background: var(--py-editor-focus, #1c1c1e);
}

.py-output {
  border-top: 1px solid var(--py-border, #3a3a3c);
  padding: 12px 16px;
  max-height: 260px;
  overflow-y: auto;
}

.py-output pre {
  background: transparent;
  padding: 0;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.83em;
  line-height: 1.5;
  color: var(--vp-c-text-1);
  white-space: pre-wrap;
  word-break: break-all;
}

.py-error pre {
  color: #FF453A;
}

.py-seg { margin: 4px 0; }
.py-seg pre { background: transparent; padding: 0; margin: 0; }
.py-img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 8px 0;
  border-radius: 6px;
  border: 1px solid var(--py-border, #3a3a3c);
  background: white;
}

.py-placeholder {
  color: var(--vp-c-text-3);
  font-size: 0.85em;
  font-style: italic;
}

/* ============ 后台预加载动画 ============ */
.py-preloading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px 16px !important;
  font-style: normal !important;
  background: linear-gradient(135deg,
    rgba(0,229,160,.04) 0%,
    rgba(0,212,255,.03) 100%);
  border-left: 3px solid var(--ft-brand, #00E5A0);
}
.py-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(0,229,160,.2);
  border-top-color: var(--ft-brand, #00E5A0);
  border-radius: 50%;
  animation: py-spin 0.9s linear infinite;
  margin-bottom: 4px;
}
@keyframes py-spin {
  to { transform: rotate(360deg); }
}
.py-preload-text {
  font-weight: 600;
  color: var(--ft-brand, #00E5A0);
  font-size: 14px;
}
.py-preload-detail {
  font-size: 12px;
  color: var(--vp-c-text-2);
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
  text-align: center;
  max-width: 90%;
  word-break: break-word;
}
.py-preload-hint {
  margin-top: 6px;
  font-size: 11px;
  color: var(--vp-c-text-3);
  text-align: center;
  font-style: italic;
  opacity: 0.8;
}
.py-ready {
  background: linear-gradient(135deg, rgba(0,229,160,.08), rgba(0,212,255,.04));
  border-left: 3px solid var(--ft-brand, #00E5A0);
  font-style: normal !important;
  color: var(--vp-c-text-1) !important;
}
.py-pkgs--loading {
  color: var(--ft-brand, #00E5A0) !important;
  animation: py-pulse 1.5s ease-in-out infinite;
}
@keyframes py-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.py-slot-source {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
  white-space: pre;
}

.py-loading .py-editor {
  opacity: 0.6;
}

:root .py-playground {
  --py-bg: #f5f5f7;
  --py-border: #d2d2d7;
  --py-header-bg: rgba(0, 0, 0, 0.04);
  --py-editor-bg: #ffffff;
  --py-editor-focus: #ffffff;
}

.dark .py-playground {
  --py-bg: #2c2c2e;
  --py-border: #3a3a3c;
  --py-header-bg: rgba(0, 0, 0, 0.2);
  --py-editor-bg: #1c1c1e;
  --py-editor-focus: #1c1c1e;
}
</style>
