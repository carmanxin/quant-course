import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'

// 模拟 vite 注入
const __vite_injected_original_import_meta_url = `file:///d:/AI/study/quant/.vitepress/config.ts.timestamp-1786500747458-3fc350d4fefd8.mjs`
const __dirname = path.dirname(fileURLToPath(__vite_injected_original_import_meta_url))

console.log('__dirname:', __dirname)
const idxPath = path.join(__dirname, '../public/code/_index.json')
console.log('idxPath:', idxPath)
console.log('exists:', fs.existsSync(idxPath))

// 检查 1.3-bootstrap.output.json
const outPath = path.join(__dirname, '../public/code/1.3-bootstrap.output.json')
console.log('outPath:', outPath)
console.log('out exists:', fs.existsSync(outPath))

// 测 FNV-1a
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

const md = fs.readFileSync('guide/m01-overview/1.3-quant-mindset.md', 'utf8')
const lines = md.split('\n')
let inFence = false, lang = '', buf = [], fencesList = []
for (const line of lines) {
  if (!inFence && /^```/.test(line)) {
    inFence = true
    lang = line.replace(/^```/, '').trim()
    buf = []
  } else if (inFence && /^```\s*$/.test(line)) {
    inFence = false
    if (['python', 'py'].includes(lang)) fencesList.push(buf.join('\n'))
  } else if (inFence) buf.push(line)
}

const index = JSON.parse(fs.readFileSync(idxPath, 'utf8'))
console.log('index size:', Object.keys(index).length)

fencesList.forEach((code, i) => {
  const hash = fnv1a(normalizeCode(code))
  const name = index[hash]
  console.log(`fence ${i}: hash=${hash} name=${name}`)
  if (name) {
    const out = JSON.parse(fs.readFileSync(path.join(__dirname, `../public/code/${name}.output.json`), 'utf8'))
    const b64 = Buffer.from(JSON.stringify(out), 'utf8').toString('base64')
    console.log(`  → output-b64 preview: ${b64.slice(0, 40)}...`)
  }
})