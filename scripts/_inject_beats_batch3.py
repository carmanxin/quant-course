# -*- coding: utf-8 -*-
# ① 第三批: m12/m13/m14/m17/m18/m20.1-5 各页补 常见误区 + 本章要点
# 用法: python scripts/_inject_beats_batch3.py
import io

CONTENT = {
# ================= m12 固收 =================
'guide/m12-fixed-income/12.1-yield-curve.md': '''
## 常见误区

**误区1：到期收益率是"未来的收益保证"。** YTM 隐含"票息按同一利率再投资"的假设，利率变动时实际收益会偏离 YTM。

**误区2：远期利率是对未来的预测。** 远期利率是无套利框架下从即期曲线推演的市场定价，包含期限溢价，不是预测值。

**误区3：收益率曲线三主成分的解释力放之四海皆准。** 水平/斜率/曲率三因子在美国国债解释力超 95%，但在新兴市场或信用债中占比结构不同。

**误区4：Nelson-Siegel 参数可以直接跨市场比较。** NS/Svensson 的四参数（水平/斜率/曲率/曲率衰减）依赖于样本与估计方法，数值本身不具可比性。

## 本章要点

- <span class="highlight">即期利率</span>是贴现率之锚，<span class="highlight">远期利率</span>由即期曲线无套利推出，<span class="highlight">YTM</span> 是两者的加权近似
- <span class="highlight">Nelson-Siegel</span> 四参数对应曲线的水平、斜率、曲率与衰减速度
- 曲线变动可分解为<span class="highlight">平移、扭转、蝶式</span>三个正交主成分
- 曲线策略（骑乘、杠铃 vs 子弹）对<span class="highlight">关键期限</span>的敏感度不同，需用关键利率久期管理
''',
'guide/m12-fixed-income/12.2-duration-convexity.md': '''
## 常见误区

**误区1：用久期线性外推大幅利率变动。** 久期只是一阶近似，利率大幅波动时凸度项（二阶）不可忽略，含权债甚至会出现负凸度。

**误区2：凸度越大越好。** 买入凸度（如期权）是有成本的——在凸度与收益率之间权衡，"凸度崇拜"会买进一篮子低收益资产。

**误区3：修正久期适用于所有债券。** 含权债（可赎回、MBS）的现金流随利率变化，修正久期失真，需用有效久期（OAS 框架）。

**误区4：免疫策略一劳永逸。** 久期随时间与利率变化而漂移，免疫组合需要定期再平衡。

## 本章要点

- 久期三定义：<span class="highlight">麦考利久期</span>（现金流加权时间）、<span class="highlight">修正久期</span>（价格敏感度）、<span class="highlight">美元久期</span>（一基点价值）
- 凸度是<span class="highlight">二阶修正</span>：利率下行多赚、上行少亏，是买入期权价值的体现
- <span class="highlight">免疫策略</span> = 资产与负债久期匹配 + 定期再平衡
- <span class="highlight">关键利率久期（KRD）</span>把曲线风险按期限分桶，管理扭转风险
''',
'guide/m12-fixed-income/12.3-irs-swaption.md': '''
## 常见误区

**误区1：IRS 固定端的久期可以直接与债券久期比较。** 互换的固定腿久期近似于同期限债券，但浮动腿会不断重置，整体久期与"名义本金的债券"不同。

**误区2：互换利差是信用利差。** 互换利差主要反映银行间体系的系统性风险与供需，与国债的利差还含回购市场的制度因素。

**误区3：Swaption 只有行权才有价值。** 互换期权在行权前是纯波动率敞口，其价值随隐含波动率变化，未行权也可交易获利。

**误区4：对冲曲线风险只需对冲一个期限点。** 用单一期限工具对冲组合会留下扭转风险，应按 KRD 分桶对冲。

## 本章要点

- IRS 定价：<span class="highlight">固定腿现值 = 浮动腿现值</span>，平价利率由贴现曲线推出
- <span class="highlight">Swaption</span> = 进入互换的期权，是利率波动率的直接载体
- 收益率曲线风险的全面对冲要按<span class="highlight">关键利率分桶</span>，而非单一久期对冲
- IRS 可用于<span class="highlight">资产负债券配置</span>：收浮付固/收固付浮改变久期敞口
''',
'guide/m12-fixed-income/12.4-credit-spread.md': '''
## 常见误区

**误区1：信用利差 = 预期违约损失。** 利差还包含风险溢价、流动性溢价与税收因素，历史上违约损失只能解释一部分。

**误区2：Merton 结构模型可直接实盘定价。** 它是概念框架（股权=看涨期权），假设简化（恒定波动率、无破产成本），实盘需大量校准。

**误区3：CDS 与债券利差的基差恒为零。** CDS-Bond Basis 因回收率假设、最便宜交割期权、融资成本而长期存在，是交易机会也是风险。

**误区4：信用曲线总是向上倾斜。** 危机时短端利差飙升，曲线可能反转，对短久期信用头寸的冲击最大。

## 本章要点

- 利差构成：<span class="highlight">预期违约损失 + 风险溢价 + 流动性溢价</span>
- <span class="highlight">Merton 模型</span>：股权是公司资产的看涨期权，违约概率由资产价值分布决定
- <span class="highlight">CDS 定价</span>与 CDS-Bond Basis 是信用相对价值策略的基础
- <span class="highlight">信用曲线</span>在压力时期可能反转，短端保护需求飙升
''',
'guide/m12-fixed-income/12.5-mbs.md': '''
## 常见误区

**误区1：MBS 久期是静态属性。** 提前还款使现金流随利率变化，MBS 久期随利率水平动态变化（利率降→久期缩短）。

**误区2：CPR/PSA 模型通用。** 提前还款行为依赖贷款池年龄、利率激励、 burnout 效应，模型参数需按池校准。

**误区3：负凸度只对发行人有利。** 负凸度意味着"利率下行涨得少、上行跌得多"，投资者承担再投资与逆向提前还款风险，应有收益率补偿。

**误区4：CMO 分层消灭了风险。** 分层只是把提前还款与信用风险重新分配到不同层级（如 PAC 承担时间风险、Support 吸收风险）。

## 本章要点

- MBS 的核心是<span class="highlight">借款人的提前还款期权</span>，导致<span class="highlight">负凸度</span>
- 提前还款速度用 <span class="highlight">CPR/PSA</span> 刻画，对利率路径高度敏感
- <span class="highlight">CMO 分层</span>（PAC/Support 等）重新分配现金流风险，不消灭风险
- 中美资产证券化在<span class="highlight">担保机制、发行结构、流动性</span>上差异显著
''',
# ================= m13 加密 =================
'guide/m13-crypto/13.1-onchain.md': '''
## 常见误区

**误区1：链上数据完全透明可信。** 交易所内部账本在链下，链上只反映最终结算；混币器与内部转账使"透明"打折扣。

**误区2：巨鲸转账 = 买卖信号。** 大额转账可能是交易所内部冷热钱包调拨、托管迁移，需过滤已知地址再做解读。

**误区3：链上指标跨链可比。** 不同链的账户模型、出块时间、费用结构不同，活跃地址数等指标的"含义"不可直接平移。

**误区4：活跃地址数与价格线性相关。** 历史上相关结构随市场阶段变化，需动态评估。

## 本章要点

- 链上数据三层来源：<span class="highlight">自建节点、索引 API、Dune 类分析平台</span>
- 核心指标：<span class="highlight">SOPR、MVRV、交易所净流出</span>等衡量链上持仓成本与行为
- <span class="highlight">巨鲸与矿工</span>行为需过滤内部转账与已知标签地址
- 链上指标应与<span class="highlight">资金流向</span>、衍生品数据交叉验证，不单独作为交易信号
''',
'guide/m13-crypto/13.2-funding-rate.md': '''
## 常见误区

**误区1：资金费率只反映多头拥挤。** 费率是永续合约锚定指数的均衡机制，极端正费率说明多头支付拥挤，极端负费率反之，但中间区域信息量有限。

**误区2：期现套利无风险。** 现货腿占用全额资金、合约腿有强平与交易所风险，费率可能反转，收益/风险需动态评估。

**误区3：跨所套利忽略摩擦。** 转账时间（链上确认）、提币费用、各所保证金独立，都侵蚀费率套利收益。

**误区4：极端负费率是精确的见顶信号。** 它是情绪的极端化读数，历史上出现过连续负费率后继续上涨的情形。

## 本章要点

- 资金费率机制：<span class="highlight">永续合约定期向对方支付</span>，锚定合约价格与指数
- <span class="highlight">Cash-and-Carry</span>：买现货 + 空永续，赚费率与基差收敛
- 跨所费率套利需计入<span class="highlight">滑点、转账延迟、保证金占用</span>
- 极端费率是<span class="highlight">情绪指标</span>，用于风险预算而非精确择时
''',
'guide/m13-crypto/13.3-mev.md': '''
## 常见误区

**误区1：MEV 只存在于以太坊。** 任何具备公开内存池与排序权的链都存在 MEV，只是提取生态成熟度不同。

**误区2：三明治攻击与量化策略无关。** 任何经 DEX 执行的策略都在支付 MEV 成本（滑点恶化），执行层必须考虑。

**误区3：使用 Flashbots 私有内存池没有成本。** 需向构建者支付小费（tip），且不能保证必然打包。

**误区4：PBS 一劳永逸解决 MEV。** 它改变了 MEV 的分配（流向提议者），并未消除提取动机。

## 本章要点

- MEV = 通过<span class="highlight">重排、插入、审查</span>交易可提取的价值
- <span class="highlight">三明治攻击</span>抬高 DEX 交易的执行成本，是量化策略的隐性摩擦
- 缓解手段：<span class="highlight">私有 RPC / Flashbots Protect</span>、批量拍卖、限价单
- 量化涉及 MEV 策略时注意<span class="highlight">合规边界</span>与中心化交易所的替代路径
''',
'guide/m13-crypto/13.4-dex-mm.md': '''
## 常见误区

**误区1：AMM 做 LP 稳赚手续费。** 手续费收入需与无常损失比较，波动大、相关性低的池长期可能亏损。

**误区2：无常损失只在"价格回归"时消失。** 只要价格偏离入场比例，机会成本就存在，与是否"回归"无关。

**误区3：集中流动性（v3）无脑优于 v2。** 集中区间=杠杆化敞口，价格出区间后头寸单一化，需要主动管理区间。

**误区4：v3 报价行为与 v2 一样可预测。** 区间设置因 LP 而异，流动性分布（Liquidity Distribution）是新的研究对象。

## 本章要点

- AMM 基础：<span class="highlight">x·y=k 恒定乘积</span>，价格由储备比例决定
- <span class="highlight">无常损失</span> = 持币 vs 做 LP 的机会成本，与价格偏离的平方根成正比
- <span class="highlight">v3 集中流动性</span>：资本效率提升但需主动管理区间，本质是杠杆化做市
- LP 收益 = <span class="highlight">手续费收入 − 无常损失</span>，可用模拟器做区间优化
''',
'guide/m13-crypto/13.5-perps.md': '''
## 常见误区

**误区1：永续合约可以无限期持有而无成本。** 资金费率持续支付/收取，长持仓期的费率成本可能超过预期。

**误区2：高杠杆只放大收益。** 同比例放大爆仓风险，且维持保证金分档、ADL 机制在极端行情下强制减仓。

**误区3：跨所价差套利没有保证金问题。** 两端各需独立保证金，价差走阔时浮亏端可能被强平。

**误区4：爆仓价格只由杠杆决定。** 维持保证金率、仓位阶梯、未实现盈亏都影响强平价。

## 本章要点

- 永续 vs 交割：<span class="highlight">无到期日</span>，靠<span class="highlight">资金费率</span>锚定指数
- <span class="highlight">费率预测</span>：持仓情绪、期现基差、历史均值回归
- 跨所价差统计套利要管理<span class="highlight">两端保证金</span>与转账通道
- 杠杆管理：<span class="highlight">维持保证金、强平价、ADL</span> 三件事在开仓前就算清
''',
# ================= m14 微结构进阶 =================
'guide/m14-microstructure-deep/14.1-toxicity.md': '''
## 常见误区

**误区1：VPIN 高就一定会被逆向选择。** VPIN 是毒性概率的度量，是报价调整的依据，不是确定的失败预测。

**误区2：按成交量分桶（Volume Bucket）是最优构造。** 桶大小、买卖方向分类方法（BVC/LR）都会显著影响指标表现。

**误区3：VPIN 万能。** 它依赖分类假设，在 tick 级数据可得时,更精细的方法可能更好。

**误区4：毒性只影响做市商。** 任何被动挂单（限价单）策略都暴露于逆向选择。

## 本章要点

- <span class="highlight">VPIN</span>：把订单流毒性概率化，是 Easley-O'Hara 系列的核心贡献
- 构造三要素：<span class="highlight">量桶划分、买卖方向分类（BVC）、毒性累积</span>
- 高毒性 → <span class="highlight">扩大价差或退出报价</span>，这是做市商的生存机制
- 2010 闪崩研究显示 VPIN 在极端事件前有<span class="highlight">预警能力</span>（学术上有争议）
''',
'guide/m14-microstructure-deep/14.2-information-models.md': '''
## 常见误区

**误区1：Kyle lambda 只是实证回归系数。** 它有严格的理论含义——单位订单流的价格冲击，连接信息、流动性与市场质量。

**误区2：Kyle 模型与 Glosten-Milgrom 模型可以互相替代。** 前者是策略知情者+批量均衡，后者是噪声交易者+序贯报价，机制不同。

**误区3：买卖价差只补偿订单处理成本。** GM 模型证明价差的核心成分是<span class="highlight">逆向选择补偿</span>。

**误区4：模型假设（知情者比例等）是真实参数。** 它们是校准工具，实证中通过 lambda 等间接估计。

## 本章要点

- <span class="highlight">Kyle(1985)</span>：知情者最优交易 + 做市商线性定价，lambda 刻画市场深度
- <span class="highlight">Glosten-Milgrom(1985)</span>：序贯交易模型，价差源于逆向选择
- 两模型关联：一个是<span class="highlight">流对价格的冲击</span>，一个是<span class="highlight">报价对信息的调整</span>
- 信息不对称下的最优策略：<span class="highlight">伪装与动态学习</span>贯穿始终
''',
'guide/m14-microstructure-deep/14.3-optimal-execution.md': '''
## 常见误区

**误区1：Almgren-Chriss 模型可以直接实盘下单。** 它假设线性冲击、稳定深度，是轨迹规划的起点而非终局。

**误区2：风险厌恶越高执行越慢。** 恰恰相反——风险厌恶越大，越倾向于<span class="highlight">前载</span>（更快执行）以降低持有期风险。

**误区3：闭式解无需校准。** 暂时性/永久性冲击系数必须用自有成交数据估计，且随市场状态变化。

**误区4：市场深度是常数。** 盘口深度时变，轨迹需要在线调整（closed-loop 优于 open-loop）。

## 本章要点

- AC 框架核心：<span class="highlight">冲击成本（暂时+永久）与持有风险的权衡</span>
- 最优轨迹有<span class="highlight">闭式解</span>：风险厌恶参数决定前载/后载程度
- <span class="highlight">风险厌恶参数</span>↑ → 执行更快、更接近 TWAP 前载形态
- 现实拓展：<span class="highlight">非线性冲击、离散监控、ML 轨迹优化</span>
''',
'guide/m14-microstructure-deep/14.4-lob-dynamics.md': '''
## 常见误区

**误区1：队列位置的价值与排队量线性相关。** 前方撤单速率、新订单到达率共同决定成交概率，是非线性的。

**误区2：Hawkes 过程参数恒定。** 自激强度随市场状态（平静/动荡）显著变化，需滚动校准。

**误区3：LOB 模拟器可以替代真实市场。** 模拟器是策略预演工具，其保真度依赖校准数据与模型假设。

**误区4：订单流自激性可以忽略。** 忽略自激会系统性低估短期波动与成交聚集。

## 本章要点

- <span class="highlight">队列位置模型</span>：先到先服务下，估计自己订单的成交概率
- <span class="highlight">Hawkes 过程</span>：用自激强度刻画"订单引发订单"的聚集现象
- <span class="highlight">LOB 模拟器</span>：回测做市/执行策略的必要基础设施，需校准撤单率等参数
- LOB 统计特性（深度分布、价差跳跃）是<span class="highlight">策略参数化</span>的输入
''',
'guide/m14-microstructure-deep/14.5-hft-mm-advanced.md': '''
## 常见误区

**误区1：库存风险可以完全对冲。** 对冲工具自身有成本与基差，实践中是"报价偏移+限额+部分对冲"的组合。

**误区2：用 tick 数据回测做市策略就等于实盘。** 排队位置、成交不确定性、撤单竞争都无法从历史 tick 完全复现。

**误区3：价差调整只看库存。** 现代做市价差 = 库存 + 订单流毒性 + 外部信号的多因子函数。

**误区4：信号与报价模块独立。** 信号驱动报价（signal-driven quoting）已是从业主流。

## 本章要点

- <span class="highlight">库存风险管理</span>：报价偏移(skew) + 硬性限额 + 必要时主动对冲
- 做市<span class="highlight">回测难点</span>：成交假设、排队模拟、对抗环境
- <span class="highlight">动态价差</span> = 库存偏移 × 毒性调整 × 信号权重
- <span class="highlight">信号驱动报价</span>：把 alpha 信号直接嵌入报价参数，是进阶做市的核心
''',
# ================= m17 数工 =================
'guide/m17-data-engineering/17.1-tick-db.md': '''
## 常见误区

**误区1：行式数据库也能扛 tick 量级。** 海量 tick 的聚合查询在列式存储上的性价比高出数量级。

**误区2：压缩率越高越好。** 高压缩比增加查询时解压成本，需按查询模式权衡。

**误区3：分区越细查询越快。** 过细分区带来元数据开销与小文件问题，通常按日/合约分区即可。

**误区4：只存 tick 不存快照。** 衍生品定价、实时风控都需要快照层，混合存储是常态。

## 本章要点

- <span class="highlight">Parquet / ClickHouse</span> 列式存储是 tick 数据的事实标准
- <span class="highlight">分区（按日/合约）+ 排序键 + 稀疏索引</span>是查询性能的三件套
- <span class="highlight">压缩</span>与查询解压成本需要按实际查询模式权衡
- <span class="highlight">分片与冷热分层</span>：热数据 SSD、冷数据对象存储
''',
'guide/m17-data-engineering/17.2-realtime-etl.md': '''
## 常见误区

**误区1：WebSocket 不会丢数据。** 网络抖动、交易所限频、重连间隙都会丢包，必须有缺口检测与补拉机制。

**误区2：时间戳用本地接收时间。** 必须以交易所事件时间为准，本地时间只作辅助排序。

**误区3：Flink 是唯一正确的流处理框架。** Kafka Streams、自研内存引擎都是可行选项，看延迟需求与团队能力。

**误区4：数据规范化可以后置。** 时间对齐、单位统一必须在进入分析层之前完成，否则信号计算全错。

## 本章要点

- 接入方式：<span class="highlight">交易所直连、REST 轮询、WebSocket</span>，各有延迟与可靠性权衡
- <span class="highlight">流处理框架</span>：Flink / Kafka Streams 提供窗口、水位线、恰好一次语义
- <span class="highlight">时间对齐</span>：交易所事件时间 + 本地单调时钟双时间轴
- <span class="highlight">延迟监控与容错</span>：断线重连、缺口补拉、告警分级
''',
'guide/m17-data-engineering/17.3-data-quality.md': '''
## 常见误区

**误区1：异常值都是错误。** 真实的跳空、闪崩也是"异常值"，自动修复必须区分数据错误与市场事件。

**误区2：修复比标注重要。** 任何修复都要留痕（原值、规则、时间），可回溯比"看起来干净"更重要。

**误区3：数据版本管理可有可无。** 没有 version 的回测结果不可复现，策略迭代无法归因。

**误区4：对账只对持仓。** 行情序列、成交回报、资金余额三层都要对账。

## 本章要点

- <span class="highlight">完整性检查</span>：缺口检测、重复检测、时间乱序检测
- <span class="highlight">异常值处理</span>：区分数据错误与真实市场事件，修复规则留痕
- <span class="highlight">数据版本管理</span>：快照 + 变更日志，保证回测可复现
- <span class="highlight">对账机制</span>：行情、持仓、资金三层对账闭环
''',
'guide/m17-data-engineering/17.4-batch-streaming.md': '''
## 常见误区

**误区1：Lambda 与 Kappa 二选一就完事。** 多数量化团队是"Lambda 为主、局部 Kappa 化"的混合体。

**误区2：批处理将被流处理完全取代。** 日终对账、全量重算、监管报送天然是批处理场景。

**误区3：数据血缘是数据团队的内部事务。** 策略团队需要血缘来定位"哪个上游变更污染了信号"。

**误区4：引擎性能是选型唯一标准。** 生态、运维成本、团队熟悉度往往比跑分更重要。

## 本章要点

- <span class="highlight">Lambda</span>：批流双链路互为校验；<span class="highlight">Kappa</span>：单一流链路重放代替批处理
- <span class="highlight">日终批处理</span>（对账/全量因子）与<span class="highlight">实时流</span>（信号计算）职责分明
- <span class="highlight">数据血缘</span>：从信号回溯到原始数据的依赖图
- 计算引擎对比看<span class="highlight">生态与运维</span>，不只看吞吐跑分
''',
'guide/m17-data-engineering/17.5-feature-store.md': '''
## 常见误区

**误区1：Feature Store 只是一个缓存。** 它的核心价值是训练/服务特征一致性，缓存只是实现细节。

**误区2：在线与离线一致性天然成立。** 训练用历史点时数据、服务用实时计算，二者的微小差异（training-serving skew）足以毁掉模型。

**误区3：特征不需要版本管理。** 特征定义变更后，旧模型与新特征的组合是隐形炸弹，必须版本化+可回滚。

**误区4：开源方案拿来即用。** Feast/Tecton 各有适用边界，自建轻量方案在量化场景常常更快落地。

## 本章要点

- Feature Store 的核心命题：<span class="highlight">在线/离线特征一致性</span>
- <span class="highlight">Point-in-time 正确性</span>：训练特征只用当时可得数据，杜绝未来函数
- <span class="highlight">特征版本管理</span>：定义、计算逻辑、回滚三位一体
- 开源方案（<span class="highlight">Feast/Tecton</span>）与自建的取舍看规模与实时性要求
''',
# ================= m18 策略生命周期 =================
'guide/m18-strategy-lifecycle/18.1-incubation.md': '''
## 常见误区

**误区1：策略想法越多越好。** 没有筛选漏斗的堆叠只会稀释研究资源，想法要有明确的证伪标准再进入孵化。

**误区2：MVP 就是简化版回测。** MVP 应是"数据→信号→风控→执行"的最小全流程闭环，缺一环的验证都是幻觉。

**误区3：评审清单走形式。** 清单的价值在于强制回答"逻辑是什么、容量多大、与现有策略相关性多高"。

**误区4：策略库就是一个代码仓库。** 代码之外，假设、失效条件、复盘记录才是沉淀的核心。

## 本章要点

- 想法来源与<span class="highlight">筛选漏斗</span>：先证伪标准，再投入资源
- <span class="highlight">MVP 全流程闭环</span>：任何一环缺失的验证都不可信
- <span class="highlight">策略评审清单</span>：逻辑、容量、与既有策略的相关性
- <span class="highlight">策略库管理</span>：沉淀假设、数据依赖与复盘，形成知识复利
''',
'guide/m18-strategy-lifecycle/18.2-paper-to-live.md': '''
## 常见误区

**误区1：模拟盘跑通就等于实盘没问题。** 模拟盘无法复现排队、冲击、拒单与心理压力。

**误区2：验证通过就直接全仓上。** 渐进式上线（小资金→分批加仓）是控制未知风险的唯一路径。

**误区3：实盘差异只有滑点。** 延迟、部分成交、拒单、资金占用都造成模拟与实盘的偏差。

**误区4：上线检查清单走完一次即可。** 每次加仓都是一个新决策点，需要重新过清单。

## 本章要点

- 模拟盘的<span class="highlight">必要性与局限</span>：验证逻辑，验证不了执行
- <span class="highlight">渐进式上线</span>：小资金试点 → 观察期 → 分批放大
- 实盘差异来源：<span class="highlight">滑点、延迟、拒单、资金效率</span>
- <span class="highlight">检查清单 + 观察期</span>：每个放大决策都有数据依据
''',
'guide/m18-strategy-lifecycle/18.3-ab-testing.md': '''
## 常见误区

**误区1：A/B 测试就是新旧策略各跑一半时间。** 时间错开的市场环境不同，必须同资金、同期限并行对照。

**误区2：统计显著=策略更好。** 显著性之外还要看经济显著性与容量，p<0.05 不等于值得切换。

**误区3：金丝雀发布就是普通上线。** 金丝雀的核心是"小流量+预设观察指标+自动熔断"。

**误区4：回滚意味着失败。** 事前定义的回滚标准被触发而回滚，恰恰是流程在正常工作。

## 本章要点

- A/B 设计：<span class="highlight">同资金、同期限并行对照</span>，排除市场环境差异
- 判定 = <span class="highlight">统计显著性 + 经济显著性</span>双重门槛
- <span class="highlight">金丝雀发布</span>：小流量灰度、预设指标、自动熔断
- <span class="highlight">回滚标准</span>事前写死，触发即执行，不临时辩论
''',
'guide/m18-strategy-lifecycle/18.4-attribution.md': '''
## 常见误区

**误区1：归因就是写事后报告。** 归因是持续运行的诊断系统，目标是发现策略退化与风险漂移。

**误区2：Brinson 模型适用于一切组合。** 它是配置/选择框架，对因子驱动的量化组合，因子归因更贴切。

**误区3：因子归因一次建模永久使用。** 因子库与暴露估计需要随策略迭代更新。

**误区4：归因结果只是给领导看的。** 不进入优化闭环的归因是成本不是资产。

## 本章要点

- <span class="highlight">Brinson 归因</span>：配置效应 + 选择效应 + 交互效应
- <span class="highlight">因子归因</span>：收益 = 因子暴露 × 因子收益 + 特异收益
- 归因报告<span class="highlight">自动化</span>：日/周频生成，异常自动标注
- <span class="highlight">闭环</span>：归因结果 → 策略参数与风控调整 → 下期验证
''',
'guide/m18-strategy-lifecycle/18.5-retirement.md': '''
## 常见误区

**误区1：只有持续亏损才退役。** 相关性上升、容量枯竭、拥挤度飙升、逻辑失效都是退役信号，常常先于亏损出现。

**误区2：退役就是删除策略代码。** 保留完整档案（参数、数据依赖、失效复盘）是知识资产。

**误区3：资金立即再配置到其他策略。** 应评估再配置目标与退役策略的相关性，避免风险换仓而非减仓。

**误区4：复盘可以省略。** 不写退役复盘的组织会不断重复同一种死法。

## 本章要点

- 退役信号：<span class="highlight">容量、拥挤度、相关性、逻辑失效</span>，亏损只是最滞后的一个
- <span class="highlight">退役决策框架</span>：信号 → 评审 → 灰度退出
- <span class="highlight">资金再配置</span>：优先流向与退役策略低相关的方向
- <span class="highlight">复盘报告</span>：沉淀失效模式，形成组织的负知识库
''',
# ================= m20 面试 =================
'guide/m20-interview-prep/20.1-math-stats.md': '''
## 常见误区

**误区1：只刷标准题。** 面试官几乎必然追问变体（改条件、改分布），理解推导比记住答案重要。

**误区2：背公式不推过程。** 现场要求从假设推到结论时，背的公式撑不住三句追问。

**误区3：只给答案。** 口头表达假设、思路与验证方式占分不低，沉默写对不一定赢。

**误区4：高深技巧优于朴素直觉。** 面试官更看重把复杂问题拆解成直觉可验证的小块的能力。

## 本章要点

- <span class="highlight">概率题</span>：条件概率、期望/方差计算、马氏链与递推
- <span class="highlight">统计题</span>：假设检验、回归诊断、贝叶斯更新
- 回答框架：<span class="highlight">先讲假设 → 再推结论 → 最后给 sanity check</span>
- 被追问时<span class="highlight">说出思考过程</span>比硬给答案更加分
''',
'guide/m20-interview-prep/20.2-coding.md': '''
## 常见误区

**误区1：只刷算法题不练 Pandas。** 量化面试的数据处理题频率不低于算法题。

**误区2：写对就行。** 面试官同时看复杂度、边界条件（空输入/重复值/乱序）与代码风格。

**误区3：系统设计题没有答题框架。** 行情接入→策略计算→风控→执行的分层框架是标准答案骨架。

**误区4：Python 陷阱靠背。** 理解可变默认参数、GIL、浮点比较背后的机制才能应对追问。

## 本章要点

- 算法变形高频区：<span class="highlight">滑动窗口、堆、二分、状态压缩 DP</span>
- <span class="highlight">Pandas/NumPy</span>：groupby/merge/时序重采样要闭眼写出
- 系统设计：<span class="highlight">行情接入 → 策略 → 风控 → 执行</span>分层 + 容错
- Python 陷阱：<span class="highlight">可变默认参数、GIL、浮点比较、深浅拷贝</span>
''',
'guide/m20-interview-prep/20.3-finance.md': '''
## 常见误区

**误区1：期权定价只会背 BS 公式。** 追问假设（对数正态、常数波动率、无摩擦）与失效场景才是考点。

**误区2：做市题回答"报中间价"。** 考的是逆向选择、库存与波动率如何决定报价宽度与偏移。

**误区3：策略设计题只讲收益来源。** 不谈容量、拥挤与失效条件的策略设计等于没设计。

**误区4：组合概念只背名词。** 分散化为什么失效、杠杆在什么条件下放大回撤，要能推演。

## 本章要点

- <span class="highlight">期权定价</span>：BS 假设与失效、二叉树、希腊字母的直觉
- <span class="highlight">做市博弈</span>：逆向选择决定宽度、库存决定偏移
- <span class="highlight">策略设计</span>：信号 → 容量 → 风控三段式作答
- <span class="highlight">组合核心</span>：分散化、相关性、杠杆与回撤的交互
''',
'guide/m20-interview-prep/20.4-brain-teasers.md': '''
## 本章要点

- <span class="highlight">费米估算</span>：把无解问题拆成数量级可估的小块，过程即答案
- <span class="highlight">经典脑筋急转弯</span>：考反应速度与表达清晰度，答案本身不重要
- <span class="highlight">行为面试</span>：用 STAR 结构（情境-任务-行动-结果）组织回答
- <span class="highlight">诚实</span>：不会就说不会，强行编造的扣分远大于承认
''',
'guide/m20-interview-prep/20.5-mock-interview.md': '''
## 常见误区

**误区1：模拟面试等于重复刷题。** 模拟的价值在于压力下的表达、时间分配与追问应对。

**误区2：自我介绍不重要。** 它决定了面试官前五分钟的提问方向，是最可控的部分。

**误区3：被问倒就完了。** 处理方式（澄清问题、给思路、承认边界）比答对所有题更能体现素养。

**误区4：只练技术面。** 行为面与价值观面在终面的权重往往更高。

## 本章要点

- 量化面试全流程：<span class="highlight">简历筛选 → 笔试 → 技术面 → 行为面 → 终面</span>
- 各轮侧重：<span class="highlight">数学/编程/金融/行为</span>各有评分表
- 模拟组织：<span class="highlight">真人面试官 + 计时 + 全程录音复盘</span>
- 复盘迭代：每场模拟的失分点进入<span class="highlight">下一场练习清单</span>
''',
}

n = 0
for path, md in CONTENT.items():
    txt = io.open(path, encoding='utf-8').read()
    if '## 本章要点' in txt:
        print('SKIP(已有要点)', path)
        continue
    if not txt.endswith('\n'):
        txt += '\n'
    io.open(path, 'w', encoding='utf-8', newline='').write(txt + md)
    n += 1
print(f'补齐 {n} 页节拍')
