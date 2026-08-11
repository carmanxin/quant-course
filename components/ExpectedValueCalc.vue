<template>
  <div class="card">
    <h4>🎲 期望值计算器</h4>
    <div class="input-group">
      <label>胜率(%) <input v-model.number="winRate" type="number" min="0" max="100"></label>
      <label>平均盈利($) <input v-model.number="winAmt" type="number" step="1"></label>
      <label>平均亏损($) <input v-model.number="lossAmt" type="number" step="1"></label>
    </div>
    <p class="result-text" :style="{ color: ev >= 0 ? '#10b981' : '#ef4444' }">
      期望值 = {{ ev.toFixed(2) }} 美元/笔。{{ ev >= 0 ? '✅ 正期望策略' : '❌ 负期望' }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const winRate = ref(55)
const winAmt = ref(100)
const lossAmt = ref(90)

const ev = computed(() => {
  return (winRate.value / 100) * winAmt.value - ((100 - winRate.value) / 100) * lossAmt.value
})
</script>
