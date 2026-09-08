import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'

// 找所有 portable/dist/guide/**/*.html
const distDir = 'portable/dist'
const files = execSync(`find ${distDir}/guide -name "*.html"`, { encoding: 'utf8' }).trim().split('\n')

console.log(`checking ${files.length} html files...`)

let totalScb = 0, totalWithOutput = 0, totalEmpty = 0, filesWithAllEmpty = []

for (const file of files) {
  const html = fs.readFileSync(file, 'utf8')
  const re = /<div class="scb-out-body"[^>]*>([\s\S]*?)<\/div><\/details>/g
  let m
  const scbCount = (html.match(/<div class="scb" /g) || []).length
  totalScb += scbCount
  let fileHasEmpty = 0, fileHasOutput = 0
  while ((m = re.exec(html)) !== null) {
    const body = m[1]
    if (body.includes('scb-out-text') || body.includes('scb-out-svgs')) {
      fileHasOutput++
      totalWithOutput++
    } else if (body.includes('scb-out-empty')) {
      fileHasEmpty++
      totalEmpty++
    }
  }
  if (fileHasEmpty > 0) {
    filesWithAllEmpty.push({ file, scb: scbCount, empty: fileHasEmpty, out: fileHasOutput })
  }
}

console.log(`\nSummary:`)
console.log(`  total scb blocks: ${totalScb}`)
console.log(`  with output: ${totalWithOutput}`)
console.log(`  empty: ${totalEmpty}`)
console.log(`  files with any empty: ${filesWithAllEmpty.length}`)

if (filesWithAllEmpty.length > 0) {
  console.log(`\nFiles with empty (first 20):`)
  filesWithAllEmpty.slice(0, 20).forEach(({ file, scb, empty, out }) => {
    console.log(`  ${file.replace(distDir + '/', '')}: scb=${scb} out=${out} empty=${empty}`)
  })
}