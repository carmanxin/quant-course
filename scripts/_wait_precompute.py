#!/usr/bin/env python3
# 监控预计算进程，直到其结束（python3 工作进程数回落到基线且 3 分钟内无新输出文件）
import os, time, glob, subprocess, sys

def python_workers():
    try:
        out = subprocess.run(['tasklist'], capture_output=True, text=True).stdout
        return out.lower().count('python3.exe')
    except Exception:
        return -1

def recent_writes(mins=3):
    now = time.time()
    return len([f for f in glob.glob('public/code/*.output.json') if now - os.path.getmtime(f) < mins*60])

start = time.time()
last_write_check = time.time()
stable_since = None
# 基线：当前未运行预计算时的 python3 数（含不可杀孤儿）。先采样
baseline = python_workers()
print(f"[monitor] baseline python3 workers = {baseline}", flush=True)

while True:
    workers = python_workers()
    rw = recent_writes(3)
    elapsed = time.time() - start
    # 判定结束：_worker 数显著下降（预计算 node 退出，worker 被回收/变孤儿）
    # 且 3 分钟内无新写入
    if rw == 0 and elapsed > 60:
        # 无新写入，且已运行至少 60s；检查 worker 是否回落
        # 预计算运行时 worker 应 >= baseline - 孤儿 + workers。用更宽松判据：连续 3 次无写入
        if stable_since is None:
            stable_since = time.time()
        elif time.time() - stable_since > 120:
            print(f"[monitor] DONE after {elapsed/60:.1f} min (no writes for >2min, workers={workers})", flush=True)
            break
    else:
        stable_since = None
    if elapsed > 180*60:
        print("[monitor] TIMEOUT 180min, aborting wait", flush=True)
        break
    time.sleep(20)
