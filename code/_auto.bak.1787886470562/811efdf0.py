# @quantlab/output: 811efdf0
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np

@dataclass
class ComplianceRule:
    """合规规则定义"""
    rule_id: str
    name: str
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL

    # 指标监控参数
    metric_name: str
    threshold: float
    window_seconds: int = 60
    cooldown_seconds: int = 300

class ComplianceMonitor:
    """合规监控器 - 实时检测违规行为"""

    def __init__(self):
        # 定义规则库
        self.rules = self._initialize_rules()

        # 订单历史（滑动窗口）
        self.order_history: deque = deque(maxlen=10000)
        self.cancel_history: deque = deque(maxlen=5000)
        self.fill_history: deque = deque(maxlen=10000)

        # 违规记录
        self.violations: deque = deque(maxlen=1000)

        # 状态追踪
        self.is_throttled = False  # 是否被限流
        self.trading_paused = False  # 交易是否暂停

    def _initialize_rules(self) -> List[ComplianceRule]:
        """初始化合规规则库"""
        return [
            ComplianceRule(
                'R001', '撤单率过高',
                '订单撤单率超过监管阈值', 'HIGH',
                metric_name='cancel_rate', threshold=0.30, window_seconds=300
            ),
            ComplianceRule(
                'R002', '自成交检测',
                '检测自己的买卖订单相互成交', 'CRITICAL',
                metric_name='self_trade_ratio', threshold=0.01, window_seconds=300
            ),
            ComplianceRule(
                'R003', '申报速率超限',
                '每秒钟订单申报数量超过交易所限制', 'HIGH',
                metric_name='order_rate_per_sec', threshold=300, window_seconds=5
            ),
            ComplianceRule(
                'R004', '价格异常偏离',
                '订单价格与最新成交价偏离超过合理范围', 'MEDIUM',
                metric_name='price_deviation_pct', threshold=0.05, window_seconds=60
            ),
            ComplianceRule(
                'R005', '大额申报未成交',
                '大额挂单在成交前被撤销（疑似spoofing）', 'CRITICAL',
                metric_name='spoofing_score', threshold=0.50, window_seconds=600
            ),
            ComplianceRule(
                'R006', '频繁修改订单',
                '短时间内对同一订单频繁修改价格/数量', 'MEDIUM',
                metric_name='modify_frequency', threshold=5, window_seconds=10
            ),
            ComplianceRule(
                'R007', '持仓超限',
                '单只股票持仓超过监管或内部限制', 'HIGH',
                metric_name='position_limit_pct', threshold=1.0, window_seconds=60
            ),
            ComplianceRule(
                'R008', 'T+0回转超限',
                '日内回转交易超过允许次数', 'MEDIUM',
                metric_name='day_trade_count', threshold=100, window_seconds=23400  # 交易时段
            ),
        ]

    def record_order(self, order_info: dict):
        """记录一笔订单"""
        order_info['timestamp'] = datetime.now()
        self.order_history.append(order_info)

    def record_cancel(self, order_id: str, timestamp: datetime = None):
        """记录一笔撤单"""
        self.cancel_history.append({
            'order_id': order_id,
            'timestamp': timestamp or datetime.now()
        })

    def record_fill(self, fill_info: dict):
        """记录一笔成交"""
        fill_info['timestamp'] = datetime.now()
        self.fill_history.append(fill_info)

    def check_compliance(self) -> List[dict]:
        """执行所有合规检查，返回违规列表"""
        now = datetime.now()
        violations = []

        for rule in self.rules:
            result = self._check_rule(rule, now)
            if result:
                violations.append(result)
                self.violations.append(result)

        # 如果存在CRITICAL违规，自动暂停交易
        if any(v['severity'] == 'CRITICAL' for v in violations):
            self.trading_paused = True

        return violations

    def _check_rule(self, rule: ComplianceRule, now: datetime) -> Optional[dict]:
        """检查单条合规规则"""
        window_start = now - timedelta(seconds=rule.window_seconds)

        # 根据规则类型计算指标
        current_value = None

        if rule.rule_id == 'R001':  # 撤单率
            recent_orders = [o for o in self.order_history
                           if o['timestamp'] > window_start]
            recent_cancels = [c for c in self.cancel_history
                            if c['timestamp'] > window_start]
            if len(recent_orders) > 20:  # 足够样本量才判断
                current_value = len(recent_cancels) / max(len(recent_orders), 1)

        elif rule.rule_id == 'R002':  # 自成交
            recent_fills = [f for f in self.fill_history
                          if f['timestamp'] > window_start]
            if recent_fills:
                self_trades = sum(1 for f in recent_fills if f.get('is_self_trade', False))
                current_value = self_trades / len(recent_fills)

        elif rule.rule_id == 'R003':  # 申报速率
            recent_orders = [o for o in self.order_history
                           if o['timestamp'] > window_start]
            if recent_orders:
                elapsed = (now - recent_orders[0]['timestamp']).total_seconds()
                current_value = len(recent_orders) / max(elapsed, 1)

        elif rule.rule_id == 'R004':  # 价格偏离
            recent_orders = [o for o in self.order_history
                           if o['timestamp'] > window_start]
            deviations = []
            for o in recent_orders:
                if 'market_price' in o and 'order_price' in o and o['market_price'] > 0:
                    dev = abs(o['order_price'] - o['market_price']) / o['market_price']
                    deviations.append(dev)
            if deviations:
                current_value = max(deviations)

        elif rule.rule_id == 'R005':  # Spoofing检测
            recent_orders = [o for o in self.order_history
                           if o['timestamp'] > window_start]
            spoofing_candidates = [
                o for o in recent_orders
                if o.get('quantity', 0) > 10000  # 大单
                and o.get('cancel_time') is not None
                and (o['cancel_time'] - o['timestamp']).total_seconds() < 0.5  # 0.5秒内撤销
                and o.get('filled_qty', 0) == 0  # 未成交
            ]
            if recent_orders:
                current_value = len(spoofing_candidates) / len(recent_orders)

        elif rule.rule_id == 'R006':  # 频繁修改
            recent_orders = [o for o in self.order_history
                           if o['timestamp'] > window_start]
            # 按order_id分组，检查每个订单的修改次数
            mod_counts = defaultdict(int)
            for o in recent_orders:
                if o.get('is_modify'):
                    mod_counts[o.get('order_id', '')] += 1
            if mod_counts:
                current_value = max(mod_counts.values())

        # 判断是否违规
        if current_value is not None and current_value > rule.threshold:
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'severity': rule.severity,
                'current_value': current_value,
                'threshold': rule.threshold,
                'window_seconds': rule.window_seconds,
                'timestamp': now.isoformat(),
                'description': (f"{rule.name}: 当前值={current_value:.3f} "
                              f"阈值={rule.threshold:.3f}")
            }

        return None

    def get_compliance_report(self) -> dict:
        """生成合规报告摘要"""
        return {
            'trading_paused': self.trading_paused,
            'is_throttled': self.is_throttled,
            'total_violations_today': len(self.violations),
            'violations_by_severity': {
                sev: sum(1 for v in self.violations if v['severity'] == sev)
                for sev in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            },
            'recent_violations': list(self.violations)[-10:]
        }

# ==================== 使用示例 ====================

monitor = ComplianceMonitor()

# 模拟正常交易
print("合规监控系统演示:")
for i in range(100):
    # 模拟订单
    monitor.record_order({
        'order_id': f'ORD_{i:05d}',
        'symbol': 'AAPL',
        'side': 'BUY',
        'quantity': np.random.randint(100, 5000),
        'order_price': 150.0 + np.random.uniform(-0.5, 0.5),
        'market_price': 150.0,
        'is_modify': np.random.random() < 0.1,
    })

    # 模拟一些撤单
    if np.random.random() < 0.15:  # 15%撤单率 - 正常
        monitor.record_cancel(f'ORD_{i:05d}')

    # 模拟一些成交
    if np.random.random() < 0.7:
        monitor.record_fill({
            'order_id': f'ORD_{i:05d}',
            'symbol': 'AAPL',
            'filled_qty': np.random.randint(100, 5000),
            'fill_price': 150.0,
            'is_self_trade': False,
        })

# 注入异常行为模拟：超高撤单率
for i in range(50):
    monitor.record_order({
        'order_id': f'SPAM_{i:05d}',
        'symbol': 'TSLA',
        'side': 'SELL',
        'quantity': 10000,
        'order_price': 250.0,
        'market_price': 250.0,
        'is_modify': False,
    })
    # 所有都立即撤单
    monitor.record_cancel(f'SPAM_{i:05d}')

# 执行合规检查
violations = monitor.check_compliance()
report = monitor.get_compliance_report()

print(f"\n合规检查报告:")
print(f"  交易状态: {'暂停' if report['trading_paused'] else '正常'}")
print(f"  今日违规数: {report['total_violations_today']}")
print(f"  按严重程度: {report['violations_by_severity']}")

if violations:
    print(f"\n  最新违规:")
    for v in violations[:5]:
        print(f"    [{v['severity']}] {v['description']}")
