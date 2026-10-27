#!/usr/bin/env node
// scripts/count-unique-fences.mjs
// 统计 guide/**/*.md 中唯一 python fence 数（与 extract-py-fences.mjs 同口径：
//   归一化后取 FNV-1a hash 去重）。
//
// 用途：CI 判据「索引完整性」——_index.json 条目数应等于本脚��输出。
//   索引 == fence 数 ⇒ 全部代码块都已被索引，产物齐全。
//
// 用法：node scripts/count-unique-fences.mjs
import { readFile, readdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const GUIDE_DIR = path.join(ROOT, 'guide')

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

async function walk(dir) {
  const out = []
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...(await walk(p)))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

function extractFences(md) {
  const fences = []
  const lines = md.split('\n')
  let inFence = false, lang = '', buf = []
  for (const line of lines) {
    if (!inFence && /^```/.test(line)) {
      inFence = true
      lang = line.replace(/^```/, '').trim()
      buf = []
    } else if (inFence && /^```\s*$/.test(line)) {
      inFence = false
      if (['python', 'py'].includes(lang)) fences.push(buf.join('\n'))
    } else if (inFence) buf.push(line)
  }
  return fences
}

const set = new Set()
for (const f of await walk(GUIDE_DIR)) {
  const md = await readFile(f, 'utf8')
  for (const raw of extractFences(md)) {
    const n = normalizeCode(raw)
    if (n) set.add(fnv1a(n))
  }
}
console.log(set.size)
