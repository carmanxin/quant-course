// 直接用 precompute 脚本里的 runOne 跑 2ab5dad7 看输出
// import 整个脚本然后调用

// 用 spawn python 直接跑 augmentedText（手工构造）
import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'

const text = await readFile('public/code/_auto/2ab5dad7.py', 'utf8')
const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')

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

// inline buildScaffold (copy from production)
function buildScaffold(codeBody) {
  const declared = new Set()
  for (const line of codeBody.split(/\r?\n/)) {
    let mm
    if ((mm = line.match(/^\s*def\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^\s*class\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^\s*import\s+(\w+)/))) declared.add(mm[1])
    if ((mm = line.match(/^\s*from\s+[\w.]+\s+import\s+([\w,\s]+)/))) {
      for (const tok of mm[1].split(',')) {
        const t = tok.trim().split(/\s+as\s+/).pop()
        if (t && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t)
      }
    }
  }
  const ignore = new Set([
    'print','len','range','int','float','str','list','dict','set','tuple','bool',
    'True','False','None','self','cls','return','yield','pass','lambda',
    'np','pd','plt','sns','yf','nx','math','os','sys','json','csv','re','time',
    'datetime','timedelta','coint','adfuller','stats','scipy','numpy',
    'pandas','matplotlib','sklearn','torch','warnings',
    'and','or','not','in','is','for','while','if','elif','else','try','except',
    'finally','raise','with','from','import','def','class','return','global',
    'nonlocal','assert','del','break','continue','async','await',
  ])
  const used = new Set()
  const locallyDefined = new Set()
  for (const line of codeBody.split(/\r?\n/)) {
    if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(line)) continue
    const eqMatch = line.match(/^([^=]*?)=(?!=)/)
    if (eqMatch) {
      const lhsStripped = eqMatch[1].replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""')
      for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
        const id = m[1]
        if (ignore.has(id)) continue
        locallyDefined.add(id)
      }
    }
    let rhs = eqMatch ? line.slice(eqMatch[0].length) : line
    rhs = rhs.replace(/"""[\s\S]*?"""/g, '""').replace(/'''[\s\S]*?'''/g, "''")
    rhs = rhs.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''")
    rhs = rhs.replace(/\b\w+(?=\s*\()/g, '')
    for (const m of rhs.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1]
      if (declared.has(id)) continue
      if (locallyDefined.has(id)) continue
      if (ignore.has(id)) continue
      if (!used.has(id)) used.add(id)
    }
  }
  if (used.size === 0) return null
  const lines = ['import numpy as np, pandas as pd', 'np.random.seed(42)']
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
      lines.push(`${name} = pd.DataFrame({`)
      lines.push(`    "Open":   100 + np.cumsum(np.random.randn(252)*0.02),`)
      lines.push(`    "High":   100 + np.cumsum(np.random.randn(252)*0.02) + np.abs(np.random.randn(252)*0.5),`)
      lines.push(`    "Low":    100 + np.cumsum(np.random.randn(252)*0.02) - np.abs(np.random.randn(252)*0.5),`)
      lines.push(`    "Close":  100 + np.cumsum(np.random.randn(252)*0.02),`)
      lines.push(`    "Volume": np.random.randint(1_000_000, 10_000_000, 252),`)
      lines.push(`    "signal": np.random.choice([0, 1], size=252),`)
      lines.push(`})`)
      lines.push(`${name}.index = pd.date_range("2024-01-01", periods=252)`)
    } else if (lower === 'signal' || lower === 'df_signal' || lower.startsWith('signal_') || lower.endsWith('_signal')) {
      lines.push(`${name} = np.random.choice([0, 1], size=252)`)
    } else if (lower === 'prices' || lower.startsWith('prices_') || lower === 'price' || lower.startsWith('price_')) {
      lines.push(`${name} = 100 + np.cumsum(np.random.randn(252)*0.02)`)
    } else if (lower === 'prices_df' || lower === 'stock_prices' || lower.includes('price_df')) {
      lines.push(`${name} = pd.DataFrame(100 + np.cumsum(np.random.randn(252,5)*0.02, axis=0), columns=[f"S{i}" for i in range(5)])`)
    } else if (lower === 'returns' || lower === 'strategy_returns' || lower === 'market_returns' || lower.endsWith('_returns')) {
      // depends on df - skip
    } else if (lower === 'positions' || lower.startsWith('positions_')) {
      lines.push(`${name} = np.random.choice([-1, 0, 1], size=252).astype(float)`)
    } else if (lower.includes('hedge') || lower.includes('beta')) {
      lines.push(`${name} = np.random.uniform(0.5, 1.5, size=100)`)
    } else if (lower === 'x' || lower === 'y' || /^x_\d+$/.test(lower) || /^y_\d+$/.test(lower)) {
      lines.push(`${name} = np.random.randn(252)`)
    } else if (lower === 'stock1' || lower === 'stock2') {
      lines.push(`${name} = 100 + np.cumsum(np.random.randn(252)*0.02)`)
    } else {
      lines.push(`${name} = np.random.randn(100)`)
    }
  }
  return { scaffold: lines.join('\n'), locallyDefined }
}

// Detect isFragment
const isPureDefinition = /^\s*(def |class |@|\s+# )/.test(codeBody) && !/^\s*(import |from )/m.test(codeBody)
const hasDefOrClass = /^\s*(def |class )/m.test(codeBody)
const needsScaffold = /\b(df|prices|signal|stock1|stock2)\b/.test(codeBody) && !/^\s*(df|prices|signal|stock1|stock2)\s*=/m.test(codeBody)
const isFragment = isPureDefinition || (hasDefOrClass && false) || needsScaffold
console.log('isFragment:', isFragment, 'needsScaffold:', needsScaffold)

const sb = buildScaffold(codeBody)
console.log('scaffold returned:', !!sb, 'len:', sb?.scaffold?.length)

if (isFragment && sb?.scaffold) {
  const scaffold = sb.scaffold
  const locallyDefined = sb.locallyDefined
  const preambleEnd = preamble.length
  const beforeUserCode = preamble
  const userCode = codeBody
  const summaryVars = [...(locallyDefined || [])].filter(v => /^\s*[a-z_]/.test(v))
  console.log('summaryVars:', summaryVars)
  const summaryPrint = '\n# === Scaffold summary ===\n' +
    'print("--- 结果 ---\")\n' +
    (summaryVars.length > 0
      ? 'for _v in [' + summaryVars.map(v => `'${v}'`).join(',') + ']:\n' +
        '    try:\n        _x = eval(_v)\n' +
        '        if hasattr(_x, "tail"): print(_v + " tail():", _x.tail().to_string())\n' +
        '        elif hasattr(_x, "head"): print(_v + " head():", _x.head().to_string())\n' +
        '        elif hasattr(_x, "__len__") and len(_x) < 20: print(_v + " =", repr(_x))\n' +
        '        else: print(_v + " =", repr(_x)[:200])\n' +
        '    except Exception: pass\n'
      : 'pass\n')
  const wrappedUserCode = 'try:\n' + userCode.split('\n').map(l => '    ' + l).join('\n') + summaryPrint + 'except Exception as _e:\n    print(f"⚠ 末尾操作失败: {_e}")\n'
  const augmentedText = beforeUserCode + '\n# === Auto-injected scaffold ===\n' + scaffold + '\n' + wrappedUserCode

  console.log('--- augmentedText ---')
  console.log(augmentedText)
  console.log('---')

  // Run it
  const proc = spawn('python3', ['-c', augmentedText], {
    env: {
      ...process.env,
      MPLBACKEND: 'svg',
      QT_QPA_PLATFORM: 'offscreen',
      PYTHONUNBUFFERED: '1',
      QUANTLAB_SVG_DIR: '/tmp/svg-test',
      QUANTLAB_OUTPUT_NAME: '2ab5dad7',
    }
  })
  let stdout = '', stderr = ''
  proc.stdout.on('data', d => stdout += d)
  proc.stderr.on('data', d => stderr += d)
  proc.on('close', code => {
    console.log('exit:', code)
    console.log('stdout:')
    console.log(stdout)
    console.log('stderr:', stderr.slice(0, 300))
  })
}