# -*- coding: utf-8 -*-
"""导出所有小测验题目（m11 + m20 等）到纯文本，便于逐题编写答案与解析。"""
import io, os, re, json, glob

files = sorted(glob.glob('guide/m11-derivatives/*.md')) + sorted(
    glob.glob('guide/m20-interview-prep/20.[678]*.md')) + sorted(
    glob.glob('guide/m01-overview/1.[567]*.md')) + ['guide/m04-backtest/4.4-pitfalls.md']

out = io.open('scripts/_quiz_dump.txt', 'w', encoding='utf-8')

for f in files:
    txt = io.open(f, encoding='utf-8').read()
    # 只取 小测验 之后的段落
    m = re.search(r'^##\s*(?:📝\s*)?小测验.*$', txt, re.M)
    start = m.start() if m else 0
    seg = txt[start:]
    blocks = re.split(r'\n(?=\*\*题目\s*\d+\*\*|\*\*题目\s*\d+：|###\s*📝\s*测验)', seg)
    has = [b for b in blocks if 'quiz-option' in b]
    if not has:
        continue
    out.write('\n' + '=' * 78 + '\n### FILE: %s\n' % f + '=' * 78 + '\n')
    for b in has:
        out.write(b.strip() + '\n\n')

out.close()
print('written scripts/_quiz_dump.txt')
print(io.open('scripts/_quiz_dump.txt', encoding='utf-8').read()[:1500])
