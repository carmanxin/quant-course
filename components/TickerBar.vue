<template>
  <div class="ft-ticker-wrap" aria-label="实时行情">
    <div class="ft-ticker-label">
      <span class="ft-ticker-dot"></span>
      <span>实时行情</span>
    </div>
    <div class="ft-marquee">
      <div class="ft-marquee-track">
        <span v-for="(item, i) in itemsDoubled" :key="i" class="ft-marquee-item">
          <span class="sym">{{ item.sym }}</span>
          <span class="px">{{ item.px.toFixed(2) }}</span>
          <span :class="['chg', item.chg >= 0 ? 'up' : 'down']">
            {{ item.chg >= 0 ? '▲' : '▼' }}
            {{ Math.abs(item.chg).toFixed(2) }}%
          </span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Item { sym: string; px: number; chg: number }

const items = ref<Item[]>([
  { sym: 'BTC',  px: 67890.12, chg:  2.34 },
  { sym: 'ETH',  px:  3456.78, chg:  1.56 },
  { sym: 'AAPL', px:   219.45, chg: -0.78 },
  { sym: 'TSLA', px:   245.30, chg:  3.21 },
  { sym: 'NVDA', px:   912.80, chg:  4.56 },
  { sym: 'SPX',  px:  5680.10, chg:  0.42 },
  { sym: 'NDX',  px: 19245.60, chg:  0.65 },
  { sym: 'CSI300', px:  3789.2, chg: -1.12 },
  { sym: 'USDCNH', px:    7.12, chg:  0.08 },
  { sym: 'GOLD', px:  2648.30, chg:  0.92 },
  { sym: 'OIL',  px:    74.85, chg: -2.13 },
  { sym: 'VIX',  px:    16.42, chg: -3.46 },
])

// 复制 2 份用于无缝循环
const itemsDoubled = computed(() => [...items.value, ...items.value])

let timer: number | undefined

onMounted(() => {
  // 每 2 秒模拟价格跳动
  timer = window.setInterval(() => {
    items.value = items.value.map(it => {
      // 随机漫步
      const drift = (Math.random() - 0.5) * 0.006
      const newChg = it.chg + drift * 10
      const newPx  = it.px * (1 + drift)
      return { ...it, px: newPx, chg: newChg }
    })
  }, 2000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.ft-ticker-wrap {
  display: flex;
  align-items: stretch;
  margin: 24px 0;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--ft-border);
  background: var(--ft-surface);
  box-shadow: var(--ft-shadow-sm);
}
.ft-ticker-label {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 18px;
  background: linear-gradient(135deg, #0B1220, #1B2A4E);
  color: #fff;
  font-weight: 700;
  font-size: .82em;
  letter-spacing: .06em;
}
.ft-ticker-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--ft-brand);
  box-shadow: 0 0 8px var(--ft-brand);
  animation: dotPulse 1.6s infinite;
}
@keyframes dotPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: .4; transform: scale(.7); }
}
.ft-marquee {
  flex: 1;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 10px 0;
  background: var(--ft-surface);
  font-family: var(--ft-font-mono);
  font-size: .85em;
  white-space: nowrap;
  position: relative;
}
.ft-marquee-track {
  display: flex;
  gap: 36px;
  padding-left: 36px;
  animation: marquee 48s linear infinite;
}
.ft-marquee:hover .ft-marquee-track { animation-play-state: paused; }
@keyframes marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.ft-marquee-item {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}
.ft-marquee-item .sym {
  color: var(--ft-text-1);
  letter-spacing: -.01em;
}
.ft-marquee-item .px {
  color: var(--ft-text-2);
  font-variant-numeric: tabular-nums;
}
.ft-marquee-item .chg.up   { color: var(--ft-bull); }
.ft-marquee-item .chg.down { color: var(--ft-bear); }
</style>
