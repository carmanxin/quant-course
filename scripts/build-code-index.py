#!/usr/bin/env python3
"""扫描当前 guide/**/*.md，构建 hash → output-name 映射，写入 public/code/_index.json。

策略：
  1. 直接读当前 guide/**/*.md，不依赖 git 历史。
  2. 对每个 python fence 算 FNV-1a hash。
  3. 默认映射 hash → hash（extract-py-fences.mjs 会以 hash 命名每个 .py）。
  4. 若公共/code/<X>.output.json 存在且 X 不是 8 位 hex，则保留 hash → X（兼容
     25 个手工命名的预计算文件）。
  5. 若旧的 _index.json 已有非 hash 名称且对应的 .output.json 仍存在，也保留。

用法：
  python scripts/build-code-index.py [--out public/code/_index.json]
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FENCE_RE = re.compile(r"```(python|py)\n(.*?)```", re.DOTALL)
HEX8 = re.compile(r"^[0-9a-f]{8}$")


def fnv1a(s: str) -> str:
    """FNV-1a 32-bit，与组件端一致。"""
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return "%08x" % h


def normalize(raw: str) -> str:
    t = re.sub(r"^#\s*@quantlab/output:\s*[\w.\-]+\s*\n?", "", raw)
    t = t.replace("\r\n", "\n")
    t = re.sub(r"[ \t]+$", "", t, flags=re.M)
    return t.strip()


def extract_fences(text: str):
    """逐行解析 fence（不依赖正则 .NET 跨行，更稳）。"""
    fences = []
    lines = text.split("\n")
    in_fence = False
    lang = ""
    buf = []
    for line in lines:
        if not in_fence and line.startswith("```"):
            in_fence = True
            lang = line[3:].strip().split()[0] if len(line) > 3 else ""
            buf = []
        elif in_fence and line.strip() == "```":
            in_fence = False
            if lang in ("python", "py"):
                fences.append("\n".join(buf))
        elif in_fence:
            buf.append(line)
    return fences


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "public" / "code" / "_index.json"))
    p.add_argument("--guide", default=str(ROOT / "guide"))
    args = p.parse_args()

    guide_dir = pathlib.Path(args.guide)
    if not guide_dir.is_dir():
        print(f"ERROR: {guide_dir} not found", file=sys.stderr)
        return 1

    code_dir = ROOT / "public" / "code"
    available = set()
    for f in code_dir.iterdir():
        if f.name.endswith(".output.json"):
            available.add(f.name[: -len(".output.json")])

    # 旧索引（如果有）：先读本地，再读 git 历史（兜底，避免覆盖丢失 human-named）
    old_index: dict[str, str] = {}
    old_path = pathlib.Path(args.out)
    if old_path.exists():
        try:
            old_index.update(json.loads(old_path.read_text(encoding="utf-8")))
        except Exception:
            pass
    try:
        proc = subprocess.run(
            ["git", "show", "b120b57:public/code/_index.json"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        if proc.returncode == 0:
            old_index.update(json.loads(proc.stdout))
            print(f"[build-code-index] loaded {len(old_index)} entries from git b120b57 fallback")
    except Exception as e:
        print(f"[build-code-index] git fallback failed: {e}", file=sys.stderr)

    new_index: dict[str, str] = {}
    n_fences = 0

    for md in sorted(guide_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for fence in extract_fences(text):
            n_fences += 1
            key = fnv1a(normalize(fence))
            # 优先保留旧索引里映射到非 hash 且 .output.json 存在的条目
            old_name = old_index.get(key)
            if old_name and old_name in available and not HEX8.match(old_name):
                new_index[key] = old_name
            else:
                new_index[key] = hash_name = key
                # sanity check: hash 名文件应该存在
                if hash_name not in available:
                    # hash 索引将在 build 时不存在 → 不影响（component 显示暂无）
                    pass

    old_path.write_text(
        json.dumps(new_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    n_human = sum(1 for v in new_index.values() if not HEX8.match(v))
    n_auto = sum(1 for v in new_index.values() if HEX8.match(v))
    print(
        f"[build-code-index] fences={n_fences} index={len(new_index)} "
        f"(human-named={n_human}, hash-named={n_auto})"
    )
    print(f"[build-code-index] wrote {old_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())