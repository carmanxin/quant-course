# @quantlab/output: b127eb37
class FeatureRegistry:
    """
    特征注册中心：统一管理在线和离线特征的定义和版本。

    确保同一特征在训练和推理时使用完全相同的逻辑。
    """

    def __init__(self):
        self.features: Dict[str, FeatureDefinition] = {}
        self.feature_transformations: Dict[str, callable] = {}

    def register(self,
                 feature_def: FeatureDefinition,
                 offline_compute_fn: callable,
                 online_compute_fn: Optional[callable] = None):
        """
        注册一个特征，同时提供在线和离线计算函数。

        参数:
            feature_def: 特征定义
            offline_compute_fn: 离线（回测）计算函数
            online_compute_fn: 在线（实时）计算函数，若为None则使用离线函数
        """
        self.features[feature_def.name] = feature_def
        self.feature_transformations[feature_def.name] = {
            'offline': offline_compute_fn,
            'online': online_compute_fn or offline_compute_fn
        }

    def compute_offline(self,
                         feature_name: str,
                         data: pd.DataFrame,
                         **kwargs) -> pd.Series:
        """使用离线函数计算特征"""
        if feature_name not in self.feature_transformations:
            raise ValueError(f"Feature '{feature_name}' not registered")

        fn = self.feature_transformations[feature_name]['offline']
        return fn(data, **kwargs)

    def compute_online(self,
                        feature_name: str,
                        data: Dict[str, Any],
                        **kwargs) -> float:
        """使用在线函数计算特征"""
        if feature_name not in self.feature_transformations:
            raise ValueError(f"Feature '{feature_name}' not registered")

        fn = self.feature_transformations[feature_name]['online']
        return fn(data, **kwargs)


# 示例：注册动量特征
def momentum_offline(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """离线计算：Pandas rolling window"""
    return data['close'].pct_change(window)


def momentum_online(data: Dict[str, Any], window: int = 20) -> float:
    """在线计算：增量更新（使用缓存的历史值）"""
    # data 包含 'current_close' 和 'close_N_days_ago'
    if data['close_N_days_ago'] is None or data['close_N_days_ago'] == 0:
        return 0.0
    return data['current_close'] / data['close_N_days_ago'] - 1.0


# 注册
registry = FeatureRegistry()
registry.register(
    FeatureDefinition(
        name="momentum_20d",
        description="20日价格动量",
        feature_type=FeatureType.PRICE_DERIVED,
        entity="stock",
        data_sources=["market_data"],
        computation_function="momentum",
        parameters={"window": 20},
        output_type="float",
        refresh_frequency="daily"
    ),
    offline_compute_fn=lambda data: momentum_offline(data, window=20),
    online_compute_fn=lambda data: momentum_online(data, window=20)
)
