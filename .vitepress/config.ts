import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const sidebar = [
    {
      text: '模块一：量化交易全景与行业认知',
      collapsed: false,
      items: [
        { text: '1.1 发展史与生态', link: '/guide/m01-overview/1.1-history' },
        { text: '1.2 策略分类', link: '/guide/m01-overview/1.2-strategy-types' },
        { text: '1.3 量化思维核心', link: '/guide/m01-overview/1.3-quant-mindset' },
        { text: '1.4 现实挑战', link: '/guide/m01-overview/1.4-challenges' },
        { text: '1.5 行业格局 2024-2026', link: '/guide/m01-overview/1.5-industry-2026' },
        { text: '1.6 岗位图谱与能力模型', link: '/guide/m01-overview/1.6-career-map' },
        { text: '1.7 学习路径与坑点', link: '/guide/m01-overview/1.7-learning-roadmap' },
      ]
    },
  {
    text: '模块二：金融基础与数理工具',
    collapsed: true,
    items: [
      { text: '2.1 市场微观结构', link: '/guide/m02-finance-math/2.1-microstructure' },
      { text: '2.2 资产定价基础', link: '/guide/m02-finance-math/2.2-asset-pricing' },
      { text: '2.3 概率统计与相关性', link: '/guide/m02-finance-math/2.3-prob-stats' },
      { text: '2.4 时间序列分析', link: '/guide/m02-finance-math/2.4-time-series' },
      { text: '2.5 线性模型与正则化', link: '/guide/m02-finance-math/2.5-linear-models' },
    ]
  },
  {
    text: '模块三：Python 量化编程与数据工程',
    collapsed: true,
    items: [
      { text: '3.1 Python数据栈', link: '/guide/m03-python-data/3.1-python-stack' },
      { text: '3.2 数据获取与清洗', link: '/guide/m03-python-data/3.2-data-cleaning' },
      { text: '3.3 性能优化', link: '/guide/m03-python-data/3.3-performance' },
      { text: '3.4 金融数据特色处理', link: '/guide/m03-python-data/3.4-fin-data' },
      { text: '3.5 可视化与探索', link: '/guide/m03-python-data/3.5-visualization' },
    ]
  },
  {
    text: '模块四：回测框架与绩效评估',
    collapsed: true,
    items: [
      { text: '4.1 回测引擎原理', link: '/guide/m04-backtest/4.1-engine' },
      { text: '4.2 交易成本建模', link: '/guide/m04-backtest/4.2-cost-model' },
      { text: '4.3 绩效指标全景', link: '/guide/m04-backtest/4.3-metrics' },
      { text: '4.4 回测陷阱与对策', link: '/guide/m04-backtest/4.4-pitfalls' },
      { text: '4.5 统计检验', link: '/guide/m04-backtest/4.5-stat-tests' },
      { text: '4.6 主流回测框架横评', link: '/guide/m04-backtest/4.6-frameworks-comparison' },
      { text: '4.7 完整事件驱动回测实战', link: '/guide/m04-backtest/4.7-event-driven-full' },
      { text: '4.8 合成数据回测', link: '/guide/m04-backtest/4.8-synthetic-data' },
      { text: '4.9 多策略组合回测', link: '/guide/m04-backtest/4.9-multi-strategy' },
      { text: '4.10 Walk-Forward 滚动回测', link: '/guide/m04-backtest/4.10-walk-forward' },
    ]
  },
  {
    text: '模块五：策略开发工坊',
    collapsed: true,
    items: [
      { text: '5.1 因子投资体系', link: '/guide/m05-strategies/5.1-factors' },
      { text: '5.2 双均线策略模拟', link: '/guide/m05-strategies/5.2-dual-ma' },
      { text: '5.3 统计套利', link: '/guide/m05-strategies/5.3-stat-arb' },
      { text: '5.4 CTA趋势跟踪', link: '/guide/m05-strategies/5.4-cta' },
      { text: '5.5 事件驱动策略', link: '/guide/m05-strategies/5.5-event-driven' },
      { text: '5.6 多因子组合与择时', link: '/guide/m05-strategies/5.6-multi-factor' },
    ]
  },
  {
    text: '模块六：投资组合管理与优化',
    collapsed: true,
    items: [
      { text: '6.1 均值-方差优化', link: '/guide/m06-portfolio/6.1-mvo' },
      { text: '6.2 风险平价与分散度', link: '/guide/m06-portfolio/6.2-risk-parity' },
      { text: '6.3 动态权重管理', link: '/guide/m06-portfolio/6.3-kelly' },
      { text: '6.4 约束处理', link: '/guide/m06-portfolio/6.4-constraints' },
      { text: '6.5 压力测试与VaR', link: '/guide/m06-portfolio/6.5-var' },
    ]
  },
  {
    text: '模块七：执行算法与微观结构',
    collapsed: true,
    items: [
      { text: '7.1 订单类型与风险', link: '/guide/m07-execution/7.1-order-types' },
      { text: '7.2 算法执行原理', link: '/guide/m07-execution/7.2-algo-execution' },
      { text: '7.3 做市策略思想', link: '/guide/m07-execution/7.3-market-making' },
      { text: '7.4 高频交易简介', link: '/guide/m07-execution/7.4-hft' },
      { text: '7.5 执行成本分析', link: '/guide/m07-execution/7.5-tca' },
    ]
  },
  {
    text: '模块八：机器学习与另类数据',
    collapsed: true,
    items: [
      { text: '8.1 监督学习选股', link: '/guide/m08-ml-alt-data/8.1-supervised' },
      { text: '8.2 无监督与降维', link: '/guide/m08-ml-alt-data/8.2-unsupervised' },
      { text: '8.3 NLP应用', link: '/guide/m08-ml-alt-data/8.3-nlp' },
      { text: '8.4 另类数据', link: '/guide/m08-ml-alt-data/8.4-alt-data' },
      { text: '8.5 过拟合防御', link: '/guide/m08-ml-alt-data/8.5-overfitting' },
    ]
  },
  {
    text: '模块九：实盘部署与系统架构',
    collapsed: true,
    items: [
      { text: '9.1 量化系统设计', link: '/guide/m09-live-trading/9.1-system-design' },
      { text: '9.2 实时数据管道', link: '/guide/m09-live-trading/9.2-data-pipeline' },
      { text: '9.3 模拟与实盘对接', link: '/guide/m09-live-trading/9.3-broker-api' },
      { text: '9.4 策略监控与运维', link: '/guide/m09-live-trading/9.4-monitoring' },
      { text: '9.5 合规与监管', link: '/guide/m09-live-trading/9.5-compliance' },
    ]
  },
  {
    text: '模块十：前沿专题与职业成长',
    collapsed: true,
    items: [
      { text: '10.1 强化学习交易', link: '/guide/m10-frontier/10.1-rl' },
      { text: '10.2 生成式AI', link: '/guide/m10-frontier/10.2-gen-ai' },
      { text: '10.3 暗池', link: '/guide/m10-frontier/10.3-dark-pool' },
      { text: '10.4 团队分工', link: '/guide/m10-frontier/10.4-career' },
      { text: '10.5 终极项目', link: '/guide/m10-frontier/10.5-final-project' },
    ]
  },
  {
    text: '模块十一：期权与衍生品定价进阶',
    collapsed: true,
    items: [
      { text: '11.1 期权 Greeks 详解', link: '/guide/m11-derivatives/11.1-greeks' },
      { text: '11.2 波动率曲面与套利', link: '/guide/m11-derivatives/11.2-vol-surface' },
      { text: '11.3 奇异期权与结构化产品', link: '/guide/m11-derivatives/11.3-exotic-options' },
      { text: '11.4 二叉树与有限差分法', link: '/guide/m11-derivatives/11.4-tree-fdm' },
      { text: '11.5 蒙特卡洛定价进阶', link: '/guide/m11-derivatives/11.5-mc-pricing' },
      { text: '11.6 期权市场基础', link: '/guide/m11-derivatives/11.6-options-market' },
      { text: '11.7 隐含波动率 vs 历史波动率', link: '/guide/m11-derivatives/11.7-iv-vs-hv' },
      { text: '11.8 波动率交易策略', link: '/guide/m11-derivatives/11.8-vol-trading' },
      { text: '11.9 套保策略实战', link: '/guide/m11-derivatives/11.9-hedging-practice' },
      { text: '11.10 场内期权策略中国 A 股', link: '/guide/m11-derivatives/11.10-china-listed-options' },
    ]
  },
  {
    text: '模块十二：固定收益量化',
    collapsed: true,
    items: [
      { text: '12.1 收益率曲线建模', link: '/guide/m12-fixed-income/12.1-yield-curve' },
      { text: '12.2 久期与凸度免疫', link: '/guide/m12-fixed-income/12.2-duration-convexity' },
      { text: '12.3 利率互换与互换期权', link: '/guide/m12-fixed-income/12.3-irs-swaption' },
      { text: '12.4 信用利差与CDS', link: '/guide/m12-fixed-income/12.4-credit-spread' },
      { text: '12.5 MBS与资产证券化', link: '/guide/m12-fixed-income/12.5-mbs' },
    ]
  },
  {
    text: '模块十三：加密货币量化',
    collapsed: true,
    items: [
      { text: '13.1 链上数据分析', link: '/guide/m13-crypto/13.1-onchain' },
      { text: '13.2 资金费率与套利', link: '/guide/m13-crypto/13.2-funding-rate' },
      { text: '13.3 MEV与交易排序', link: '/guide/m13-crypto/13.3-mev' },
      { text: '13.4 DEX流动性做市', link: '/guide/m13-crypto/13.4-dex-mm' },
      { text: '13.5 永续合约策略', link: '/guide/m13-crypto/13.5-perps' },
    ]
  },
  {
    text: '模块十四：市场微观结构深度',
    collapsed: true,
    items: [
      { text: '14.1 订单流毒性模型', link: '/guide/m14-microstructure-deep/14.1-toxicity' },
      { text: '14.2 Kyle与Glosten-Milgrom', link: '/guide/m14-microstructure-deep/14.2-information-models' },
      { text: '14.3 最优执行理论', link: '/guide/m14-microstructure-deep/14.3-optimal-execution' },
      { text: '14.4 限价订单簿动力学', link: '/guide/m14-microstructure-deep/14.4-lob-dynamics' },
      { text: '14.5 高频做市策略进阶', link: '/guide/m14-microstructure-deep/14.5-hft-mm-advanced' },
    ]
  },
  {
    text: '模块十五：宏观经济量化',
    collapsed: true,
    items: [
      { text: '15.1 宏观因子模型', link: '/guide/m15-macro/15.1-macro-factors' },
      { text: '15.2 美联储政策量化', link: '/guide/m15-macro/15.2-fed-policy' },
      { text: '15.3 通胀预期建模', link: '/guide/m15-macro/15.3-inflation' },
      { text: '15.4 经济周期择时', link: '/guide/m15-macro/15.4-cycle-timing' },
      { text: '15.5 跨资产宏观策略', link: '/guide/m15-macro/15.5-cross-asset' },
    ]
  },
  {
    text: '模块十六：风险管理体系',
    collapsed: true,
    items: [
      { text: '16.1 风险分解与归因', link: '/guide/m16-risk-management/16.1-risk-decomposition' },
      { text: '16.2 极值理论与尾部风险', link: '/guide/m16-risk-management/16.2-evt-tail' },
      { text: '16.3 压力测试与情景分析', link: '/guide/m16-risk-management/16.3-stress-testing' },
      { text: '16.4 巴塞尔协议与监管资本', link: '/guide/m16-risk-management/16.4-basel' },
      { text: '16.5 尾部对冲策略', link: '/guide/m16-risk-management/16.5-tail-hedge' },
    ]
  },
  {
    text: '模块十七：量化数据工程',
    collapsed: true,
    items: [
      { text: '17.1 Tick数据库设计', link: '/guide/m17-data-engineering/17.1-tick-db' },
      { text: '17.2 实时ETL管道', link: '/guide/m17-data-engineering/17.2-realtime-etl' },
      { text: '17.3 数据质量监控', link: '/guide/m17-data-engineering/17.3-data-quality' },
      { text: '17.4 批处理与流处理', link: '/guide/m17-data-engineering/17.4-batch-streaming' },
      { text: '17.5 特征存储(Feature Store)', link: '/guide/m17-data-engineering/17.5-feature-store' },
    ]
  },
  {
    text: '模块十八：策略生命周期管理',
    collapsed: true,
    items: [
      { text: '18.1 策略孵化与评审', link: '/guide/m18-strategy-lifecycle/18.1-incubation' },
      { text: '18.2 模拟盘与实盘过渡', link: '/guide/m18-strategy-lifecycle/18.2-paper-to-live' },
      { text: '18.3 A/B测试与金丝雀发布', link: '/guide/m18-strategy-lifecycle/18.3-ab-testing' },
      { text: '18.4 策略绩效归因', link: '/guide/m18-strategy-lifecycle/18.4-attribution' },
      { text: '18.5 策略退役与复盘', link: '/guide/m18-strategy-lifecycle/18.5-retirement' },
    ]
  },
  {
    text: '模块十九：中国A股特色量化',
    collapsed: true,
    items: [
      { text: '19.1 涨跌停板策略', link: '/guide/m19-a-share/19.1-limit-up' },
      { text: '19.2 打新策略分析', link: '/guide/m19-a-share/19.2-ipo' },
      { text: '19.3 行业轮动模型', link: '/guide/m19-a-share/19.3-sector-rotation' },
      { text: '19.4 北向资金与龙虎榜', link: '/guide/m19-a-share/19.4-northbound' },
      { text: '19.5 政策因子与事件驱动', link: '/guide/m19-a-share/19.5-policy-events' },
    ]
  },
  {
    text: '模块二十：量化面试准备',
    collapsed: true,
    items: [
      { text: '20.1 数学与统计面试题', link: '/guide/m20-interview-prep/20.1-math-stats' },
      { text: '20.2 编程与算法题', link: '/guide/m20-interview-prep/20.2-coding' },
      { text: '20.3 金融与策略题', link: '/guide/m20-interview-prep/20.3-finance' },
      { text: '20.4 脑筋急转弯与行为面', link: '/guide/m20-interview-prep/20.4-brain-teasers' },
      { text: '20.5 模拟面试与复盘', link: '/guide/m20-interview-prep/20.5-mock-interview' },
      { text: '20.6 高频面试题(中外机构)', link: '/guide/m20-interview-prep/20.6-real-interviews' },
      { text: '20.7 C++ 量化面试专题', link: '/guide/m20-interview-prep/20.7-cpp-quant' },
      { text: '20.8 Research 项目包装', link: '/guide/m20-interview-prep/20.8-resume-portfolio' },
    ]
  },
]

export default defineConfig({
  title: 'QuantLab · 量化交易系统设计与实践',
  description: 'FinTech 风格的量化交易学习平台 · 20 大模块 · 120+ 章节 · 8 个交互式计算器 · 439 个 Python 实战案例',
  lang: 'zh-CN',
  appearance: true,
  cleanUrls: true,
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#00E5A0' }],
    ['meta', { name: 'description', content: 'FinTech 风格的量化交易学习平台' }],
  ],
  themeConfig: {
    sidebar,
    nav: [
      { text: '课程首页', link: '/' },
      { text: '模块概览', link: '/guide/' },
    ],
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索文档' },
          modal: { noResultsText: '无结果', resetButtonTitle: '清除', displayDetails: '显示详情', footer: { selectText: '选择', closeText: '关闭' } }
        }
      }
    },
    docFooter: { prev: '上一章', next: '下一章' },
    darkModeSwitchLabel: '主题切换',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '回到顶部',
    outline: { label: '本页目录' },
  },
  markdown: {
    math: true,
    config(md) {
      // ============ 自动给所有 python 代码块加 StaticCodeBlock 容器 ============
      // 把 ```python ``` 块改写成 <StaticCodeBlock code-b64="..." lang="...">...</StaticCodeBlock>
      // 默认 Shiki 高亮保留(由 Vue 渲染插槽 HTML 保留)
      //
      // 运行结果在构建期直接内联进 output-json prop:
      //   1. 对 fence 内容算 FNV-1a hash（与组件端一致）
      //   2. 查 public/code/_index.json（由 scripts/build-code-index.py 生成）
      //   3. 命中则读对应 <name>.output.json 内联到组件
      // 这样折叠块内容已写死在 HTML 里，浏览器无需 fetch，file:// 打开也能显示。
      const defaultFence = md.renderer.rules.fence
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx]
        const info = (token.info || '').trim().split(/\s+/)[0]
        if (['python', 'py'].includes(info)) {
          const codeB64 = Buffer.from(token.content, 'utf8').toString('base64')
          const rendered = defaultFence!(tokens, idx, options, env, self)
          // 运行结果 base64 内联进 output-b64（attr 安全，无转义地狱；组件端解码）
          const outputB64 = inlineOutputB64(token.content, env)
          const inline = outputB64
            ? ` output-b64="${outputB64}"`
            : ''
          return `<StaticCodeBlock code-b64="${codeB64}" lang="${info}"${inline}>${rendered}</StaticCodeBlock>`
        }
        return defaultFence!(tokens, idx, options, env, self)
      }

      // ============ 小测验 → 交互式 QuizBlock ============
      // 把「题目文本 + 若干 <div class="quiz-option">…</div>」转换成
      // <QuizBlock question-b64 options-b64 answer explain-b64>
      // 正确答案与解析来自 .vitepress/quiz-answers.json（key = 相对路径 + 题号）。
      // 找不到答案的题目保持原样，不会退化成"点了没反应"。
      let _quizCache: Record<string, Record<string, { answer: string; explain: string }>> | null = null
      function loadQuizAnswers() {
        if (_quizCache) return _quizCache
        try {
          _quizCache = JSON.parse(
            fs.readFileSync(path.join(__dirname, 'quiz-answers.json'), 'utf8'),
          )
        } catch {
          _quizCache = {}
        }
        return _quizCache!
      }
      function b64(s: string): string {
        return Buffer.from(s, 'utf8').toString('base64')
      }
      const OPTION_RE = /<div\s+class="quiz-option"[^>]*>([\s\S]*?)<\/div>/g
      const TITLE_RE = /^\s*\*\*题目\s*(\d+)\s*\*\*\s*[:：]?\s*/

      md.core.ruler.push('quiz-block', (state) => {
        const rel = (state.env as any)?.relativePath
        if (!rel) return false
        const answers = loadQuizAnswers()[String(rel).replace(/\\/g, '/')]
        if (!answers) return false

        const tokens = state.tokens
        const out: typeof tokens = []
        let quizIdx = 0
        let changed = false

        const isQuizBlock = (t: any) => t.type === 'html_block' && /class="quiz-option"/.test(t.content)

        for (let i = 0; i < tokens.length; i++) {
          const t = tokens[i] as any
          if (!isQuizBlock(t)) { out.push(t); continue }

          // 收集紧随其后的其它 quiz-option html_block（有些文件中间有空行会断块）
          const blocks = [t]
          let j = i + 1
          while (j < tokens.length && isQuizBlock(tokens[j] as any)) {
            blocks.push(tokens[j] as any); j++
          }

          // 从原始 HTML 里抠出每个选项
          const options: string[] = []
          for (const b of blocks) {
            let m: RegExpExecArray | null
            OPTION_RE.lastIndex = 0
            while ((m = OPTION_RE.exec(b.content))) options.push(m[1].trim())
          }
          if (options.length < 2) { out.push(t); continue }

          // 往前找题面：末尾的 paragraph 组 + 可选的 heading 组（heading 在前）
          const qTokens: any[] = []
          const takeGroup = (closeType: string, openType: string) => {
            if (out.length < 3) return false
            const c = out[out.length - 1], mid = out[out.length - 2], o = out[out.length - 3]
            if (c.type !== closeType || o.type !== openType || mid.type !== 'inline') return false
            qTokens.unshift(o, mid, c)
            out.length -= 3
            return true
          }
          takeGroup('paragraph_close', 'paragraph_open')
          takeGroup('heading_close', 'heading_open')
          if (!qTokens.length) { out.push(t); continue }

          let qRaw = ''
          for (const qt of qTokens) if (qt.type === 'inline') qRaw += (qRaw ? '<br>' : '') + qt.content
          const numMatch = qRaw.match(TITLE_RE)
          const num = numMatch ? numMatch[1] : String(++quizIdx)
          qRaw = qRaw.replace(TITLE_RE, '')

          const ans = answers[String(num)]
          if (!ans) {
            // 无答案数据 → 原样输出，避免破坏已有可交互版本
            out.push(...qTokens, ...blocks)
            i = j - 1
            continue
          }

          // 题面 / 选项 / 解析都走 markdown inline，让 $...$ 公式正常渲染
          const qHtml = md.renderInline(qRaw)
          const optHtml = options.map((o) => md.renderInline(o.replace(/\s*\n\s*/g, ' ').trim()))
          const explainHtml = md.renderInline(ans.explain)

          const attrs = [
            `num="${num}"`,
            `question="${b64(qHtml)}"`,
            `options="${b64(JSON.stringify(optHtml))}"`,
            `answer="${ans.answer}"`,
            `explain="${b64(explainHtml)}"`,
          ].join(' ')
          const quizToken = new state.Token('html_block', '', 0)
          quizToken.content = `<QuizBlock ${attrs}></QuizBlock>\n`
          out.push(quizToken)
          changed = true
          i = j - 1
        }

        if (changed) state.tokens = out
        return false
      })

      // FNV-1a 32-bit（与 StaticCodeBlock.vue / build-code-index.py 一致）
      function fnv1a(str: string): string {
        let h = 0x811c9dc5
        for (let i = 0; i < str.length; i++) {
          h ^= str.charCodeAt(i)
          h = Math.imul(h, 0x01000193)
        }
        return (h >>> 0).toString(16).padStart(8, '0')
      }
      // 归一化（与组件端 normalizeCode 一致）
      function normalizeCode(raw: string): string {
        return raw
          .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
          .replace(/\r\n/g, '\n')
          .replace(/[ \t]+$/gm, '')
          .trim()
      }
      // 计算当前页面到站点根(code/)的相对前缀，供 svgs 路径相对化（file:// 可用）
      function relPrefixFromEnv(env: any): string {
        const rel = (env && (env.relativePath || env.page)) || ''
        const parts = rel.split('/')
        parts.pop() // 去掉文件名
        return parts.map(() => '../').join('')
      }
      // 构建期查找输出并 base64 内联；找不到返回 null（组件显示"暂无运行结果"）
      // svgs 里的 /code/... 绝对路径改写为相对路径（base='./' + file:// 场景）
      // 缓存 _index.json 与每个 *.output.json，避免每 fence 都做 fs.readFileSync（Windows 慢）
      let _indexCache: Record<string, string> | null = null
      const _outputCache = new Map<string, any>()
      function inlineOutputB64(code: string, env: any): string | null {
        try {
          const hash = fnv1a(normalizeCode(code))
          if (!_indexCache) {
            _indexCache = JSON.parse(
              fs.readFileSync(path.join(__dirname, '../public/code/_index.json'), 'utf8'),
            )
          }
          const name = _indexCache[hash]
          if (!name) return null
          let out = _outputCache.get(name)
          if (!out) {
            out = JSON.parse(
              fs.readFileSync(path.join(__dirname, `../public/code/${name}.output.json`), 'utf8'),
            )
            _outputCache.set(name, out)
          }
          // 把 svgs 绝对路径改为相对当前页面的路径
          if (Array.isArray(out.svgs)) {
            const prefix = relPrefixFromEnv(env)
            out.svgs = out.svgs.map((s: string) =>
              s.replace(/^\/code\//, `${prefix}code/`),
            )
          }
          return Buffer.from(JSON.stringify(out), 'utf8').toString('base64')
        } catch (e) {
          return null
        }
      }
    },
  },
  // 排除非站点内容(便携包自身 + 内部研究报告 + spec/plan 等)
  // DEPLOY.md 是给维护者看的部署手册（含仓库结构、Secret 配置等运维信息），
  // 不应作为站点页面对外展示，故从构建中排除。
  srcExclude: ['_reports/**', 'portable/**', 'tests/**', 'docs/superpowers/**', 'DEPLOY.md'],
  ignoreDeadLinks: true,
  // 控制并发渲染数（默认 64 在 Windows 上易卡住；调到 8 缓解 file:// 兼容场景）
  buildConcurrency: 8,
  // 便携版输出位置（避免与 .vitepress/dist 的 safe-delete 冲突）
  outDir: process.env.QPORTABLE ? 'portable/dist' : '.vitepress/dist',
  vite: {
    plugins: [
      {
        name: 'quantlab-strip-woff2-preload',
        transformIndexHtml(html) {
          // VitePress 默认主题 head 会注入 Inter 字体的 woff2 preload，
          // 但项目 CSS 用的是 PingFang/YaHei，这个 preload 永远不会被命中，
          // 触发控制台 "preloaded but not used within a few seconds" 警告。
          return html.replace(
            /<link rel="preload"[^>]*\.woff2[^>]*>\s*/g,
            ''
          )
        }
      }
    ],
    build: {
      rollupOptions: {
        output: {
          // 把 echarts 拆成独立 vendor chunk：theme 不再背 950KB 图表库，
          // 包含 echarts 组件的页面才会预加载这个 chunk
          manualChunks(id) {
            if (id.includes('node_modules/echarts')) return 'echarts-vendor'
          }
        }
      }
    }
  },
})
