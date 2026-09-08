import { readFile } from 'node:fs/promises'

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
  const locallyDefined = new Set() // LHS of previous assignments
  for (const line of codeBody.split(/\r?\n/)) {
    if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(line)) continue
    // 先收集本行的 LHS（赋值目标）作为已定义
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
    // 剥离字符串字面量 + funcall 名字
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
  console.log('used:', [...used])
  if (used.size === 0) return null
  const lines = []
  lines.push('import numpy as np, pandas as pd')
  lines.push('np.random.seed(42)')
  for (const name of used) {
    const lower = name.toLowerCase()
    if (lower === 'df' || lower.startsWith('df_')) {
      lines.push(`${name} = pd.DataFrame({"Close": 100 + np.cumsum(np.random.randn(252)*0.02)})`)
    } else {
      lines.push(`${name} = np.random.randn(100)`)
    }
  }
  return lines.join('\n')
}

const text = await readFile('public/code/_auto/2ab5dad7.py', 'utf8')
const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
console.log('--- codeBody ---')
console.log(codeBody)
console.log('--- scaffold ---')
console.log(buildScaffold(codeBody))