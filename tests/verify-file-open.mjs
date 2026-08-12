// tests/verify-file-open.mjs
// 验证便携包可被 file:// 直接打开：排版(CSS 加载)、导航、折叠块、SVG 图
import { chromium } from 'playwright'
import path from 'node:path'

const DIST = path.resolve('.vitepress/dist')

function fileUrl(rel) {
  return `file:///${path.join(DIST, rel)}`
}

const browser = await chromium.launch()
const page = await browser.newPage()
page.on('pageerror', e => console.log('  PAGEERR:', e.message))
page.on('requestfailed', r => {
  if (r.url().startsWith('file://')) console.log('  REQFAIL:', r.url().slice(7))
})
page.on('console', m => {
  if (m.type() === 'error') console.log('  CONSOLE-ERR:', m.text().slice(0, 120))
})

// 1. 首页排版：CSS 是否加载成功
await page.goto(fileUrl('index.html'), { waitUntil: 'load' })
await page.waitForTimeout(1500)
const bodyBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
const hasHero = await page.locator('.VPHome, .ft-hero, .vp-doc').count()
console.log('1) 首页: body bg =', bodyBg, '| 页面区块 =', hasHero)

// 2. 点击「开始学习」导航
await page.locator('a:has-text("开始学习")').first().click()
await page.waitForTimeout(1500)
const guideUrl = page.url()
const guideTitle = await page.title()
console.log('2) 点击开始学习 →', guideUrl.replace('file:///', ''), '| title =', guideTitle.slice(0, 40))
if (!guideUrl.includes('guide') && !guideUrl.includes('index')) {
  throw new Error('导航失败: url=' + guideUrl)
}

// 3. 折叠块：进入 1.3 页面验证输出内联
await page.goto(fileUrl('guide/m01-overview/1.3-quant-mindset.html'), { waitUntil: 'load' })
await page.waitForTimeout(1500)
const det = page.locator('details.scb-out')
const n = await det.count()
await det.evaluateAll(els => els.forEach(el => (el.open = true)))
await page.waitForTimeout(300)
const hasText = await page.locator('.scb-out-text').count()
const firstText = await page.locator('.scb-out-text').first().textContent().catch(() => '')
console.log(`3) 1.3 折叠块: ${n} 个, 含输出文本块 ${hasText} 个, 首块="${firstText.trim().slice(0, 30)}"`)

// 4. SVG 加载（1.5 页面）
await page.goto(fileUrl('guide/m01-overview/1.5-industry-2026.html'), { waitUntil: 'load' })
await page.waitForTimeout(1500)
const svgs = page.locator('.scb-out-svgs img, details.scb-out img')
await page.locator('details.scb-out summary').first().click()
await page.waitForTimeout(500)
const svgResults = await svgs.evaluateAll(imgs => imgs.map(img => ({
  src: img.getAttribute('src') || '',
  w: img.naturalWidth,
})))
console.log('4) 1.5 SVG 加载:', JSON.stringify(svgResults.slice(0, 3)))

await browser.close()
