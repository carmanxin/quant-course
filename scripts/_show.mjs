#!/usr/bin/env node
// scripts/_show.mjs <md相对路径>
// 只列出该 md 中所有 python fence 的 hash / 首行 / 已有 output.json 摘要（不执行）
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

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

const idx = JSON.parse(await readFile(path.join(ROOT, 'public/code/_index.json'), 'utf8'))
const full = process.argv.includes('--full')
for (const mdRel of process.argv.slice(2).filter(a => !a.startsWith('--'))) {
  const md = await readFile(path.join(ROOT, mdRel), 'utf8')
  const fences = extractFences(md)
  console.log(`\n== ${mdRel}: ${fences.length} python fences ==`)
  for (let i = 0; i < fences.length; i++) {
    const f = fences[i]
    const hash = fnv1a(normalizeCode(f.code))
    const name = idx[hash] || hash
    const head = f.code.split('\n').filter(l => l.trim())[0]?.slice(0, 60) || ''
    let summary = '(no output.json)'
    try {
      const o = JSON.parse(await readFile(path.join(ROOT, 'public/code', `${name}.output.json`), 'utf8'))
      if (o.note) summary = 'NOTE: ' + o.note
      else if (o.error) summary = 'ERROR: ' + o.error.replace(/\s+/g, ' ').slice(0, full ? 2000 : 160)
      else summary = `text[${(o.text || '').length}] svg[${(o.svgs || []).length}] ` + (o.text || '').replace(/\s+/g, ' ').slice(0, full ? 2000 : 120)
    } catch (e) { /* keep */ }
    console.log(`  [${i}] L${f.line} ${hash} ${head}`)
    console.log(`        ${summary}`)
  }
}
