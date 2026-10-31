# @quantlab/output: 64b14796
from dataclasses import dataclass


@dataclass
class Project:
    name: str
    thesis: str
    results: list[str]
    stack: list[str]


FENCE = "`" * 3  # 避免在 Markdown 代码块里嵌套三反引号


def render_readme(project: Project) -> str:
    results = "\n".join(f"- {item}" for item in project.results)
    stack = " · ".join(f"`{item}`" for item in project.stack)
    return f"""# {project.name}

## Research Thesis
{project.thesis}

## Key Results
{results}

## Reproduce
{FENCE}bash
python -m pytest -q
python -m src.run_experiment --config configs/baseline.yaml
{FENCE}

## Tech Stack
{stack}
"""


project = Project(
    name="A-Share Factor Research",
    thesis="检验质量因子中性化后是否仍有截面预测能力。",
    results=["样本外 Rank IC：0.031", "成本后 Sharpe：1.24"],
    stack=["Python", "pandas", "pytest"],
)
print(render_readme(project))
