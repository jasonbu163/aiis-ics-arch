<!-- 保留旧质量控制叶子页面和授权标识，跳转仍由路由守卫检查质量列表权限。 -->
<template><div aria-hidden="true" /></template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
onMounted(() => router.replace({ name: 'QualityList' }))
</script>
