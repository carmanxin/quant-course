# @quantlab/output: 56035269
class DataVersionControl:
    """
    量化数据的版本控制。

    使用时间旅行查询（Time Travel）获取任意历史时点的
    "当时已知"的数据快照，防止前视偏差（Look-ahead Bias）。
    """

    def __init__(self, storage_backend):
        self.backend = storage_backend

    def write_versioned(self,
                         data: pd.DataFrame,
                         dataset: str,
                         as_of_date: str,
                         is_revision: bool = False):
        """
        写入带版本的数据。

        参数:
            data: 数据
            dataset: 数据集名称（如 'financials', 'estimates'）
            as_of_date: 数据发布日
            is_revision: 是否为对已发布数据的修订
        """
        version = {
            'dataset': dataset,
            'as_of_date': as_of_date,
            'ingestion_timestamp': datetime.now().isoformat(),
            'is_revision': is_revision,
            'version_number': self._get_next_version(dataset, as_of_date)
        }

        self.backend.write(data, metadata=version)

    def get_as_of(self,
                   dataset: str,
                   observation_date: str,
                   as_of_date: str) -> pd.DataFrame:
        """
        获取 'as_of_date' 时点已知的、关于 'observation_date' 的数据。

        这禁止"使用未来信息"的 look-ahead bias。
        """
        # 查询 observation_date 之前、as_of_date 之前的最新版本
        return self.backend.query(
            dataset=dataset,
            observation_date=observation_date,
            ingested_before=as_of_date
        )

    def _get_next_version(self, dataset: str, as_of_date: str) -> int:
        """获取下一个版本号"""
        existing = self.backend.list_versions(dataset, as_of_date)
        return len(existing) + 1
