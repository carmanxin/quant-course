from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Project:
    name: str
    thesis: str
    results: list[str]
    stack: list[str]
    structure: dict[str, str] = field(default_factory=dict)


def render_readme(project: Project) -> str:
    result_lines = "\n".join(f"- {item}" for item in project.results)
    stack_line = " · ".join(f"`{item}`" for item in project.stack)
    tree = "\n".join(f"{path:<22} # {purpose}" for path, purpose in project.structure.items())
    return f"""# {project.name}

## Research Thesis

{project.thesis}

## Key Results

{result_lines}

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.run_experiment --config configs/baseline.yaml
```

## Tech Stack

{stack_line}

## Repository Structure

```text
{tree}
```

## Validation Protocol

Results use point-in-time data, walk-forward validation, explicit costs, and a locked holdout period.
"""


project = Project(
    name="A-Share Factor Research",
    thesis="检验质量因子在行业与市值中性化后是否仍有稳定的截面预测能力。",
    results=["样本外 Rank IC：0.031", "成本后多空组合 Sharpe：1.24", "20% ADV 容量约束下结果稳定"],
    stack=["Python", "pandas", "pytest", "GitHub Actions"],
    structure={
        "configs/": "实验参数",
        "src/data/": "Point-in-Time 数据接口",
        "src/research/": "因子与组合逻辑",
        "tests/": "单元与防泄漏测试",
        "reports/": "冻结结果与图表",
    },
)

readme = render_readme(project)
print(readme)

# 本地 Python 可取消下一行注释；浏览器沙箱中默认只预览，不写文件。
# Path("README.generated.md").write_text(readme, encoding="utf-8")
