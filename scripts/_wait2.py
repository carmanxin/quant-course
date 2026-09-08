#!/usr/bin/env python3
# 干净监控：仅依赖 public/code/*.output.json 的修改时间判断预计算是否结束。
import os, time, glob, sys

def recent_writes(mins):
    now = time.time()
    return len([f for f in glob.glob('public/code/*.output.json') if now - os.path.getmtime(f) < mins*60])

start = time.time()
stable_since = None
while True:
    rw3 = recent_writes(3)
    rw10 = recent_writes(10)
    elapsed = time.time() - start
    if rw3 == 0 and elapsed > 120:
        if stable_since is None:
            stable_since = time.time()
        elif time.time() - stable_since > 150:
            print(f"[monitor] DONE after {elapsed/60:.1f} min (no writes in 3min for >2.5min, 10min-window={rw10})", flush=True)
            break
    else:
        stable_since = None
    if elapsed > 200*60:
        print("[monitor] TIMEOUT", flush=True)
        break
    time.sleep(25)
