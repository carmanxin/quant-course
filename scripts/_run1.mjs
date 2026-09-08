#!/usr/bin/env node
// scripts/_run1.mjs <hash...>  重跑指定 hash 的 py 并打印 output.json
import { readFile } from 'node:fs/promises'
import { runOne } from './precompute-py-outputs.mjs'

for (const h of process.argv.slice(2)) {
  await runOne(`public/code/_auto/${h}.py`)
  const o = JSON.parse(await readFile(`public/code/${h}.output.json`, 'utf8'))
  console.log(`\n=== ${h} ===`)
  if (o.text) console.log(o.text.slice(0, 1500))
  if (o.note) console.log('NOTE:', o.note)
  if (o.error) console.log('ERR:', o.error.replace(/\s+/g, ' ').slice(0, 300))
  if (o.svgs?.length) console.log('SVGS:', o.svgs.length)
}
