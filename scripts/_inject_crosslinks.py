# -*- coding: utf-8 -*-
# ④ 前后场交叉引用: 后半场"跨模块延伸" + 前半场"跨模块进阶"
import io, re

CROSS = '**跨模块延伸**：'

BACK = {
    'guide/m12-fixed-income/12.1-yield-curve.md': ['../m02-finance-math/2.2-asset-pricing.md|资产定价与因子模型', '../m11-derivatives/11.4-tree-fdm.md|定价数值方法'],
    'guide/m12-fixed-income/12.2-duration-convexity.md': ['../m02-finance-math/2.2-asset-pricing.md|资产定价'],
    'guide/m12-fixed-income/12.3-irs-swaption.md': ['../m11-derivatives/11.2-vol-surface.md|波动率曲面'],
    'guide/m12-fixed-income/12.4-credit-spread.md': ['../m11-derivatives/11.3-exotic-options.md|奇异期权与结构化'],
    'guide/m12-fixed-income/12.5-mbs.md': ['../m16-risk-management/16.3-stress-testing.md|压力测试'],
    'guide/m13-crypto/13.1-onchain.md': ['../m17-data-engineering/17.3-data-quality.md|数据质量'],
    'guide/m13-crypto/13.2-funding-rate.md': ['../m07-execution/7.1-order-types.md|订单类型'],
    'guide/m13-crypto/13.3-mev.md': ['../m14-microstructure-deep/14.4-lob-dynamics.md|订单簿动力学'],
    'guide/m13-crypto/13.4-dex-mm.md': ['../m07-execution/7.3-market-making.md|做市基础'],
    'guide/m13-crypto/13.5-perps.md': ['../m16-risk-management/16.5-tail-hedge.md|尾部对冲'],
    'guide/m14-microstructure-deep/14.1-toxicity.md': ['../m07-execution/7.3-market-making.md|做市基础'],
    'guide/m14-microstructure-deep/14.2-information-models.md': ['../m05-strategies/5.3-stat-arb.md|统计套利'],
    'guide/m14-microstructure-deep/14.3-optimal-execution.md': ['../m07-execution/7.2-algo-execution.md|执行算法'],
    'guide/m14-microstructure-deep/14.4-lob-dynamics.md': ['../m17-data-engineering/17.2-realtime-etl.md|实时数据管道'],
    'guide/m14-microstructure-deep/14.5-hft-mm-advanced.md': ['../m09-live-trading/9.1-system-design.md|交易系统设计'],
    'guide/m17-data-engineering/17.1-tick-db.md': ['../m03-python-data/3.3-performance.md|性能优化'],
    'guide/m17-data-engineering/17.2-realtime-etl.md': ['../m09-live-trading/9.2-data-pipeline.md|实盘数据管道'],
    'guide/m17-data-engineering/17.3-data-quality.md': ['../m04-backtest/4.4-pitfalls.md|回测陷阱'],
    'guide/m17-data-engineering/17.4-batch-streaming.md': ['../m09-live-trading/9.4-monitoring.md|实盘监控'],
    'guide/m17-data-engineering/17.5-feature-store.md': ['../m08-ml-alt-data/8.1-supervised.md|监督学习'],
    'guide/m18-strategy-lifecycle/18.1-incubation.md': ['../m10-frontier/10.5-final-project.md|毕业项目'],
    'guide/m18-strategy-lifecycle/18.2-paper-to-live.md': ['../m09-live-trading/9.1-system-design.md|交易系统设计'],
    'guide/m18-strategy-lifecycle/18.3-ab-testing.md': ['../m04-backtest/4.5-stat-tests.md|统计检验'],
    'guide/m18-strategy-lifecycle/18.4-attribution.md': ['../m16-risk-management/16.1-risk-decomposition.md|风险分解'],
    'guide/m18-strategy-lifecycle/18.5-retirement.md': ['../m16-risk-management/16.3-stress-testing.md|压力测试'],
    'guide/m20-interview-prep/20.1-math-stats.md': ['../m02-finance-math/2.4-time-series.md|时间序列'],
    'guide/m20-interview-prep/20.2-coding.md': ['../m03-python-data/3.3-performance.md|性能优化'],
    'guide/m20-interview-prep/20.3-finance.md': ['../m11-derivatives/11.1-greeks.md|Greeks'],
    'guide/m20-interview-prep/20.4-brain-teasers.md': ['../m04-backtest/4.4-pitfalls.md|回测陷阱'],
    'guide/m20-interview-prep/20.5-mock-interview.md': ['../m16-risk-management/16.4-basel.md|巴塞尔协议'],
}

FRONT = {
    'guide/m04-backtest/4.4-pitfalls.md': ['../m18-strategy-lifecycle/18.3-ab-testing.md|A/B 测试与回滚', '../m16-risk-management/16.2-evt-tail.md|极值理论与尾部风险'],
    'guide/m04-backtest/4.1-engine.md': ['../m18-strategy-lifecycle/18.1-incubation.md|策略孵化'],
    'guide/m05-strategies/5.2-dual-ma.md': ['../m14-microstructure-deep/14.3-optimal-execution.md|最优执行'],
    'guide/m05-strategies/5.3-stat-arb.md': ['../m14-microstructure-deep/14.1-toxicity.md|订单流毒性'],
    'guide/m06-portfolio/6.1-mvo.md': ['../m16-risk-management/16.1-risk-decomposition.md|风险分解与预算'],
    'guide/m06-portfolio/6.5-var.md': ['../m16-risk-management/16.2-evt-tail.md|极值理论', '../m16-risk-management/16.3-stress-testing.md|压力测试'],
    'guide/m07-execution/7.2-algo-execution.md': ['../m14-microstructure-deep/14.3-optimal-execution.md|Almgren-Chriss 模型'],
    'guide/m07-execution/7.3-market-making.md': ['../m14-microstructure-deep/14.5-hft-mm-advanced.md|做市进阶'],
    'guide/m09-live-trading/9.1-system-design.md': ['../m17-data-engineering/17.1-tick-db.md|Tick 数据库', '../m18-strategy-lifecycle/18.2-paper-to-live.md|模拟转实盘'],
    'guide/m09-live-trading/9.2-data-pipeline.md': ['../m17-data-engineering/17.2-realtime-etl.md|实时 ETL'],
    'guide/m10-frontier/10.5-final-project.md': ['../m18-strategy-lifecycle/18.1-incubation.md|策略孵化', '../m18-strategy-lifecycle/18.5-retirement.md|策略退役'],
}

def fmt(links):
    parts = []
    for item in links:
        if isinstance(item, str):
            p, t = item.split('|', 1)
        else:
            p, t = item
        parts.append(f'[{t}]({p})')
    return CROSS + '、'.join(parts)

# 后半场: 追加到文件末尾(本章要点之后)
for path, links in BACK.items():
    txt = io.open(path, encoding='utf-8').read()
    if '跨模块延伸' in txt:
        print('SKIP', path); continue
    if not txt.endswith('\n'):
        txt += '\n'
    txt += '\n' + fmt(links) + '\n'
    io.open(path, 'w', encoding='utf-8', newline='').write(txt)
    print('OK(back)', path)

# 前半场: 插入到"延伸阅读"节末尾(下一个 ## 之前)
for path, links in FRONT.items():
    txt = io.open(path, encoding='utf-8').read()
    if '跨模块进阶' in txt:
        print('SKIP', path); continue
    m = re.search(r'## 延伸阅读.*?(?=\n## |\Z)', txt, re.S)
    if not m:
        print('MISS 延伸阅读', path); continue
    seg_end = m.end()
    insert = '\n\n**跨模块进阶：**' + '、'.join(f'[{t}]({p})' for p, t in [x.split('|', 1) if isinstance(x, str) else x for x in links]) + '\n'
    new_txt = txt[:seg_end] + insert + txt[seg_end:]
    io.open(path, 'w', encoding='utf-8', newline='').write(new_txt)
    print('OK(front)', path)
