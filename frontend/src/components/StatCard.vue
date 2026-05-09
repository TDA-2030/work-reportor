<template>
  <el-card shadow="hover" class="stat-card">
    <div class="stat-card-body">
      <div class="stat-info">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-value">{{ value }}</div>
      </div>
      <div class="stat-icon" :style="{ background: color }">
        <el-icon :size="28"><component :is="icon" /></el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  icon: string
  color?: string
}>()
</script>

<style scoped>
.stat-card {
  height: 100%;
}
.stat-card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: #409EFF;
}
</style>
