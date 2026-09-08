# @quantlab/output: f7cddcb8
class FeatureVersionManager:
    """
    特征版本管理器。

    支持：
    1. 特征定义的版本化存储
    2. 回滚到历史版本
    3. 版本间差异比较
    """

    def __init__(self, backend=None):
        self.backend = backend or {}  # 简化：使用内存字典
        self.feature_versions: Dict[str, List[Dict]] = {}

    def save_version(self,
                      feature_name: str,
                      definition: FeatureDefinition,
                      metadata: Dict[str, Any] = None):
        """
        保存特征的新版本。

        使用语义化版本号：MAJOR.MINOR.PATCH
        - MAJOR: 计算逻辑发生重大变更（可能改变特征含义）
        - MINOR: 参数调整或数据源变更
        - PATCH: 错误修复不影响特征语义
        """
        if feature_name not in self.feature_versions:
            self.feature_versions[feature_name] = []

        # 版本号递增
        if self.feature_versions[feature_name]:
            prev_version = self.feature_versions[feature_name][-1]['version']
            new_version = self._increment_version(
                prev_version, metadata.get('change_type', 'PATCH')
            )
        else:
            new_version = '1.0.0'

        version_record = {
            'version': new_version,
            'definition': definition,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'change_type': metadata.get('change_type', 'PATCH') if metadata
                           else 'PATCH'
        }

        self.feature_versions[feature_name].append(version_record)

        return new_version

    def get_version(self,
                     feature_name: str,
                     version: str = None,
                     as_of_timestamp: str = None) -> Dict:
        """
        获取指定版本的特征定义。

        参数:
            feature_name: 特征名称
            version: 版本号，若指定 as_of_timestamp 则忽略
            as_of_timestamp: 获取该时间点之前的最新版本
        """
        versions = self.feature_versions.get(feature_name, [])

        if version:
            for v in versions:
                if v['version'] == version:
                    return v
            return None

        if as_of_timestamp:
            ts = pd.Timestamp(as_of_timestamp)
            valid_versions = [v for v in versions
                              if pd.Timestamp(v['timestamp']) <= ts]
            return valid_versions[-1] if valid_versions else None

        return versions[-1] if versions else None

    def rollback(self, feature_name: str, target_version: str) -> Dict:
        """
        回滚到指定的历史版本。

        回滚会创建一个新版本，其计算逻辑与目标版本相同。
        """
        target = self.get_version(feature_name, target_version)
        if target is None:
            raise ValueError(f"Version '{target_version}' not found "
                             f"for feature '{feature_name}'")

        # 创建回滚版本（更新版本号，继承计算逻辑）
        rolled = self.save_version(
            feature_name,
            target['definition'],
            {
                'change_type': 'ROLLBACK',
                'rolled_from_version': target_version,
                'reason': 'Rollback requested'
            }
        )

        return self.get_version(feature_name, rolled)

    def compare_versions(self,
                          feature_name: str,
                          version_a: str,
                          version_b: str) -> Dict:
        """
        比较两个版本的特征定义差异。
        """
        a = self.get_version(feature_name, version_a)
        b = self.get_version(feature_name, version_b)

        if a is None or b is None:
            return {'error': 'Version not found'}

        diffs = {}

        # 比较参数
        params_a = a['definition'].parameters
        params_b = b['definition'].parameters

        all_params = set(list(params_a.keys()) + list(params_b.keys()))
        for param in all_params:
            val_a = params_a.get(param)
            val_b = params_b.get(param)
            if val_a != val_b:
                diffs[f'parameter.{param}'] = {
                    'old': val_a,
                    'new': val_b
                }

        return {
            'version_a': version_a,
            'version_b': version_b,
            'differences': diffs,
            'has_changes': len(diffs) > 0
        }

    def _increment_version(self,
                            current: str,
                            change_type: str) -> str:
        """语义化版本号递增"""
        major, minor, patch = map(int, current.split('.'))

        if change_type == 'MAJOR':
            return f"{major + 1}.0.0"
        elif change_type == 'MINOR':
            return f"{major}.{minor + 1}.0"
        else:  # PATCH or ROLLBACK
            return f"{major}.{minor}.{patch + 1}"
