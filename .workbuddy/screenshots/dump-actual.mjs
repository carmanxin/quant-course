// Dump actual augmented text for 93ba1436
import { readFile } from 'node:fs/promises';

const codeBody = (await readFile('public/code/_auto/93ba1436.py', 'utf8'))
  .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '').trim();

// Mirror buildScaffold exactly
function buildScaffold(codeBody) {
  const declared = new Set();
  for (const line of codeBody.split(/\r?\n/)) {
    let mm;
    if ((mm = line.match(/^\s*def\s+(\w+)/))) declared.add(mm[1]);
    if ((mm = line.match(/^\s*class\s+(\w+)/))) declared.add(mm[1]);
    if ((mm = line.match(/^\s*import\s+(\w+)/))) declared.add(mm[1]);
    if ((mm = line.match(/^\s*from\s+[\w.]+\s+import\s+([\w,\s]+)/))) {
      for (const tok of mm[1].split(',')) {
        const t = tok.trim().split(/\s+as\s+/).pop();
        if (t && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t);
      }
    }
    if ((mm = line.match(/^\s*def\s+\w+\s*\(([^)]*)\)/))) {
      for (const p of mm[1].split(',')) {
        const t = p.trim().replace(/[:\s=].*/, '').replace(/^\*+/, '');
        if (t && t !== 'self' && t !== 'cls' && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t);
      }
    }
  }
  const ignore = new Set([
    'print','len','range','int','float','str','list','dict','set','tuple','bool',
    'True','False','None','self','cls','return','yield','pass','lambda',
    'np','pd','plt','sns','yf','nx','math','os','sys','json','csv','re','time',
    'datetime','timedelta','coint','adfuller','stats','scipy','numpy',
    'pandas','matplotlib','sklearn','torch','warnings',
    'and','or','not','in','is','for','while','if','elif','else','try','except',
    'finally','raise','with','from','import','def','class','return','global',
    'nonlocal','assert','del','break','continue','async','await',
  ]);
  const used = new Set();
  const locallyDefined = new Set();
  for (const line of codeBody.split(/\r?\n/)) {
    if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(line)) continue;
    const eqMatch = line.match(/^([^=]*?)=(?!=)/);
    if (eqMatch) {
      const lhsStripped = eqMatch[1].replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""');
      for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
        const id = m[1];
        if (ignore.has(id)) continue;
        locallyDefined.add(id);
      }
    }
    let rhs = eqMatch ? line.slice(eqMatch[0].length) : line;
    rhs = rhs.replace(/"""[\s\S]*?"""/g, '""').replace(/'''[\s\S]*?'''/g, "''");
    rhs = rhs.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''");
    rhs = rhs.replace(/\b\w+(?=\s*\()/g, '');
    for (const m of rhs.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1];
      if (declared.has(id)) continue;
      if (locallyDefined.has(id)) continue;
      if (ignore.has(id)) continue;
      if (!used.has(id)) used.add(id);
    }
  }
  if (used.size === 0) return null;
  const preLines = [];
  const postLines = [];
  preLines.push('import numpy as np, pandas as pd');
  preLines.push('np.random.seed(42)');
  const usedSorted = [...used].sort();
  for (const name of usedSorted) {
    const lower = name.toLowerCase();
    preLines.push(`${name} = np.random.randn(100)`);
  }
  for (const m of codeBody.matchAll(/^\s*def\s+(\w+)\s*\(([^)]*)\)/gm)) {
    const fname = m[1];
    const params = m[2].trim();
    if (params === '' || params === 'self') {
      postLines.push(`print('--- ${fname}() ---')`);
      postLines.push(`try:\n    print(${fname}())\nexcept Exception as _e:\n    print(f"调用失败: {_e}")`);
    } else {
      postLines.push(`print('--- ${fname}(...) ---')`);
      postLines.push(`try:`);
      const first = [...used][0];
      postLines.push(`    _r = ${fname}(${first})`);
      postLines.push(`    print(type(_r).__name__, repr(_r)[:300])`);
      postLines.push(`except Exception as _e:\n    print(f"调用失败: {_e}")`);
    }
  }
  return { pre: preLines.join('\n'), post: postLines.join('\n'), locallyDefined };
}

const preamble = `
import os, matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')
def _patched_show(*a, **k): pass
plt.show = _patched_show
`;

const sb = buildScaffold(codeBody);
console.log('used:', [...sb.locallyDefined]);

const wrappedUserCode = 'try:\n' + codeBody.split('\n').map(l => '    ' + l).join('\n') + '    # === Scaffold summary ===\n    print("--- 结果 ---")\n    pass\nexcept Exception as _e:\n    print(f"末尾操作失败: {_e}")\n';

const augmented = preamble + (sb.pre ? '\n# pre\n' + sb.pre : '') + '\n# wrapped\n' + wrappedUserCode + (sb.post ? '\n# post\n' + sb.post : '');

// Write to stdout directly (no headers)
process.stdout.write(augmented);