import fs from 'node:fs'
import path from 'node:path'

const files = fs.readdirSync('public/code').filter(f => f.endsWith('.output.json'))
const buckets = {
  success: [],
  fragment: [],   // function def without main
  importMissing: [],
  otherError: [],
}

for (const f of files) {
  const o = JSON.parse(fs.readFileSync(path.join('public/code', f), 'utf8'))
  if (o.error === undefined) {
    buckets.success.push(f)
  } else {
    const e = o.error
    if (/NameError.*not defined/.test(e)) buckets.importMissing.push(f)
    else if (/^def\s/.test(o.text || '')) buckets.fragment.push(f)
    else buckets.otherError.push(f)
  }
}
console.log('success:', buckets.success.length)
console.log('import-missing:', buckets.importMissing.length)
console.log('fragment:', buckets.fragment.length)
console.log('other-error:', buckets.otherError.length)
console.log('\nsample errors (first 5):')
buckets.importMissing.slice(0, 5).forEach(f => {
  const o = JSON.parse(fs.readFileSync(path.join('public/code', f), 'utf8'))
  console.log(`  ${f}: ${o.error.slice(0, 100)}`)
})