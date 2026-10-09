<!--
  文件路径: /frontend-js/src/components/shell/BrandLogo.vue
  功能描述: 全局壳层复用的品牌 Logo 渲染组件
  主要功能:
    - 使用 VITE_BRAND_LOGO_FILE 指向的已打包品牌资源
    - 让登录页、顶部栏和侧栏保持同一 Logo 来源
    - 按 Logo 自然比例计算 contain 显示框并在框内生成三段独立光源
-->
<template>
  <span
    ref="shellRef"
    :class="['brand-logo-shell', `brand-logo-shell--${variant}`]"
    :style="brandGlowStyle"
  >
    <span class="brand-logo-fit" :style="brandLogoFitStyle">
      <span class="brand-logo-glow" aria-hidden="true">
        <span class="brand-logo-glow-source brand-logo-glow-source--left" />
        <span class="brand-logo-glow-source brand-logo-glow-source--center" />
        <span class="brand-logo-glow-source brand-logo-glow-source--right" />
      </span>
      <img class="brand-logo" :src="brandLogoUrl" :alt="$t('common.systemTitle')" @load="handleLogoLoad" />
    </span>
  </span>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { brandGlowModes, brandLogoAlign, brandLogoUrl } from '@/config/brand'

defineProps({
  variant: {
    type: String,
    default: 'shell'
  }
})

const shellRef = ref()
const logoNaturalSize = reactive({ width: 1, height: 1 })
const shellSize = reactive({ width: 0, height: 0 })
let shellResizeObserver

const brandLogoFitStyle = computed(() => {
  const slotWidth = shellSize.width
  const slotHeight = shellSize.height

  if (!slotWidth || !slotHeight) {
    return {
      width: '100%',
      height: '100%',
      left: '0',
      top: '0'
    }
  }

  const logoRatio = logoNaturalSize.width / logoNaturalSize.height
  const slotRatio = slotWidth / slotHeight
  const fitsByWidth = logoRatio >= slotRatio
  const fitWidth = fitsByWidth ? slotWidth : slotHeight * logoRatio
  const fitHeight = fitsByWidth ? slotWidth / logoRatio : slotHeight
  const remainingWidth = slotWidth - fitWidth
  const fitLeft = {
    left: 0,
    center: remainingWidth / 2,
    right: remainingWidth
  }[brandLogoAlign]

  return {
    width: `${fitWidth}px`,
    height: `${fitHeight}px`,
    left: `${fitLeft}px`,
    top: `${(slotHeight - fitHeight) / 2}px`
  }
})

function updateShellSize(width, height) {
  shellSize.width = width
  shellSize.height = height
}

function measureShell() {
  if (!shellRef.value) return

  updateShellSize(shellRef.value.clientWidth, shellRef.value.clientHeight)
}

function handleLogoLoad(event) {
  logoNaturalSize.width = event.currentTarget.naturalWidth || 1
  logoNaturalSize.height = event.currentTarget.naturalHeight || 1
  measureShell()
}

onMounted(() => {
  measureShell()
  shellResizeObserver = new ResizeObserver(([entry]) => {
    updateShellSize(entry.contentRect.width, entry.contentRect.height)
  })
  shellResizeObserver.observe(shellRef.value)
})

onBeforeUnmount(() => {
  shellResizeObserver?.disconnect()
})

const brandGlowStyle = {
  '--brand-logo-glow-left': `var(--brand-logo-glow-${brandGlowModes.left})`,
  '--brand-logo-glow-center': `var(--brand-logo-glow-${brandGlowModes.center})`,
  '--brand-logo-glow-right': `var(--brand-logo-glow-${brandGlowModes.right})`,
  '--brand-logo-shell-glow-opacity': Object.values(brandGlowModes).includes('high-light') ? '0.76' : '0.56'
}
</script>

<style scoped>
.brand-logo-shell {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
  isolation: isolate;
}

.brand-logo-fit {
  position: absolute;
  isolation: isolate;
}

.brand-logo-glow {
  position: absolute;
  z-index: 0;
  display: var(--brand-logo-glow-display, none);
  grid-template-columns: repeat(3, minmax(0, 1fr));
  inset: 0;
  pointer-events: none;
}

.brand-logo-glow-source {
  position: relative;
}

.brand-logo-glow-source::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 126%;
  height: min(160%, 80px);
  border-radius: 24px;
  background: var(--brand-logo-glow-source-color);
  filter: blur(12px);
  transform: translate(-50%, -50%);
}

.brand-logo-glow-source--left {
  --brand-logo-glow-source-color: var(--brand-logo-glow-left);
}

.brand-logo-glow-source--center {
  --brand-logo-glow-source-color: var(--brand-logo-glow-center);
}

.brand-logo-glow-source--right {
  --brand-logo-glow-source-color: var(--brand-logo-glow-right);
}

.brand-logo-shell--shell .brand-logo-glow {
  opacity: var(--brand-logo-shell-glow-opacity);
}

.brand-logo-shell--shell .brand-logo-glow-source::before {
  width: 126%;
  height: min(170%, 56px);
  border-radius: 18px;
  filter: blur(9px);
}

.brand-logo {
  position: relative;
  z-index: 1;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
}

</style>
