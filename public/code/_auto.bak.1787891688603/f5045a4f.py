# @quantlab/output: f5045a4f
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

# ==================== 监控指标 ====================

@dataclass
class StrategyMetrics:
    """策略运行指标"""
    strategy_name: str
    timestamp: float = 0.0

    # PnL指标
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    daily_pnl: float = 0.0
    total_commission: float = 0.0

    # 交易指标
    n_orders_today: int = 0
    n_fills_today: int = 0
    n_cancels_today: int = 0
    fill_rate: float = 0.0
    avg_slippage_bp: float = 0.0

    # 风险指标
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    leverage: float = 0.0
    var_99: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0

    # 信号指标
    signal_quality_score: float = 0.0
    n_signals_today: int = 0
    signal_dispersion: float = 0.0

@dataclass
class SystemMetrics:
    """系统运行指标"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_latency_ms: float = 0.0
    kafka_lag: int = 0
    db_connections_active: int = 0

    tick_rate_per_sec: float = 0.0
    order_rate_per_sec: float = 0.0

    process_uptime_hours: float = 0.0
    n_restarts: int = 0

class AlertLevel:
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class Alert:
    """告警消息"""
    level: str
    source: str
    message: str
    timestamp: float = field(default_factory=time.time)
    value: float = 0.0
    threshold: float = 0.0

# ==================== 策略监控器 ====================

class StrategyMonitor:
    """策略运行状态监控器"""

    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.logger = logging.getLogger(f"monitor.{strategy_name}")

        # 历史指标存储（用于趋势分析）
        self.metrics_history: deque = deque(maxlen=1000)
        self.alert_history: deque = deque(maxlen=500)

        # 告警去重（相同类型告警N秒内不重复发送）
        self._alert_cooldown: Dict[str, float] = {}
        self.alert_cooldown_seconds = 300  # 5分钟

        # PnL追踪
        self.peak_equity = 0.0
        self.max_drawdown = 0.0

        # 阈值配置
        self.thresholds = {
            'max_daily_loss': -50000.0,
            'max_drawdown_pct': 0.15,
            'max_leverage': 3.0,
            'max_cancel_rate': 0.30,
            'min_fill_rate': 0.50,
            'max_signal_silence_minutes': 30,
            'max_slippage_bp': 20.0,
        }

        # 告警处理器（可配置多个输出通道）
        self.alert_handlers: list = []

    def add_alert_handler(self, handler):
        """添加告警处理器（如飞书、短信、邮件等）"""
        self.alert_handlers.append(handler)

    def record_metrics(self, metrics: StrategyMetrics):
        """记录一个指标快照"""
        metrics.timestamp = time.time()
        self.metrics_history.append(metrics)

        # 更新峰值和回撤
        current_equity = metrics.realized_pnl + metrics.unrealized_pnl
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_equity) / abs(self.peak_equity)
            self.max_drawdown = max(self.max_drawdown, drawdown)
            metrics.max_drawdown = self.max_drawdown

        # 执行告警检查
        self._check_alerts(metrics)

    def _check_alerts(self, metrics: StrategyMetrics):
        """检查各项指标是否触发告警阈值"""
        alerts = []

        # 1. 日内亏损检查
        if metrics.daily_pnl < self.thresholds['max_daily_loss']:
            alerts.append(Alert(
                AlertLevel.CRITICAL, self.strategy_name,
                f"日内亏损超限: {metrics.daily_pnl:,.0f}",
                value=metrics.daily_pnl,
                threshold=self.thresholds['max_daily_loss']
            ))

        # 2. 最大回撤检查
        if metrics.max_drawdown > self.thresholds['max_drawdown_pct']:
            alerts.append(Alert(
                AlertLevel.CRITICAL, self.strategy_name,
                f"最大回撤超限: {metrics.max_drawdown:.2%}",
                value=metrics.max_drawdown,
                threshold=self.thresholds['max_drawdown_pct']
            ))

        # 3. 杠杆率检查
        if metrics.leverage > self.thresholds['max_leverage']:
            alerts.append(Alert(
                AlertLevel.WARNING, self.strategy_name,
                f"杠杆率超限: {metrics.leverage:.2f}x",
                value=metrics.leverage,
                threshold=self.thresholds['max_leverage']
            ))

        # 4. 撤单率检查
        cancel_rate = (metrics.n_cancels_today / max(metrics.n_orders_today, 1))
        if cancel_rate > self.thresholds['max_cancel_rate']:
            alerts.append(Alert(
                AlertLevel.WARNING, self.strategy_name,
                f"撤单率过高: {cancel_rate:.1%}",
                value=cancel_rate,
                threshold=self.thresholds['max_cancel_rate']
            ))

        # 5. 成交率检查
        if (metrics.n_orders_today > 10 and
            metrics.fill_rate < self.thresholds['min_fill_rate']):
            alerts.append(Alert(
                AlertLevel.WARNING, self.strategy_name,
                f"成交率过低: {metrics.fill_rate:.1%}",
                value=metrics.fill_rate,
                threshold=self.thresholds['min_fill_rate']
            ))

        # 6. 滑点检查
        if abs(metrics.avg_slippage_bp) > self.thresholds['max_slippage_bp']:
            alerts.append(Alert(
                AlertLevel.WARNING, self.strategy_name,
                f"滑点过高: {metrics.avg_slippage_bp:.1f}bp",
                value=metrics.avg_slippage_bp,
                threshold=self.thresholds['max_slippage_bp']
            ))

        # 7. 信号沉默检查
        if (metrics.n_signals_today == 0 and
            time.time() - metrics.timestamp > self.thresholds['max_signal_silence_minutes'] * 60):
            alerts.append(Alert(
                AlertLevel.INFO, self.strategy_name,
                "策略无信号输出，请检查数据源和策略逻辑"
            ))

        # 发送告警（带去重）
        for alert in alerts:
            if self._should_send_alert(alert):
                self._send_alert(alert)

    def _should_send_alert(self, alert: Alert) -> bool:
        """检查告警是否应发送（去重逻辑）"""
        alert_key = f"{alert.level}:{alert.source}:{alert.message[:30]}"
        last_sent = self._alert_cooldown.get(alert_key, 0)

        if time.time() - last_sent > self.alert_cooldown_seconds:
            self._alert_cooldown[alert_key] = time.time()
            return True

        # CRITICAL级别告警不受冷却限制
        if alert.level == AlertLevel.CRITICAL:
            return True

        return False

    def _send_alert(self, alert: Alert):
        """发送告警到所有处理器"""
        self.alert_history.append(alert)

        # 日志
        log_func = {
            AlertLevel.INFO: self.logger.info,
            AlertLevel.WARNING: self.logger.warning,
            AlertLevel.CRITICAL: self.logger.error,
        }.get(alert.level, self.logger.info)

        log_func(f"[{alert.level}] {alert.source}: {alert.message} "
                f"(值={alert.value:.2f}, 阈值={alert.threshold:.2f})")

        # 推送告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"告警处理器异常: {e}")

    def get_status_summary(self) -> dict:
        """获取当前状态摘要"""
        if not self.metrics_history:
            return {'status': 'NO_DATA'}

        latest = self.metrics_history[-1]

        # 判断总体状态
        status = 'HEALTHY'
        reasons = []

        if latest.max_drawdown > self.thresholds['max_drawdown_pct']:
            status = 'CRITICAL'
            reasons.append(f"回撤{latest.max_drawdown:.1%}")
        elif latest.daily_pnl < self.thresholds['max_daily_loss']:
            status = 'CRITICAL'
            reasons.append(f"亏损{latest.daily_pnl:,.0f}")
        elif latest.leverage > self.thresholds['max_leverage']:
            status = 'WARNING'
            reasons.append(f"杠杆{latest.leverage:.1f}x")

        return {
            'strategy': self.strategy_name,
            'status': status,
            'concerns': reasons,
            'daily_pnl': latest.daily_pnl,
            'max_drawdown': latest.max_drawdown,
            'leverage': latest.leverage,
            'fill_rate': latest.fill_rate,
            'n_orders_today': latest.n_orders_today,
            'last_update': datetime.fromtimestamp(latest.timestamp).isoformat()
        }

# ==================== Grafana仪表盘数据源 ====================

class MetricsExporter:
    """将监控指标导出为Prometheus格式，供Grafana仪表盘消费"""

    def __init__(self, pushgateway_url='localhost:9091'):
        self.pushgateway = pushgateway_url
        self.metrics_registry = {}

    def register_metric(self, name, description, labels=None):
        """注册一个指标"""
        self.metrics_registry[name] = {
            'description': description,
            'value': 0.0,
            'labels': labels or {}
        }

    def set_metric(self, name, value, labels=None):
        """设置指标值"""
        if name in self.metrics_registry:
            self.metrics_registry[name]['value'] = value
            if labels:
                self.metrics_registry[name]['labels'].update(labels)

    def push_metrics(self):
        """推送指标到Pushgateway"""
        # 生成Prometheus文本格式
        lines = []
        for name, metric in self.metrics_registry.items():
            lines.append(f"# HELP {name} {metric['description']}")
            lines.append(f"# TYPE {name} gauge")

            labels_str = ','.join(f'{k}="{v}"' for k, v in metric['labels'].items())
            if labels_str:
                lines.append(f"{name}{{{labels_str}}} {metric['value']}")
            else:
                lines.append(f"{name} {metric['value']}")

        payload = '\n'.join(lines) + '\n'

        # HTTP POST to Pushgateway
        try:
            import urllib.request
            url = f"http://{self.pushgateway}/metrics/job/quant_strategy"
            req = urllib.request.Request(url, data=payload.encode(), method='POST')
            urllib.request.urlopen(req)
        except Exception as e:
            logging.error(f"推送指标失败: {e}")

# ==================== 使用示例 ====================

# 初始化监控
monitor = StrategyMonitor("momentum_strategy_v2")
exporter = MetricsExporter()

# 模拟告警处理器（飞书webhook）
def lark_alert_handler(alert: Alert):
    """飞书告警推送"""
    emoji = {'CRITICAL': '&#x1F534', 'WARNING': '&#x1F7E0', 'INFO': '&#x1F7E2'}
    msg = {
        "msg_type": "text",
        "content": {
            "text": f"{emoji.get(alert.level, '')} [{alert.level}] {alert.source}\n"
                   f"{alert.message}\n"
                   f"时间: {datetime.fromtimestamp(alert.timestamp).strftime('%H:%M:%S')}"
        }
    }
    # 实际发送: requests.post(webhook_url, json=msg)
    print(f"[飞书告警] {alert.level}: {alert.message}")

monitor.add_alert_handler(lark_alert_handler)

# 模拟运行一段时间
print("策略监控系统演示:")
for i in range(5):
    metrics = StrategyMetrics(
        strategy_name="momentum_strategy_v2",
        realized_pnl=np.random.uniform(-5000, 10000),
        unrealized_pnl=np.random.uniform(-3000, 5000),
        daily_pnl=np.random.uniform(-30000, 20000),
        n_orders_today=np.random.randint(5, 50),
        n_fills_today=np.random.randint(3, 40),
        n_cancels_today=np.random.randint(0, 5),
        fill_rate=np.random.uniform(0.6, 1.0),
        avg_slippage_bp=np.random.uniform(-5, 15),
        leverage=np.random.uniform(0.5, 3.5),
        max_drawdown=np.random.uniform(0.0, 0.2),
        signal_quality_score=np.random.uniform(-0.5, 1.0),
        n_signals_today=np.random.randint(20, 100),
    )
    monitor.record_metrics(metrics)
    time.sleep(0.1)

# 打印状态摘要
status = monitor.get_status_summary()
print(f"\n策略状态: {status['status']}")
if status['concerns']:
    print(f"关注事项: {', '.join(status['concerns'])}")
print(f"日内PnL: {status['daily_pnl']:,.0f}")
print(f"最大回撤: {status['max_drawdown']:.2%}")
print(f"杠杆率: {status['leverage']:.2f}x")
