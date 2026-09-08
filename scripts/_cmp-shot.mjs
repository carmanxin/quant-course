// 对比截图：线上预览版 vs 离线单文件版
import { chromium } from 'playwright'

const PAGE = 'guide/m01-overview/1.7-learning-roadmap'
const ONLINE = `http://127.0.0.1:4179/${PAGE}.html`
const OFFLINE = `file:///D:/AI/study/quant/QuantLab-离线单文件.html#${PAGE}`

const browser = await chromium.launch()

for (const [name, url, extraWait] of [
  ['online', ONLINE, 1500],
  ['offline', OFFLINE, 2500],
]) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } })
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 })
    await page.waitForTimeout(extraWait)
    await page.screenshot({ path: `/tmp/cmp-${name}.png`, fullPage: false })
    console.log(`[OK] ${name} -> /tmp/cmp-${name}.png`)
  } catch (e) {
    console.log(`[ERR] ${name}: ${e.message}`)
  }
  await page.close()
}

await browser.close()
