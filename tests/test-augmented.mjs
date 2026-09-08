import { spawn } from 'node:child_process'

// Build the same augmentedText the production code would build
const text = await import('node:fs/promises').then(fs => fs.readFile('public/code/_auto/2ab5dad7.py', 'utf8'))
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

// Inline buildScaffold
const declared = new Set()
for (const line of codeBody.split(/\r?\n/)) {
  let mm
  if ((mm = line.match(/^\s*def\s+(\w+)/))) declared.add(mm[1])
  if ((mm = line.match(/^\s*class\s+(\w+)/))) declared.add(mm[1])
  if ((mm = line.match(/^\s*import\s+(\w+)/))) declared.add(mm[1])
}
const ignore = new Set(['print','True','False','None','and','or','not','in','is','for','while','if','elif','else','try','except','finally','raise','with','from','import','def','class','return','global','nonlocal','assert','del','break','continue','async','await','lambda','pass','yield'])
const used = new Set()
const locallyDefined = new Set()
for (const line of codeBody.split(/\r?\n/)) {
  if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(line)) continue
  const eqMatch = line.match(/^([^=]*?)=(?!=)/)
  if (eqMatch) {
    const lhsStripped = eqMatch[1].replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""')
    for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1]
      if (!ignore.has(id)) locallyDefined.add(id)
    }
  }
  let rhs = eqMatch ? line.slice(eqMatch[0].length) : line
  rhs = rhs.replace(/"""[\s\S]*?"""/g, '""').replace(/'''[\s\S]*?'''/g, "''")
  rhs = rhs.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''")
  rhs = rhs.replace(/\b\w+(?=\s*\()/g, '')
  for (const m of rhs.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
    const id = m[1]
    if (!declared.has(id) && !locallyDefined.has(id) && !ignore.has(id)) {
      used.add(id)
    }
  }
}
console.log('used:', [...used])

// Build scaffold
const lines = ['import numpy as np, pandas as pd', 'np.random.seed(42)']
for (const name of [...used].sort()) {
  const lower = name.toLowerCase()
  if (lower === 'df') {
    lines.push(`${name} = pd.DataFrame({"Close": 100 + np.cumsum(np.random.randn(252)*0.02)})`)
  } else {
    lines.push(`${name} = np.random.randn(100)`)
  }
}
const scaffold = lines.join('\n')

const preambleEnd = preamble.length
const userCode = codeBody
const wrappedUserCode = 'try:\n' + userCode.split('\n').map(l => '    ' + l).join('\n') + '\nexcept Exception as _e:\n    print(f"⚠ 末尾操作失败: {_e}")\n'

const augmentedText = preamble + '\n# === Auto-injected scaffold ===\n' + scaffold + '\n' + wrappedUserCode

console.log('--- augmentedText ---')
console.log(augmentedText)

console.log('--- 跑 python ---')
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
  console.log('stdout:', stdout)
  console.log('stderr:', stderr.slice(0, 300))
})