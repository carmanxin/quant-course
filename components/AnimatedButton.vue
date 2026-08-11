<template>
  <component
    :is="tag"
    :class="['ft-btn-anim', `ft-btn-anim--${variant}`, { 'ft-btn-anim--lg': size === 'lg', 'ft-btn-anim--sm': size === 'sm' }]"
    :href="href"
    @click="onClick"
  >
    <span v-if="$slots.icon" class="ft-btn-anim__icon"><slot name="icon" /></span>
    <span class="ft-btn-anim__label"><slot /></span>
    <span v-if="arrow" class="ft-btn-anim__arrow">→</span>
    <span class="ft-btn-anim__shine"></span>
    <span class="ft-btn-anim__ripple" ref="ripple"></span>
  </component>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vitepress'

const props = withDefaults(defineProps<{
  variant?: 'primary' | 'mint' | 'cyan' | 'purple' | 'pink' | 'gold' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  arrow?: boolean
  href?: string
  to?: string
}>(), {
  variant: 'primary',
  size: 'md',
  arrow: false,
})

const ripple = ref<HTMLElement | null>(null)
const router = useRouter()

const tag = computed(() => {
  if (props.to) return 'a'
  if (props.href) return 'a'
  return 'button'
})

function onClick(e: MouseEvent) {
  // 波纹效果
  const btn = e.currentTarget as HTMLElement
  const rect = btn.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = e.clientX - rect.left - size / 2
  const y = e.clientY - rect.top  - size / 2
  const span = document.createElement('span')
  span.style.cssText = `
    position: absolute;
    width: ${size}px; height: ${size}px;
    left: ${x}px; top: ${y}px;
    background: rgba(255,255,255,.35);
    border-radius: 50%;
    transform: scale(0);
    animation: ripple .65s ease-out;
    pointer-events: none;
  `
  btn.appendChild(span)
  setTimeout(() => span.remove(), 700)

  if (props.to) {
    e.preventDefault()
    router.go(props.to)
  }
}
</script>

<style scoped>
.ft-btn-anim {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 999px;
  font-weight: 700;
  font-size: .95em;
  letter-spacing: .01em;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  isolation: isolate;
  border: none;
  text-decoration: none !important;
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s var(--ft-ease);
  font-family: var(--ft-font-sans);
}
.ft-btn-anim--lg { padding: 16px 32px; font-size: 1.05em; }
.ft-btn-anim--sm { padding: 8px 18px;  font-size: .85em; }

/* 光斑扫描 */
.ft-btn-anim__shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,.5) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform .7s var(--ft-ease);
  pointer-events: none;
}
.ft-btn-anim:hover .ft-btn-anim__shine { transform: translateX(100%); }

/* 箭头 */
.ft-btn-anim__arrow {
  transition: transform .3s var(--ft-ease);
  font-size: 1.1em;
}
.ft-btn-anim:hover .ft-btn-anim__arrow { transform: translateX(4px); }

/* ==== 变体 ==== */
.ft-btn-anim--primary {
  background: linear-gradient(135deg, #00E5A0 0%, #00D4FF 100%);
  color: #051912;
  box-shadow: 0 6px 20px rgba(0, 229, 160, .35);
}
.ft-btn-anim--primary:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 36px rgba(0, 229, 160, .6), 0 12px 32px rgba(0, 229, 160, .4);
}
.ft-btn-anim--primary:active { transform: translateY(-1px) scale(.99); }

.ft-btn-anim--mint {
  background: linear-gradient(135deg, #00E5A0 0%, #34D399 100%);
  color: #051912;
  box-shadow: 0 6px 20px rgba(0, 229, 160, .3);
}
.ft-btn-anim--mint:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 30px rgba(0, 229, 160, .5), 0 12px 32px rgba(0, 229, 160, .35);
}

.ft-btn-anim--cyan {
  background: linear-gradient(135deg, #00D4FF 0%, #0EA5E9 100%);
  color: #042F4C;
  box-shadow: 0 6px 20px rgba(0, 212, 255, .3);
}
.ft-btn-anim--cyan:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 30px rgba(0, 212, 255, .55), 0 12px 32px rgba(0, 212, 255, .35);
}

.ft-btn-anim--purple {
  background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
  color: #fff;
  box-shadow: 0 6px 20px rgba(124, 58, 237, .35);
}
.ft-btn-anim--purple:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 36px rgba(124, 58, 237, .55), 0 12px 32px rgba(124, 58, 237, .35);
}

.ft-btn-anim--pink {
  background: linear-gradient(135deg, #FF0080 0%, #FF4D6D 100%);
  color: #fff;
  box-shadow: 0 6px 20px rgba(255, 0, 128, .35);
}
.ft-btn-anim--pink:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 36px rgba(255, 0, 128, .55), 0 12px 32px rgba(255, 0, 128, .35);
}

.ft-btn-anim--gold {
  background: linear-gradient(135deg, #FFB800 0%, #FF8A00 100%);
  color: #3D2600;
  box-shadow: 0 6px 20px rgba(255, 184, 0, .35);
}
.ft-btn-anim--gold:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 0 30px rgba(255, 184, 0, .55), 0 12px 32px rgba(255, 184, 0, .35);
}

/* 描边按钮 - 渐变描边 */
.ft-btn-anim--outline {
  background: var(--ft-surface);
  color: var(--ft-text-1);
  border: 2px solid transparent;
  position: relative;
  box-shadow: none;
}
.ft-btn-anim--outline::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  padding: 2px;
  background: linear-gradient(135deg, #00E5A0 0%, #00D4FF 50%, #7C3AED 100%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: .8;
  transition: opacity .3s;
}
.ft-btn-anim--outline:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 24px rgba(13, 26, 56, .12);
}
.ft-btn-anim--outline:hover::before { opacity: 1; }

@keyframes ripple {
  to { transform: scale(2.5); opacity: 0; }
}
</style>
