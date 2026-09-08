#!/usr/bin/env node
// scripts/_find-hash-md.mjs
import fs from 'node:fs'
import path from 'node:path'

const TARGET = process.argv.slice(2)

function fnv1a(str) {
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

for (const t of TARGET) {
  console.log(t, '->', hashToMd[t] || 'NOT FOUND')
}