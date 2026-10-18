# -*- coding: utf-8 -*-
# ④ 补: m15/m16/m19 (上一批已补拍的模块) 的跨模块延伸
import io

BACK = {
    'guide/m15-macro/15.1-macro-factors.md': ['../m06-portfolio/6.1-mvo.md|组合优化', '../m05-strategies/5.6-multi-factor.md|多因子策略'],
    'guide/m15-macro/15.2-fed-policy.md': ['../m02-finance-math/2.4-time-series.md|时间序列'],
    'guide/m15-macro/15.3-inflation.md': ['../m06-portfolio/6.2-risk-parity.md|风险平价'],
    'guide/m15-macro/15.4-cycle-timing.md': ['../m05-strategies/5.4-cta.md|CTA 策略'],
    'guide/m15-macro/15.5-cross-asset.md': ['../m06-portfolio/6.2-risk-parity.md|风险平价', '../m16-risk-management/16.3-stress-testing.md|压力测试'],
    'guide/m16-risk-management/16.1-risk-decomposition.md': ['../m06-portfolio/6.1-mvo.md|组合优化', '../m18-strategy-lifecycle/18.4-attribution.md|归因分析'],
    'guide/m16-risk-management/16.2-evt-tail.md': ['../m06-portfolio/6.5-var.md|VaR 体系'],
    'guide/m16-risk-management/16.3-stress-testing.md': ['../m04-backtest/4.4-pitfalls.md|回测陷阱'],
    'guide/m16-risk-management/16.4-basel.md': ['../m09-live-trading/9.5-compliance.md|实盘合规'],
    'guide/m16-risk-management/16.5-tail-hedge.md': ['../m11-derivatives/11.8-vol-trading.md|波动率交易'],
    'guide/m19-a-share/19.1-limit-up.md': ['../m14-microstructure-deep/14.4-lob-dynamics.md|订单簿动力学'],
    'guide/m19-a-share/19.2-ipo.md': ['../m04-backtest/4.4-pitfalls.md|回测陷阱'],
    'guide/m19-a-share/19.3-sector-rotation.md': ['../m05-strategies/5.6-multi-factor.md|多因子策略'],
    'guide/m19-a-share/19.4-northbound.md': ['../m03-python-data/3.2-data-cleaning.md|数据清洗'],
    'guide/m19-a-share/19.5-policy-events.md': ['../m08-ml-alt-data/8.3-nlp.md|金融 NLP'],
}

n = 0
for path, links in BACK.items():
    txt = io.open(path, encoding='utf-8').read()
    if '跨模块延伸' in txt:
        print('SKIP', path)
        continue
    if not txt.endswith('\n'):
        txt += '\n'
    parts = '、'.join(f'[{t}]({p})' for p, t in [x.split('|', 1) for x in links])
    txt += '\n**跨模块延伸**：' + parts + '\n'
    io.open(path, 'w', encoding='utf-8', newline='').write(txt)
    n += 1
print(f'补齐 {n} 页跨模块延伸')
