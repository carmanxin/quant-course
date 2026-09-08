// 直接 import 预计算脚本并模拟 production flow
import('/d:/AI/study/quant/scripts/precompute-py-outputs.mjs').catch(console.error);

// inline 模拟 runOne 的 augmentedText 生成
import { readFile } from 'node:fs/promises'

const fs = await import('node:fs/promises')
const text = await fs.readFile('public/code/_auto/2ab5dad7.py', 'utf8')
const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')

// 直接复制 production 代码片段
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
  for (const name of [...used].sort()) {
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
    } else {
      lines.push(`${name} = np.random.randn(100)`)
    }
  }
  return { scaffold: lines.join('\n'), locallyDefined }
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

const finalText = preamble + codeBody
const { scaffold, locallyDefined } = buildScaffold(codeBody) || {}
console.log('scaffold:', scaffold?.slice(0, 200))
console.log('locallyDefined:', [...(locallyDefined || [])])

if (scaffold) {
  const preambleEnd = finalText.indexOf(preamble) + preamble.length
  const beforeUserCode = finalText.slice(0, preambleEnd)
  const userCode = finalText.slice(preambleEnd)
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
  console.log(augmentedText.slice(0, 1500))
  console.log('...')
}