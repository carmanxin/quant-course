#!/usr/bin/env node
// scripts/relativize-dist.mjs
// 构建后处理：把 dist/**/*.html 里的绝对路径资源与链接改写为相对路径。
// 目的：portable 包可被 file:// 直接打开（双击 index.html 排版正常、导航可点）。
//   - 绝对路径如 /assets/x.css /guide/ /code/x.svg /favicon.svg
//   - 按每个 HTML 相对站点根(dist)的深度加前缀：./ 或 ../../
// 相对路径在 HTTP 与 file:// 下都正确，不影响线上部署。

import { readFile, writeFile, readdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const DIST = process.env.QPORTABLE ? path.join(ROOT, 'portable', 'dist') : path.join(ROOT, '.vitepress', 'dist')

// (src|href)=["']/...  →  相对路径（url 不含前导 /，由 \/ 已消耗）
const ABS_RE = /(\b(?:src|href)=)["']\/([^"']*)["']/g

function relPrefix(depth) {
  return depth === 0 ? './' : '../'.repeat(depth)
}

async function walk(dir) {
  const out = []
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...(await walk(p)))
    else if (e.name.endsWith('.html')) out.push(p)
  }
  return out
}

async function main() {
  const htmls = await walk(DIST)
  let changed = 0
  for (const file of htmls) {
    const rel = path.relative(DIST, file).split(path.sep)
    const depth = rel.length - 1
    const prefix = relPrefix(depth)
    let html = await readFile(file, 'utf8')
    const before = html
    html = html.replace(ABS_RE, (m, attr, url) => {
      // 排除协议相对(//)等非站内绝对引用
      if (url.startsWith('/') || url.startsWith('//')) return m
      // /guide/#锚点 → ./guide/#锚点（相对化后锚点仍有效）
      return `${attr}"${prefix}${url}"`
    })
    if (html !== before) {
      await writeFile(file, html, 'utf8')
      changed++
    }
  }
  console.log(`[relativize-dist] ${htmls.length} html files, ${changed} rewritten`)
}

main().catch((e) => {
  console.error(`[relativize-dist] fatal: ${e.message}`)
  process.exit(1)
})
