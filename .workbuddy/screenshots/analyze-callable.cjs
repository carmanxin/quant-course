const fs = require('fs');
const path = require('path');
const list = JSON.parse(fs.readFileSync('.workbuddy/frag-list.json', 'utf8'));
console.log('fragment count:', list.length);
let callable = [], notCallable = 0, moduleLevel = [];
for (const name of list) {
  const pyPath = path.join('public/code/_auto', name + '.py');
  if (!fs.existsSync(pyPath)) continue;
  const code = fs.readFileSync(pyPath, 'utf8').replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  let hasModule = false;
  for (const line of code.split(/\r?\n/)) {
    const t = line.trim();
    if (!t || /^(def |class |#|@|from |import )/.test(t)) continue;
    if (/^[ \t]/.test(line)) continue;
    hasModule = true; break;
  }
  if (hasModule) { moduleLevel.push(name); continue; }
  const defs = [...code.matchAll(/^def\s+(\w+)\s*\(([^)]*)\)/gm)];
  if (defs.length === 0) { notCallable++; continue; }
  let allCallable = true, callableNames = [];
  for (const m of defs) {
    const fn = m[1], params = m[2].trim();
    if (params === '' || params === 'self') { callableNames.push(fn); continue; }
    const parts = params.split(',').map(s => s.trim()).filter(s => s && s !== 'self');
    const ok = parts.every(p => p.includes('=') || /:.+=/.test(p));
    if (ok) callableNames.push(fn); else { allCallable = false; break; }
  }
  if (allCallable) callable.push({ name, fns: callableNames.slice(0, 4) });
  else notCallable++;
}
console.log('有模块级语句但被标 fragment:', moduleLevel.length, moduleLevel.join(','));
console.log('全默认参数可无参调用:', callable.length);
callable.slice(0, 30).forEach(c => console.log('  ', c.name, '->', c.fns.join(', ')));
console.log('不可调用（缺必需参数）:', notCallable);