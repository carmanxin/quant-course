#!/usr/bin/env node
// scripts/_rerun-ranges.mjs (临时批量重跑)
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')

const HASHES = process.argv.slice(2)
const { runOne } = await import('file://' + path.join(ROOT, 'scripts', 'precompute-py-outputs.mjs').replace(/\\/g, '/'))

let ok = 0, fail = 0
for (const h of HASHES) {
  const pyFile = path.join(ROOT, 'public', 'code', '_auto', `${h}.py`)
  try {
    const r = await runOne(pyFile)
    if (r && r.code === 0) ok++
    else fail++
  } catch (e) {
    console.error(`  ERROR ${h}: ${e.message}`)
    fail++
  }
}
console.log(`[rerun] DONE: ${ok}/${HASHES.length} ok, ${fail} failed`)