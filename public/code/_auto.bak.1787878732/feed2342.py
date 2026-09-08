# @quantlab/output: feed2342
from dataclasses import dataclass


@dataclass
class Project:
    name: str
    thesis: str
    results: list[str]
    stack: list[str]


def render_readme(project: Project) -> str:
    results = "\n".join(f"- {item}" for item in project.results)
    stack = " · ".join(f"`{item}`" for item in project.stack)
    return f"""# {project.name}

## Research Thesis
{project.thesis}

## Key Results
{results}

## Reproduce
```bash
python -m pytest -q
python -m src.run_experiment --config configs/baseline.yaml
