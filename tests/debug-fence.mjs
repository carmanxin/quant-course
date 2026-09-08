import fs from 'node:fs'
import path from 'node:path'

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

const configDir = path.resolve('.vitepress')
const idxPath = path.join(configDir, '..', 'public', 'code', '_index.json')
const index = JSON.parse(fs.readFileSync(idxPath, 'utf8'))
console.log('index size:', Object.keys(index).length)

const md = fs.readFileSync('guide/m01-overview/1.3-quant-mindset.md', 'utf8')
console.log('md size:', md.length)

// split by fence lines directly
const lines = md.split('\n')
let fences = []
let inFence = false
let lang = ''
let buf = []
for (const line of lines) {
  if (!inFence && /^```/.test(line)) {
    inFence = true
    lang = line.replace(/^```/, '').trim()
    buf = []
  } else if (inFence && /^```\s*$/.test(line)) {
    inFence = false
    if (['python', 'py'].includes(lang)) {
      fences.push(buf.join('\n'))
    }
  } else if (inFence) {
    buf.push(line)
  }
}
console.log('found', fences.length, 'python fences')

fences.forEach((code, i) => {
  const norm = normalizeCode(code)
  const hash = fnv1a(norm)
  const mapped = index[hash]
  console.log(`fence ${i}: hash=${hash} size=${code.length} -> ${mapped || '<NONE>'}`)
})