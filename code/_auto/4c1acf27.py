# @quantlab/output: 4c1acf27
# 不同市场的隐含波动率偏度（25-delta Risk Reversal）对比
# 构造方法: skew = IV(25d put) - IV(25d call)，单位为波动率点(vol pt)
# 这是衡量"暴跌恐惧"定价程度的市场指标: 越负 = 看跌保护越贵

MARKET_IV_QUOTES = {
    # 市场: (25-delta put IV, ATM IV, 25-delta call IV)  单位 %
    'US SPX (标普500)':      (22.5, 16.0, 13.8),
    'KR KO200 (韩国200)':    (26.4, 17.5, 13.2),
    'CN 50ETF (上证50ETF)':  (19.8, 16.2, 14.6),
    'HK HSI (恒生指数)':      (24.1, 19.0, 16.3),
}

print(f"{'市场':<22}{'25dP IV':>9}{'ATM IV':>8}{'25dC IV':>9}{'偏度':>8}{'微笑曲率':>10}")
print("-" * 68)
for market, (put_iv, atm_iv, call_iv) in MARKET_IV_QUOTES.items():
    skew = put_iv - call_iv                       # 负偏程度(RR)
    smile = (put_iv + call_iv) / 2 - atm_iv       # 蝶式: 两翼相对 ATM 的抬升
    print(f"{market:<22}{put_iv:>8.1f}%{atm_iv:>7.1f}%{call_iv:>8.1f}%"
          f"{skew:>+7.1f}{smile:>+9.1f}")

print("\n解读:")
ranked = sorted(MARKET_IV_QUOTES.items(), key=lambda kv: kv[1][0] - kv[1][2], reverse=True)
print(f"  偏度最陡(下跌保护最贵): {ranked[0][0]}  skew={ranked[0][1][0]-ranked[0][1][2]:+.1f}")
print(f"  偏度最平(定价最中性):   {ranked[-1][0]}  skew={ranked[-1][1][0]-ranked[-1][1][2]:+.1f}")
print("  韩国 KO200 偏度极陡: 散户占比高 + 强烈看空需求推高虚值 put")
print("  A 股 50ETF 偏度相对平: 缺乏做空工具，put 需求被涨跌停与限仓抑制")
print("  港股 HSI 整体 IV 水平最高: 与 A 股相关性高，常被当作 A 股对冲替代品")
