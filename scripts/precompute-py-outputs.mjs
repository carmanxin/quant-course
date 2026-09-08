#!/usr/bin/env node
// scripts/precompute-py-outputs.mjs
// 遍历 public/code/**/*.py（含 _auto/ 下的 hash 文件），spawn python3 执行，
// 捕获 stdout + plt.show() 的 SVG。失败不抛 exit 1（让 reader 在折叠块看到失败原因）。
//
// 并发：CONCURRENCY=8（默认），避免一次 spawn 太多 python3 把机器干爆。
// 超时：每文件 30s，SIGKILL 兜底。

import { spawn } from 'node:child_process'
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises'
import { glob } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const CODE_DIR = path.join(ROOT, 'public', 'code')
// 默认 30s；重型库（torch/transformers/vectorbt）冷启动常需 40-90s，
// 可用 PRECOMPUTE_TIMEOUT 调大，避免被误杀成空结果。
const TIMEOUT_MS = parseInt(process.env.PRECOMPUTE_TIMEOUT || '30000', 10)
const CONCURRENCY = parseInt(process.env.PRECOMPUTE_CONCURRENCY || '8', 10)
const MARKER = /^#\s*@quantlab\/output:\s*([\w.\-]+)/

// p-limit 简易实现
function pLimit(limit) {
  const queue = []
  let active = 0
  const next = () => {
    if (active >= limit || queue.length === 0) return
    active++
    const { fn, resolve, reject } = queue.shift()
    fn()
      .then((v) => { active--; resolve(v); next() })
      .catch((e) => { active--; reject(e); next() })
  }
  return (fn) => new Promise((resolve, reject) => {
    queue.push({ fn, resolve, reject })
    next()
  })
}

const limit = pLimit(CONCURRENCY)

// === 自动检测并安装缺失的 python 模块 ===
async function ensureModulesInstalled(files) {
  const STDLIB = new Set([
    'os','sys','json','csv','re','time','math','datetime','collections',
    'itertools','functools','pathlib','typing','enum','io','random',
    'string','copy','pickle','hashlib','urllib','http','socket','subprocess',
    'threading','asyncio','contextlib','dataclasses','abc','warnings','traceback',
  ])
  const wanted = new Set()
  for (const f of files) {
    let text
    try { text = await readFile(f, 'utf8') } catch { continue }
    for (const m of text.matchAll(/^\s*(?:from\s+([\w.]+)|import\s+([\w.]+))/gm)) {
      const pkg = (m[1] || m[2]).split('.')[0]
      if (!STDLIB.has(pkg) && !pkg.startsWith('_')) wanted.add(pkg)
    }
  }
  if (wanted.size === 0) return
  console.log(`[precompute] checking ${wanted.size} third-party modules: ${[...wanted].sort().join(', ')}`)
  // 试 import 每个模块
  const missing = []
  for (const mod of wanted) {
    try {
      const r = await new Promise((resolve) => {
        const p = spawn('python3', ['-c', `import ${mod}`], { stdio: 'ignore' })
        p.on('close', (code) => resolve(code))
        p.on('error', () => resolve(1))
      })
      if (r !== 0) missing.push(mod)
    } catch { missing.push(mod) }
  }
  if (missing.length === 0) {
    console.log(`[precompute] all modules present`)
    return
  }
  console.log(`[precompute] installing missing modules: ${missing.join(', ')}`)
  // 一次 pip install 全部（更稳）
  await new Promise((resolve) => {
    const p = spawn('pip', ['install', '--quiet', ...missing], { stdio: 'inherit' })
    p.on('close', (code) => {
      if (code === 0) console.log(`[precompute] installed ${missing.length} modules`)
      else console.log(`[precompute] pip install exit=${code} (some modules may still be missing)`)
      resolve()
    })
    p.on('error', (e) => {
      console.log(`[precompute] pip install failed: ${e.message}`)
      resolve()
    })
  })
}

// === Fragment-with-scaffolding: 自动注入 demo 数据 + 自动调用 def ===
// 让"片段"也能跑出真实输出（而不是 note）
function buildScaffold(codeBody, pureDefMode = false) {
  // 1. 收集代码里已声明的 identifier（模块级 def/class/import）
  // 注意：不收集模块级 def 的参数 —— 若模块级代码调用 foo(prices) 而 prices
  // 只在参数表里出现，说明 prices 是外部依赖，需要注入 demo 数据。
  // 纯 def 片段由 runOne 的 isPureDefOnly 拦截，不会走到这里，所以无副作用。
  const declared = new Set()
  // def 参数名集合：这些名字在 def 函数体内是局部变量，模块级使用视为已定义 → 不入 used
  // 修复 11.7-iv-vs-hv 等场景:def hv_simple(returns, window=20) 中的 returns/window 不应被
  // 当作"外部未声明变量"误注入 demo ndarray(导致 hv_simple(returns).rolling() 失败)
  const defParams = new Set()
  for (const line of codeBody.split(/\r?\n/)) {
    let mm
    // 只认模块级（第 0 列）def/class，类内方法（__init__/compute_costs 等）不算
    if ((mm = line.match(/^def\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^class\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^import\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^from\s+[\w.]+\s+import\s+([\w,\s]+)/))) {
      for (const tok of mm[1].split(',')) {
        const t = tok.trim().split(/\s+as\s+/).pop()
        if (t && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t)
      }
    }
    if ((mm = line.match(/^def\s+\w+\s*\(([^)]*)\)/))) {
      // 收集参数名(剔除 self 和 type-annotated 部分)
      for (const p of mm[1].split(',')) {
        const t = p.trim()
        if (!t || t === 'self') continue
        const name = t.split('=')[0].split(':')[0].trim()
        if (name && /^[_A-Za-z][_A-Za-z0-9]*$/.test(name)) defParams.add(name)
      }
    }
  }
  // 内置与常见库别名
  const ignore = new Set([
    'print','len','range','int','float','str','list','dict','set','tuple','bool',
    'True','False','None','self','cls','return','yield','pass','lambda',
    'np','pd','plt','sns','yf','nx','math','os','sys','json','csv','re','time',
    'datetime','timedelta','coint','adfuller','stats','scipy','numpy',
    'pandas','matplotlib','sklearn','torch','warnings',
    'and','or','not','in','is','for','while','if','elif','else','try','except',
    'finally','raise','with','from','import','def','class','return','global',
    'nonlocal','assert','del','break','continue','async','await','as',
    // typing 常量(若用户代码用 TypeVar/Generic/Protocol 等可能用这些)
    'Tuple','List','Dict','Optional','Any','Set','FrozenSet','Type',
    'Callable','Iterator','Iterable','Mapping','Sequence','Union',
    // __name__/main 是 if __name__ == '__main__' 的语法成分，注入会覆盖内置名破坏脚本
    '__name__','main','__main__',
    // Python 内置异常类 — 注入 ndarray 会破坏 except 子句
    'Exception','BaseException','ValueError','TypeError','AssertionError',
    'KeyError','IndexError','NameError','AttributeError','RuntimeError',
    'StopIteration','GeneratorExit','KeyboardInterrupt','SystemExit',
    'OSError','IOError','FileNotFoundError','ImportError','ModuleNotFoundError',
  ])

  // 3. 下划线开头的标识符（_np / _aligned / _demo_* / _df 等）是教学代码里的
  //    "内部别名/中间结果",用户希望自己定义(如 _np = np 或 _np.random.seed(7))。
  //    注入 ndarray 会让 _np.random.seed(...) 等调用失败。
  //    只在 used 收集阶段跳过,真正出现时若仍未声明会自然 NameError(更易诊断)。
  const UNDERSCORE_PREFIX = /^_/

  // 2. 收集"使用的未声明变量"
  // 策略：
  //   - 跳过 class 类体（self.xxx/类属性/构造参数不参与外部依赖分析）
  //   - 跳过 import/from/def/class/注释/装饰器/docstring 行（含缩进，如函数内 from import）
  //   - for 循环的迭代变量视为局部变量
  //   - 把赋值语句拆成 LHS（声明）+ RHS（使用）
  //   - RHS 剥离字符串字面量、funcall 名、关键字参数名
  //   - LHS 中收集的 identifier 加入 locallyDefined
  //   - RHS 中的 identifier 若不在 declared/locallyDefined/ignore 则加入 used
  const used = new Set()
  const locallyDefined = new Set()
  let classIndent = -1
  for (const line of codeBody.split(/\r?\n/)) {
    const trimmed = line.trim()
    const indent = line.length - line.trimStart().length
    if (trimmed === '') continue
    // class 块状态机：进入 class 后，缩进大于 class 行缩进的行全部跳过
    if (/^class\s+/.test(trimmed)) {
      classIndent = indent
      continue
    }
    if (classIndent >= 0) {
      if (indent > classIndent) continue // class 体内
      classIndent = -1 // 已离开 class 块
    }
    // 跳过 import/from/def/class/#/@/docstring 行（允许缩进的 import，如函数内 import）
    if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(trimmed)) continue
    // for 循环：迭代变量视为局部
    const forMatch = trimmed.match(/^for\s+([^:]+?)\s+in\s+/)
    if (forMatch) {
      for (const v of forMatch[1].split(',')) {
        const id = v.trim().split(/\s+/).pop()
        if (/^[A-Za-z_]\w*$/.test(id)) locallyDefined.add(id)
      }
    }
    const eqMatch = trimmed.match(/^([^=]*?)=(?!=)/)
    if (eqMatch) {
      const lhs = eqMatch[1]
      // df['col'] = ... 或 obj.attr = ...：根对象是"已存在的变量"，不是本行定义 → 视为外部依赖
      const indexAssign = lhs.match(/^\s*([A-Za-z_]\w*)\s*(?:\[|\.)/)
      if (indexAssign) {
        const rootId = indexAssign[1]
        if (!ignore.has(rootId) && !declared.has(rootId) && !defParams.has(rootId) && !locallyDefined.has(rootId)) used.add(rootId)
      }
      // 关键修复:索引赋值如 continuous[t] = ... 中,只把根对象(continuous)作为 LHS 本行定义;
      // 索引内容(t)不是本行定义的局部变量,可能在 for 循环或外部 — 应进入 used
      const lhsStripped = indexAssign
        ? indexAssign[1]  // 只保留根对象名
        : lhs.replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""')
      for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
        const id = m[1]
        if (ignore.has(id)) continue
        if (indexAssign && id === indexAssign[1]) {
          // 根对象已经在 used 中,这里不再加 locallyDefined
          continue
        }
        locallyDefined.add(id)
      }
    }
    let rhs = eqMatch ? trimmed.slice(eqMatch[0].length) : trimmed
    rhs = rhs.replace(/"""[\s\S]*?"""/g, '""').replace(/'''[\s\S]*?'''/g, "''")
    rhs = rhs.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''")
    rhs = rhs.replace(/\b[rf]?"[^"]*"/g, '""').replace(/\b[rf]?'[^']*'/g, "''") // f-string 前缀
    rhs = rhs.replace(/\b\w+(?=\s*\()/g, '')
    // 去除属性访问名（foo.bar 里的 bar；np.linalg 里的 linalg）
    rhs = rhs.replace(/\.\w+/g, '')
    // 去除关键字参数名（如 CostSimulator(commission_rate=0.00025) 里的 commission_rate）
    rhs = rhs.replace(/\b[A-Za-z_]\w*(?=\s*=)/g, '')
    // 把 generator expression 中的迭代变量加到 locallyDefined:
    // 例: sum(p[1] * ... for p in xs) → p 是迭代变量,不是模块级外部依赖
    for (const gm of rhs.matchAll(/\bfor\s+([A-Za-z_]\w*)\s+in\b/g)) {
      locallyDefined.add(gm[1])
    }
    for (const m of rhs.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1]
      if (declared.has(id)) continue
      if (locallyDefined.has(id)) continue
      if (ignore.has(id)) continue
      // def 参数名视为该函数体内的局部变量,不当作模块级外部依赖
      if (defParams.has(id)) continue
      // 注:下划线前缀(_np/_pd/_plt/_demo_* 等)不跳过——
      //     它们会被 3.5 节特殊处理:模块别名注入模块引用,其他下划线变量注入合理 demo 数据
      if (!used.has(id)) used.add(id)
    }
  }

  // 无外部依赖 或 纯 def 片段（pureDefMode）：
  // - 若存在可无参调用的 def（空参数或全默认值），生成只调用的 post
  // - 否则返回 null（无法运行，显示"代码片段"note）
  if (pureDefMode || used.size === 0) {
    const postLines = []
    for (const m of codeBody.matchAll(/^def\s+(\w+)\s*\(([^)]*)\)/gm)) {
      const fname = m[1]
      const params = m[2].trim()
      let callable = false
      if (params === '' || params === 'self') callable = true
      else {
        const parts = params.split(',').map((s) => s.trim()).filter((s) => s && s !== 'self')
        callable = parts.every((p) => p.includes('=') || /:.+=/.test(p))
      }
      if (callable) {
        postLines.push(`print('--- ${fname}() ---')`)
        postLines.push(`try:\n    _r = ${fname}()\n    print(type(_r).__name__, repr(_r)[:300] if not hasattr(_r, 'to_string') else _r.head().to_string())\nexcept Exception as _e:\n    print(f"调用失败: {_e}")`)
      }
    }
    if (postLines.length > 0) return { pre: '', post: postLines.join('\n'), locallyDefined }
    return null
  }

  // 把 locallyDefined 提升到外层以便 caller 使用
  // 注：JS 没有引用语义，用闭包传入即可
  // 拆成 pre（用户代码之前注入 demo 数据）+ post（用户代码之后调用 def）
  // 避免 NameError：调用必须在 def 注册到模块作用域之后执行
  const preLines = []
  const postLines = []
  preLines.push('import numpy as np, pandas as pd')
  preLines.push('np.random.seed(42)')

  const usedSorted = [...used].sort((a, b) => {
    const aIsDF = /^df[\W_]?/.test(a.toLowerCase())
    const bIsDF = /^df[\W_]?/.test(b.toLowerCase())
    if (aIsDF && !bIsDF) return -1
    if (!aIsDF && bIsDF) return 1
    return 0
  })

  for (const name of usedSorted) {
    const lower = name.toLowerCase()
    if (lower === 'df' || (lower.startsWith('df_') && !lower.startsWith('df_signal'))) {
      preLines.push(`${name} = pd.DataFrame({`)
      preLines.push(`    "Open":   100 + np.cumsum(np.random.randn(252)*0.02),`)
      preLines.push(`    "High":   100 + np.cumsum(np.random.randn(252)*0.02) + np.abs(np.random.randn(252)*0.5),`)
      preLines.push(`    "Low":    100 + np.cumsum(np.random.randn(252)*0.02) - np.abs(np.random.randn(252)*0.5),`)
      preLines.push(`    "Close":  100 + np.cumsum(np.random.randn(252)*0.02),`)
      preLines.push(`    "Volume": np.random.randint(1_000_000, 10_000_000, 252),`)
      preLines.push(`    "signal": np.random.choice([0, 1], size=252),`)
      preLines.push(`    "returns": np.random.randn(252) * 0.02,`)  // M2 教学片段常引用 df['returns']
      preLines.push(`    "X":      100 + np.cumsum(np.random.randn(252)*0.02),`)  // 2.4 案例1 协整检验用 df['X'], df['Y']
      preLines.push(`    "Y":      100 + np.cumsum(np.random.randn(252)*0.02),`)
      preLines.push(`})`)
      preLines.push(`${name}.index = pd.date_range("2024-01-01", periods=252)`)
    } else if (lower === 'signal' || lower === 'df_signal' || lower.startsWith('signal_') || lower.endsWith('_signal')) {
      preLines.push(`${name} = np.random.choice([0, 1], size=252)`)
    } else if (lower === 'prices' || lower.startsWith('prices_') || lower === 'price' || lower.startsWith('price_')) {
      // prices 默认 Series(OHLC 数据常见 + .量 价格) — 用 DateTimeIndex 方便后续回测/rolling
      // 但同时支持 .iterrows / .groupby / .rolling,所以升级为 DataFrame
      preLines.push(`${name} = pd.DataFrame({"close": 100 + np.cumsum(np.random.randn(252)*0.02)}, index=pd.date_range("2024-01-01", periods=252))`)
    } else if (lower === 'prices_df' || lower === 'stock_prices' || lower.includes('price_df') || lower.endsWith('_df') || lower === 'returns_df') {
      // returns_df / xxx_df 视为"多策略收益矩阵" DataFrame
      preLines.push(`${name} = pd.DataFrame(100 + np.cumsum(np.random.randn(252,5)*0.02, axis=0), columns=[f"S{i}" for i in range(5)])`)
    } else if (lower === 'factors' || lower === 'factor_data' || lower === 'factor_df' || lower === 'factor_returns' || lower.startsWith('factors_') || lower.endsWith('_factors')) {
      // M2/M5 教学片段里 factors 约定为 DataFrame(每列一个因子)
      // 用量化标准因子名(momentum/value/quality/size/lowvol)而非 f0/f1/...
      // 这样跨章节共享同一套因子,案例2.3 _aligned_factors['momentum']['value'] 等能直接命中
      preLines.push(`${name} = pd.DataFrame(np.random.randn(252, 5) * 0.02, columns=["momentum","value","quality","size","lowvol"], index=pd.date_range("2024-01-01", periods=252))`)
    } else if (lower === 'returns' || lower === 'strategy_returns' || lower === 'market_returns' || lower.endsWith('_returns')) {
      // 升级为 Series — 既支持 .mean/.std/.rolling/.groupby 也兼容 ndarray 操作
      preLines.push(`${name} = pd.Series(np.random.randn(252) * 0.02, index=pd.date_range("2024-01-01", periods=252), name="${name}")`)
    } else if (lower === 'returns_series' || lower === 'returns_array') {
      preLines.push(`${name} = 100 + np.cumsum(np.random.randn(252)*0.02)`)
    } else if (lower === 'positions' || lower.startsWith('positions_') || lower === 'position') {
      // position/positions 是 Series(M4 回测的常见参数),不是 ndarray — 需要索引/滚动/比较
      preLines.push(`${name} = pd.Series(np.random.choice([-1, 0, 1], size=252).astype(float), index=pd.date_range("2024-01-01", periods=252), name="${name}")`)
    } else if (lower === 'data' || lower === 'price_data' || lower === 'market_data') {
      // M3/M4 数据常为 OHLCV DataFrame(需要 iterrows / rolling / groupby)
      // 同时提供大小写列名,兼容不同源码习惯
      preLines.push(`${name} = pd.DataFrame({\n        "Open":   100 + np.cumsum(np.random.randn(252)*0.02),\n        "High":   100 + np.cumsum(np.random.randn(252)*0.02) + np.abs(np.random.randn(252)*0.5),\n        "Low":    100 + np.cumsum(np.random.randn(252)*0.02) - np.abs(np.random.randn(252)*0.5),\n        "Close":  100 + np.cumsum(np.random.randn(252)*0.02),\n        "Volume": np.random.randint(1_000_000, 10_000_000, 252),\n        "open":   100 + np.cumsum(np.random.randn(252)*0.02),\n        "high":   100 + np.cumsum(np.random.randn(252)*0.02) + np.abs(np.random.randn(252)*0.5),\n        "low":    100 + np.cumsum(np.random.randn(252)*0.02) - np.abs(np.random.randn(252)*0.5),\n        "close":  100 + np.cumsum(np.random.randn(252)*0.02),\n        "volume": np.random.randint(1_000_000, 10_000_000, 252),\n      }, index=pd.date_range("2024-01-01", periods=252))`)
    } else if (lower.includes('hedge') || lower.includes('beta')) {
      preLines.push(`${name} = np.random.uniform(0.5, 1.5, size=100)`)
    } else if (lower === 'x' || lower === 'y' || /^x_\d+$/.test(lower) || /^y_\d+$/.test(lower)) {
      preLines.push(`${name} = np.random.randn(252)`)
    } else if (lower === 'date' || lower === 'dates' || lower === 'trading_dates') {
      // M3/M9 时间序列常用 date_range — 给 DatetimeIndex Series
      preLines.push(`${name} = pd.Series(pd.date_range("2024-01-01", periods=252), name="date")`)
    } else if (lower === 'eps_actual' || lower === 'eps_estimate' || lower === 'eps_surprise' || lower.includes('eps')) {
      // 5.5 财报事件 — 单变量数值序列
      preLines.push(`${name} = pd.Series(np.random.randn(100) * 0.5, name="${name}")`)
    } else if (lower === 'rank' || lower.endsWith('_rank')) {
      // 8.4 截面排序
      preLines.push(`${name} = pd.Series(np.random.randint(1, 100, size=100), name="${name}")`)
    } else if (lower === 'stock1' || lower === 'stock2') {
      preLines.push(`${name} = 100 + np.cumsum(np.random.randn(252)*0.02)`)
    } else if (lower.includes('matrix') || lower.endsWith('_matrix') || lower.endsWith('_mat')) {
      // 2D 矩阵(PCA / 回归常用)— 兜底 ndarray 但保持 2D
      preLines.push(`${name} = np.random.randn(100, 5)`)
    } else if (lower.endsWith('_3d') || lower === 'array_3d') {
      preLines.push(`${name} = np.random.randn(10, 100, 3)`)
    } else if (lower === 'industry' || lower === 'sectors' || lower === 'industries' || lower.endsWith('_industry') || lower.endsWith('_sector')) {
      // 行业/板块代码(整数 0..n 序列)
      preLines.push(`${name} = np.random.randint(0, 10, size=100)`)
    } else if (lower === 'market_cap' || lower.endsWith('_market_cap') || lower === 'caps') {
      preLines.push(`${name} = np.random.uniform(1e8, 1e10, size=100)`)
    } else if (lower === 'weights' || lower.endsWith('_weights') || lower === 'w') {
      // 组合权重(0..1 之和小于等于1)
      preLines.push(`${name} = np.random.dirichlet(np.ones(10))`)
    } else if (lower === 'n_industries' || lower === 'n_sectors' || lower === 'k') {
      preLines.push(`${name} = 10`)
    } else if (lower === 'n_days' || lower === 'n_periods' || lower === 'n_obs' || lower === 'window_size' || lower === 'size' || lower === 'n_samples' || /^n_\w+$/.test(lower)) {
      // 时间序列样本量(252 一年交易日)
      preLines.push(`${name} = 252`)
    } else {
      // 兜底：np 数组
      preLines.push(`${name} = np.random.randn(100)`)
    }
  }

// 3.5 下划线开头的"模块别名"(_np / _pd / _plt 等) 注入为模块引用,
//     让用户代码里的 _np.random.seed(7) 这类调用成立
  // 处理顺序必须在 used 收集之后(已跳过 _ 前缀)、pre 生成期间
  // 用正则匹配: 名字以 _ 开头 + 后缀为已知模块别名(2-5 字母)
  const MODULE_ALIASES = new Set(['np','pd','plt','sns','math','stats','nx','yf'])
  for (const name of usedSorted) {
    if (!UNDERSCORE_PREFIX.test(name)) continue
    const alias = name.slice(1).toLowerCase()
    if (MODULE_ALIASES.has(alias)) {
      preLines.push(`${name} = ${alias}  # 教学代码的模块别名,_ 前缀为防止污染作用域`)
    }
  }

  // 4. 自动调用每个模块级 def（放在用户代码之后，def 已注册到模块作用域）
//    只认第 0 列的 def —— 类内方法（__init__/compute_costs 等）不单独调用
  for (const m of codeBody.matchAll(/^def\s+(\w+)\s*\(([^)]*)\)/gm)) {
    const fname = m[1]
    const params = m[2].trim()
    if (params === '' || params === 'self') {
      postLines.push(`print('--- ${fname}() ---')`)
      postLines.push(`try:\n    print(${fname}())\nexcept Exception as _e:\n    print(f"调用失败: {_e}")`)
    } else {
      // 拆分参数表,只取无默认值的(必填参数)
      const paramList = params.split(',').map(s => s.trim()).filter(s => s && s !== 'self')
      const requiredParams = paramList.filter(p => !p.includes('=') && !/:.+=/.test(p))
      postLines.push(`print('--- ${fname}(...) ---')`)
      postLines.push(`try:`)
      // 必填参数 > 1 → 用户代码负责调用(避免我们瞎传参造成 TypeError 噪音)
      // 必填参数 0 → 直接调,传 user code 已用变量的对应别名
      // 必填参数 1 → 选 best match (df > prices > ...) 传入
      if (requiredParams.length > 1) {
        postLines.push(`    pass  # 多必填参数,留给用户代码调用`)
      } else {
        let arg = null
        for (const u of used) {
          const lu = u.toLowerCase()
          if (lu === 'df' || lu.startsWith('df_')) { arg = `df`; break }
          if (lu === 'prices' || lu.startsWith('prices')) { arg = `prices`; break }
          if (lu === 'prices_df') { arg = `prices_df`; break }
          if (lu === 'signal') { arg = `signal`; break }
          if (lu === 'factors' || lu.startsWith('factors')) { arg = `factors`; break }
          if (lu === 'returns' || lu.endsWith('_returns')) { arg = `returns`; break }
        }
        if (arg) {
          postLines.push(`    _r = ${fname}(${arg})`)
          postLines.push(`    print(type(_r).__name__, repr(_r)[:300] if not hasattr(_r, 'to_string') else _r.head().to_string())`)
        } else if (requiredParams.length === 0) {
          // 无必填参数 + 无 best match → 不调用,避免传奇怪参数
          postLines.push(`    pass  # 无明确参数,留给用户代码调用`)
        } else {
          // 兜底:用第一个 used 变量
          const first = [...used][0]
          if (first) {
            postLines.push(`    _r = ${fname}(${first})`)
            postLines.push(`    print(type(_r).__name__, repr(_r)[:300])`)
          } else {
            postLines.push(`    pass  # 无可传参数,跳过`)
          }
        }
      }
      postLines.push(`except Exception as _e:\n    print(f"调用失败: {_e}")`)
    }
  }

  return { pre: preLines.join('\n'), post: postLines.join('\n'), locallyDefined }
}

// === 静默脚本（运行成功但无 print/图表）的自动汇总 ===
// 这类脚本把结果留在模块级变量里（或只定义类/函数），读者什么都看不到。
// 这里在用户代码执行前后各快照一次 globals，把"新增的模块级名字"自动打印出来，
// 既能给出真实运行结果，也能顺便说明这段代码到底产出了什么。
// 用 inspect.getmodule 检查 __module__ 是否 '__main__',排除 from X import 引入的外部库名字,
// 否则会把 statsmodels 的 ARIMA / adfuller / kpss 等当成"用户定义的类/函数"误报。
const SILENT_EPILOGUE = `
# === Auto-injected summary (脚本本身无 print，自动汇总模块级产物) ===
if True:
    import types as _types
    try:
        import inspect as _inspect
    except Exception:
        _inspect = None
    def _summarize(_v):
        try:
            import numpy as _np, pandas as _pd
            if isinstance(_v, _pd.DataFrame):
                return f"DataFrame shape={_v.shape}\\n{_v.head(6).to_string()}"
            if isinstance(_v, _pd.Series):
                return f"Series shape={_v.shape} name={_v.name}\\n{_v.head(8).to_string()}"
            if isinstance(_v, _np.ndarray):
                _flat = list(_v.reshape(-1)[:10])
                return f"ndarray shape={_v.shape} dtype={_v.dtype} head10={_flat}"
        except Exception:
            pass
        try:
            if isinstance(_v, dict):
                return f"dict n={len(_v)} keys={list(_v.keys())[:12]}"
            if isinstance(_v, (list, tuple)):
                return f"{type(_v).__name__} len={len(_v)}: {repr(_v[:8])}"
            if isinstance(_v, (set, frozenset)):
                return f"{type(_v).__name__} n={len(_v)}: {repr(sorted(_v)[:8])}"
        except Exception:
            pass
        return repr(_v)[:300]
    # 关键修复:排除用户代码里 from/import 引入的外部名字。
    # 仅当 __module__ == '__main__'(用户本文件定义)时才认定为"本段代码定义"，
    # from X import Y 引入的名字 __module__ 是外部库(如 'statsmodels.tsa.arima.model'),
    # 不应该被当作用户定义的类/函数 — 否则会出现"类 ARIMA、函数 adfuller()"这种噪音
    def _is_user_defined(_obj):
        if _inspect is None:
            return True
        try:
            _mod = _inspect.getmodule(_obj)
        except Exception:
            _mod = None
        if _mod is None:
            return True
        _name = getattr(_obj, '__module__', None)
        if _name in ('__main__', None):
            return True
        return False
    _new = sorted(set(globals().keys()) - _QUANTLAB_PRE_NAMES)
    _classes, _funcs, _vals = [], [], []
    for _n in _new:
        if _n.startswith('_'):
            continue
        try:
            _v = globals()[_n]
        except Exception:
            continue
        if isinstance(_v, _types.ModuleType):
            continue
        if isinstance(_v, type):
            if _is_user_defined(_v):
                _classes.append(_n)
        elif isinstance(_v, (_types.FunctionType, _types.BuiltinFunctionType)):
            if _is_user_defined(_v):
                _funcs.append(_n)
        elif callable(_v):
            continue
        else:
            _vals.append((_n, _v))
    _shown = False
    if _classes or _funcs:
        print("本段代码定义：" + "、".join(
            ([f"类 {c}" for c in _classes] + [f"函数 {f}()" for f in _funcs])
        ))
        _shown = True
    for _n, _v in _vals:
        print(f"\\n--- {_n} ({type(_v).__name__}) ---")
        print(_summarize(_v))
        _shown = True
    if not _shown:
        print("（脚本执行完成，未产生可展示的模块级变量或函数定义）")
`

// 统计"用户代码自己打印了多少字符"的 stdout 代理。
// 用途：只有当用户代码完全没有输出时，才追加 scaffold 的自动汇总 / 自动调用结果，
// 避免真实输出后面拖一段 "--- 结果 --- xxx = repr(...)" 噪声。
const STDOUT_TEE = `
# === Auto-injected stdout tee (判断用户代码是否自己有输出) ===
import sys as _ql_sys
class _QLTee:
    def __init__(self, s):
        self._s = s
        self.n = 0
    def write(self, d):
        if d and d.strip():
            self.n += len(d)
        return self._s.write(d)
    def __getattr__(self, k):
        return getattr(self._s, k)
_QL_TEE = _QLTee(_ql_sys.stdout)
_ql_sys.stdout = _QL_TEE
_QL_N1 = 0
`

// 静默（无 print/图表）时的兜底说明：用代码结构描述这段脚本在做什么
function describeSilentScript(codeBody) {
  const lines = codeBody.split(/\r?\n/)
  const defs = []
  const classes = []
  for (const l of lines) {
    let m
    if ((m = l.match(/^class\s+(\w+)/))) classes.push(m[1])
    if ((m = l.match(/^def\s+(\w+)/))) defs.push(m[1])
  }
  const assigns = new Set()
  for (const l of lines) {
    const m = l.match(/^([A-Za-z_]\w*)\s*=[^=]/)
    if (m) assigns.add(m[1])
  }
  const parts = []
  if (classes.length) parts.push(`定义了 ${classes.length} 个类：${classes.map((c) => `\`${c}\``).join('、')}`)
  if (defs.length) parts.push(`${defs.length} 个模块级函数：${defs.map((d) => `\`${d}()\``).join('、')}`)
  if (assigns.size) parts.push(`并计算/装配了 ${assigns.size} 个模块级对象（${[...assigns].slice(0, 8).join('、')}${assigns.size > 8 ? ' 等' : ''}）`)
  if (!parts.length) return '脚本运行成功（无 print 与图表输出，纯配置/状态修改类脚本）'
  return `脚本运行成功：${parts.join('，')}。结果保存在变量/对象中未主动打印，可在本机运行后查看。`
}

// 用同一 env 再跑一次给定源码（用于静默脚本的自动汇总变体）
// 健壮版 spawn：detached 进程组 + 硬性超时保证 resolve。
// Windows 上 python 若派生孙进程并持有 stdout 管道，'close' 事件可能永不触发，
// 导致并发槽被永久占用、预计算卡死。这里：
//  1. detached:true 让子进程成组，超时用 process.kill(-pid) 杀整组；
//  2. 额外的硬性兜底超时（TIMEOUT_MS + 8s）保证 Promise 一定会 resolve，
//     即使 'close' 永远不来也继续推进。
function spawnPy(src, env) {
  return new Promise((resolve) => {
    let stdout = '', stderr = ''
    let settled = false
    const proc = spawn('python3', ['-c', src], {
      env,
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    const finish = (code, timedOut) => {
      if (settled) return
      settled = true
      clearTimeout(soft)
      clearTimeout(hard)
      resolve({ code, stdout, stderr, timedOut: !!timedOut })
    }
    const soft = setTimeout(() => {
      try { proc.kill('SIGKILL') } catch {}
      try { process.kill(-proc.pid, 'SIGKILL') } catch {}
    }, TIMEOUT_MS)
    const hard = setTimeout(() => finish(124, true), TIMEOUT_MS + 8000)
    proc.stdout.on('data', (d) => { stdout += d })
    proc.stderr.on('data', (d) => { stderr += d })
    proc.on('close', (code) => finish(code, false))
    proc.on('error', () => finish(1, false))
  })
}

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
# 常备 numpy/pandas：教学片段常假定上下文已有（重复 import 无害）
import numpy as np, pandas as pd
# typing 常量(M4/M5/M7/M9 常在函数签名里出现,缺了会触发 NameError)
from typing import Tuple, List, Dict, Optional, Any, Callable, Union, Set
# 老 pandas 的 BusinessDay frequency 在 ≥2.2 已弃用,统一用 B (business day)
pd._orig_bday = pd._orig_bday if hasattr(pd, '_orig_bday') else None
try:
    pd.tseries.offsets.BusinessDay  # noqa
except AttributeError:
    import pandas._libs.tslibs.offsets as _off
    _off.BusinessDay = _off.BDay
    pd.tseries.offsets.BusinessDay = _off.BDay
# vectorbt 1.1 + pandas 3.0 兼容:BusinessDay 缺 is_fixed 属性(vectorbt 断言失败)
import pandas._libs.tslibs.offsets as _off2
if not hasattr(_off2.BusinessDay, 'is_fixed'):
    _off2.BusinessDay.is_fixed = True
if not hasattr(_off2.BDay, 'is_fixed'):
    _off2.BDay.is_fixed = True
# 中文字体回退链：优先项目内置的 CJK 字体；找不到就用 matplotlib 自带的 DejaVu + 符号替换
def _find_cjk_font():
    candidates = [
        os.environ.get("QUANTLAB_FONT_PATH"),
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    # matplotlib 内置 fallback
    try:
        from matplotlib import font_manager
        for f in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
            try:
                font_manager.FontProperties(fname=f)
                if any(k in f.lower() for k in ['cjk','noto','wqy','simhei','msyh','pingfang','sourcehan']):
                    return f
            except Exception:
                pass
    except Exception:
        pass
    return None
_cjk = _find_cjk_font()
if _cjk:
    from matplotlib import font_manager
    font_manager.fontManager.addfont(_cjk)
    from matplotlib import rcParams
    rcParams['font.sans-serif'] = [font_manager.FontProperties(fname=_cjk).get_name(), 'DejaVu Sans']
    rcParams['axes.unicode_minus'] = False
_SHOW_COUNT = [0]
def _patched_show(*a, **k):
    n = _SHOW_COUNT[0]
    _SHOW_COUNT[0] += 1
    fname = f"{os.environ['QUANTLAB_OUTPUT_NAME']}-{n}.svg"
    plt.savefig(os.path.join(os.environ['QUANTLAB_SVG_DIR'], fname), bbox_inches="tight")
    plt.close()
plt.show = _patched_show
`

  // 去除 @quantlab/output 标记后取真实代码体
  const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')

  // Insert preamble AFTER any `from __future__` import lines (must be first
  // non-comment statement in the file per Python language spec).
  const futureMatch = codeBody.match(/(?:^|\n)(?:from __future__[^\n]*\n)+/)
  const finalText = futureMatch
    ? codeBody.slice(0, futureMatch.index + futureMatch[0].length) + preamble + codeBody.slice(futureMatch.index + futureMatch[0].length)
    : preamble + codeBody

  // 启发式识别代码片段：
  // 1. 起始行是 def/class/装饰器/参数类型注解（不含 import）
  // 2. OR 代码里有 def 或 class，且没有任何顶层表达式语句（如 fn()、print()、赋值等）
  // 3. OR 代码依赖未声明的变量（df/signal/prices 等）——即使有顶层代码也无意义
  const isPureDefinition = /^\s*(def |class |@|\s+# )/.test(codeBody)
    && !/^\s*(import |from )/m.test(codeBody)
  const hasDefOrClass = /^\s*(def |class )/m.test(codeBody)
  // 检测有 def/class 的代码中是否有真正的模块级调用/赋值/打印等语句
  // 关键：只识别真正的顶层（无缩进）调用。函数体内的 x = ... 不能算
  let hasModuleLevelCall = false
  if (hasDefOrClass) {
    const lines = codeBody.split(/\r?\n/)
    for (const line of lines) {
      // 必须从第 0 列开始（无缩进）才可能是模块级
      if (!/^[^ \t]/.test(line)) continue
      if (/^(def |class |#|from |import |@)/.test(line)) continue
      // 模块级调用：identifier(...) 或 identifier = ... 或 print(...) 或 if __name__ 块
      if (/^[A-Za-z_][A-Za-z0-9_]*\s*[(\s=,]/.test(line)) {
        hasModuleLevelCall = true
        break
      }
    }
  }
  // 第三种情况：代码引用了"约定俗成"的上下文变量（df/signal/prices 等）
  // 即使不在 def 里也应注入 demo 数据
  const needsScaffold = /\b(df|prices|signal|stock1|stock2)\b/.test(codeBody)
    && !/^\s*(df|prices|signal|stock1|stock2)\s*=/m.test(codeBody)
  // 第四种情况：代码极短(<120 字符)、无 def/class/import → 数学公式演示片段(如 continuous[t]=...)
  // 这种不应执行(变量名 t/continuous 等都是伪代码占位符),直接当作 fragment 显示 note
  const hasModuleStructure = /^\s*(import |from |def |class |@)/m.test(codeBody)
  const isMathSnippet = !hasModuleStructure && codeBody.length < 120 && !/\bprint\s*\(/.test(codeBody)
  const isFragment = isPureDefinition || (hasDefOrClass && !hasModuleLevelCall) || needsScaffold || isMathSnippet
  // 纯 def/class 片段（无模块级调用）：不注入 demo 数据；若函数可无参调用则自动调用，否则显示 note
  const isPureDefOnly = hasDefOrClass && !hasModuleLevelCall

  // 对 fragment 自动注入 demo 数据 + 自动调用 def，让"片段"也能跑出真输出
  // 触发条件：
  //   - 非纯 def 片段：依赖上下文变量 → pre 注入 + post 调用
  //   - 纯 def 片段（pureDefMode）：只尝试无参调用（不注入）
  //   - 数学公式演示片段（isMathSnippet）：不注入、不执行,直接当 fragment 显示 note
  let augmentedText = finalText
  let scaffoldUsed = false
  let skipExecution = false  // 标记完全跳过 python 执行(只生成 note)
  // 静默重跑（脚本无 print/图表时自动汇总模块级产物）用的组装件
  let silentText = null
  // 无论是否用 scaffold，都准备好"用户代码之前"的分界点，供静默汇总变体复用
  const _preambleEnd = finalText.indexOf(preamble) + preamble.length
  const _beforeUserCode = finalText.slice(0, _preambleEnd)
  const _userCode = finalText.slice(_preambleEnd)
  if (isMathSnippet) {
    skipExecution = true
  } else {
    const sb = buildScaffold(codeBody, isPureDefOnly)
    const pre = sb?.pre
    const post = sb?.post
    const locallyDefined = sb?.locallyDefined
    if (pre || post) {
      const beforeUserCode = _beforeUserCode
      const userCode = _userCode
      const summaryVars = [...(locallyDefined || [])].filter(v => /^\s*[a-z_]/.test(v))
      // summaryPrint 必须在 outer try 内（缩进 4）
      // 只有在「用户代码自己什么都没打印」时才追加 scaffold 汇总，避免污染真实输出
      // summaryPrint 必须在 outer try 内（缩进 4）。
      // 跳过 matplotlib 图表对象（已在 SVG 中渲染,repr 无意义且噪音大）：
      //   - 用 type(_x).__module__.startswith('matplotlib') 兜底
      //   - 额外判 Figure/Aaxes 直接类型检查(双保险,避免某些后端类型的 module 异常)
      // 其余逻辑保持兼容（pandas tail/head、短集合 repr、长 repr 截断 200 字符）。
      const summaryPrint = '    # === Scaffold summary ===\n' +
        '    _QL_N1 = _QL_TEE.n\n' +
        '    if _QL_N1 == 0:\n' +
        '        print("--- 结果 ---")\n' +
        '        try:\n' +
        '            import matplotlib.figure as _mfig, matplotlib.axes as _maxs\n' +
        '            _MPL_TYPES = (_mfig.Figure, _maxs.Axes)\n' +
        '        except Exception:\n' +
        '            _MPL_TYPES = ()\n' +
        (summaryVars.length > 0
          ? '        for _v in [' + summaryVars.map(v => `'${v}'`).join(',') + ']:\n' +
            '            try:\n                _x = eval(_v)\n' +
            '                if isinstance(_x, _MPL_TYPES):\n' +
            '                    continue\n' +
            '                _tmod = type(_x).__module__\n' +
            '                if _tmod.startswith("matplotlib") or _tmod.startswith("mpl_toolkits"):\n' +
            '                    continue\n' +
            '                if hasattr(_x, "_repr_html_"):\n' +
            '                    continue\n' +
            '                # 数组/列表里的元素若全是 matplotlib 对象(常见于 subplots 返回的 ndarray),整体跳过\n' +
            '                if hasattr(_x, "__iter__") and not isinstance(_x, (str, bytes, dict)):\n' +
            '                    try:\n' +
            '                        _els = list(_x)\n' +
            '                        if _els and all((type(_e).__module__.startswith("matplotlib") or type(_e).__module__.startswith("mpl_toolkits")) for _e in _els):\n' +
            '                            continue\n' +
            '                    except Exception:\n' +
            '                        pass\n' +
            '                if hasattr(_x, "tail"): print(_v + " tail():", _x.tail().to_string())\n' +
            '                elif hasattr(_x, "head"): print(_v + " head():", _x.head().to_string())\n' +
            '                elif hasattr(_x, "__len__") and len(_x) < 20: print(_v + " =", repr(_x))\n' +
            '                else: print(_v + " =", repr(_x)[:200])\n' +
            '            except Exception: pass\n'
          : '        pass\n')
      const wrappedUserCode = 'try:\n' + userCode.split('\n').map(l => '    ' + l).join('\n') + summaryPrint +
        'except Exception as _e:\n    _QL_N1 = _QL_TEE.n\n    print(f"⚠ 末尾操作失败: {_e}")\n'
      // 关键修复：post（自动调用 def）放在用户代码之后，def 才会注册到模块作用域
      const preBlock = (pre ? '\n# === Auto-injected scaffold (pre: demo data) ===\n' + pre + '\n' : '') + STDOUT_TEE
      const postBlock = post
        ? '\n# === Auto-injected scaffold (post: def calls) ===\nif _QL_N1 == 0:\n' +
          post.split('\n').map(l => '    ' + l).join('\n') + '\n'
        : ''
      augmentedText = beforeUserCode + preBlock + wrappedUserCode + postBlock
      // 静默变体：在 scaffold 之后、用户代码之前快照 globals，末尾追加自动汇总
      silentText = beforeUserCode + preBlock +
        '\n_QUANTLAB_PRE_NAMES = set(globals().keys())\n' +
        wrappedUserCode + postBlock + SILENT_EPILOGUE
      scaffoldUsed = true
    }
  }
  // 无 scaffold 的独立脚本同样支持静默汇总：快照放在用户代码之前
  if (!silentText && !skipExecution) {
    silentText = _beforeUserCode +
      '\n_QUANTLAB_PRE_NAMES = set(globals().keys())\n' +
      _userCode + SILENT_EPILOGUE
  }

  return new Promise(async (resolve) => {
    // 数学公式演示片段直接跳过 python 执行,返回 note
    if (skipExecution) {
      const payload = { text: '', svgs: [], note: '本段为公式演示片段（伪代码占位符，无完整上下文）' }
      await writeFile(
        path.join(CODE_DIR, `${name}.output.json`),
        JSON.stringify(payload, null, 2),
      )
      return resolve({ name, file: path.basename(pyFile), code: 0, len: 0 })
    }
    const r = await spawnPy(augmentedText, env)
    let code = r.code
    let stdout = r.stdout
    let stderr = r.stderr
    if (r.timedOut) {
      const payload = { text: '', svgs: [], note: `本段运行超时（>${TIMEOUT_MS / 1000}s），已在预计算中跳过（不阻塞页面）` }
      await writeFile(
        path.join(CODE_DIR, `${name}.output.json`),
        JSON.stringify(payload, null, 2),
      )
      return resolve({ name, file: path.basename(pyFile), code: 124, len: 0 })
    }
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
      let text = stdout.trim()

      // === 静默脚本自动汇总 ===
      // 运行成功但既没有 print 也没有图表（结果留在模块级变量里 / 只定义了类与函数），
      // 重跑一次带"模块级产物汇总"的变体，让读者看到真实结果而不是一句空提示。
      if (code === 0 && !text && (!svgs || svgs.length === 0) && silentText) {
        const r = await spawnPy(silentText, env)
        if (r.code === 0 && r.stdout.trim().length > 10) {
          const rText = r.stdout.trim()
          // 关键修复:SILENT_EPILOGUE 在用户代码只 def 不调用时,会输出形如
          // "本段代码定义：函数 xxx()" + 空 — 这是名字罗列,无任何数值结果,
          // 直接展示只会让读者更困惑("这代码到底干了啥?"),并且 131 个 fence 全落
          // 这种模式(查 2026-09-07)。剔除掉,改走下方 isFragment 的 note 路径
          // (组件会渲染蓝色"📘 本段代码定义了 N 个函数/类:函数 X(描述)..."),
          // 既说明白代码意图,又不会留裸字符串噪音。
          const looksLikeNameListing =
            /^本段代码定义：/.test(rText) &&
            !/^--- .+ \(/.test(rText) &&           // 没有"--- name (type) ---"数值块
            !/^--- 结果 ---/m.test(rText)            // 没有"--- 结果 ---"自动摘要
          if (!looksLikeNameListing) {
            text = rText
            stdout = r.stdout
            code = r.code
            try {
              const files = await readdir(svgDir)
              svgs = files.filter((f) => f.endsWith('.svg')).sort()
                .map((f) => `/code/${name}.svgs/${f}`)
            } catch (e) { /* ignore */ }
          }
        }
      }

      const hasNameError = /NameError/.test(stderr)
      const moduleMissing = /ModuleNotFoundError|ImportError/.test(stderr)
      // 关键修复:即使有"末尾操作失败"输出,只要错误本质是 NameError 或缺模块,
      // 也应该归类为 NameError/moduleMissing 显示 note — 避免展示 raw traceback
      const wrappedErrorMatch = text.match(/⚠\s*末尾操作失败:\s*(.+?)$/m)
      const wrappedError = wrappedErrorMatch ? wrappedErrorMatch[1].trim() : null
      // 拓展识别:NameError / AttributeError(包含 ndarray 无属性)/ shape mismatch / truth value / KeyError / 不支持操作符 / 子集长度
      // 这些都属于"代码片段上下文不足"或"scaffold 注入类型不对",统一归为 note
      // 追加: vectorbt numba 类型错误 / numba typing 错误 / scalar 索引错误 / dead code 片段
      const wrappedIsNameError = wrappedError && /NameError|is not defined|has no attribute|object has no|attribute.*no attribute|object is not|cannot unpack|truth value.*ambiguous|operands could not be broadcast|only integers.*slices|Dot product|IndexError|KeyError|Unable to coerce|Invalid classes inferred|only 0-dimensional|non-fixed frequency|non-finite|ufunc|setting.*array.*element|nopython|non-precise type|numba|invalid index to scalar|does not support|^0$|^0\.\d+$|maximum supported dimension|UnboundLocalError|^\d+$|Free var|may be undefined|name '.*' is not defined|operands.*broadcast/i.test(wrappedError)
      const wrappedIsModuleMissing = wrappedError && /No module named|ModuleNotFoundError|ImportError/.test(wrappedError)
      // === 已产出图表时，丢弃 scaffold 自动变量摘要 ===
      let strippedSummary = false
      // summaryPrint 在用户代码无 print 时会自动 eval 模块级变量并打印
      // （"--- 结果 ---" + `name = repr`）。若本次运行已产出图表，这些变量多半是
      // 绘图原料与 for 循环末态值（idx / size / angles / colors_radar / ...），
      // 对读者是纯噪音 —— 图本身已完整表达结果，直接丢弃文字只留图表。
      // 注意：仅丢弃"自动摘要"；用户自己 print 的内容不受影响（不以该分隔符开头）。
      if (svgs && svgs.length > 0 && text.trim().startsWith('--- 结果 ---')) {
        text = ''
        strippedSummary = true
      }

      // 有真实输出（print/图）则优先保留 — 但如果 wrap 错误是 NameError/AttributeError 等,
      // 即使 text 非空也只是 "⚠ 末尾操作失败:..." + 空调用结果,应归 note 而非 raw 文本
      const hasRealOutput = !!(text || (svgs && svgs.length > 0))
      const wrappedIsFatal = wrappedError && (wrappedIsNameError || wrappedIsModuleMissing)
      // 特殊:numba/vectorbt 编译错误 → 视为"片段代码,需要外部数据,无法独立运行"
      const wrappedIsNumbaError = wrappedError && /nopython|numba.*pipeline|nopython mode|non-precise type|TypingError|CompileError/i.test(wrappedError)
      // text 中除了"末尾操作失败"那行,是否还有别的实质性输出(>30 字符)?否则不算有真实输出
      const textExcludingWrap = wrappedError ? text.replace(/⚠\s*末尾操作失败:.*\n?/, '').trim() : text
      const hasUsefulText = textExcludingWrap.length > 30
      // 有图表即算"有产出"。仅在 strippedSummary 时放宽：上面可能已把自动变量摘要
      // 清空（text 变空），此时不能因为 hasUsefulText 为 false 就掉进 isFragment
      // 分支冒出 "仅展示函数/类定义" 的误报 note —— 图本身就是运行结果。
      // 限定 strippedSummary 避免误伤其他带图 fence（如缺模块时仍需保留提示）。
      const hasVisual = !!(svgs && svgs.length > 0) && strippedSummary
      // 如果 stderr 有内容且 text 主要就是 wrap 的 "末尾操作失败" 那行 → text 不可信,优先看 stderr
      const stderrClean = (stderr || '').trim().slice(0, 500)
      const payload = (hasRealOutput && !wrappedIsFatal && (hasUsefulText || hasVisual) && code === 0)
        ? { text, svgs }
        : isFragment
          ? { text: '', svgs, note: '本段为代码片段（仅展示函数/类定义，未提供运行入口，无需运行）' }
          : (wrappedIsNameError || hasNameError)
            ? { text: '', svgs, note: '本段为代码片段（依赖上文变量或外部输入，如 df/data/参数等），无法独立运行' }
            : (wrappedIsModuleMissing || moduleMissing)
              ? (() => {
                  let mod = '未知'
                  if (wrappedError) {
                    const m = wrappedError.match(/No module named ['"]([^'"]+)['"]?/)
                    if (m) mod = m[1]
                  } else {
                    const m = stderr.match(/(?:ModuleNotFoundError|ImportError):\s*No module named '([^']+)'/)
                    if (m) mod = m[1]
                  }
                  return { text: '', svgs, note: `本脚本依赖外部模块 \`${mod}\`（未在预计算环境安装，无法独立运行；安装后可重跑 precompute）` }
                })()
              : hasRealOutput && code === 0 && !wrappedIsFatal
                ? { text, svgs }
                : wrappedIsNumbaError
                  ? { text: '', svgs, note: '本段依赖 numba JIT 编译环境(vectorbt 等),代码片段无法独立运行' }
                  : hasUsefulText && code !== 0 && stderrClean
                    ? { text, svgs, error: stderrClean }
                    : code === 0 && !text && (!svgs || svgs.length === 0)
                      ? { text: '', svgs, note: describeSilentScript(codeBody) }
                      : code !== 0 && stderrClean
                        ? { text: textExcludingWrap || text || '', svgs, error: stderrClean }
                        : code === 0
                          ? { text, svgs }
                          : { text: textExcludingWrap || text || '', svgs, error: stderrClean }
      await writeFile(
        path.join(CODE_DIR, `${name}.output.json`),
        JSON.stringify(payload, null, 2),
      )
      resolve({ name, file: path.basename(pyFile), code, len: stdout.length })
  })
}

async function main() {
  // 递归匹配所有 .py（含 _auto/）
  const files = []
  try {
    for await (const f of glob('public/code/**/*.py', { exclude: [
      'public/code/_auto/*.svgs/**',
      'public/code/_auto.bak*/**',
      'public/code/_auto.bak*',
    ] })) files.push(f)
  } catch (e) {
    console.error(`[precompute] glob failed: ${e.message}`)
    process.exit(0)
  }
  console.log(`[precompute] ${files.length} files, concurrency=${CONCURRENCY}, timeout=${TIMEOUT_MS}ms`)

  // 仅重跑指定文件（逗号分隔的 name/hash，不含扩展名）：PRECOMPUTE_ONLY="h1,h2"
  const onlyEnv = process.env.PRECOMPUTE_ONLY
  if (onlyEnv) {
    const only = new Set(onlyEnv.split(',').map((s) => s.trim()).filter(Boolean))
    const before = files.length
    for (let i = files.length - 1; i >= 0; i--) {
      const base = path.basename(files[i], '.py')
      if (!only.has(base)) files.splice(i, 1)
    }
    console.log(`[precompute] PRECOMPUTE_ONLY → ${files.length}/${before} files`)
  }

  // 自动安装缺失的常见模块（best-effort，不阻塞 precompute）
  // 默认关闭（环境网络常 timeout）；开启：set PRECOMPUTE_INSTALL=1
  if (process.env.PRECOMPUTE_INSTALL === '1') {
    await ensureModulesInstalled(files)
  } else {
    console.log(`[precompute] module auto-install skipped (set PRECOMPUTE_INSTALL=1 to enable)`)
  }

  let done = 0, failed = 0, skipped = 0
  const tasks = files.map((f) => limit(async () => {
    const r = await runOne(f)
    done++
    if (r.skipped) skipped++
    else if (r.code !== 0) failed++
    if (done % 25 === 0 || done === files.length) {
      const pct = ((done / files.length) * 100).toFixed(1)
      console.log(`[precompute] ${done}/${files.length} (${pct}%) — failed=${failed} skipped=${skipped}`)
    }
    return r
  }))
  await Promise.all(tasks)
  console.log(`[precompute] DONE: ${files.length - failed - skipped}/${files.length} succeeded, ${failed} failed, ${skipped} skipped`)
  process.exit(0)
}

// 仅当直接调用本脚本(而非 import)时才跑 main(),便于复用 runOne
// 修复:path.resolve 规范化 argv[1],避免相对路径比较失败导致 main() 静默不执行
const _mainPath = fileURLToPath(import.meta.url).replace(/\\/g, '/')
const _argvPath = process.argv[1] ? path.resolve(process.argv[1]).replace(/\\/g, '/') : ''
if (process.argv[1] && _mainPath === _argvPath) {
  main().catch((e) => {
    console.error('[precompute] fatal:', e)
    process.exit(0)
  })
}

export { runOne, buildScaffold }