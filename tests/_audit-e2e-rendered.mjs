// 端到端审计（渲染层）：从 dist HTML 里把每个代码块的 <pre class="scb-out-text">
// 抽出来，与该代码块的源码 hash 对照 public/code/*.output.json，
// 验证「页面展示的代码」与「页面展示的运行结果」确实来自同一次预计算。
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..')
const DIST = path.join(ROOT, '.vitepress', 'dist')
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
function walk(dir, filter) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p, filter))
    else if (filter(e.name)) out.push(p)
  }
  return out
}

// 索引：hash -> name
const idx = JSON.parse(fs.readFileSync(path.join(CODE, '_index.json'), 'utf8'))

// 预加载所有 output.json
const outMap = new Map()
for (const f of fs.readdirSync(CODE)) {
  if (!f.endsWith('.output.json')) continue
  try { outMap.set(f.slice(0, -'.output.json'.length), JSON.parse(fs.readFileSync(path.join(CODE, f), 'utf8'))) } catch { }
}

const htmlFiles = walk(DIST, n => n.endsWith('.html'))
let blocks = 0, rendered = 0, noRender = 0
let matched = 0, mismatched = 0, unresolved = 0
const problems = []

// 页面里代码块渲染顺序：<details class="scb-code-wrap"> ... </details> 之后跟 <details class="scb-out">
const codeRe = /<details class="scb-code-wrap"[\s\S]*?<\/details>/g
const outRe = /<details class="scb-out"[\s\S]*?<\/details>/g

for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8')
  const rel = path.relative(DIST, f).split(path.sep).join('/')
  const codeBlocks = html.match(codeRe) || []
  const outBlocks = html.match(outRe) || []
  // 逐个 code block：取其内 <pre ... vp-code> 的文本，反推 hash
  for (let i = 0; i < codeBlocks.length; i++) {
    blocks++
    const cb = codeBlocks[i]
    // 提取行数
    const lm = cb.match(/scb-code-meta[^>]*>(\d+) 行/)
    // 提取代码文本：<code> 内去标签
    const codeHtml = (cb.match(/<code>([\s\S]*?)<\/code>/) || [])[1] || ''
    const codeText = codeHtml
      .replace(/<[^>]+>/g, '')
      .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>').replace(/&amp;/g, '&')
      .replace(/\n+$/, '')
    if (!codeText.trim()) continue
    const h = fnv1a(normalize(codeText))
    const name = idx[h]
    if (!name) { unresolved++; continue }

    // 对应的输出块（同序位）
    const ob = outBlocks[i]
    if (!ob) { noRender++; continue }
    const pre = (ob.match(/<pre class="scb-out-text"[^>]*>([\s\S]*?)<\/pre>/) || [])[1] || ''
    const renderedText = pre.replace(/<[^>]+>/g, '')
      .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim()
    const payload = outMap.get(name)
    if (!payload) { unresolved++; continue }
    const expect = (payload.text || '').trim()
    if (!expect) { noRender++; continue }
    rendered++
    if (renderedText === expect) matched++
    else {
      mismatched++
      if (problems.length < 8) problems.push({ rel, h, name, r: renderedText.slice(0, 90), e: expect.slice(0, 90) })
    }
  }
}

console.log('=== dist 渲染层端到端核对 ===')
console.log('HTML 文件            :', htmlFiles.length)
console.log('代码块(从 DOM 抽)    :', blocks)
console.log('可定位 hash 的        :', blocks - unresolved)
console.log('hash 无法定位        :', unresolved)
console.log('有预期输出的         :', rendered)
console.log('渲染文本 == 产物文本 :', matched)
console.log('不一致               :', mismatched)
console.log('')
if (problems.length) {
  console.log('--- 不一致样本 ---')
  problems.forEach(p => console.log('  ', p.rel, p.h, p.name, '\n     页面:', p.r.replace(/\n/g, '\\n'), '\n     产物:', p.e.replace(/\n/g, '\\n')))
}
