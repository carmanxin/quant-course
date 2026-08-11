#!/usr/bin/env node
// scripts/precompute-py-outputs.mjs
// 遍历 public/code/*.py，spawn python3 执行，捕获 stdout + plt.show() 的 SVG。
// 失败不抛 exit 1（让 reader 在折叠块看到失败原因）。

import { spawn } from 'node:child_process'
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises'
import { glob } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const CODE_DIR = path.join(ROOT, 'public', 'code')
const TIMEOUT_MS = 30_000
const MARKER = /^#\s*@quantlab\/output:\s*([\w.\-]+)/

async function runOne(pyFile) {
  const text = await readFile(pyFile, 'utf8')
  const m = text.match(MARKER)
  if (!m) return { skipped: true, file: path.basename(pyFile) }

  const name = m[1]
  const svgDir = path.join(CODE_DIR, `${name}.svgs`)
  await mkdir(svgDir, { recursive: true })

  const env = {
    ...process.env,
    MPLBACKEND: 'svg',
    QT_QPA_PLATFORM: 'offscreen',
    PYTHONUNBUFFERED: '1',
    QUANTLAB_SVG_DIR: svgDir,
    QUANTLAB_OUTPUT_NAME: name,
  }

  const preamble = `
import os, matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
_SHOW_COUNT = [0]
def _patched_show(*a, **k):
    n = _SHOW_COUNT[0]
    _SHOW_COUNT[0] += 1
    fname = f"{os.environ['QUANTLAB_OUTPUT_NAME']}-{n}.svg"
    plt.savefig(os.path.join(os.environ['QUANTLAB_SVG_DIR'], fname), bbox_inches="tight")
    plt.close()
plt.show = _patched_show
`

  // Insert preamble AFTER any `from __future__` import lines (must be first
  // non-comment statement in the file per Python language spec).
  const futureMatch = text.match(/(?:^|\n)(?:from __future__[^\n]*\n)+/)
  const finalText = futureMatch
    ? text.slice(0, futureMatch.index + futureMatch[0].length) + preamble + text.slice(futureMatch.index + futureMatch[0].length)
    : preamble + text

  return new Promise((resolve) => {
    let stdout = '', stderr = ''
    const proc = spawn('python3', ['-c', finalText], { env })
    const timer = setTimeout(() => proc.kill('SIGKILL'), TIMEOUT_MS)
    proc.stdout.on('data', (d) => stdout += d)
    proc.stderr.on('data', (d) => stderr += d)
    proc.on('close', async (code) => {
      clearTimeout(timer)
      let svgs = []
      try {
        const files = await readdir(svgDir)
        svgs = files
          .filter((f) => f.endsWith('.svg'))
          .sort()
          .map((f) => `/code/${name}.svgs/${f}`)
      } catch (e) {
        // svgDir 不存在则 svgs 留空
      }
      const payload = code === 0
        ? { text: stdout.trim(), svgs }
        : { text: stdout.trim(), svgs, error: stderr.trim().slice(0, 500) }
      await writeFile(
        path.join(CODE_DIR, `${name}.output.json`),
        JSON.stringify(payload, null, 2),
      )
      resolve({ name, file: path.basename(pyFile), code, len: stdout.length })
    })
  })
}

async function main() {
  const files = []
  try {
    for await (const f of glob('public/code/*.py')) files.push(f)
  } catch (e) {
    console.error(`[precompute] glob failed: ${e.message}`)
    process.exit(0)  // 不抛 exit 1
  }
  console.log(`[precompute] running ${files.length} files...`)
  const results = await Promise.all(files.map(runOne))
  const failed = results.filter((r) => !r.skipped && r.code !== 0)
  const skipped = results.filter((r) => r.skipped).length
  console.log(
    `[precompute] done: ${results.length - failed.length - skipped}/${results.length} succeeded, ${failed.length} failed, ${skipped} skipped (no marker)`,
  )
  if (failed.length) {
    console.log('[precompute] FAILED:')
    for (const f of failed) console.log(`  - ${f.name} (${f.file}): exit ${f.code}`)
  }
  process.exit(0)  // 永远 exit 0
}

main().catch((e) => {
  console.error(`[precompute] fatal: ${e.message}`)
  process.exit(0)
})