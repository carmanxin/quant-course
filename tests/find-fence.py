#!/usr/bin/env python3
"""查某个 hash 对应的 md 源文件"""
import sys, os, re

def fnv1a(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return '%08x' % h

target = sys.argv[1]
for path in ['guide/']:
    for root, dirs, files in os.walk(path):
        for f in files:
            if not f.endswith('.md'): continue
            full = os.path.join(root, f)
            content = open(full, encoding='utf-8').read()
            lines = content.split('\n')
            in_fence = False
            lang = ''
            buf = []
            for line in lines:
                if not in_fence and line.startswith('```'):
                    in_fence = True
                    lang = line[3:].strip().split()[0] if len(line) > 3 else ''
                    buf = []
                elif in_fence and line.strip() == '```':
                    in_fence = False
                    if lang in ('python', 'py'):
                        raw = '\n'.join(buf)
                        norm = re.sub(r'^#\s*@quantlab/output:\s*[\w.\-]+\s*\n?', '', raw).replace('\r\n', '\n')
                        norm = re.sub(r'[ \t]+$', '', norm, flags=re.M).strip()
                        if fnv1a(norm) == target:
                            print(f'Found in: {full}')
                elif in_fence:
                    buf.append(line)