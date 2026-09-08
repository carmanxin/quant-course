import { readFileSync } from 'node:fs'

const text = readFileSync('public/code/_auto/2ab5dad7.py', 'utf8')
const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')

const declared = new Set()
for (const line of codeBody.split(/\r?\n/)) {
  let mm
  if ((mm = line.match(/^\s*def\s+(\w+)/))) declared.add(mm[1])
  if ((mm = line.match(/^\s*class\s+(\w+)/))) declared.add(mm[1])
  if ((mm = line.match(/^\s*import\s+(\w+)/))) declared.add(mm[1])
}
console.log('declared:', [...declared])

const ignore = new Set(['print','True','False','None'])
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
console.log('locallyDefined:', [...locallyDefined])