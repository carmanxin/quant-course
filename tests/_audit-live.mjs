#!/usr/bin/env node
/**
 * _audit-live.mjs —— 线上产物核验（可常态化重跑）
 *
 * 用途：验证「线上所载」与「dist 分支真源」是否一致，防��：
 *   ① 部署了旧版 / 半版产物
 *   ② 平台缓存了过期内容
 *   ③ 某些页面漏传或内容丢失
 *
 * 用法：
 *   node tests/_audit-live.mjs [baseUrl] [ref]
 *   node tests/_audit-live.mjs https://quant-course.pages.dev origin/dist
 *
 * 比对策略（三级判定）：
 *   完全一致  → 逐字节 sha256 相同
 *   仅环境差异 → 归一化后相同（CRLF/资源 hash/Vue scoped id 三类构建环境差异）
 *   实质差异  → 归一化后仍不同 → 报出首个差异位置与上下文
 *
 * ⚠ 三类「环境差异」的成因（CI 构建机为 Windows，本地为 Git Bash）：
 *   1. 换行符     线上 \r\n vs 本地 \n
 *   2. 资源 hash  style.XXXXXXXX.css / app.XXXXXXXX.js（页面级 chunk 全部相同）
 *   3. Vue scoped id  data-v-XXXXXXXX
 */
import fs from 'node:fs'
import path from 'node:path'
import os from 'node:os'
import crypto from 'node:crypto'
import { execSync } from 'node:child_process'

const BASE = (process.argv[2] || 'https://quant-course.pages.dev').replace(/\/$/, '')
const REF = process.argv[3] || 'origin/dist'
const TIMEOUT = 45000
const RETRIES = 8

const sha = (s) => crypto.createHash('sha256').update(s).digest('hex')

/** 归一化三类构建环境差异 */
const normalize = (s) =>
  s
    .replace(/\r\n/g, '\n')
    .replace(/data-v-[0-9a-f]{8}/g, 'data-v-SCOPED')
    .replace(/\.([A-Za-z0-9_-]{8})\.(css|js)/g, '.HASH.$2')
    .replace(/\\"([a-z0-9_.\-]+\.md)\\":\\"([A-Za-z0-9_-]{8})\\"/g, '\\"$1\\":\\"HASH\\"')

async function fetchText(url) {
  let last = null
  for (let i = 0; i < RETRIES; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT) })
      if (r.status === 200) return await r.text()
      last = `HTTP ${r.status}`
    } catch (e) {
      last = String(e).slice(0, 90)
    }
    await new Promise((r) => setTimeout(r, 1500 * (i + 1)))
  }
  throw new Error(last || 'unknown')
}

/** 导出 ref 到临时目录 */
function exportRef(ref) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'quantlab-live-'))
  execSync(`git archive "${ref}" | tar -x -C "${dir}"`, { stdio: 'pipe' })
  return dir
}

/** 递归列出 html 相对路径 */
function listHtml(dir, base = dir, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) listHtml(p, base, acc)
    else if (e.name.endsWith('.html')) acc.push(path.relative(base, p).split(path.sep).join('/'))
  }
  return acc
}

async function main() {
  console.log(`线上核验：${BASE}`)
  console.log(`真源引用：${REF}`)
  const dir = exportRef(REF)
  const pages = listHtml(dir).sort()
  console.log(`页面总数：${pages.length}\n`)

  let exact = 0, envOnly = 0, realDiff = 0, fail = 0
  const issues = []
  const markers = { qzBadge: 0, runLocally: 0, scb: 0 }

  for (const p of pages) {
    let remote
    try {
      remote = await fetchText(`${BASE}/${p}`)
    } catch (e) {
      fail++
      issues.push({ p, kind: 'FETCH_FAIL', detail: String(e.message).slice(0, 90) })
      continue
    }
    const local = fs.readFileSync(path.join(dir, p), 'utf8')

    markers.qzBadge += (remote.match(/qz-badge/g) || []).length
    markers.runLocally += (remote.match(/run-locally/g) || []).length
    markers.scb += (remote.match(/class="scb/g) || []).length

    if (remote.length < 5000) {
      issues.push({ p, kind: 'TOO_SHORT', detail: `${remote.length} B` })
    }
    if (sha(local) === sha(remote)) { exact++; continue }
    if (sha(normalize(local)) === sha(normalize(remote))) { envOnly++; continue }

    realDiff++
    const a = normalize(local), b = normalize(remote)
    let f = -1
    for (let i = 0; i < Math.min(a.length, b.length); i++) { if (a[i] !== b[i]) { f = i; break } }
    issues.push({
      p, kind: 'REAL_DIFF', detail: `首差=${f} len ${a.length}/${b.length}`,
      local: a.slice(Math.max(0, f - 90), f + 170),
      remote: b.slice(Math.max(0, f - 90), f + 170),
    })
  }

  fs.rmSync(dir, { recursive: true, force: true })

  console.log('===== 核验结果 =====')
  console.log(`逐字节完全一致 : ${exact}`)
  console.log(`仅环境差异     : ${envOnly}`)
  console.log(`实质差异       : ${realDiff}`)
  console.log(`取不到         : ${fail}`)
  console.log(`\n线上渲染痕迹   : qz-badge ${markers.qzBadge} · run-locally ${markers.runLocally} · scb ${markers.scb}`)

  if (issues.length) {
    console.log(`\n--- 异常明细（${issues.length}）---`)
    for (const it of issues.slice(0, 20)) {
      console.log(`[${it.kind}] ${it.p} :: ${it.detail}`)
      if (it.local) {
        console.log(`   真源: ${JSON.stringify(it.local)}`)
        console.log(`   线上: ${JSON.stringify(it.remote)}`)
      }
    }
  }

  const pass = realDiff === 0 && fail === 0
  console.log(`\n结论：${pass ? '✅ 通过 —— 线上与真源内容一致' : '❌ 未通过 —— 见上方明细'}`)
  process.exit(pass ? 0 : 1)
}

main().catch((e) => { console.error('核验异常:', e); process.exit(2) })
