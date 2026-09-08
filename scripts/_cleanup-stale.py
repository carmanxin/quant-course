#!/usr/bin/env python3
# 清理陈旧产物：public/code 下不在当前 _index.json 中的 *.output.json / *.py / *.svgs
# （改源码会改变 fence hash，旧产物被遗留，页面不会引用，但会打进 dist 增体积）
import json, os, glob, sys

idx = json.load(open('public/code/_index.json', encoding='utf-8'))
names = set(idx.values())
print('index entries:', len(names))

stale = []
for f in glob.glob('public/code/*.output.json'):
    n = os.path.basename(f)[:-len('.output.json')]
    if n not in names:
        stale.append(f)
for f in glob.glob('public/code/*.py'):
    n = os.path.basename(f)[:-3]
    # 保留 _auto/ 下的提取产物由 extract 管理；根目录 .py 多为人工脚本，不动
    if n in names:
        continue
import shutil
for d in glob.glob('public/code/*.svgs'):
    n = os.path.basename(d)[:-len('.svgs')]
    if n not in names:
        stale.append(d)

print('stale output.json / svgs dirs:', len(stale))
if '--apply' not in sys.argv:
    print('dry-run (pass --apply to delete)')
    for s in stale[:15]:
        print('  would remove', s)
    if len(stale) > 15:
        print(f'  ... and {len(stale)-15} more')
else:
    ok = 0
    for s in stale:
        try:
            if os.path.isdir(s):
                shutil.rmtree(s)
            else:
                os.remove(s)
            ok += 1
        except Exception as e:
            print('  FAILED', s, e)
    print('removed', ok)
