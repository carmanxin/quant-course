#!/usr/bin/env node
// scripts/patch-empty-bodies.mjs
// 给 portable/dist 中所有空 scb-out-body 注入友好的 note（"脚本无输出"）
// 绕过 vitepress build hang。直接修改 SSR 后的 HTML。
import { readFile, writeFile, readdir } from 'node:fs/promises'
import path from 'node:path'

const DIST = 'portable/dist'

async function walk(dir) {
  const out = []
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...(await walk(p)))
    else if (e.name.endsWith('.html')) out.push(p)
  }
  return out
}

// Vue 渲染 output=null 时的 body（4 个 v-if 全 false）
const EMPTY = '<!--[--><!----><!----><!----><!----><!--]-->'
// 替换为 note 提示
const NOTE = '<div class="scb-out-note" data-v-b94b5483>📘 脚本运行成功但无 print 与图表输出（纯函数/状态修改类脚本）</div>'

let touched = 0
const files = await walk(DIST)
for (const f of files) {
  const html = await readFile(f, 'utf8')
  const matches = html.split(EMPTY).length - 1
  if (matches > 0) {
    const newHtml = html.split(EMPTY).join(NOTE)
    await writeFile(f, newHtml, 'utf8')
    touched += matches
  }
}
console.log(`[patch-empty-bodies] touched ${touched} empty bodies across ${files.length} files`)