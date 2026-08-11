<template>
  <div class="card">
    <h4>📊 实战模拟</h4>
    <button @click="simulate">生成并评估</button>
    <div v-if="metrics" class="result-text" style="margin:12px 0">
      <p>年化收益率：<strong>{{ (metrics.annRet * 100).toFixed(2) }}%</strong>，年化波动率：<strong>{{ (metrics.annVol * 100).toFixed(2) }}%</strong></p>
      <p>夏普比率：<strong>{{ metrics.sharpe.toFixed(2) }}</strong>，最大回撤：<strong>{{ (metrics.mdd * 100).toFixed(2) }}%</strong>，卡玛比率：<strong>{{ metrics.calmar.toFixed(2) }}</strong></p>
    </div>
    <div ref="navRef" class="chart-container" style="height:240px"></div>
    <div ref="ddRef" class="chart-container" style="height:140px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useData } from 'vitepress'
import { normalRandom } from './useRandom'

const { isDark } = useData()
const navRef = ref<HTMLElement | null>(null)
const ddRef = ref<HTMLElement | null>(null)
let navChart: echarts.ECharts | null = null
let ddChart: echarts.ECharts | null = null

interface Metrics { annRet: number; annVol: number; sharpe: number; mdd: number; calmar: number }
const metrics = ref<Metrics | null>(null)

function simulate() {
  const rets = Array.from({ length: 500 }, () => normalRandom(0.0004, 0.012))
  const nav = [1]
  rets.forEach(r => nav.push(nav[nav.length - 1] * (1 + r)))

  const meanD = rets.reduce((a, b) => a + b, 0) / 500
  const stdD = Math.sqrt(rets.reduce((s, r) => s + (r - meanD) ** 2, 0) / 500)
  const annRet = meanD * 252
  const annVol = stdD * Math.sqrt(252)
  const sharpe = annVol ? annRet / annVol : 0

  let peak = nav[0], mdd = 0
  const dds: number[] = []
  nav.forEach(v => {
    if (v > peak) peak = v
    const dd = (v - peak) / peak
    dds.push(dd)
    if (dd < mdd) mdd = dd
  })
  const calmar = mdd ? annRet / Math.abs(mdd) : 0

  metrics.value = { annRet, annVol, sharpe, mdd, calmar }

  const baseGrid = { left: 50, right: 20, top: 15, bottom: 30 }
  navChart?.setOption({
    grid: baseGrid,
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{ type: 'line', data: nav, showSymbol: false, lineStyle: { color: '#38bdf8', width: 2 } }]
  }, { notMerge: true })

  ddChart?.setOption({
    grid: baseGrid,
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'line', data: dds, showSymbol: false,
      lineStyle: { color: '#ef4444', width: 2 },
      areaStyle: { color: 'rgba(239,68,68,0.15)' }
    }]
  }, { notMerge: true })
}

onMounted(() => {
  const theme = isDark.value ? 'dark' : undefined
  if (navRef.value) navChart = echarts.init(navRef.value, theme)
  if (ddRef.value) ddChart = echarts.init(ddRef.value, theme)
  simulate()
  window.addEventListener('resize', () => { navChart?.resize(); ddChart?.resize() })
  watch(isDark, () => {
    navChart?.dispose(); ddChart?.dispose()
    const t = isDark.value ? 'dark' : undefined
    if (navRef.value) navChart = echarts.init(navRef.value, t)
    if (ddRef.value) ddChart = echarts.init(ddRef.value, t)
    simulate()
  })
})
</script>
