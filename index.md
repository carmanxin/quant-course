---
layout: home

hero:
  name: QUANT LAB
  text: 量化交易系统设计与实践
  tagline: 从金融数学基础到实盘部署,系统化掌握 10 大模块 · 50+ 章节 · 9 个交互式计算器
  actions:
    - theme: brand
      text: 开始学习
      link: /guide/
    - theme: alt
      text: 模块概览
      link: /guide/#模块概览

features:
  - title: 金融数学基础
    details: 微观结构、资产定价、概率统计、时间序列、线性模型、相关性与协方差
  - title: 策略开发实战
    details: 双均线、统计套利、CTA 趋势、事件驱动、多因子组合、Kelly 仓位
  - title: Python 数据栈
    details: NumPy · Pandas · Scikit-learn · XGBoost · 代码示例 + 预计算运行结果
  - title: 回测与绩效评估
    details: 回测引擎原理、交易成本建模、夏普 / Calmar / 最大回撤、统计检验
  - title: 投资组合优化
    details: 均值方差、有效前沿、风险平价、蒙特卡洛 VaR、压力测试
  - title: 机器学习应用
    details: 监督学习选股、无监督聚类、NLP 舆情、另类数据、过拟合防御
---

<ClientOnly>
  <MarketDashboard />
</ClientOnly>

<ClientOnly>
  <TickerBar />
</ClientOnly>

## 课程亮点

<div class="vp-features-mini">

| 模块 | 核心技能 | 学习产物 |
|:----:|:--------|:--------|
| M1 - 行业认知 | 量化思维、发展史、策略分类 | 行业地图思维导图 |
| M2 - 数理工具 | 资产定价、时间序列、统计检验 | 概率与相关性计算器 |
| M3 - 数据工程 | Python 三件套、性能优化 | 配套交互沙箱 |
| M4 - 回测框架 | 引擎原理、成本建模、绩效归因 | 双均线回测工具 |
| M5 - 策略工坊 | 因子 / 双均线 / 统计套利 / CTA | 6 大策略代码模板 |
| M6 - 组合优化 | 均值方差、风险平价、VaR | 有效前沿与蒙特卡洛 |

</div>

<!--
================================================================
以下为内部视觉规范与组件库示例,只对维护者开放,不在站点展示。
如需查看源码请直接看 .vitepress/theme/style.css 与 components/
================================================================

## 组件库预览 · 按钮交互效果

下面展示 FinTech 主题中的所有按钮变体。鼠标悬停查看 **光斑扫描 + 缩放发光** 动效:

<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:24px 0;padding:24px;background:var(--ft-bg-soft);border-radius:16px;border:1px solid var(--ft-border)">

<ClientOnly>
  <AnimatedButton variant="primary" arrow to="/guide/">进入课程</AnimatedButton>
  <AnimatedButton variant="mint" arrow>立即体验</AnimatedButton>
  <AnimatedButton variant="cyan" arrow>开始计算</AnimatedButton>
  <AnimatedButton variant="purple" arrow>查看策略</AnimatedButton>
  <AnimatedButton variant="pink" arrow>风险预警</AnimatedButton>
  <AnimatedButton variant="gold" arrow>胜率分析</AnimatedButton>
  <AnimatedButton variant="outline" arrow>更多模块</AnimatedButton>
  <AnimatedButton variant="primary" size="lg" arrow>大尺寸主按钮</AnimatedButton>
  <AnimatedButton variant="primary" size="sm">小型</AnimatedButton>
</ClientOnly>

</div>

## 关键视觉规范

```css
/* 主品牌色 - 乐观绿(上涨) */
--ft-brand:   #00E5A0   /* Electric Mint */
--ft-brand-2: #00D4FF   /* Cyber Cyan    */
--ft-brand-3: #7C3AED   /* Royal Purple  */
--ft-brand-4: #FF0080   /* Hot Pink      */

/* 多空语义色 */
--ft-bull:    #00E5A0   /* 多 - 涨 */
--ft-bear:    #FF4D6D   /* 空 - 跌 */

/* 阴影发光 */
box-shadow: 0 0 32px rgba(0, 229, 160, .45);

/* Aurora 渐变 */
background: linear-gradient(135deg, #00E5A0 0%, #00D4FF 35%, #7C3AED 70%, #FF0080 100%);
```

内规结束
-->

## 开始学习

🎯 **零基础入门** · 建议从 [模块 1·量化全景](/guide/m01-overview/1.1-history) 开始

📈 **实战派选手** · 直接跳到 [模块 5·策略工坊](/guide/m05-strategies/5.2-dual-ma) 查看 6 大策略

🧮 **算法工程师** · 推荐 [模块 8·机器学习](/guide/m08-ml-alt-data/8.1-supervised) 与 [模块 17·数据工程](/guide/m17-data-engineering/17.5-feature-store)

⚡ **面试冲刺** · 专攻 [模块 20·面试准备](/guide/m20-interview-prep/20.1-math-stats)

<style scoped>
.vp-features-mini {
  margin: 32px 0;
  border: 1px solid var(--ft-border);
  border-radius: 16px;
  overflow: hidden;
  background: var(--ft-surface);
  box-shadow: 0 8px 24px rgba(13,26,56,.06);
}
.vp-features-mini table {
  border: none !important;
  border-radius: 0 !important;
  margin: 0;
}
.vp-features-mini th {
  background: linear-gradient(135deg, rgba(0,229,160,.08), rgba(0,212,255,.06)) !important;
  border-bottom: 2px solid var(--ft-brand) !important;
  font-weight: 700;
}
</style>
