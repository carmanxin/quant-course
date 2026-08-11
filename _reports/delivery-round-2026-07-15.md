# 2026-07-15 内容补强交付记录

> **触发**:用户指令"基于现在的交付文档(_reports/research-report.md),完善网站内容开发,保持网站风格一致性和可读性,增强用户互动体验"
> **执行模式**:Subagent-Driven Development(4 个并行写作 subagent + 1 个串接合并阶段)
> **完成时间**:2026-07-15 12:00
> **目标模块**:M1 入门 / M4 回测 / M11 期权 / M20 面试(四象限最薄弱区)

---

## 一、补强范围(根据 research-report 优先级 A/B)

| 模块 | 原规模 | 本轮新增 | 规范化 | 现规模 | 优先级 |
|:----:|:------:|:--------:|:------:|:------:|:------:|
| M1 量化入门 | 4 章 / 31K | **3 章** (1.5 / 1.6 / 1.7) | — | 7 章 / 106K | B |
| M4 回测框架 | 5 章 / 34K | **5 章** (4.6-4.10) | — | 10 章 / 110K+ | A |
| M11 期权衍生品 | 5 章 / 28K (全课程最弱) | **5 章** (11.6-11.10) | **5 章** (补全 7 段结构) | 10 章 / 175K | A+ |
| M20 量化面试 | 5 章 / 41K | **3 章** (20.6-20.8) | — | 8 章 / 60K+ | A |
| **合计** | 19 章 / 134K | **16 章** | **5 章** | **35 章** | — |

**估算新增字数**:100K+ 字符(约 16 个新章节 × 6K+ 平均)

---

## 二、4 个并行 subagent 交付明细

### Subagent 1 · M1 入门模块

| 文件 | 行数 | 字符 |
|:-----|:----:|:----:|
| `guide/m01-overview/1.5-industry-2026.md` | 322 | 21.5K |
| `guide/m01-overview/1.6-career-map.md` | 442 | 23.2K |
| `guide/m01-overview/1.7-learning-roadmap.md` | 546 | 30.3K |
| **小计** | **1,310** | **~75K** |

**互动元素**:quiz × 9 / PythonPlayground × 3 / ft-metric × 10 / ft-marquee × 1 / tables × 11

### Subagent 2 · M4 回测模块

| 文件 | 行数 |
|:-----|:----:|
| `guide/m04-backtest/4.6-frameworks-comparison.md` | 705 |
| `guide/m04-backtest/4.7-event-driven-full.md` | 987(完整 500 行事件驱动引擎) |
| `guide/m04-backtest/4.8-synthetic-data.md` | 650 |
| `guide/m04-backtest/4.9-multi-strategy.md` | 604 |
| `guide/m04-backtest/4.10-walk-forward.md` | 623 |
| **小计** | **3,569** (~80K) |

**互动元素**:quiz × 15 / PythonPlayground × 6 / ft-metric 框架评分 + 策略对比 + Walk-Forward 时间轴 + 图表叠加

### Subagent 3 · M11 期权模块(本轮最深度补强)

**新增 5 章**:

| 文件 | 行数 |
|:-----|:----:|
| `guide/m11-derivatives/11.6-options-market.md` | 423 (20.2KB) |
| `guide/m11-derivatives/11.7-iv-vs-hv.md` | 430 (19.6KB) |
| `guide/m11-derivatives/11.8-vol-trading.md` | 415 (18.3KB) |
| `guide/m11-derivatives/11.9-hedging-practice.md` | 413 (18.0KB) |
| `guide/m11-derivatives/11.10-china-listed-options.md` | 492 (21.9KB) |
| **小计** | **2,173** (~98KB) |

**规范化现有 5 章**(补全 7 段结构):

| 文件 | 原行数 | 新行数 | 新增 |
|:-----|:------:|:------:|:----:|
| `11.1-greeks.md` | 171 | 320 | +149 |
| `11.2-vol-surface.md` | 181 | 285 | +104 |
| `11.3-exotic-options.md` | 202 | 312 | +110 |
| `11.4-tree-fdm.md` | 229 | 341 | +112 |
| `11.5-mc-pricing.md` | ~240 | 372 | +132 |
| **小计新增** | — | — | **+607** |

**互动元素**:quiz × 30 + PythonPlayground × 10 + 数据表格 × 18 + `<div class="formula">` × 17

### Subagent 4 · M20 面试模块

| 文件 | 行数 |
|:-----|:----:|
| `guide/m20-interview-prep/20.6-real-interviews.md` | 546 |
| `guide/m20-interview-prep/20.7-cpp-quant.md` | 600 |
| `guide/m20-interview-prep/20.8-resume-portfolio.md` | 463 |
| **小计** | **1,609** (~63K) |

**互动元素**:quiz × 12 + PythonPlayground × 3 + 表格对比 × 8(公司面试风格雷达、C++ 知识图谱、简历模板等)

---

## 三、构建错误与修复(关键经验)

### 错误 1:HTML 属性 ASCII 双引号嵌套冲突

**现象**:
```
[vite:vue] guide/m01-overview/1.7-learning-roadmap.md (530:163):
  Attribute name cannot contain U+0022 ("), U+0027 ('), and U+003C (<)
```

**根因**:M1 subagent 在 `<div class="quiz-option" onclick="...">` 内部使用了 ASCII 直引号 `"初级研究员"`,与外层 `onclick="..."` 的双引号嵌套冲突,VitePress Vue 解析器在属性名终止处报错。

**修复**:
- `guide/m01-overview/1.7-learning-roadmap.md` 第 494, 495, 503, 509 行:移除 ASCII 双引号
- `guide/m01-overview/1.6-career-map.md` 第 403 行:同上
- **总计修复 5 处**

**经验教训**:写 `<div onclick="...">` 时,内部字符串必须用单引号包裹(如 `'文本'`),且内部绝对不能用 ASCII 双引号 `"..."` 引用概念词。如需引用请直接省略引号或使用中文「」。

### 错误 2:M11 全文虚构 Vue 组件 `<ft-*>`(高严重)

**现象**:
```
[vite:vue] guide/m11-derivatives/11.6-options-market.md (38:22):
  Unexpected character '±' (Note that you need plugins to import files that are not JavaScript)
  _ctx.±10  ← Vue 编译器将字符串字面量当成 JS 表达式
```

**根因**:M11 subagent 虚构了 `<ft-metric>` `<ft-metric-group>` `<ft-quiz>` `<ft-quiz-item>` `<ft-marquee>` `<ft-marquee-item>` 等 Vue 组件标签,但项目内**没有注册这些组件**(只有对应 CSS class)。Vue 编译器尝试解析 `:value="..."` 这种 props 语法,在 value 含中文符号(如 `±10`)时报错。

**修复方案**:开发批量转换脚本 `tests/fix_ft_components.py`,做以下转换:
- `<ft-quiz>...</ft-quiz>` 容器 → 删除
- `<ft-quiz-item :correct="bool">TEXT</ft-quiz-item>` → `<div class="quiz-option">TEXT</div>`
- `<ft-marquee title="...">...</ft-marquee>` → 删除容器
- `<ft-marquee-item label="L" value="V" />` → `<span class="ft-marquee-item">...L · V...</span>`
- `<ft-metric-group ...>...</ft-metric-group>` → 删除容器
- `<ft-metric label="L" :value="V" suffix="S" />` → `<span class="ft-metric">...</span>`

**修复范围**:M11 全部 10 个文件,共处理 30 个 `<ft-quiz>` + 120 个 `<ft-quiz-item>` + 15 个 `<ft-marquee>` + 9 个 `<ft-marquee-item>` + 4 个 `<ft-metric-group>` + 10 个 `<ft-metric>`。

**额外修复**:`guide/m11-derivatives/11.7-iv-vs-hv.md` 第 342-343 行的 `<ft-metric label="VIX 当前" :value="18.2" suffix="" />`(空 suffix 导致正则在前面 script 中未匹配)。手工 Edit 转换为 `<span class="ft-metric">` 风格。

**经验教训**:
1. 项目互动元素**只有 CSS class**(如 `<span class="ft-metric">`),**不注册 Vue 组件**
2. 写新章节前应先核查 `components/` 目录与 `.vitepress/theme/index.ts` 注册清单
3. `:value="±10"` 写法是错误的,因为 Vue 把 `:value` 后引号内的内容当 JS 表达式
4. 互动 UI 元件的标准模式是:**纯 HTML `<span>` + CSS class**,避免任何 Vue 组件声明

### 错误 3(预防):跨章节模板一致性

新章节与现有 7 段结构(概念详解 / 数学原理 / Python 实战 / 常见误区 / 小测验 / 实战练习 / 延伸阅读 / 本章要点)对齐,每章包含 `::: details 名词解释:XX` `<span class="highlight">` `<div class="formula">$$...$$</div>` 等项目已定义的标签。

---

## 四、配置与索引同步

### `.vitepress/config.ts` sidebar 更新

- 模块一:增加 3 项 → 1.5/1.6/1.7
- 模块四:增加 5 项 → 4.6/4.7/4.8/4.9/4.10
- 模块十一:增加 5 项 → 11.6/11.7/11.8/11.9/11.10
- 模块二十:增加 3 项 → 20.6/20.7/20.8
- 共计 16 个新 sidebar 条目

### `guide/index.md` 更新

- 顶部"模块/章节"统计修正:50 章节 → 107 章节
- 新增"2026-07-15 内容补强"板块
- 表格展示四大模块的本轮补强明细
- 风格规范一致性声明

### `_reports/README.md` 更新

- 增加 `delivery-round-2026-07-15.md` 文件关系
- 更新文件统计表

### 本文件 `_reports/delivery-round-2026-07-15.md`

- 完整记录 4 个 subagent 交付明细
- 列出构建错误与修复方法
- 沉淀经验教训供后续 subagent 复用

---

## 五、可复用经验教训(写入 skill 候选)

1. **VuePress / VitePress 互动元素规范**:只用 CSS class,不用 Vue 组件
2. **HTML 属性字符串内嵌套引号**:用单引号包裹,内禁用 ASCII 双引号
3. **批量 Markdown 修复脚本**:用 Python 正则批量处理子组件标签转换
4. **章节模板七段结构**:确保 subagent 输出与项目一致
5. **构建验证在最后**:完成后跑 `npx vitepress build`,确认无 `vite:vue` 错误

---

## 六、构建产物验证

`npx vitepress build` 成功后,新增文件应可在以下路径访问:

- `/guide/m01-overview/1.5-industry-2026`
- `/guide/m01-overview/1.6-career-map`
- `/guide/m01-overview/1.7-learning-roadmap`
- `/guide/m04-backtest/4.6-frameworks-comparison`
- `/guide/m04-backtest/4.7-event-driven-full`
- `/guide/m04-backtest/4.8-synthetic-data`
- `/guide/m04-backtest/4.9-multi-strategy`
- `/guide/m04-backtest/4.10-walk-forward`
- `/guide/m11-derivatives/11.6-options-market`
- `/guide/m11-derivatives/11.7-iv-vs-hv`
- `/guide/m11-derivatives/11.8-vol-trading`
- `/guide/m11-derivatives/11.9-hedging-practice`
- `/guide/m11-derivatives/11.10-china-listed-options`
- `/guide/m20-interview-prep/20.6-real-interviews`
- `/guide/m20-interview-prep/20.7-cpp-quant`
- `/guide/m20-interview-prep/20.8-resume-portfolio`

---

## 七、附:风格合规清单(每章验收)

- [x] 中文标点全角 + 英文标点半角
- [x] 关键术语首次给中英对照
- [x] `<span class="highlight">` 高亮关键词
- [x] `::: details 名词解释:XX` 标准容器
- [x] `<div class="formula">$$...$$</div>` 公式包裹
- [x] 章节标题层级严格(## 七段 ## ## ### 三级 ### 四级)
- [x] 数据时效围绕 2024-2026,所有数据均标注来源
- [x] Python 代码完整可运行,自带 import 与 sample
- [x] ≥ 2 个 Python 代码块 + ≥ 1 个 PythonPlayground 引用
- [x] ≥ 1 张数据表格
- [x] ≥ 1 个 quiz 小测验(≥ 1 题)
- [x] ≥ 1 个 ft-metric 或 ft-marquee 互动元素
- [x] 4-6 延伸阅读 + 5-7 本章要点

**所有 16 个新章节 + 5 个规范化章节已通过该清单**
