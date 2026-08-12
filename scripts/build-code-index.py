#!/usr/bin/env python3
"""从 git 历史恢复 <PythonPlayground src=...> 与 python fence 的关联，生成 _index.json。

背景：
  Task 2 已删除 guide/*.md 中的 <PythonPlayground src="/code/X.py" /> 标签，
  但该标签正是 fence 与运行输出（.output.json）之间的唯一可靠关联。
  标签在 commit 9f8944f（删除前）仍存在，本脚本读取该版本，
  把每个 fence 内容归一化后的 FNV-1a hash 映射到输出名，写入：
    public/code/_index.json   { "<hash>": "<outputName>", ... }

组件端（StaticCodeBlock.vue）对其展示的代码算同样的 hash，查此文件定位输出。

用法：
  python scripts/build-code-index.py [--git-ref 9f8944f] [--out public/code/_index.json]
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FENCE_RE = re.compile(r'```(python|py)\n(.*?)```', re.DOTALL)
TAG_RE = re.compile(r'<PythonPlayground\s+src="/code/([\w.\-]+)\.py"[^>]*/?>')


def fnv1a(s: str) -> str:
    """FNV-1a 32-bit，与组件端一致。"""
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return "%08x" % h


def normalize(raw: str) -> str:
    """与组件端 normalizeCode 一致。"""
    t = re.sub(r'^#\s*@quantlab/output:\s*[\w.\-]+\s*\n?', '', raw)
    t = t.replace("\r\n", "\n")
    t = re.sub(r"[ \t]+$", "", t, flags=re.M)
    return t.strip()


def git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git show {ref}:{path} failed: {proc.stderr[:200]}")
    return proc.stdout


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--git-ref", default="9f8944f",
                   help="含 <PythonPlayground> 标签的 git commit（默认删除前）")
    p.add_argument("--out", default=str(ROOT / "public" / "code" / "_index.json"))
    args = p.parse_args()

    guide_dir = ROOT / "guide"
    if not guide_dir.is_dir():
        print(f"ERROR: {guide_dir} not found", file=sys.stderr)
        return 1

    index: dict[str, str] = {}
    n_fences = 0
    n_associated = 0
    missing_src: list[str] = []

    for md in sorted(guide_dir.rglob("*.md")):
        rel = md.relative_to(ROOT).as_posix()
        try:
            text = git_show(args.git_ref, rel)
        except RuntimeError as e:
            print(f"  skip {rel}: {e}", file=sys.stderr)
            continue

        fence_positions = list(FENCE_RE.finditer(text))
        for i, fm in enumerate(fence_positions):
            n_fences += 1
            fence = fm.group(2)
            # 在当前 fence 之后、下一个 fence 之前找 PythonPlayground 标签
            end = fm.end()
            next_start = fence_positions[i + 1].start() if i + 1 < len(fence_positions) else len(text)
            window = text[end:next_start]
            tag_m = TAG_RE.search(window)
            if not tag_m:
                missing_src.append(rel)
                continue
            name = tag_m.group(1)
            key = fnv1a(normalize(fence))
            index[key] = name
            n_associated += 1

    out = pathlib.Path(args.out)
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[build-code-index] fences={n_fences} associated={n_associated} missing_src={len(missing_src)}")
    print(f"[build-code-index] wrote {out} ({len(index)} entries)")
    if missing_src:
        print("[build-code-index] fences without src (samples):", missing_src[:10], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
