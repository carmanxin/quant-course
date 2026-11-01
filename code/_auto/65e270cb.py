# @quantlab/output: 65e270cb
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any

class DataLineageTracker:
    """
    数据血缘追踪器。

    记录每个数据集的来源、转换步骤和依赖关系。
    使用有向无环图（DAG）表示数据流转。
    """

    def __init__(self):
        self.lineage_graph: Dict[str, Dict[str, Any]] = {}

    def record_transformation(self,
                               input_datasets: List[str],
                               output_dataset: str,
                               transformation_name: str,
                               parameters: Dict[str, Any],
                               code_version: str = 'latest') -> str:
        """
        记录一次数据转换的血缘信息。

        参数:
            input_datasets: 上游输入数据集名称列表
            output_dataset: 输出数据集名称
            transformation_name: 转换函数/任务名称
            parameters: 转换参数
            code_version: 代码版本
        返回:
            本次转换的唯一 ID
        """
        # 生成 lineage ID
        content = f"{transformation_name}:{output_dataset}:{datetime.now().isoformat()}"
        lineage_id = hashlib.md5(content.encode()).hexdigest()[:12]

        # 记录输入数据集的哈希（确保可复现）
        input_hashes = {}
        for ds in input_datasets:
            if ds in self.lineage_graph:
                input_hashes[ds] = self.lineage_graph[ds].get('output_hash')

        record = {
            'lineage_id': lineage_id,
            'timestamp': datetime.now().isoformat(),
            'input_datasets': input_datasets,
            'input_hashes': input_hashes,
            'output_dataset': output_dataset,
            'transformation': transformation_name,
            'parameters': parameters,
            'code_version': code_version,
            'dependencies': input_datasets.copy()
        }

        self.lineage_graph[output_dataset] = record

        return lineage_id

    def trace_lineage(self, dataset: str) -> Dict[str, Any]:
        """
        追溯指定数据集的完整上游血缘链。

        递归追溯所有上游依赖，构建完整的 DAG 路径。
        """
        if dataset not in self.lineage_graph:
            return {'dataset': dataset, 'error': 'No lineage recorded'}

        lineage = []
        to_visit = [dataset]
        visited = set()

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current in self.lineage_graph:
                record = self.lineage_graph[current]
                lineage.append({
                    'dataset': current,
                    'transformation': record['transformation'],
                    'lineage_id': record['lineage_id']
                })

                for upstream in record['dependencies']:
                    if upstream not in visited:
                        to_visit.append(upstream)

        return {
            'dataset': dataset,
            'upstream_lineage': lineage,
            'depth': len(lineage)
        }
