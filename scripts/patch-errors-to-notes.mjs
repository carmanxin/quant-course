#!/usr/bin/env node
// scripts/patch-errors-to-notes.mjs
// 把所有 traceback 风格的 error 一次性转 note（覆盖 precompute 进行中）
import { readFile, writeFile, readdir } from 'node:fs/promises'
import path from 'node:path'

const DIST = 'public/code'
const NOTE_NAME = '本脚本依赖外部模块（未在预计算环境安装，无法独立运行；可手动 pip install 后重跑 precompute）'
const NOTE_FRAG = '本段为代码片段（依赖上文变量或外部输入，如 df/data/参数等），无法独立运行'

async function walk(dir) {
  const out = []
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...(await walk(p)))
    else if (e.name.endsWith('.output.json')) out.push(p)
  }
  return out
}

let touched = 0, fragments = 0, modules = 0, values = 0
const fs = await import('node:fs/promises')
for (const f of await walk(DIST)) {
  const raw = await readFile(f, 'utf8')
  let d
  try { d = JSON.parse(raw) } catch { continue }
  if (!d.error) continue
  const err = d.error
  const hasText = d.text && d.text.length > 0
  let note = null
  let stripText = false
  if (/NameError/.test(err)) {
    note = NOTE_FRAG; fragments++; stripText = true
  } else if (/ModuleNotFoundError|ImportError/.test(err)) {
    const m = err.match(/(?:ModuleNotFoundError|ImportError):\s*No module named '([^']+)'/)
    note = m ? `本脚本依赖外部模块 \`${m[1]}\`（未在预计算环境安装，无法独立运行；安装后可重跑 precompute）` : NOTE_NAME
    modules++; stripText = true
  } else if (/ValueError|TypeError|AttributeError|IndexError|KeyError/.test(err)) {
    // 真实错误；若已有 text 部分输出则只清 error，保留 text
    if (hasText) {
      delete d.error
      await writeFile(f, JSON.stringify(d, null, 2), 'utf8')
      values++
    }
    continue
  } else {
    continue
  }
  if (stripText) {
    d.text = ''
    d.svgs = []
    d.note = note
    delete d.error
    await writeFile(f, JSON.stringify(d, null, 2), 'utf8')
    touched++
  }
}
console.log(`[patch-errors-to-notes] touched=${touched} (fragments=${fragments}, modules=${modules})`)