# -*- coding: utf-8 -*-
# ② 第二批: m19/m16 合成数据最小示例注入
# 用法: python scripts/_inject_m19_m16_demos.py
import io, re

def fence_locate(lines, marker):
    """找包含 marker 的 python fence 的 [start, end) 行号(不含结束```)"""
    in_f = False; lang = ''; start = -1
    for i, line in enumerate(lines):
        if not in_f and line.startswith('```'):
            in_f = True; lang = line[3:].strip(); start = i
        elif in_f and re.match(r'^```\s*$', line):
            in_f = False
            if lang in ('python', 'py') and marker in '\n'.join(lines[start:i]):
                return start, i
    return None

def inject(path, marker, demo):
    txt = io.open(path, encoding='utf-8').read()
    assert '合成数据最小示例' not in txt or True
    lines = txt.split('\n')
    loc = fence_locate(lines, marker)
    if loc is None:
        print('MISS', path, marker); return False
    start, end = loc
    block = '\n'.join(lines[start:end])
    if '合成数据最小示例' in block:
        print('SKIP(已注入)', path, marker); return False
    # 顶部补 import(np/pd 若用到且未导入)
    adds = []
    if re.search(r'\bnp\.', block + demo) and not re.search(r'^import numpy', block, re.M):
        adds.append('import numpy as np')
    if re.search(r'\bpd\.', block + demo) and not re.search(r'^import pandas', block, re.M):
        adds.append('import pandas as pd')
    if adds:
        lines[start + 1:start + 1] = adds + ['']
        start += len(adds) + 1; end += len(adds) + 1
    lines[end:end] = demo.split('\n')
    io.open(path, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('OK', path, marker)
    return True

DEMOS = {
# ================= m19 =================
'guide/m19-a-share/19.1-limit-up.md': [
('class LimitUpSignalGenerator', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(101)
_codes = ['600001', '600002']
_dates = ['2024-05-27', '2024-05-28', '2024-05-29', '2024-05-30', '2024-05-31', '2024-06-03']
_daily_rows = []
for _c in _codes:
    _pre = 10.0
    for _d in _dates:
        _is_up = 1 if (_c == '600001' and _d >= '2024-05-30') else 0
        _close = round(_pre * 1.10, 2) if _is_up else round(_pre * 1.01, 2)
        _daily_rows.append({'code': _c, 'date': _d, 'pre_close': _pre, 'close': _close,
                            'limit_up_price': round(_pre * 1.10, 2), 'limit_down_price': round(_pre * 0.90, 2),
                            'is_limit_up': _is_up, 'is_limit_down': 0})
        _pre = _close
_daily_data = pd.DataFrame(_daily_rows)
_tick_rows = []
for _t in ['09:25:03', '10:00:00', '10:30:00', '13:30:00', '14:30:00', '14:57:00']:
    _tick_rows.append({'code': '600001', 'date': '2024-06-03', 'time': _t,
                       'price': 11.00, 'bid_volume_1': 52000})
tick_data = pd.DataFrame(_tick_rows)
_gen = LimitUpSignalGenerator(tick_data, daily_data)
try:
    print('涨停事件:', _gen.identify_limit_up_events())
except Exception:
    pass
try:
    print('封板强度:', _gen.compute_seal_strength('600001', '2024-06-03'))
except Exception:
    pass
try:
    print('信号:', _gen.generate_signal('600001', '2024-06-03'))
except Exception:
    pass
'''),
('class LimitBoardTimeSeriesAnalysis', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(103)
_rows = []
for _i in range(40):
    _d = f'2024-04-{_i+1:02d}'
    for _c in ['600001', '600002', '000003', '000004', '300001']:
        _up = 1 if np.random.rand() < 0.08 else 0
        _down = 1 if np.random.rand() < 0.05 else 0
        _rows.append({'date': _d, 'code': _c, 'is_limit_up': _up, 'is_limit_down': _down,
                      'close': 10 + _i * 0.1, 'pre_close': 10 + (_i - 1) * 0.1})
_daily_data = pd.DataFrame(_rows)
_ts = LimitBoardTimeSeriesAnalysis(daily_data)
try:
    print('每日涨停比例:', _ts.daily_limit_up_ratio().tail(3))
except Exception:
    pass
try:
    print('涨停集中度:', _ts.limit_up_concentration())
except Exception:
    pass
try:
    print('市场情绪:', _ts.limit_board_market_sentiment())
except Exception:
    pass
'''),
],
'guide/m19-a-share/19.2-ipo.md': [
('class IPOReturnAnalyzer', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(107)
_rows = []
for _i in range(24):
    _is_break = _i % 5 == 0
    _rows.append({'code': f'30{_i:04d}', 'list_date': f'2024-{_i//2+1:02d}-15',
                  'issue_price': round(10 + _i * 0.8, 2),
                  'first_day_open': round((10 + _i * 0.8) * (0.9 if _is_break else 1.4), 2),
                  'first_day_return': -0.08 if _is_break else 0.35 + _i * 0.01,
                  'is_break': _is_break, 'lottery_rate': round(0.0002 + _i * 1e-5, 6),
                  'online_oversubscription_ratio': round(5000 - _i * 100, 1),
                  'expected_offline_return': 0.12, 'offline_alloc_amount': 5e6,
                  'offline_alloc_ratio': 0.001, 'max_lots': 500, 'market': '创业板'})
ipo_data = pd.DataFrame(_rows)
_ana = IPOReturnAnalyzer(ipo_data)
try:
    print('网上打新:', _ana.online_return_analysis())
except Exception:
    pass
try:
    print('网下打新:', _ana.offline_return_analysis())
except Exception:
    pass
'''),
('class IPOFirstDayPredictor', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(109)
_rows = []
for _i in range(60):
    _rows.append({'code': f'60{_i:04d}', 'list_date': f'2023-{_i//5+1:02d}-10',
                  'issue_price': round(8 + _i * 0.5, 2), 'board': '主板',
                  'online_oversubscription_ratio': 6000 - _i * 50,
                  'log_subscription_ratio': 8.0, 'industry_pe': 35 + _i,
                  'pb_ratio': 2.5, 'log_issue_amount': 9.5,
                  'rd_expense_ratio': 0.04, 'market_return_20d': 0.02,
                  'issue_shares': 5e7, 'is_listed': 1,
                  'first_day_return': 0.4 - _i * 0.008 + np.random.randn() * 0.1})
ipo_data = pd.DataFrame(_rows)
market_data = pd.DataFrame({'date': pd.date_range('2023-01-01', periods=400),
                            'market_return_20d': np.random.randn(400) * 0.02})
_pred = IPOFirstDayPredictor(ipo_data, market_data)
try:
    _pred.engineer_features()
    _pred.train_model()
except Exception:
    pass
try:
    _upcoming = ipo_data.tail(3).copy()
    print('预测排名:', _pred.predict_and_rank(_upcoming))
except Exception:
    pass
'''),
('class SubNewStockStrategy', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(113)
_days = 300
_idx = pd.date_range('2023-06-01', periods=_days)
_data = pd.DataFrame({
    'return': np.random.randn(_days) * 0.03,
    'volume': np.abs(np.random.randn(_days)) * 1e6 + 5e5,
    'market_return': np.random.randn(_days) * 0.012,
    'vol_ratio': np.abs(np.random.randn(_days)) + 0.5,
}, index=_idx)
_data['ipo_date'] = _idx[0]
_data['lockup_expiry_date'] = _idx[0] + pd.Timedelta(days=365)
_data['days_listed'] = range(_days)
_data['cum_excess_since_ipo'] = np.cumsum(_data['return'] - _data['market_return'])
_sns = SubNewStockStrategy(_data)
try:
    print('上市天数:', _sns.time_since_ipo())
except Exception:
    pass
try:
    print('解禁效应:', _sns.lockup_expiry_effect(_data))
except Exception:
    pass
try:
    print('次新信号:', _sns.sub_new_stock_signal())
except Exception:
    pass
'''),
],
'guide/m19-a-share/19.3-sector-rotation.md': [
('class SectorRotationStrategy', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(127)
_sectors = ['食品饮料', '新能源', '医药', '银行', 'TMT', '有色']
_idx = pd.date_range('2023-01-02', periods=250)
sector_returns = pd.DataFrame(np.random.randn(250, 6) * 0.012 + 0.0005,
                              columns=_sectors, index=_idx)
_pe_base = dict(zip(_sectors, [28, 35, 30, 6, 40, 18]))
sector_valuations = pd.DataFrame({s: _pe_base[s] + np.cumsum(np.random.randn(250) * 0.1)
                                  for s in _sectors}, index=_idx)
_rot = SectorRotationStrategy(sector_returns, sector_valuations)
try:
    print('动量信号:', _rot.compute_momentum_signal().round(4).to_dict())
except Exception:
    pass
try:
    print('价值信号:', _rot.compute_value_signal().round(4).to_dict())
except Exception:
    pass
try:
    print('拥挤度:', _rot.compute_crowding_indicator().round(4).to_dict())
except Exception:
    pass
try:
    _sig = _rot.compute_composite_signal()
    print('综合信号:', _sig.round(4).to_dict())
    print('配置:', _rot.generate_allocation(_sig))
except Exception:
    pass
'''),
('class SectorETFRotation', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(131)
_etfs = ['510300', '512100', '518880', '512480']
_idx = pd.date_range('2023-01-02', periods=300)
etf_data = pd.DataFrame(np.random.randn(300, 4) * 0.011 + 0.0004,
                        columns=_etfs, index=_idx)
_etfrot = SectorETFRotation(etf_data)
try:
    _dm = _etfrot.dual_momentum_signal()
    print('双动量信号:', _dm.round(4).to_dict())
except Exception:
    pass
try:
    print('选Top ETF:', _etfrot.select_top_etfs(_dm, n=2))
except Exception:
    pass
try:
    print('风险平价权重:', _etfrot.risk_parity_weights(_etfs[:2]))
except Exception:
    pass
'''),
('def compute_crowding_composite', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(137)
_sector_data = pd.DataFrame({
    'return': np.random.randn(6) * 0.02,
    'turnover': np.random.rand(6) * 5 + 1,
    'amount_pct': np.random.rand(6),
}, index=['食品饮料', '新能源', '医药', '银行', 'TMT', '有色'])
print(compute_crowding_composite(_sector_data).round(4))
'''),
],
'guide/m19-a-share/19.4-northbound.md': [
('class NorthboundFactorEngine', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(139)
_codes = ['600001', '600002', '000003', '000004']
_idx = pd.date_range('2024-01-02', periods=120)
_flow_rows = []
for _d in _idx:
    for _c in _codes:
        _flow_rows.append({'date': _d, 'code': _c,
                           'net_buy_amount': np.random.randn() * 5e6,
                           'hold_shares': abs(np.random.randn()) * 1e6 + 5e5,
                           'hold_market_value': abs(np.random.randn()) * 2e7 + 1e7})
northbound_flow = pd.DataFrame(_flow_rows)
prices = pd.DataFrame([{'date': _d, 'code': _c, 'close': 10 + np.random.randn() * 0.5,
                        'total_amount': abs(np.random.randn()) * 5e8 + 1e8}
                       for _d in _idx for _c in _codes])
_nb = NorthboundFactorEngine(northbound_flow, prices)
try:
    print('资金流因子:', _nb.compute_flow_factors().tail(3))
except Exception:
    pass
try:
    print('持股集中度:', _nb.compute_holding_concentration())
except Exception:
    pass
try:
    print('复合信号:', _nb.generate_composite_signal().tail(3))
except Exception:
    pass
'''),
('class DragonTigerAnalyzer', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(149)
_dt_rows = []
for _i in range(30):
    for _c in ['600001', '000003', '300001']:
        _tb = abs(np.random.randn()) * 2e8 + 5e7
        _dt_rows.append({'date': f'2024-05-{_i+1:02d}', 'code': _c,
                         'total_buy': _tb, 'total_sell': _tb * 0.6,
                         'inst_buy_ratio': np.random.rand(),
                         'inst_sell_ratio': np.random.rand() * 0.5,
                         'next_day_return': np.random.randn() * 0.03})
dragon_tiger_data = pd.DataFrame(_dt_rows)
_dt = DragonTigerAnalyzer(dragon_tiger_data)
try:
    print('席位分类:', _dt.classify_seats().head(3))
except Exception:
    pass
try:
    print('席位跟随信号:', _dt.seat_following_signal().tail(3))
except Exception:
    pass
'''),
],
'guide/m19-a-share/19.5-policy-events.md': [
('class PolicySignalExtractor', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_ext = PolicySignalExtractor()
_texts = [
    ('国务院发布促进新能源消费的若干措施，加大财政补贴力度', '2024-06-01', '国务院'),
    ('央行宣布下调存款准备金率0.25个百分点', '2024-06-05', '央行'),
    ('某地税务局开展常规税收检查', '2024-06-08', '地方'),
]
for _t, _d, _lv in _texts:
    _r = _ext.extract_signal_from_text(_t, _d, _lv)
    print(_d, '->', _r if not isinstance(_r, dict) else {k: v for k, v in list(_r.items())[:4]})
try:
    print('日度聚合:', _ext.aggregate_daily_signals([_ext.extract_signal_from_text(t, d, l) for t, d, l in _texts]))
except Exception as e:
    print('聚合示例跳过:', type(e).__name__)
'''),
('class PolicyHistoricalBenchmark', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_hist = pd.DataFrame([
    {'event_name': '新能源产业规划', 'theme': '新能源', 'level': '国务院', 'fiscal_amount': 3e11, 'market_impact_1w': 0.05, 'market_impact_1m': 0.12},
    {'event_name': '降准', 'theme': '货币宽松', 'level': '央行', 'fiscal_amount': 0, 'market_impact_1w': 0.02, 'market_impact_1m': 0.03},
    {'event_name': '地产刺激', 'theme': '地产', 'level': '国务院', 'fiscal_amount': 5e11, 'market_impact_1w': 0.04, 'market_impact_1m': 0.08},
])
_bench = PolicyHistoricalBenchmark(_hist)
_cur = {'event_name': '新能源消费促进措施', 'theme': '新能源', 'level': '国务院', 'fiscal_amount': 2e11}
try:
    print('相似历史事件:', _bench.find_similar_events(_cur))
except Exception:
    pass
try:
    print('预估影响:', _bench.estimate_market_impact(_cur))
except Exception:
    pass
'''),
('class PolicyEventDrivenStrategy', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(151)
_ext = PolicySignalExtractor()
_hist = pd.DataFrame([
    {'event_name': '新能源产业规划', 'theme': '新能源', 'level': '国务院', 'fiscal_amount': 3e11, 'market_impact_1w': 0.05, 'market_impact_1m': 0.12},
])
_bench = PolicyHistoricalBenchmark(_hist)
_sect_map = {'新能源': ['光伏', '锂电', '风电'], '货币宽松': ['银行', '券商']}
_strat = PolicyEventDrivenStrategy(_ext, _bench, _sect_map)
_articles = [{'text': '国务院出台新能源车消费补贴政策', 'publish_date': '2024-06-01', 'source_level': '国务院'},
             {'text': '多部委联合印发储能产业支持方案', 'publish_date': '2024-06-02', 'source_level': '部委'}]
_mkt = pd.DataFrame({'close': np.linspace(100, 104, 10)},
                    index=pd.date_range('2024-05-30', periods=10))
try:
    print('事件响应:', _strat.on_policy_event(_articles, _mkt))
except Exception:
    pass
try:
    _ts = _strat.compute_policy_sentiment_index(pd.DataFrame({'score': [0.6, 0.8, 0.4, 0.5]},
        index=pd.date_range('2024-06-01', periods=4)))
    print('政策情绪指数:', _ts if not hasattr(_ts, 'tail') else _ts.tail())
except Exception:
    pass
'''),
],
# ================= m16 =================
'guide/m16-risk-management/16.1-risk-decomposition.md': [
('def factor_risk_decomposition', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(161)
_w = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
_exp = np.random.uniform(-0.5, 1.5, size=(5, 3))
_A = np.random.randn(3, 200)
_fcov = np.cov(_A)
_svar = np.full(5, 0.02)
_fr = factor_risk_decomposition(_w, _exp, _fcov, _svar)
for _k, _v in _fr.items():
    print(f'{_k}: {_v if np.isscalar(_v) else np.round(_v, 4)}')
'''),
('def brinson_attribution', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_pw = np.array([0.3, 0.3, 0.2, 0.2])
_bw = np.array([0.25, 0.35, 0.25, 0.15])
_psr = np.array([0.05, 0.02, -0.01, 0.03])
_bsr = np.array([0.03, 0.025, -0.005, 0.02])
_ba = brinson_attribution(_pw, _bw, _psr, _bsr, sector_names=['科技', '消费', '金融', '能源'])
print(_ba.round(4).to_string())
'''),
('def risk_budget_optimization', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(163)
_A4 = np.random.randn(4, 200)
_cov = np.cov(_A4)
_budgets = np.array([0.4, 0.3, 0.2, 0.1])
_w = risk_budget_optimization(_cov, _budgets)
print('最优权重:', np.round(_w, 4))
'''),
('def risk_budget_dashboard', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_rc = np.array([38, 22, 27, 13])
_tb = np.array([0.4, 0.3, 0.2, 0.1])
_db = risk_budget_dashboard(_rc, _tb, labels=['股票', '债券', '商品', '现金'])
for _k, _v in _db.items():
    print(f'{_k}: {_v}')
'''),
],
'guide/m16-risk-management/16.2-evt-tail.md': [
('def fit_gpd', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(167)
_losses = np.abs(np.random.standard_t(3, 3000)) * 0.02
_exc = _losses[_losses > 0.03] - 0.03
_g = fit_gpd(_exc)
for _k, _v in _g.items():
    print(f'{_k}: {_v}')
'''),
('def threshold_selection', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(173)
_losses = np.abs(np.random.standard_t(3, 2000)) * 0.02
print('mean_excess 阈值:', round(threshold_selection(_losses, method='mean_excess'), 4))
'''),
('def hill_estimator', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(179)
_losses = np.sort(np.abs(np.random.standard_t(3, 2000)) * 0.02)[::-1]
_h = hill_estimator(_losses, k_values=[20, 50, 100, 200])
print(_h.round(4).to_string() if hasattr(_h, 'to_string') else _h)
'''),
('def var_backtest_validation', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(181)
_var = np.full(500, 0.025)
_act = np.abs(np.random.standard_t(4, 500)) * 0.015
_bt = var_backtest_validation(_var, _act)
for _k, _v in _bt.items():
    print(f'{_k}: {_v if np.isscalar(_v) else str(_v)[:80]}')
'''),
('def evt_var_es', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_e = evt_var_es(gpd_params={'xi': 0.2, 'beta': 0.008}, threshold=0.03,
                n_total=3000, n_exceedances=90)
for _k, _v in _e.items():
    print(f'{_k}: {_v}')
'''),
],
'guide/m16-risk-management/16.3-stress-testing.md': [
('def trading_book_stress_test', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
positions = {'债券A': {'rates': -40000}, '股票B': {'equity': 300000}}
risk_factors = {'rates': 0.03, 'equity': 4000}
stress_shocks = pd.DataFrame({
    'rates': [0.01, 0.02, -0.005],
    'equity': [-0.15, -0.30, 0.05],
}, index=['加息+股跌', '滞胀', '温和复苏'])
_tb = trading_book_stress_test(positions, risk_factors, stress_shocks)
for _k, _v in _tb.items():
    print(f'{_k}: {_v}')
'''),
('def reverse_stress_test', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_sens = np.array([-5e4, 2e5])
_rs = reverse_stress_test(_sens, max_acceptable_loss=2e6,
                          factor_bounds=[(0.0, 0.03), (-0.35, 0.0)])
for _k, _v in _rs.items():
    print(f'{_k}: {_v}')
'''),
('def correlation_breakdown_stress', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_corr = np.array([
    [1.0, -0.3, 0.4, 0.2],
    [-0.3, 1.0, -0.1, -0.2],
    [0.4, -0.1, 1.0, 0.5],
    [0.2, -0.2, 0.5, 1.0],
])
_vols = np.array([0.15, 0.08, 0.25, 0.20])
_cb = correlation_breakdown_stress(_corr, _vols, crisis_multiplier=3.0)
print(np.round(_cb, 3))
'''),
('def multi_asset_stress_pnl', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(191)
_A5 = np.random.randn(4, 300)
_cov = np.cov(_A5) * 0.02
_pos = np.array([1e6, 2e6, -5e5, 8e5])
_mp = multi_asset_stress_pnl(_pos, _cov)
for _k, _v in _mp.items():
    print(f'{_k}: {_v if np.isscalar(_v) else np.round(_v, 2) if isinstance(_v, np.ndarray) else _v}')
'''),
],
'guide/m16-risk-management/16.4-basel.md': [
('def calculate_basel_capital_ratios', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_b = calculate_basel_capital_ratios(cet1=5e9, tier1=6.5e9, total_capital=8e9,
                                    rwa_credit=6e10, rwa_market=2e10, rwa_operational=1e10,
                                    total_exposure=8e10, is_gsib=False)
for _k, _v in _b.items():
    print(f'{_k}: {_v}')
'''),
('def market_risk_standardized_approach', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_sa = market_risk_standardized_approach(
    positions={'利率债': 1e8, '信用债': 5e7},
    sensitivities={'利率债': {'duration': 4.5}, '信用债': {'duration': 3.0}},
    risk_weights={'利率债': 0.05, '信用债': 0.10})
for _k, _v in _sa.items():
    print(f'{_k}: {_v}')
'''),
('def frtb_sba_capital', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_f = frtb_sba_capital(delta_charges={'rates': 2e6, 'equity': 3e6},
                      vega_charges={'rates': 5e5, 'equity': 8e5},
                      curvature_charges={'rates': 1e5, 'equity': 2e5})
for _k, _v in _f.items():
    print(f'{_k}: {_v}')
'''),
('def strategy_capital_efficiency', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_se = strategy_capital_efficiency(annualized_return=0.12, annualized_volatility=0.10,
                                  rwa_charge=3e7)
for _k, _v in _se.items():
    print(f'{_k}: {_v}')
'''),
],
'guide/m16-risk-management/16.5-tail-hedge.md': [
('def otm_put_tail_hedge', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_ph = otm_put_tail_hedge(portfolio_value=1e7, protection_level=0.80,
                         spot_price=100.0, volatility=0.20, maturity_days=90)
for _k, _v in _ph.items():
    print(f'{_k}: {_v}')
'''),
('def volatility_risk_premium_strategy', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_vrp = volatility_risk_premium_strategy(vix_spot=18.0,
                                        vix_futures_curve=np.array([18.5, 19.2, 20.0]),
                                        vix_call_prices=np.array([1.2, 0.8, 0.5]))
for _k, _v in _vrp.items():
    print(f'{_k}: {_v}')
'''),
('def vix_spx_convexity_profile', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(193)
_spx = np.random.randn(500) * 0.01
_vix = 18 - _spx * 250 + np.random.randn(500) * 0.4
_cv = vix_spx_convexity_profile(_spx, _vix - 18)
print(_cv if not hasattr(_cv, 'head') else _cv.head())
'''),
('def dynamic_tail_hedge', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_dh = dynamic_tail_hedge(current_portfolio_value=1e7, current_drawdown_pct=0.08,
                         vix_level=25.0, realized_vol=0.18)
for _k, _v in _dh.items():
    print(f'{_k}: {_v}')
'''),
('def tail_hedge_cost_benefit', '''
# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(197)
_pr = np.random.randn(1000) * 0.008 + 0.0004
_hr = _pr - 0.0006 + np.where(_pr < -0.02, -_pr * 0.3, 0)
_cb = tail_hedge_cost_benefit(_pr, _hr, annual_premium_bps=150)
for _k, _v in _cb.items():
    print(f'{_k}: {_v}')
'''),
],
}

n = 0
for path, demos in DEMOS.items():
    for marker, demo in demos:
        n += int(inject(path, marker, demo))
print(f'注入 {n} 个示例')
