"""
从 Pyodide lock.json 读取准确的 wheel 文件名,批量下载到 public/pyodide/
"""
import json
import os
import subprocess
import sys
import urllib.request

LOCK_PATH = "node_modules/pyodide/pyodide-lock.json"
DEST_DIR = "public/pyodide"
CDN = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"

# Python deps we want to ship (recursive)
WANT = ["numpy", "pandas", "scipy", "matplotlib", "micropip"]


def find_deps(name, pkgs, seen=None):
    if seen is None:
        seen = set()
    if name in seen:
        return []
    seen.add(name)
    p = pkgs.get(name)
    if not p:
        return []
    out = [name]
    for d in p.get("depends", []) or []:
        out.extend(find_deps(d, pkgs, seen))
    return out


def main():
    with open(LOCK_PATH) as f:
        lock = json.load(f)
    pkgs = lock["packages"]

    # 收集所有需要的 wheel 文件
    needed = set()
    for n in WANT:
        needed.update(find_deps(n, pkgs))
    # 也保留 stdlib 相关 (sqlite3, ssl 等已被 cpython_module)

    # 文件名 (轮子)
    files = []
    for name in sorted(needed):
        p = pkgs.get(name)
        if not p:
            continue
        fn = p.get("file_name")
        if fn:
            files.append((name, fn, p.get("install_dir"), p.get("package_type")))

    print(f"找到 {len(files)} 个包,开始下载到 {DEST_DIR}/")
    os.makedirs(DEST_DIR, exist_ok=True)

    # 跳过已下载的
    total_size = 0
    success = 0
    failed = []
    for name, fn, install_dir, pkg_type in files:
        dest = os.path.join(DEST_DIR, fn)
        if os.path.exists(dest) and os.path.getsize(dest) > 100:
            sz = os.path.getsize(dest)
            total_size += sz
            success += 1
            # print(f"  SKIP {fn} ({sz} bytes)")
            continue
        url = CDN + fn
        # Use curl since pyodide wheels can be large
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "180", url, "-o", dest],
            capture_output=True,
            text=True,
        )
        if os.path.exists(dest):
            sz = os.path.getsize(dest)
            if sz > 100:
                total_size += sz
                success += 1
                print(f"  ✓ {fn:<60} ({sz//1024} KB) {pkg_type}/{install_dir}")
            else:
                failed.append((name, fn, sz))
                print(f"  ✗ {fn:<60} TOO SMALL ({sz} bytes)")
        else:
            failed.append((name, fn, 0))
            print(f"  ✗ {fn:<60} MISSING")

    print(f"\nDone. {success}/{len(files)} OK, total {total_size//1024//1024} MB downloaded.")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for n, f, sz in failed[:10]:
            print(f"  - {n}: {f} ({sz} bytes)")


if __name__ == "__main__":
    main()
