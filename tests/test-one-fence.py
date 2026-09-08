import subprocess, os, sys, re, pathlib

test_file = sys.argv[1] if len(sys.argv) > 1 else 'public/code/_auto/00325c46.py'
with open(test_file) as f:
    text = f.read()

# Simulate precompute preamble (no QUANTLAB_ env vars here, so plt.savefig will fail)
preamble = '''
import os, matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
'''

future = re.search(r'(?:^|\n)(?:from __future__[^\n]*\n)+', text)
final = (text[:future.end()] + preamble + text[future.end():]) if future else (preamble + text)

print('Testing:', test_file, 'len=', len(final))
try:
    r = subprocess.run(['python3', '-c', final], capture_output=True, text=True, timeout=20)
    print('exit:', r.returncode)
    print('stdout:', r.stdout[:300])
    print('stderr:', r.stderr[:300])
except subprocess.TimeoutExpired:
    print('TIMEOUT!')