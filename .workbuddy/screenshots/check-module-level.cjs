// Find fragments that have module-level calls but ended up as note/fragment
const fs = require('fs');
const path = require('path');

const dir = 'public/code';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.output.json'));

function hasModuleLevelCall(codeBody) {
  const hasDefOrClass = /^\s*(def |class )/m.test(codeBody);
  if (!hasDefOrClass) return false;
  for (const line of codeBody.split(/\r?\n/)) {
    if (!/^[^ \t]/.test(line)) continue;
    if (/^(def |class |#|from |import |@|if __name__)/.test(line)) continue;
    if (/^[A-Za-z_][A-Za-z0-9_]*\s*[(\s=,]/.test(line)) return true;
  }
  return false;
}

let degraded = 0;
const samples = [];
for (const f of files) {
  const name = f.replace('.output.json', '');
  const pyPath = path.join('public/code/_auto', name + '.py');
  if (!fs.existsSync(pyPath)) continue;
  const code = fs.readFileSync(pyPath, 'utf8').replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  if (!hasModuleLevelCall(code)) continue;
  const out = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  if (out.note) {
    degraded++;
    if (samples.length < 15) {
      const moduleLevelLines = code.split(/\r?\n/).filter(l => !/^[ \t]/.test(l) && !/^(def |class |#|from |import |@|"""|\'\'\')/.test(l)).slice(0, 4);
      samples.push({ name, note: out.note.slice(0, 40), lines: moduleLevelLines.slice(0, 3) });
    }
  }
}
console.log('Fragments WITH module-level calls but ended as note:', degraded);
samples.forEach(s => {
  console.log('---', s.name, '| note:', s.note);
  s.lines.forEach(l => console.log('    ', l));
});