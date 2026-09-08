# @quantlab/output: bb3e4826
class LightweightFeatureStore:
    """
    轻量级 Feature Store 实现（适用于中小型量化团队）。

    理念：在已有的数据基础设施（Parquet + Redis）上
    增加一层 Feature 抽象，避免引入重型框架。
    """

    def __init__(self,
                  offline_store_path: str,
                  redis_config: Dict = None):
        """
        参数:
            offline_store_path: 离线特征存储路径（Parquet 文件）
            redis_config: Redis 连接配置（用于在线服务）
        """
        self.offline_path = offline_store_path
        self.redis_client = None

        if redis_config:
            try:
                import redis
                self.redis_client = redis.Redis(**redis_config)
            except ImportError:
                print("redis 库未安装，在线特征服务不可用")

    def get_offline_features(self,
                              feature_names: List[str],
                              symbols: List[str],
                              start_date: str,
                              end_date: str) -> pd.DataFrame:
        """
        从离线存储获取历史特征值（用于回测）。

        自动处理 point-in-time join。
        """
        frames = []

        for feature in feature_names:
            feature_path = f"{self.offline_path}/{feature}/"

            try:
                feature_data = pd.read_parquet(
                    feature_path,
                    filters=[
                        ('symbol', 'in', symbols),
                        ('date', '>=', start_date),
                        ('date', '<=', end_date)
                    ]
                )
                feature_data = feature_data.set_index(['date', 'symbol'])
                frames.append(feature_data[[feature]])
            except FileNotFoundError:
                print(f"警告: 特征 '{feature}' 的数据未找到")
                continue

        if not frames:
            return pd.DataFrame()

        # 横向拼接
        result = pd.concat(frames, axis=1).reset_index()

        return result

    def get_online_features(self,
                             symbol: str,
                             feature_names: List[str]) -> Dict[str, float]:
        """
        从 Redis 在线存储获取最新的特征值（用于实时交易）。

        延迟目标：< 1ms（本地 Redis）或 < 5ms（网络 Redis）。
        """
        if self.redis_client is None:
            raise RuntimeError("Redis 未配置，无法获取在线特征")

        features = {}
        pipeline = self.redis_client.pipeline()

        for feat in feature_names:
            key = f"feature:{symbol}:{feat}"
            pipeline.get(key)

        try:
            values = pipeline.execute()
        except Exception as e:
            print(f"Redis pipeline 执行失败: {e}")
            return {}

        for feat, val in zip(feature_names, values):
            features[feat] = float(val) if val is not None else None

        return features

    def materialize_features(self,
                              feature_names: List[str],
                              date: str):
        """
        将当天的离线特征计算结果同步到在线 Redis 存储。

        应在每日批处理完成后调用。
        """
        if self.redis_client is None:
            return

        offline = self.get_offline_features(
            feature_names,
            symbols=[],  # 所有 symbol
            start_date=date,
            end_date=date
        )

        pipeline = self.redis_client.pipeline()

        for _, row in offline.iterrows():
            symbol = row['symbol']
            for feat in feature_names:
                if feat in row and not pd.isna(row[feat]):
                    key = f"feature:{symbol}:{feat}"
                    pipeline.set(key, float(row[feat]))

        pipeline.execute()
