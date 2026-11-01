#!/usr/bin/env node
// scripts/check-precompute-ready.mjs
// 判定「预计算产物是否齐全」，三个数一次算完：
//   INDEX_N   —— public/code/_index.json 的条目数
//   FENCE_N   —— guide/**/*.md 中唯一 python fence 数（与 extract-py-fences.mjs 同口径）
//   MISSING   —— 索引引用的产物文件里，有几个在 public/code/ 下不存在
//
// 判据（CI 第 6 步）：INDEX_N > 0 && INDEX_N == FENCE_N && MISSING == 0
//   ⇒ 索引已覆盖全部代码块、产物齐全 ⇒ 可跳过 precompute（20min → 4min）
//
// 用法：
//   node scripts/check-precompute-ready.mjs
//   node scripts/check-precompute-ready.mjs --json      # 机器可读
//
// 输出格式：最后一行为 `index=<N> fences=<N> missing=<N> ready=<true|false>`
// CI 会把这一行原样写进 job summary，便于事后核对判据是否按预期生效。
//
// ⚠ 2026-11-01 新立：原 CI 判据用 `python3 -c ...` 分别算 INDEX_N / MISSING，
//   两处静默失败时会被 `|| echo 0` / `|| echo 999` 兜底成假值，
//   于是「判据不通过 → 跑 precompute」被误当成常态，掩盖了真实原因。
//   改用 Node 一次算完：Node 是 CI 的既成依赖（build 就要用），不会缺；
//   且任一环节失败会显式报错并返回非 0，不再静默兜底。
import fs from 'node:fs'
import path from 'node:path'
import { readFile, readdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const GUIDE_DIR = path.join(ROOT, 'guide')
const CODE_DIR = path.join(ROOT, 'public', 'code')
const INDEX_FILE = path.join(CODE_DIR, '_index.json')

/** 与 extract-py-fences.mjs 同口径的 FNV-1a 32bit */
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

function fail(msg) {
  console.error(`[check-precompute-ready] 判定失败：${msg}`)
  process.exit(1)
}

// ---- 1. 索引 ----
if (!fs.existsSync(INDEX_FILE)) fail(`找不到 ${path.relative(ROOT, INDEX_FILE)}（产物未提交进仓库？）`)
let idx
try {
  idx = JSON.parse(await readFile(INDEX_FILE, 'utf8'))
} catch (e) {
  fail(`${path.relative(ROOT, INDEX_FILE)} 解析失败：${e.message}`)
}
if (!idx || typeof idx !== 'object') fail('_index.json 不是合法对象')
const INDEX_N = Object.keys(idx).length
const names = new Set(Object.values(idx))

// ---- 2. 唯一 fence 数 ----
const fenceSet = new Set()
for (const f of await walk(GUIDE_DIR)) {
  const md = await readFile(f, 'utf8')
  for (const raw of extractFences(md)) {
    const n = normalizeCode(raw)
    if (n) fenceSet.add(fnv1a(n))
  }
}
const FENCE_N = fenceSet.size

// ---- 3. 缺失产物 ----
const MISSING = []
for (const n of names) {
  if (!fs.existsSync(path.join(CODE_DIR, n + '.output.json'))) MISSING.push(n)
}

const ready = INDEX_N > 0 && INDEX_N === FENCE_N && MISSING.length === 0
const line = `index=${INDEX_N} fences=${FENCE_N} missing=${MISSING.length} ready=${ready}`

if (process.argv.includes('--json')) {
  console.log(JSON.stringify({
    index: INDEX_N, fences: FENCE_N, missing: MISSING.length,
    missingSample: MISSING.slice(0, 10), ready,
  }))
} else {
  console.log(`  索引条目     : ${INDEX_N}`)
  console.log(`  唯一 fence   : ${FENCE_N}`)
  console.log(`  缺失产物     : ${MISSING.length}${MISSING.length ? ' (例: ' + MISSING.slice(0, 3).join(', ') + ')' : ''}`)
  console.log(`  判定         : ${ready ? '齐全，可跳过 precompute' : '不齐全，需跑 precompute'}`)
}
console.log(line)
