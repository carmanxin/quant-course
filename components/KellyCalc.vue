<template>
  <div class="card">
    <h4>💰 凯利公式计算器</h4>
    <div class="input-group">
      <label>胜率 p (%) <input v-model.number="p" type="number" min="0" max="100"></label>
      <label>盈亏比 b <input v-model.number="b" type="number" step="0.1" min="0.1"></label>
    </div>
    <p v-if="f > 0" class="result-text" style="color:#10b981">
      凯利最优比例：<strong>{{ (f * 100).toFixed(1) }}%</strong>。半凯利：{{ (f * 50).toFixed(1) }}%。
    </p>
    <p v-else class="result-text" style="color:#ef4444">凯利比例为负或零，不该参与。</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const p = ref(55)
const b = ref(1.5)

const f = computed(() => {
  const winProb = p.value / 100
  return (b.value * winProb - (1 - winProb)) / b.value
})
</script>
