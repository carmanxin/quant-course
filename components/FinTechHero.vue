<template>
  <section class="ft-hero">
    <!-- 背景层 -->
    <div class="ft-hero-bg">
      <div class="ft-hero-glow ft-hero-glow--1"></div>
      <div class="ft-hero-glow ft-hero-glow--2"></div>
      <div class="ft-hero-glow ft-hero-glow--3"></div>
      <svg class="ft-hero-wave" viewBox="0 0 1200 200" preserveAspectRatio="none">
        <path :d="wavePath1" class="ft-wave-1" />
        <path :d="wavePath2" class="ft-wave-2" />
        <path :d="wavePath3" class="ft-wave-3" />
      </svg>
    </div>

    <!-- 内容层 -->
    <div class="ft-hero-content">
      <div class="ft-hero-badge">
        <span class="ft-hero-dot"></span>
        LIVE · 实时数据驱动 · {{ todayStr }}
      </div>

      <h1 class="ft-hero-title">
        量化交易 <span class="ft-hero-accent">系统设计</span> 与实践
      </h1>

      <p class="ft-hero-subtitle">
        从金融数学基础到实盘部署,系统化掌握 <strong>10 大模块 · 50+ 章节</strong>,
        配套 9 个交互式计算器、Python 在线沙箱、可视化回测引擎。
      </p>

      <!-- 实时指标 -->
      <div class="ft-hero-metrics">
        <div class="ft-metric bull">
          <div class="ft-metric-val"><span class="ft-counter">{{ metrics.sharpe }}</span></div>
          <div class="ft-metric-label">Avg Sharpe</div>
        </div>
        <div class="ft-metric bull">
          <div class="ft-metric-val">+<span class="ft-counter">{{ metrics.annRet }}</span>%</div>
          <div class="ft-metric-label">年化收益 (回测)</div>
        </div>
        <div class="ft-metric bear">
          <div class="ft-metric-val">-<span class="ft-counter">{{ metrics.mdd }}</span>%</div>
          <div class="ft-metric-label">最大回撤</div>
        </div>
        <div class="ft-metric">
          <div class="ft-metric-val"><span class="ft-counter">{{ metrics.modules }}</span></div>
          <div class="ft-metric-label">学习模块</div>
        </div>
      </div>

      <!-- CTA 按钮组 -->
      <div class="ft-hero-cta">
        <a class="ft-btn ft-btn--primary" href="/guide/" @click.prevent="navigateTo('/guide/')">
          <span class="ft-btn-icon">▶</span>
          <span>开始学习之旅</span>
          <span class="ft-btn-arrow">→</span>
        </a>
        <a class="ft-btn ft-btn--ghost" href="/" @click.prevent="navigateTo('/')">
          <span>查看课程概览</span>
        </a>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vitepress'

const router = useRouter()

// 指标数字
const metrics = ref({ sharpe: 0, annRet: 0, mdd: 0, modules: 0 })

// 逐帧计数动画
function animateCounter(target: number, key: keyof typeof metrics.value, duration = 1400) {
  const start = performance.now()
  const startVal = 0
  const decimals = target % 1 !== 0 ? 2 : 0
  const step = (now: number) => {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic
    const v = startVal + (target - startVal) * eased
    metrics.value[key] = decimals ? Number(v.toFixed(decimals)) : Math.round(v)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

// 波形路径
const wavePath1 = ref('')
const wavePath2 = ref('')
const wavePath3 = ref('')

function makeWave(amp: number, offset: number, freq: number) {
  let d = 'M0,100'
  for (let x = 0; x <= 1200; x += 12) {
    const y = 100 + amp * Math.sin((x / 1200) * Math.PI * freq + offset)
    d += ` L${x},${y.toFixed(2)}`
  }
  return d
}

// 日期
const todayStr = ref('')

onMounted(() => {
  // 数字滚动
  animateCounter(1.84, 'sharpe', 1600)
  animateCounter(28.6, 'annRet', 1800)
  animateCounter(12.3, 'mdd', 1500)
  animateCounter(20, 'modules', 1200)

  // 初始化波形
  let t = 0
  const tick = () => {
    t += 0.04
    wavePath1.value = makeWave(22, t * 1.2, 4)
    wavePath2.value = makeWave(14, t * 0.8 + 1, 5)
    wavePath3.value = makeWave(8,  t * 1.5 + 2, 7)
    requestAnimationFrame(tick)
  }
  tick()

  // 日期
  const d = new Date()
  todayStr.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
})

function navigateTo(path: string) {
  router.go(path)
}
</script>

<style scoped>
.ft-hero {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 24px;
  padding: 72px 56px 80px;
  background: linear-gradient(135deg, #050810 0%, #0B1220 50%, #1B2A4E 100%);
  color: #fff;
  margin: 16px 0 48px;
  box-shadow: 0 30px 80px rgba(13, 26, 56, .35);
  min-height: 480px;
}
@media (max-width: 768px) {
  .ft-hero { padding: 48px 24px 56px; border-radius: 16px; }
}

/* ---------- 背景 ---------- */
.ft-hero-bg {
  position: absolute;
  inset: 0;
  z-index: -2;
  overflow: hidden;
}
.ft-hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: .55;
  animation: ft-float 16s ease-in-out infinite;
}
.ft-hero-glow--1 {
  width: 520px; height: 520px;
  background: radial-gradient(circle, #00E5A0, transparent 70%);
  top: -160px; left: -120px;
}
.ft-hero-glow--2 {
  width: 460px; height: 460px;
  background: radial-gradient(circle, #FF0080, transparent 70%);
  bottom: -180px; right: -100px;
  animation-delay: -5s;
}
.ft-hero-glow--3 {
  width: 380px; height: 380px;
  background: radial-gradient(circle, #7C3AED, transparent 70%);
  top: 30%; right: 20%;
  animation-delay: -10s;
}
@keyframes ft-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%      { transform: translate(40px, -30px) scale(1.08); }
}

/* 网格点阵 */
.ft-hero-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: linear-gradient(180deg, transparent 0%, #000 30%, #000 70%, transparent 100%);
}

/* 波形 */
.ft-hero-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 220px;
  z-index: -1;
  opacity: .35;
}
.ft-wave-1 { fill: none; stroke: #00E5A0; stroke-width: 1.5; stroke-linecap: round; }
.ft-wave-2 { fill: none; stroke: #00D4FF; stroke-width: 1.2; stroke-linecap: round; }
.ft-wave-3 { fill: none; stroke: #FF0080; stroke-width: 1; stroke-linecap: round; }

/* ---------- 内容 ---------- */
.ft-hero-content {
  position: relative;
  max-width: 820px;
}

.ft-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .18);
  backdrop-filter: blur(12px);
  font-size: .82em;
  font-weight: 600;
  letter-spacing: .04em;
  margin-bottom: 24px;
  animation: ft-fade-up .8s .1s var(--ft-ease) backwards;
}
.ft-hero-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--ft-brand);
  box-shadow: 0 0 12px var(--ft-brand);
  animation: ft-pulse 1.6s infinite;
}

.ft-hero-title {
  font-size: clamp(2.4rem, 5.4vw, 4rem);
  line-height: 1.1;
  font-weight: 900;
  letter-spacing: -.03em;
  margin: 0 0 24px;
  animation: ft-fade-up .8s .2s var(--ft-ease) backwards;
}
.ft-hero-accent {
  background: linear-gradient(135deg, #00E5A0 0%, #00D4FF 60%, #7C3AED 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 200% 200%;
  animation: ft-shimmer 4s ease infinite;
}
@keyframes ft-shimmer {
  0%, 100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}

.ft-hero-subtitle {
  font-size: 1.1rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, .75);
  max-width: 640px;
  margin: 0 0 32px;
  animation: ft-fade-up .8s .3s var(--ft-ease) backwards;
}
.ft-hero-subtitle strong {
  color: var(--ft-brand);
  font-weight: 700;
}

.ft-hero-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 0 0 40px;
  animation: ft-fade-up .8s .4s var(--ft-ease) backwards;
}

/* ---------- CTA 按钮 ---------- */
.ft-hero-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  animation: ft-fade-up .8s .5s var(--ft-ease) backwards;
}
.ft-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 1em;
  letter-spacing: .01em;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  isolation: isolate;
  text-decoration: none !important;
  transition: transform .3s var(--ft-ease-bounce), box-shadow .3s var(--ft-ease);
}
.ft-btn::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,.5) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform .7s var(--ft-ease);
  z-index: 1;
}
.ft-btn:hover::before { transform: translateX(100%); }

.ft-btn--primary {
  background: linear-gradient(135deg, #00E5A0 0%, #00D4FF 100%);
  color: #051912;
  box-shadow: 0 8px 24px rgba(0, 229, 160, .4);
}
.ft-btn--primary:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 36px rgba(0, 229, 160, .55), 0 16px 40px rgba(0, 229, 160, .35);
}
.ft-btn--primary:active {
  transform: translateY(-1px) scale(1);
}

.ft-btn--ghost {
  background: transparent;
  color: #fff;
  border: 1.5px solid rgba(255,255,255,.3);
}
.ft-btn--ghost:hover {
  background: rgba(255, 255, 255, .08);
  border-color: rgba(255, 255, 255, .6);
  transform: translateY(-3px) scale(1.02);
}

.ft-btn-icon {
  display: inline-flex;
  width: 24px; height: 24px;
  align-items: center;
  justify-content: center;
  background: #051912;
  border-radius: 50%;
  color: var(--ft-brand);
  font-size: .6em;
  z-index: 2;
}
.ft-btn-arrow {
  transition: transform .3s var(--ft-ease);
  z-index: 2;
}
.ft-btn:hover .ft-btn-arrow { transform: translateX(4px); }

@keyframes ft-fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes ft-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: .4; transform: scale(.7); }
}
</style>
