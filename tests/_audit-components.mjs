// 审计（渲染层·组件）：核对所有自定义 Vue 组件在 dist 产物中是否真正渲染。
//
// 背景（2026-10-26 司礼监第三令）：QuizBlock 与 RunLocally 在 .vitepress/theme/index.ts
// 里只做了 `import` 未做 `app.component(...)` 注册。未注册的自定义元素在 SSR 阶段
// 会被当作未知 HTML 元素处理 —— Vue 不会渲染它，**内容在产物里直接消失且无任何报错**。
// 本脚本把这类「静默丢失」纳入常态化审计：
//   1. 组件目录全量扫描 → theme 注册状态核对
//   2. md 中 <Tag> 使用点 → dist 产物中的渲染痕迹核对
//   3. SSR 后的痕迹用组件自身的 class 名判定（组件名/原始属性在 SSR 后不可见）
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..')
const DIST = path.join(ROOT, '.vitepress', 'dist')
const COMPONENTS = path.join(ROOT, 'components')
const THEME = path.join(ROOT, '.vitepress', 'theme', 'index.ts')

// 组件的 SSR 痕迹：取其 template 根元素上出现的第一个 class，作为「已渲染」判据
function rootClassOf(vueFile) {
  const src = fs.readFileSync(vueFile, 'utf8')
  const tpl = src.slice(src.indexOf('<template>'), src.indexOf('</template>'))
  // 根元素可能带动态 class（:class / :class="..."），取静态 class 的第一段
  const m = tpl.match(/<div[^>]*\sclass="([^"]+)"/)
  if (!m) return null
  return m[1].split(/\s+/)[0]
}

const theme = fs.readFileSync(THEME, 'utf8')
const vueFiles = fs.readdirSync(COMPONENTS).filter(n => n.endsWith('.vue'))

console.log('=== 组件注册状态核对 ===')
console.log('组件目录 .vue 总数:', vueFiles.length)

const importOnly = []
for (const f of vueFiles) {
  const name = f.replace(/\.vue$/, '')
  const imported = new RegExp(`import\\s+${name}\\s+from`).test(theme)
  const registered = new RegExp(`app\\.component\\(\\s*['"]${name}['"]`).test(theme)
  if (!registered) {
    importOnly.push(name)
    console.log(`  ✗ ${name} 未注册（import=${imported ? '有' : '无'}）`)
  }
}
console.log('未注册组件数:', importOnly.length)
console.log('')

// ---- 渲染痕迹核对 ----
function walk(dir, filter) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p, filter))
    else if (filter(e.name)) out.push(p)
  }
  return out
}

// 收集 md 中所有自定义标签使用点
const mdFiles = walk(path.join(ROOT, 'guide'), n => n.endsWith('.md'))
const usage = new Map() // tag -> [{md, count}]
const known = new Set(vueFiles.map(f => f.replace(/\.vue$/, '')))
for (const m of mdFiles) {
  const src = fs.readFileSync(m, 'utf8')
  const rel = path.relative(ROOT, m).split(path.sep).join('/')
  for (const tag of new Set(src.match(/<([A-Z][A-Za-z0-9]*)\b/g) || [])) {
    const name = tag.slice(1)
    if (!known.has(name)) continue
    const n = (src.match(new RegExp(`<${name}\\b`, 'g')) || []).length
    if (!usage.has(name)) usage.set(name, [])
    usage.get(name).push({ md: rel, count: n })
  }
}

// ---- 构建期注入型组件 ----
// md 里不会出现 <StaticCodeBlock> / <QuizBlock> 字面量：它们由 .vitepress/config.ts
// 的 markdown-it 转换器在构建期生成标签。这类的「使用点」必须从**源文件特征**反推：
//   StaticCodeBlock ← 每个 ```python 代码块
//   QuizBlock       ← 每个含 <div class="quiz-option"> 的页面（每题一个）
const PY_FENCE_RE = /^```\s*(python|py)\s*$/gm
const QUIZ_OPT_RE = /<div\s+class="quiz-option"/g

// 计算每个 md 的 python fence 数
for (const m of mdFiles) {
  const src = fs.readFileSync(m, 'utf8')
  const rel = path.relative(ROOT, m).split(path.sep).join('/')
  const fences = (src.match(PY_FENCE_RE) || []).length
  if (fences > 0) {
    if (!usage.has('StaticCodeBlock')) usage.set('StaticCodeBlock', [])
    usage.get('StaticCodeBlock').push({ md: rel, count: fences })
  }
  // QuizBlock：题数 = 题面数（答案文件里有对应 key 的才算）
  const quizOpts = (src.match(QUIZ_OPT_RE) || []).length
  if (quizOpts > 0) {
    if (!usage.has('QuizBlock')) usage.set('QuizBlock', [])
    usage.get('QuizBlock').push({ md: rel, count: quizOpts, kind: 'quiz' })
  }
}

console.log('=== 渲染痕迹核对（md 使用点 → dist 产物） ===')
// 每个组件的「计数单位」不同，必须按组件语义分别判：
//   StaticCodeBlock ← 每个 python 代码块 1 个，产物里 class="scb" 出现 1 次/块
//   QuizBlock       ← 每个**题目** 1 个，产物里 class="qz-badge" 出现 1 次/题
//                    ⚠ 不能拿 <div class="quiz-option"> 的个数当题数 ——
//                      那是**选项数**（m11 每页 12 个 div = 3 题 × 4 选项）。
//   其它组件        ← 每个使用点 1 个
const COUNT_RULE = {
  QuizBlock: { class: 'qz-badge', unit: '题' },
  StaticCodeBlock: { class: 'scb', unit: '代码块' },
}

// 答案文件收录的页面 —— 只有这些页面才走 QuizBlock 转换
const ANSWER_KEYS = new Set(
  Object.keys(JSON.parse(fs.readFileSync(path.join(ROOT, '.vitepress', 'quiz-answers.json'), 'utf8')))
    .map(k => k.split(path.sep).join('/'))
)

let totalUse = 0, totalRendered = 0
const silent = []
for (const [name, sites] of usage) {
  const vueFile = path.join(COMPONENTS, name + '.vue')
  const rule = COUNT_RULE[name]
  const cls = rule ? rule.class : rootClassOf(vueFile)
  const unit = rule ? rule.unit : '处'
  let useCount = 0, rendered = 0
  for (const s of sites) {
    const dist = path.join(DIST, s.md.replace(/\.md$/, '.html'))
    if (!fs.existsSync(dist)) continue
    const html = fs.readFileSync(dist, 'utf8')
    // 该页的「应渲染数」按组件语义折算
    let expect = s.count
    if (name === 'QuizBlock') {
      // QuizBlock 只服务于「有答案数据 + 有题面标记」的页面：
      //   .vitepress/quiz-answers.json 收录的 13 个页面 → 走 QuizBlock 交互式
      //   其余页面（m01 三页、m04/4.4 等）→ 源文件里就是原生 onclick 形式，
      //   不经转换器、不应有 qz-badge，属设计如此，不计入缺失。
      const srcTxt = fs.readFileSync(path.join(ROOT, s.md), 'utf8')
      const qCount = (srcTxt.match(/\*\*\s*题目\s*\d+\s*\*\*/g) || []).length
      const rel = s.md.split(path.sep).join('/')
      if (!ANSWER_KEYS.has(rel) || qCount === 0) continue
      expect = qCount
    }
    useCount += expect
    if (!cls) { rendered += expect; continue }
    const inHtml = (html.match(new RegExp(`class="[^"]*\\b${cls}\\b`, 'g')) || []).length
    rendered += Math.min(expect, inHtml)
  }
  totalUse += useCount
  totalRendered += rendered
  const ok = rendered >= useCount
  if (!ok) silent.push({ name, cls, useCount, rendered, sites })
  console.log(`  ${ok ? '✓' : '✗'} ${name.padEnd(20)} 判据=${String(cls).padEnd(14)} md用${useCount}${unit} → 渲染${rendered}`)
}
console.log('')
console.log('md 使用点总计  :', totalUse)
console.log('产物中可渲染   :', totalRendered)
console.log('静默丢失       :', totalUse - totalRendered)
if (silent.length) {
  console.log('')
  console.log('--- 静默丢失明细 ---')
  silent.forEach(s => {
    console.log(`  ${s.name}（${s.sites.length} 个页面）`)
    s.sites.slice(0, 20).forEach(x => console.log(`     ${x.md}  用${x.count}次`))
  })
}
