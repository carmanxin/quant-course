import * as echarts from 'echarts'
import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { useData } from 'vitepress'

export function useECharts(options: Ref<any>) {
  const chartRef = ref<HTMLElement | null>(null)
  let chart: echarts.ECharts | null = null

  const { isDark } = useData()

  const getTheme = () => isDark.value ? 'dark' : undefined

  const initChart = () => {
    if (chartRef.value) {
      chart?.dispose()
      chart = echarts.init(chartRef.value, getTheme())
      chart.setOption(options.value)
    }
  }

  const updateChart = () => {
    if (chart) {
      chart.setOption(options.value, { notMerge: true })
    } else {
      initChart()
    }
  }

  onMounted(() => {
    initChart()
    const onResize = () => chart?.resize()
    window.addEventListener('resize', onResize)
    // 保存清理函数
    ;(chartRef.value as any).__cleanup = () => window.removeEventListener('resize', onResize)
  })

  onUnmounted(() => {
    if (chartRef.value && (chartRef.value as any).__cleanup) {
      ;(chartRef.value as any).__cleanup()
    }
    chart?.dispose()
  })

  watch(options, updateChart, { deep: true })
  watch(isDark, () => {
    // Re-init chart on theme change
    initChart()
  })

  return { chartRef, updateChart, isDark }
}
