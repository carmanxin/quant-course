// 审计：验证 md fence → hash 的三方一致性（Node extract / Python build-code-index / 组件端）
// 用法：node tests/_audit-hash-consistency.mjs
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..')
const GUIDE = path.join(ROOT, 'guide')
const CODE = path.join(ROOT, 'public', 'code')

function fnv1a(str) {
  let h = 0x811c9dc5
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}

function normalize(raw) {
  return raw
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+$/gm, '')
    .trim()
}

function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

function extractFences(md) {
  const out = []
  const lines = md.split('\n')
  let inFence = false, lang = '', buf = []
  for (const line of lines) {
    if (!inFence && /^```/.test(line)) {
      inFence = true
      lang = line.replace(/^```/, '').trim()
      buf = []
    } else if (inFence && /^```\s*$/.test(line)) {
      inFence = false
      if (['python', 'py'].includes(lang)) out.push(buf.join('\n'))
    } else if (inFence) buf.push(line)
  }
  return out
}

const mdFiles = walk(GUIDE)
const all = []
const uniq = new Map()
for (const f of mdFiles) {
  const md = fs.readFileSync(f, 'utf8')
  for (const raw of extractFences(md)) {
    const n = normalize(raw)
    if (!n) continue
    const h = fnv1a(n)
    all.push({ file: path.relative(ROOT, f), h })
    if (!uniq.has(h)) uniq.set(h, n)
  }
}

const idx = JSON.parse(fs.readFileSync(path.join(CODE, '_index.json'), 'utf8'))
const idxKeys = new Set(Object.keys(idx))
const mdHashes = new Set(all.map(a => a.h))

const avail = new Set(fs.readdirSync(CODE).filter(f => f.endsWith('.output.json')).map(f => f.slice(0, -'.output.json'.length)))
const mapped = new Set(Object.values(idx))
const orphans = [...avail].filter(v => !mapped.has(v))

console.log('md 文件数            :', mdFiles.length)
console.log('fence 总数(含重复)   :', all.length)
console.log('唯一 fence (hash)    :', uniq.size)
console.log('_index.json 条目     :', idxKeys.size)
console.log('output.json 文件数   :', avail.size)
console.log('')
console.log('md fence hash 不在索引中 :', all.filter(a => !idxKeys.has(a.h)).length)
console.log('索引条目在 md 中不存在     :', [...idxKeys].filter(k => !mdHashes.has(k)).length)
console.log('索引指向但文件缺失        :', [...mapped].filter(v => !avail.has(v)).length)
console.log('孤儿产物(存在但未引用)    :', orphans.length)
console.log('')

// 孤儿产物里有多少是真有结果的
let orphanReal = 0
for (const o of orphans) {
  try {
    const d = JSON.parse(fs.readFileSync(path.join(CODE, o + '.output.json'), 'utf8'))
    if ((d.text || '').trim()) orphanReal++
  } catch { /* ignore */ }
}
console.log('孤儿产物中有真实 text 的 :', orphanReal)

// CI 阈值推演
const THRESHOLD = 480
console.log('')
console.log('=== CI 预计算跳过逻辑推演 ===')
console.log('CI 判定条件: ls public/code/*.output.json | wc -l >= ' + THRESHOLD)
console.log('  当前仓库实际文件数        :', avail.size, '=>', avail.size >= THRESHOLD ? '跳过 precompute' : '运行 precompute')
console.log('  一轮全新 precompute 产出上限: ' + uniq.size + ' (唯一 fence 数)')
console.log('  => 全新 precompute 永远达不到 ' + THRESHOLD + '，阈值只能靠孤儿产物凑够')
console.log('  => 结论: 孤儿产物让 CI 永久走"跳过"分支，precompute 在 CI 中永不执行')

// 索引中指向孤儿名称的情况
const humanNamed = Object.entries(idx).filter(([, v]) => !/^[0-9a-f]{8}$/.test(v))
console.log('')
console.log('索引中非 hash 命名(手工名)条目:', humanNamed.length)
humanNamed.slice(0, 10).forEach(([k, v]) => console.log('  ', k, '->', v, avail.has(v) ? '(存在)' : '(缺失!)'))

// 统计索引覆盖的代码块结果分布
let real = 0, note = 0, err = 0, none = 0
for (const [k, v] of Object.entries(idx)) {
  if (!avail.has(v)) { none++; continue }
  const d = JSON.parse(fs.readFileSync(path.join(CODE, v + '.output.json'), 'utf8'))
  const t = (d.text || '').trim()
  if (d.error) err++
  else if (t) real++
  else if (d.note) note++
  else none++
}
console.log('')
console.log('=== 索引覆盖 ' + idxKeys.size + ' 个代码块的结果分布 ===')
console.log('真实运行输出 :', real, `(${((real / idxKeys.size) * 100).toFixed(1)}%)`)
console.log('note 回落说明:', note)
console.log('error        :', err)
console.log('无产物       :', none)
