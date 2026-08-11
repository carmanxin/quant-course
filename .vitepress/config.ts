import { defineConfig } from 'vitepress'

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
  description: 'FinTech 风格的量化交易学习平台 · 10 大模块 · 50+ 章节 · 9 个交互式计算器',
  lang: 'zh-CN',
  appearance: true,
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
      const defaultFence = md.renderer.rules.fence
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx]
        const info = (token.info || '').trim().split(/\s+/)[0]
        if (['python', 'py'].includes(info)) {
          const codeB64 = Buffer.from(token.content, 'utf8').toString('base64')
          const rendered = defaultFence!(tokens, idx, options, env, self)
          return `<StaticCodeBlock code-b64="${codeB64}" lang="${info}">${rendered}</StaticCodeBlock>`
        }
        return defaultFence!(tokens, idx, options, env, self)
      }
    },
  },
  // 排除非站点内容(便携包自身 + 内部研究报告)
  srcExclude: ['_reports/**', 'portable/**', 'tests/**'],
  ignoreDeadLinks: true,
  // 便携版输出位置（避免与 .vitepress/dist 的 safe-delete 冲突）
  outDir: process.env.QPORTABLE ? 'portable/dist' : '.vitepress/dist',
})
