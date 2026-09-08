import fs from 'node:fs'
import path from 'node:path'

const pyHashes = new Set(
  fs.readdirSync('public/code/_auto')
    .filter(f => f.endsWith('.py'))
    .map(f => f.replace(/\.py$/, ''))
)
const outHashes = new Set(
  fs.readdirSync('public/code')
    .filter(f => /^[0-9a-f]{8}\.output\.json$/.test(f))
    .map(f => f.replace(/\.output\.json$/, ''))
)

const missing = [...pyHashes].filter(h => !outHashes.has(h))
console.log(`py files: ${pyHashes.size}`)
console.log(`output files: ${outHashes.size}`)
console.log(`missing: ${missing.length}`)
if (missing.length > 0) {
  console.log('first 10 missing:', missing.slice(0, 10))
}