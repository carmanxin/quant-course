// 审计：md 源文件与 dist HTML 产物的一一映射
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..')
const DIST = path.join(ROOT, '.vitepress', 'dist')

function walk(dir, filter) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p, filter))
    else if (filter(e.name)) out.push(p)
  }
  return out
}

// 只统计「会构建成页面」的 md：跳过以 . 开头的隐藏目录（.research/ 等）
const mdFiles = walk(path.join(ROOT, 'guide'), n => n.endsWith('.md'))
  .filter(f => !f.split(path.sep).some(seg => seg.startsWith('.')))
const htmlFiles = walk(DIST, n => n.endsWith('.html'))
const htmlSet = new Set(htmlFiles.map(f => path.relative(DIST, f).split(path.sep).join('/')))

const missing = []
for (const m of mdFiles) {
  const rel = path.relative(path.join(ROOT, 'guide'), m).split(path.sep).join('/')
  const expect = 'guide/' + rel.replace(/\.md$/, '.html')
  if (!htmlSet.has(expect)) missing.push({ md: path.relative(ROOT, m).split(path.sep).join('/'), expect })
}

// dist 里额外存在的 html：404、目录 index 等属正常结构，不算「多出」
const mdExpect = new Set(mdFiles.map(m =>
  'guide/' + path.relative(path.join(ROOT, 'guide'), m).split(path.sep).join('/').replace(/\.md$/, '.html')))
const extra = [...htmlSet].filter(h =>
  !mdExpect.has(h) &&
  h !== '404.html' &&
  !h.endsWith('/index.html'))

console.log('guide md 总数    :', mdFiles.length)
console.log('dist html 总数   :', htmlFiles.length)
console.log('md 无对应 html   :', missing.length)
missing.forEach(x => console.log('   -', x.md, '-> 期望', x.expect))
console.log('dist 多出的 html :', extra.length)
extra.forEach(x => console.log('   +', x))
