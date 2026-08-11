// 截取首页与按钮区对比图
import { chromium } from 'playwright'

const BASE = 'http://localhost:4173'
const OUT_DIR = 'D:/AI/study/quant/_screenshots'

;(async () => {
  const fs = await import('fs/promises')
  await fs.mkdir(OUT_DIR, { recursive: true })

  const browser = await chromium.launch()
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  })
  const page = await ctx.newPage()

  // 浅色首页
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: `${OUT_DIR}/01-home-light-top.png`, fullPage: false })
  await page.screenshot({ path: `${OUT_DIR}/01-home-light-full.png`, fullPage: true })
  console.log('✓ Light home captured')

  // 滑到按钮区
  await page.evaluate(() => window.scrollTo(0, 900))
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${OUT_DIR}/02-buttons-light.png`, fullPage: false })
  console.log('✓ Light buttons captured')

  // 滑到表格
  await page.evaluate(() => window.scrollTo(0, 500))
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${OUT_DIR}/03-table-light.png`, fullPage: false })

  // 切换暗色
  await page.evaluate(() => {
    document.documentElement.classList.add('dark')
    localStorage.setItem('vitepress-theme-appearance', 'dark')
  })
  await page.waitForTimeout(1500)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${OUT_DIR}/04-home-dark-top.png`, fullPage: false })
  await page.screenshot({ path: `${OUT_DIR}/04-home-dark-full.png`, fullPage: true })
  console.log('✓ Dark home captured')

  await page.evaluate(() => window.scrollTo(0, 900))
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${OUT_DIR}/05-buttons-dark.png`, fullPage: false })
  console.log('✓ Dark buttons captured')

  // hover 按钮看动效
  await page.evaluate(() => window.scrollTo(0, 950))
  await page.waitForTimeout(800)
  // hover 第一个按钮
  const buttons = await page.locator('.ft-btn-anim').all()
  if (buttons.length > 0) {
    await buttons[0].hover()
    await page.waitForTimeout(500)
    await page.screenshot({ path: `${OUT_DIR}/06-button-hover-1.png`, fullPage: false })
    console.log('✓ Button hover captured')
  }

  // 关闭
  await browser.close()
  console.log('Done!')
})().catch(e => { console.error(e); process.exit(1) })
