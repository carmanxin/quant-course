// Run the augmented text and see what python outputs
import { spawn } from 'node:child_process'

const augmentedText = `

import os, matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
_SHOW_COUNT = [0]
def _patched_show(*a, **k):
    n = _SHOW_COUNT[0]
    _SHOW_COUNT[0] += 1
    fname = f"{os.environ['QUANTLAB_OUTPUT_NAME']}-{n}.svg"
    plt.savefig(os.path.join(os.environ['QUANTLAB_SVG_DIR'], fname), bbox_inches="tight")
    plt.close()
plt.show = _patched_show

# === Auto-injected scaffold ===
import numpy as np, pandas as pd
np.random.seed(42)
df = pd.DataFrame({
    "Open":   100 + np.cumsum(np.random.randn(252)*0.02),
    "High":   100 + np.cumsum(np.random.randn(252)*0.02) + np.abs(np.random.randn(252)*0.5),
    "Low":    100 + np.cumsum(np.random.randn(252)*0.02) - np.abs(np.random.randn(252)*0.5),
    "Close":  100 + np.cumsum(np.random.randn(252)*0.02),
    "Volume": np.random.randint(1_000_000, 10_000_000, 252),
    "signal": np.random.choice([0, 1], size=252),
})
df.index = pd.date_range("2024-01-01", periods=252)
try:
    import pandas as pd
    import numpy as np

    # 假设df包含：Close（收盘价）、signal（0/1信号，1表示持有）
    returns = df['Close'].pct_change()
    strategy_returns = returns * df['signal'].shift(1)
    cumulative = (1 + strategy_returns).cumprod()

    # === Scaffold summary ===
    print("--- 结果 ---")
    for _v in ['returns','strategy_returns','cumulative']:
        try:
            _x = eval(_v)
            if hasattr(_x, "tail"): print(_v + " tail():", _x.tail().to_string())
            elif hasattr(_x, "head"): print(_v + " head():", _x.head().to_string())
            elif hasattr(_x, "__len__") and len(_x) < 20: print(_v + " =", repr(_x))
            else: print(_v + " =", repr(_x)[:200])
        except Exception: pass
except Exception as _e:
    print(f"⚠ 末尾操作失败: {_e}")
`

const proc = spawn('python3', ['-c', augmentedText], {
  env: {
    ...process.env,
    MPLBACKEND: 'svg',
    QT_QPA_PLATFORM: 'offscreen',
    PYTHONUNBUFFERED: '1',
    QUANTLAB_SVG_DIR: '/tmp/svg-test',
    QUANTLAB_OUTPUT_NAME: '2ab5dad7',
  }
})
let stdout = '', stderr = ''
proc.stdout.on('data', d => stdout += d)
proc.stderr.on('data', d => stderr += d)
proc.on('close', code => {
  console.log('exit:', code)
  console.log('stdout:')
  console.log(stdout)
  console.log('stderr:', stderr.slice(0, 300))
})