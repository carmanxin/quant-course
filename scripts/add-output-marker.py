#!/usr/bin/env python3
"""为 public/code/*.py 加 # @quantlab/output: <name> 首行注释（幂等）。"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / 'public' / 'code'
MARKER_RE = re.compile(r'^#\s*@quantlab/output:\s*([\w.\-]+)', re.MULTILINE)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--code-dir', default=str(CODE_DIR))
    args = p.parse_args()
    code_dir = pathlib.Path(args.code_dir)
    if not code_dir.is_dir():
        print(f'ERROR: {code_dir} not found', file=sys.stderr)
        return 1
    modified, skipped = 0, 0
    for f in sorted(code_dir.glob('*.py')):
        text = f.read_text(encoding='utf-8')
        if MARKER_RE.search(text):
            skipped += 1
            continue
        new_text = f'# @quantlab/output: {f.stem}\n' + text
        if args.dry_run:
            print(f'would modify: {f.name}')
        else:
            f.write_text(new_text, encoding='utf-8')
        modified += 1
    print(f'[add-output-marker] modified={modified} skipped={skipped}')
    return 0


if __name__ == '__main__':
    sys.exit(main())