<!-- 文件路径: /frontend-js/src/app/aiis_demo/views/example/index.vue
     功能描述: 纯离线模板页，使用现有主题与双语文案，无外部 I/O。 -->
<template>
  <div class="page-layout">
    <el-card>
      <template #header>{{ $t('aiis_demo.example.title') }}</template>
      <p>{{ $t('aiis_demo.example.description') }}</p>
    </el-card>
  </div>
</template>
