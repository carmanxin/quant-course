# -*- coding: utf-8 -*-
# ② m15 合成数据最小示例：向目标 fence 内部追加"数据为模拟、机制真实"的调用段
# 用法: python scripts/_inject_m15_demos.py
import io, re

DEMOS = {
'guide/m15-macro/15.1-macro-factors.md': [
('build_macro_factors_pca', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(42)
_demo_dates = pd.date_range('2015-01-31', periods=120, freq='M')
_demo_growth = np.cumsum(np.random.randn(120) * 0.3)
_demo_infl = 2 + np.cumsum(np.random.randn(120) * 0.2)
_economic_data = pd.DataFrame({
    '工业增加值同比': 6 + _demo_growth * 0.5 + np.random.randn(120) * 0.3,
    'CPI同比': _demo_infl + np.random.randn(120) * 0.1,
    'PPI同比': _demo_infl * 1.2 - 1 + np.random.randn(120) * 0.5,
    '社融存量同比': 10 + _demo_growth * 0.4 + np.random.randn(120) * 0.4,
    'PMI': 50 + _demo_growth * 0.8 + np.random.randn(120) * 0.5,
    '出口同比': 5 + _demo_growth * 1.2 + np.random.randn(120) * 1.5,
}, index=_demo_dates)
_factors_df, _loadings, _ev = build_macro_factors_pca(_economic_data, n_factors=3)
print('解释方差比:', np.round(_ev, 3))
'''),
('fama_macbeth_macro', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(7)
_dates = pd.date_range('2018-01-31', periods=60, freq='M')
_macro = pd.DataFrame({
    '增长': np.random.randn(60).cumsum() * 0.2,
    '通胀': np.random.randn(60).cumsum() * 0.15,
    '利率': np.random.randn(60).cumsum() * 0.25,
}, index=_dates)
_betas = np.random.uniform(-0.5, 1.5, size=(3, 8))
_asset = pd.DataFrame(
    _macro.values @ _betas / 12 + np.random.randn(60, 8) * 0.03,
    columns=[f'资产{i+1}' for i in range(8)], index=_dates)
_res = fama_macbeth_macro(_asset, _macro)
for _k, _v in _res.items():
    print(f'--- {_k} ---')
    print(_v.head() if hasattr(_v, 'head') else _v)
'''),
('factor_interaction_analysis', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(11)
_idx = pd.date_range('2018-01-31', periods=60, freq='M')
_ar = pd.DataFrame(np.random.randn(60, 5) * 0.02,
                   columns=[f'资产{i+1}' for i in range(5)], index=_idx)
_mf = pd.DataFrame({'增长': np.random.randn(60), '通胀': np.random.randn(60)}, index=_idx)
_sf = pd.DataFrame({'动量': np.random.randn(60), '价值': np.random.randn(60), '低波': np.random.randn(60)}, index=_idx)
_int_res = factor_interaction_analysis(_ar, _mf, _sf)
print(_int_res.head(10))
'''),
('macro_regime_factor_allocation', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_universe = {'momentum': 0.2, 'growth': 0.2, 'quality': 0.2, 'value': 0.2, 'low_vol': 0.2}
for _state in ['expansion', 'contraction', 'stagflation', 'recovery']:
    _w = macro_regime_factor_allocation(_state, _universe)
    print(_state, '->', {k: round(v, 3) for k, v in _w.items()})
'''),
],
'guide/m15-macro/15.2-fed-policy.md': [
('implied_rate_probability', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_p = implied_rate_probability(futures_price=95.6, current_ffr=4.50,
                              hike_size_bps=25, days_to_meeting=18, days_in_month=30)
for _k, _v in _p.items():
    print(f'{_k}: {_v}')
'''),
('taylor_rule_ffr', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
print('Taylor 合意利率:',
      round(taylor_rule_ffr(inflation=3.2, inflation_target=2.0, output_gap=0.8), 2))
print('规则残差(实际-合意):',
      round(taylor_rule_residual(actual_ffr=4.50, inflation=3.2, inflation_target=2.0, output_gap=0.8), 2))
'''),
('fed_balance_sheet_impact', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(3)
_eq = np.random.randn(250) * 0.01 + 0.0004
_by = np.random.randn(250) * 0.03
_bs = fed_balance_sheet_impact(fed_assets_change_pct=8.0, equity_returns=_eq,
                               bond_yield_change=_by, window=60)
for _k, _v in _bs.items():
    print(f'{_k}: {_v}')
'''),
],
'guide/m15-macro/15.3-inflation.md': [
('calculate_bei', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(5)
_tenors = ['1Y', '2Y', '5Y', '10Y', '30Y']
_idx = pd.date_range('2024-01-31', periods=12, freq='M')
_nom = pd.DataFrame({t: 4.0 + i * 0.05 + np.random.randn(12) * 0.05 for i, t in enumerate(_tenors)}, index=_idx)
_tips = pd.DataFrame({t: 1.9 + i * 0.04 + np.random.randn(12) * 0.04 for i, t in enumerate(_tenors)}, index=_idx)
_bei = calculate_bei(_nom, _tips)
print('BEI(盈亏平衡通胀率):')
print(_bei.head() if hasattr(_bei, 'head') else _bei)
'''),
('tips_fair_value', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_exp_inf = np.full(10, 0.025)
print('TIPS 公平价值:',
      round(tips_fair_value(real_yield=2.0, expected_inflation=_exp_inf, maturity_years=10), 2))
'''),
('zcis_fair_rate', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_cpi_path = np.full(10, 0.024)
_disc = np.full(10, 0.042)
print('10 年期 ZCIS 公平利率:',
      round(zcis_fair_rate(expected_cpi_path=_cpi_path, discount_rates=_disc, maturity_years=10), 4))
'''),
('inflation_hedge_portfolio', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
for _reg in ['rising', 'falling', 'stable_high', 'stable_low']:
    _w = inflation_hedge_portfolio(inflation_regime=_reg, risk_budget=0.10)
    print(_reg, '->', {k: round(v, 3) for k, v in _w.items()})
'''),
('bei_momentum_signal', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(9)
_s = pd.Series(2.3 + np.cumsum(np.random.randn(120) * 0.05),
               index=pd.date_range('2023-01-31', periods=120))
_sig = bei_momentum_signal(_s)
print(_sig.tail() if hasattr(_sig, 'tail') else _sig)
'''),
],
'guide/m15-macro/15.4-cycle-timing.md': [
('enhanced_investment_clock', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
for _g, _inf in [(0.6, -0.2), (0.6, 0.8), (-0.5, 0.9), (-0.5, -0.3)]:
    _clk = enhanced_investment_clock(growth_momentum=_g, inflation_momentum=_inf, credit_momentum=0.1)
    print(f'增长{_g:+.1f}/通胀{_inf:+.1f} ->', _clk if not isinstance(_clk, dict) else {k: v for k, v in list(_clk.items())[:2]})
'''),
('decompose_economic_cycle', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(13)
_gdp = pd.Series(np.linspace(100, 118, 60) + np.sin(np.linspace(0, 6 * np.pi, 60)) * 2
                 + np.random.randn(60) * 0.5,
                 index=pd.date_range('2012-03-01', periods=60, freq='Q'))
_cycle = decompose_economic_cycle(_gdp, method='hp')
for _k, _v in _cycle.items():
    print(f'--- {_k} ---')
    print(_v.tail() if hasattr(_v, 'tail') else _v)
'''),
('economic_cycle_scoreboard', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_ind = {'pmi': 51.2, 'unemployment_rate': 3.9, 'retail_sales_yoy': 2.5,
        'industrial_production_yoy': 1.1, 'credit_spread': 1.4,
        'yield_curve_slope': -0.2, 'housing_starts_yoy': -5.0}
_sb = economic_cycle_scoreboard(_ind)
for _k, _v in _sb.items():
    print(f'{_k}: {_v}')
'''),
('diffusion_index', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_chg = np.array([0.3, -0.2, 0.5, 0.1, -0.4, 0.2, 0.6, -0.1, 0.2, 0.4])
print('扩散指数:', round(diffusion_index(_chg), 3))
'''),
],
'guide/m15-macro/15.5-cross-asset.md': [
('fx_carry_strategy', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(17)
_ccys = ['EUR', 'JPY', 'GBP', 'AUD']
_idx = pd.date_range('2023-01-02', periods=250)
_spot = pd.DataFrame({c: [1.1, 150, 1.27, 0.67][i] + np.cumsum(np.random.randn(250) * 0.004)
                      for i, c in enumerate(_ccys)}, index=_idx)
_rates = pd.DataFrame({c: [3.5, 0.1, 4.8, 4.2][i] + np.random.randn(250) * 0.02
                       for i, c in enumerate(_ccys)}, index=_idx)
_carry = fx_carry_strategy(_spot, _rates)
print('套息策略累计收益:', round(float((1 + _carry.fillna(0)).prod() - 1), 4))
'''),
('global_macro_momentum', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(19)
_assets = ['美股', '美债', '黄金', '原油', '铜', '欧元', '日元', '新兴市场', 'REITs', '商品']
_px = pd.DataFrame({a: 100 * np.cumprod(1 + np.random.randn(500) * 0.01 + 0.0003)
                    for a in _assets}, index=pd.date_range('2022-01-03', periods=500))
_mom = global_macro_momentum(_px)
print('动量策略累计收益:', round(float((1 + _mom.fillna(0)).prod() - 1), 4))
'''),
('crisis_correlation_analysis', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(23)
_rets = pd.DataFrame(np.random.randn(750, 5) * 0.01,
                     columns=['美股', '美债', '原油', '黄金', '新兴市场'],
                     index=pd.date_range('2021-01-04', periods=750))
_cr = crisis_correlation_analysis(_rets, crisis_dates=[('2022-02-24', '2022-06-30')])
for _k, _v in _cr.items():
    print(f'--- {_k} ---')
    print(_v if not hasattr(_v, 'head') else _v.head())
'''),
('simple_dcc_estimate', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(29)
_common = np.random.randn(400) * 0.01
_r1 = _common + np.random.randn(400) * 0.005
_r2 = _common + np.random.randn(400) * 0.005
_dcc = simple_dcc_estimate(_r1, _r2, half_life=20)
_dcc_v = _dcc if np.isscalar(_dcc) else (np.asarray(_dcc)[-1] if hasattr(_dcc, '__len__') else _dcc)
print('DCC 动态相关性(最新):', round(float(_dcc_v), 3))
'''),
('cross_asset_linkage', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(31)
_mkt = np.random.randn(500)
_link = cross_asset_linkage(_mkt * 0.003, _mkt * 0.002 + 0.001, _mkt * 0.004, window=60)
print(_link.tail() if hasattr(_link, 'tail') else _link)
'''),
('global_macro_risk_parity', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(37)
_rp_rets = pd.DataFrame(np.random.randn(500, 5) * 0.008,
                        columns=['美股', '美债', '黄金', '商品', '新兴市场'],
                        index=pd.date_range('2022-01-03', periods=500))
_rp = global_macro_risk_parity(_rp_rets)
print('风险平价权重:', _rp if not hasattr(_rp, 'to_string') else _rp.round(3).to_string())
'''),
],
}

def inject(path, func_name, demo):
    txt = io.open(path, encoding='utf-8').read()
    lines = txt.split('\n')
    in_f = False; lang = ''; start = -1
    for i, line in enumerate(lines):
        if not in_f and line.startswith('```'):
            in_f = True; lang = line[3:].strip(); start = i
        elif in_f and re.match(r'^```\s*$', line):
            in_f = False
            if lang in ('python', 'py') and f'def {func_name}(' in '\n'.join(lines[start:i]):
                block = '\n'.join(lines[start:i])
                assert '合成数据最小示例' not in block, f'{path}:{func_name} 已注入'
                lines[i:i] = demo.split('\n')
                io.open(path, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
                return True
    return False

n = 0
for path, demos in DEMOS.items():
    for func_name, demo in demos:
        ok = inject(path, func_name, demo)
        print(('OK ' if ok else 'MISS ') + path + ' :: ' + func_name)
        n += int(ok)
print(f'注入 {n} 个示例')
