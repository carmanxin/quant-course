<template>
  <div class="card">
    <h4>🔥 资产相关性热力图</h4>
    <button @click="generate">生成热力图</button>
    <div ref="chartRef" class="chart-container" style="height:320px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useData } from 'vitepress'
import { normalRandom } from './useRandom'

const { isDark } = useData()
const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function generate() {
  const stocks = 5, days = 200
  const returns: number[][] = []
  for (let s = 0; s < stocks; s++) {
    const rets: number[] = []
    for (let d = 0; d < days; d++) rets.push(normalRandom(0, 0.01))
    returns.push(rets)
  }

  const corrMatrix: number[][] = []
  for (let i = 0; i < stocks; i++) {
    corrMatrix[i] = []
    for (let j = 0; j < stocks; j++) {
      if (i === j) { corrMatrix[i][j] = 1; continue }
      const ri = returns[i], rj = returns[j]
      const mi = ri.reduce((a, b) => a + b, 0) / days
      const mj = rj.reduce((a, b) => a + b, 0) / days
      let cov = 0, vi = 0, vj = 0
      for (let k = 0; k < days; k++) {
        cov += (ri[k] - mi) * (rj[k] - mj)
        vi += (ri[k] - mi) ** 2
        vj += (rj[k] - mj) ** 2
      }
      cov /= (days - 1); vi /= (days - 1); vj /= (days - 1)
      corrMatrix[i][j] = (vi && vj) ? cov / Math.sqrt(vi * vj) : 0
    }
  }

  const labels = Array.from({ length: stocks }, (_, i) => `资产${i + 1}`)
  const data: [number, number, number][] = []
  for (let i = 0; i < stocks; i++) {
    for (let j = 0; j < stocks; j++) {
      data.push([j, i, +corrMatrix[i][j].toFixed(3)])
    }
  }

  chart?.setOption({
    tooltip: {},
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#94a3b8' }, position: 'top' },
    yAxis: { type: 'category', data: labels, axisLabel: { color: '#94a3b8' }, inverse: true },
    visualMap: { min: -1, max: 1, inRange: { color: ['#3b82f6', '#1e293b', '#ef4444'] } },
    series: [{
      type: 'heatmap',
      data,
      label: { show: true, color: '#e2e8f0', fontSize: 11 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
    }]
  }, { notMerge: true })
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
    generate()
    window.addEventListener('resize', () => chart?.resize())
  }
  watch(isDark, () => {
    chart?.dispose()
    if (chartRef.value) {
      chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
      generate()
    }
  })
})
</script>
