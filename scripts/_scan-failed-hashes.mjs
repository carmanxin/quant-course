#!/usr/bin/env node
// scripts/_scan-failed-hashes.mjs (临时)
import fs from 'node:fs'
import path from 'node:path'

const fnv1a = (str) => {
  let h = 0x811c9dc5
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}
const walk = (dir) => {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}
const normalize = (raw) =>
  raw
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+$/gm, '')
    .trim()

const mdFiles = walk('guide')
const hashToMd = {}
for (const f of mdFiles) {
  const text = fs.readFileSync(f, 'utf8')
  const lines = text.split('\n')
  let inFence = false, lang = '', buf = []
  for (const line of lines) {
    if (!inFence && /^```/.test(line)) {
      inFence = true; lang = line.replace(/^```/, '').trim(); buf = []
    } else if (inFence && /^```\s*$/.test(line)) {
      inFence = false
      if (['python', 'py'].includes(lang)) {
        const code = buf.join('\n')
        const h = fnv1a(normalize(code))
        hashToMd[h] = f
      }
    } else if (inFence) buf.push(line)
  }
}

const out = {}
for (const fn of fs.readdirSync('public/code')) {
  if (fn.endsWith('.output.json')) {
    const h = fn.replace('.output.json', '')
    try {
      const t = fs.readFileSync(path.join('public/code', fn), 'utf8')
      if (t.includes('末尾操作失败')) {
        out[h] = hashToMd[h] || '?'
      }
    } catch (e) {}
  }
}

const modCount = {}
const hashByMod = {}
for (const [h, md] of Object.entries(out)) {
  const m = md.match(/(m\d+-\w+)/)
  const mod = m ? m[1] : md
  modCount[mod] = (modCount[mod] || 0) + 1
  ;(hashByMod[mod] = hashByMod[mod] || []).push(h)
}
console.log('Total fails:', Object.keys(out).length)
console.log('--- by module ---')
for (const [m, n] of Object.entries(modCount).sort()) {
  console.log(`${m}: ${n}`)
  console.log('  hashes:', hashByMod[m].join(' '))
}
const orphans = Object.entries(out).filter(([, md]) => md === '?').map(([h]) => h)
console.log('--- orphan ---', orphans)
fs.writeFileSync('scripts/_failed-hashes.json', JSON.stringify(out, null, 2))
fs.writeFileSync('scripts/_failed-hashes-by-mod.json', JSON.stringify(hashByMod, null, 2))