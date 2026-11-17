<!-- 未选择或未配置时的通用空坐标；不虚构时间、单位或数值刻度。 -->
<template>
  <div class="empty-plot" role="img" :aria-label="reason">
    <div class="axes"><span class="y-axis" /><span class="x-axis" /></div>
    <p>{{ reason }}</p>
  </div>
</template>
<script setup>
defineProps({ reason: { type: String, required: true } })
</script>
<style scoped>
.empty-plot { position: relative; height: 280px; padding: 20px 24px 40px 48px; }
.axes { position: relative; width: 100%; height: 100%; }
.y-axis { position: absolute; left: 0; top: 0; bottom: 0; border-left: 1px solid var(--text-secondary); }
.x-axis { position: absolute; left: 0; right: 0; bottom: 0; border-bottom: 1px solid var(--text-secondary); }
p { position: absolute; top: 40%; left: 0; width: 100%; text-align: center; color: var(--text-secondary); }
</style>
