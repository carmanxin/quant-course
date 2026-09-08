// 从 public/code/*.output.json 直接审计（不依赖 dist）
import fs from 'node:fs'
import { execSync } from 'node:child_process'

const files = execSync('ls public/code/*.output.json', { encoding: 'utf8' })
  .trim().split('\n').filter(f => f && !f.includes('_auto'))

let total = 0, text = 0, svgs = 0, note = 0, error = 0
for (const file of files) {
  let d
  try { d = JSON.parse(fs.readFileSync(file, 'utf8')) } catch { continue }
  total++
  if (d.text && d.text.length > 0) text++
  if (d.svgs && d.svgs.length > 0) svgs++
  if (d.note && d.note.length > 0) note++
  if (d.error && d.error.length > 0) error++
}
console.log(`total precomputed: ${total}`)
console.log(`  with-text:  ${text}`)
console.log(`  with-svgs:  ${svgs}`)
console.log(`  with-note:  ${note}`)
console.log(`  with-error: ${error}`)