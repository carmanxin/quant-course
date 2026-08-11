#!/usr/bin/env python3
"""从 guide/**/*.md 删除 <PythonPlayground ... /> 单行标签（幂等）。"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r'<PythonPlayground[^>]*/>\s*\n?', re.MULTILINE)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--guide-dir', default=str(ROOT / 'guide'))
    args = p.parse_args()
    guide_dir = pathlib.Path(args.guide_dir)
    modified = 0
    for f in sorted(guide_dir.rglob('*.md')):
        text = f.read_text(encoding='utf-8')
        new_text = TAG_RE.sub('', text)
        if new_text == text:
            continue
        if args.dry_run:
            print(f'would strip: {f.relative_to(guide_dir)}')
        else:
            f.write_text(new_text, encoding='utf-8')
        modified += 1
    print(f'[strip-python-playground-tag] modified={modified}')
    return 0


if __name__ == '__main__':
    sys.exit(main())