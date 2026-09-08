#!/usr/bin/env node
// scripts/_probe.mjs
// 用法: node scripts/_probe.mjs <md相对路径> [关键字]
// 列出该 md 中所有 python fence 的 hash / 首行，命中关键字的运行并打印 output.json
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { runOne } from './precompute-py-outputs.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')

function fnv1a(str) {
  let h = 0x811c9dc5
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}
function normalizeCode(raw) {
  return raw.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n').replace(/[ \t]+$/gm, '').trim()
}
function extractFences(md) {
  const fences = []
  const lines = md.split('\n')
  let inFence = false, lang = '', buf = [], start = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (!inFence && /^```/.test(line)) {
      inFence = true; lang = line.replace(/^```/, '').trim(); buf = []; start = i
    } else if (inFence && /^```\s*$/.test(line)) {
      inFence = false
      if (['python', 'py'].includes(lang)) fences.push({ code: buf.join('\n'), line: start + 1 })
    } else if (inFence) buf.push(line)
  }
  return fences
}

const mdRel = process.argv[2]
const kw = process.argv[3] || ''
const md = await readFile(path.join(ROOT, mdRel), 'utf8')
const fences = extractFences(md)

console.log(`== ${mdRel}: ${fences.length} python fences ==`)
const targets = []
fences.forEach((f, i) => {
  const hash = fnv1a(normalizeCode(f.code))
  const head = f.code.split('\n').filter(l => l.trim()).slice(0, 2).join(' | ').slice(0, 80)
  const hit = !kw || new RegExp(kw).test(f.code) || new RegExp(kw).test(md.slice(Math.max(0, md.split('\n').slice(0, f.line).join('\n').lastIndexOf('###')), 0) )
  console.log(`  [${i}] L${f.line} ${hash}  ${head}`)
  if (hit) targets.push({ i, hash, line: f.line })
})

if (targets.length && targets.length <= fences.length) {
  for (const t of targets) {
    const pyFile = path.join(ROOT, 'public/code/_auto', `${t.hash}.py`)
    console.log(`\n>>> RUN fence[${t.i}] L${t.line} ${t.hash}`)
    await runOne(pyFile)
    const out = await readFile(path.join(ROOT, 'public/code', `${t.hash}.output.json`), 'utf8')
    console.log(JSON.stringify(JSON.parse(out), null, 2).slice(0, 3000))
  }
}
