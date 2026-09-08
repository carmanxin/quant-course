// Test precompute on specific files

// Quick test: run on a specific .py file by calling spawn manually with the augmented code
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';

async function testOne(pyFilePath) {
  const name = path.basename(pyFilePath, '.py');
  const text = await readFile(pyFilePath, 'utf8');
  const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '').trim();
  console.log('---', pyFilePath, '---');
  console.log('Hash:', name);

  // Replicate the augmented text generation (simplified)
  // Just run the raw file with preamble
  const preamble = `
import os, matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
np.random.seed(42)
df = pd.DataFrame({"Close": 100 + np.cumsum(np.random.randn(252)*0.02)})
prices_df = pd.DataFrame(100 + np.cumsum(np.random.randn(252,5)*0.02, axis=0), columns=['S0','S1','S2','S3','S4'])
stock1 = 100 + np.cumsum(np.random.randn(252)*0.02)
stock2 = 100 + np.cumsum(np.random.randn(252)*0.02)
prices = stock1
signal = np.random.choice([0, 1], size=252)
`;

  const augmentedText = preamble + '\n' + codeBody + `
# === Post-scaffold calls ===
print('--- 案例调用结果 ---')
for _n in dir():
    _v = locals().get(_n)
    if callable(_v) and not _n.startswith('_') and _n not in ['plt','np','pd','os','matplotlib','warnings','open','print','range','len','enumerate']:
        try:
            if 'prices_df' in str(_v.__code__.co_varnames[:_v.__code__.co_argcount]):
                _r = _v(prices_df)
                print(f'{_n}(prices_df):', repr(_r)[:200])
            elif 'stock1' in str(_v.__code__.co_varnames[:_v.__code__.co_argcount]):
                _r = _v(stock1, stock2)
                print(f'{_n}(stock1,stock2):', repr(_r)[:200])
            elif 'df' in str(_v.__code__.co_varnames[:_v.__code__.co_argcount]):
                _r = _v(df)
                print(f'{_n}(df):', repr(_r)[:200])
            elif _v.__code__.co_argcount == 0:
                _r = _v()
                print(f'{_n}():', repr(_r)[:200])
        except Exception as _e:
            print(f'{_n}: 调用失败 {_e}')
`;

  const proc = spawn('python3', ['-c', augmentedText], {
    env: { ...process.env, QUANTLAB_OUTPUT_NAME: name, QUANTLAB_SVG_DIR: '/tmp/test-svgs' }
  });
  let stdout = '', stderr = '';
  proc.stdout.on('data', d => stdout += d);
  proc.stderr.on('data', d => stderr += d);
  proc.on('close', code => {
    console.log('exit:', code);
    console.log('STDOUT:', stdout.slice(0, 500));
    if (stderr) console.log('STDERR:', stderr.slice(0, 200));
  });
}

await testOne('public/code/_auto/884d1420.py');
console.log('=====');
await testOne('public/code/_auto/93ba1436.py');