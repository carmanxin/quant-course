# @quantlab/output: 7b7549a8
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class StrategyStatus(Enum):
    RESEARCH = "研究中"
    PROTOTYPE = "原型验证"
    CODE_REVIEW = "代码审查中"
    PAPER_TRADING = "模拟交易中"
    LIVE_SMALL = "小资金实盘"
    LIVE_FULL = "全量实盘"
    RETIRED = "已退役"

@dataclass
class StrategyPipeline:
    """策略研发流水线 - 追踪策略从研究到实盘的完整生命周期"""

    strategy_id: str
    name: str
    researcher: str          # 量化研究员
    developer: str = ""      # 量化开发工程师
    reviewer: str = ""       # 代码审查人
    risk_analyst: str = ""   # 风险分析师

    status: StrategyStatus = StrategyStatus.RESEARCH
    created_at: str = ""
    updated_at: str = ""

    # 各阶段审批
    approvals: dict = None

    def __post_init__(self):
        if self.approvals is None:
            self.approvals = {}

    def advance_stage(self, new_status: StrategyStatus, approver: str):
        """推进策略到下一个阶段（需要相应角色审批）"""
        required_roles = {
            StrategyStatus.PROTOTYPE: "Senior Researcher",
            StrategyStatus.CODE_REVIEW: "Senior Developer",
            StrategyStatus.PAPER_TRADING: "Risk Manager",
            StrategyStatus.LIVE_SMALL: "Portfolio Manager",
            StrategyStatus.LIVE_FULL: "Investment Committee",
        }

        required = required_roles.get(new_status, "Admin")
        self.approvals[str(new_status)] = {
            'approved_by': approver,
            'role': required,
            'timestamp': datetime.now().isoformat()
        }
        self.status = new_status
        self.updated_at = datetime.now().isoformat()

        print(f"策略 {self.name}: {approver}({required}) 批准进入 [{new_status.value}]")

    def get_status_report(self):
        """生成策略当前状态报告"""
        print(f"\n策略: {self.name} [{self.strategy_id}]")
        print(f"  当前状态: {self.status.value}")
        print(f"  研究员: {self.researcher}")
        print(f"  开发工程师: {self.developer or '待分配'}")
        print(f"  审批历史:")
        for stage, approval in self.approvals.items():
            print(f"    {stage}: {approval['approved_by']} ({approval['role']})")

# ===== 模拟策略流水线 =====
print("策略研发流水线演示:\n")

strategy = StrategyPipeline(
    strategy_id="STRAT_2024_001",
    name="Multi-Factor Momentum Alpha",
    researcher="Alice Wang (QR)",
    developer="Bob Zhang (QD)",
    reviewer="Charlie Li (Senior QD)",
    risk_analyst="Diana Chen (Risk)"
)

strategy.advance_stage(StrategyStatus.PROTOTYPE, "Senior Researcher - David")
strategy.advance_stage(StrategyStatus.CODE_REVIEW, "Senior Developer - Charlie")
strategy.advance_stage(StrategyStatus.PAPER_TRADING, "Risk Manager - Diana")
strategy.advance_stage(StrategyStatus.LIVE_SMALL, "PM - Eric")

strategy.get_status_report()
