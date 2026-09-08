# @quantlab/output: 2685ac01
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class FeatureType(Enum):
    """量化特征的类型分类"""
    PRICE_DERIVED = "price_derived"     # 基于价格计算：收益率、波动率、动量
    FUNDAMENTAL = "fundamental"         # 基本面：PE、PB、ROE
    ALTERNATIVE = "alternative"         # 另类数据：情绪、卫星图、供应链
    MACRO = "macro"                     # 宏观：利率、PMI、CPI
    MICROSTRUCTURE = "microstructure"   # 微观结构：价差、VPIN、订单不平衡
    RISK = "risk"                       # 风险：Beta、VaR、因子暴露
    CUSTOM = "custom"                   # 自定义/组合特征


@dataclass
class FeatureDefinition:
    """
    特征的完整定义，包括计算逻辑、数据依赖和元数据。
    """
    name: str                          # 特征名称（全局唯一）
    description: str                   # 描述
    feature_type: FeatureType          # 特征类型
    entity: str                        # 实体（如 'stock', 'futures'）
    data_sources: List[str]            # 数据源依赖
    computation_function: str          # 计算函数名
    parameters: Dict[str, Any]         # 计算参数
    output_type: str                   # 输出类型（float, int, category）
    refresh_frequency: str             # 刷新频率（'realtime', 'daily', 'monthly'）
    owner: str                         # 负责人
    version: int = 1                   # 版本号
    created_at: str = None             # 创建时间

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
