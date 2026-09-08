import fs from 'node:fs'
import path from 'node:path'

function fnv1a(str) {
  let h = 0x811c9dc5
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}
function normalizeCode(raw) {
  return raw
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+$/gm, '')
    .trim()
}

function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const files = walk('guide')
const hashCount = new Map()
let totalFences = 0
for (const f of files) {
  const md = fs.readFileSync(f, 'utf8')
  const lines = md.split('\n')
  let inFence = false, lang = '', buf = []
  for (const line of lines) {
    if (!inFence && /^```/.test(line)) {
      inFence = true
      lang = line.replace(/^```/, '').trim()
      buf = []
    } else if (inFence && /^```\s*$/.test(line)) {
      inFence = false
      if (['python', 'py'].includes(lang)) {
        totalFences++
        const norm = normalizeCode(buf.join('\n'))
        const h = fnv1a(norm)
        hashCount.set(h, (hashCount.get(h) || 0) + 1)
      }
    } else if (inFence) buf.push(line)
  }
}
console.log('guide files:', files.length)
console.log('total python fences:', totalFences)
console.log('unique hashes:', hashCount.size)
console.log('duplicates:', totalFences - hashCount.size)
const sorted = [...hashCount.entries()].sort((a, b) => b[1] - a[1])
console.log('top 10 most-duplicated:')
sorted.slice(0, 10).forEach(([h, n]) => console.log(`  ${h}: ${n} times`))

// 对比 _index.json
const idx = JSON.parse(fs.readFileSync('public/code/_index.json', 'utf8'))
console.log('\n_index.json size:', Object.keys(idx).length)
const matched = [...hashCount.keys()].filter((h) => idx[h]).length
console.log('matched in _index.json:', matched)
console.log('unmatched:', hashCount.size - matched)