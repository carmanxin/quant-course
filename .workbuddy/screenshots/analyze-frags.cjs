// 分析所有 fragment-note 片段：判断是否有可运行入口
const fs = require('fs');
const path = require('path');

const list = JSON.parse(fs.readFileSync('.workbuddy/frag-list.json', 'utf8'));
const results = { moduleLevelCalls: [], hasModulePrint: [], pureDefs: [], hasPltShow: [], classOnly: [], other: [] };

function analyze(code) {
  const lines = code.split(/\r?\n/);
  let hasModuleLevel = false; // 模块级有非 def/class/import 的语句
  let hasModuleCall = false;  // 模块级函数调用 xxx(...)
  let hasModulePrint = false; // 模块级 print
  let hasPltShow = false;     // plt.show()
  let hasAssignment = false;  // 模块级赋值
  let onlyDefs = true;        // 只有 def/class/import/注释/空行
  let moduleLevelLines = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === '') continue;
    if (/^(def |class |#|@|from |import )/.test(trimmed)) continue;
    if (/^"""|^'''/.test(trimmed)) continue;
    // 有缩进的代码行（函数体内）跳过模块级判断
    if (/^[ \t]/.test(line)) continue;
    onlyDefs = false;
    moduleLevelLines.push(trimmed);
    if (/^print\(/.test(trimmed)) hasModulePrint = true;
    if (/^\w+[\w.]*\s*\(/.test(trimmed)) hasModuleCall = true;
    if (/plt\.show/.test(trimmed)) hasPltShow = true;
    if (/^[A-Za-z_]\w*\s*=/.test(trimmed)) hasAssignment = true;
    hasModuleLevel = true;
  }
  return { onlyDefs, hasModuleLevel, hasModuleCall, hasModulePrint, hasPltShow, hasAssignment, moduleLevelLines };
}

for (const name of list) {
  const pyPath = path.join('public/code/_auto', name + '.py');
  if (!fs.existsSync(pyPath)) { results.other.push({ name, why: 'no py file' }); continue; }
  const code = fs.readFileSync(pyPath, 'utf8').replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  const a = analyze(code);
  const rec = { name, lines: a.moduleLevelLines.slice(0, 6), defCount: (code.match(/^def\s/g) || []).length, classCount: (code.match(/^class\s/g) || []).length };
  if (a.onlyDefs) results.pureDefs.push(rec);
  else if (a.hasModulePrint) results.hasModulePrint.push(rec);
  else if (a.hasModuleCall) results.moduleLevelCalls.push(rec);
  else if (a.hasPltShow) results.hasPltShow.push(rec);
  else if (a.hasAssignment) results.hasAssignment ? results.hasModulePrint.push(rec) : results.other.push(rec);
  else results.other.push(rec);
}

// Fix: hasAssignment isn't a key; put those in moduleLevelCalls bucket conceptually
console.log('=== 纯 def/class（确实无需运行）:', results.pureDefs.length);
console.log('=== 有模块级 print（应该能跑）:', results.hasModulePrint.length);
for (const r of results.hasModulePrint.slice(0, 20)) {
  console.log(`  ${r.name} | defs=${r.defCount} classes=${r.classCount}`);
  r.lines.forEach(l => console.log(`      ${l.slice(0, 90)}`));
}
console.log('=== 有模块级函数调用（应该能跑）:', results.moduleLevelCalls.length);
for (const r of results.moduleLevelCalls.slice(0, 30)) {
  console.log(`  ${r.name} | defs=${r.defCount} classes=${r.classCount}`);
  r.lines.forEach(l => console.log(`      ${l.slice(0, 90)}`));
}
console.log('=== 有 plt.show:', results.hasPltShow.length);
for (const r of results.hasPltShow.slice(0, 10)) {
  console.log(`  ${r.name} | defs=${r.defCount}`);
  r.lines.forEach(l => console.log(`      ${l.slice(0, 90)}`));
}
console.log('=== other:', results.other.length);
for (const r of results.other.slice(0, 10)) {
  console.log(`  ${r.name} | defs=${r.defCount} classes=${r.classCount}`);
  r.lines.forEach(l => console.log(`      ${l.slice(0, 90)}`));
}