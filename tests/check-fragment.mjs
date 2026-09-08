import { readFileSync } from 'node:fs'
const text = readFileSync('public/code/_auto/2ab5dad7.py', 'utf8')
const codeBody = text.replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
console.log('---')
console.log(codeBody)
console.log('---')
const isPureDefinition = /^\s*(def |class |@|\s+# )/.test(codeBody) && !/^\s*(import |from )/m.test(codeBody)
const hasDefOrClass = /^\s*(def |class )/m.test(codeBody)
const needsScaffold = /\b(df|prices|signal|stock1|stock2)\b/.test(codeBody) && !/^\s*(df|prices|signal|stock1|stock2)\s*=/m.test(codeBody)
const isFragment = isPureDefinition || (hasDefOrClass && false) || needsScaffold
console.log('isFragment:', isFragment)
console.log('needsScaffold:', needsScaffold)