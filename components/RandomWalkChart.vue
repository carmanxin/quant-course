<template>
  <div class="card">
    <h4>📉 随机游走模拟器</h4>
    <button @click="generate">生成路径</button>
    <div ref="chartRef" class="chart-container" style="height:280px"></div>
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
  const paths: { name: string; data: number[] }[] = []
  for (let p = 0; p < 20; p++) {
    const prices = [100]
    for (let i = 1; i < 150; i++) {
      prices.push(prices[i - 1] * (1 + normalRandom(0.0002, 0.015)))
    }
    paths.push({ name: `路径${p + 1}`, data: prices })
  }

  const series = paths.map((path, i) => ({
    type: 'line',
    name: path.name,
    data: path.data,
    showSymbol: false,
    lineStyle: { width: 1 },
    silent: true,
  }))

  chart?.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
    series,
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
