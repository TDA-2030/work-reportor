<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>时间线</h2>
      <div style="display: flex; gap: 12px">
        <el-date-picker v-model="date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="选择日期" @change="loadData" />
        <el-select v-model="projectFilter" placeholder="全部项目" clearable @change="loadData" style="width: 160px">
          <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="events" stripe style="width: 100%">
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">{{ row.start_time?.split(' ')[1] || '' }}</template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="{ row }">{{ row.end_time?.split(' ')[1] || '' }}</template>
        </el-table-column>
        <el-table-column prop="app_name" label="应用" width="140" />
        <el-table-column prop="project" label="项目" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.project" size="small">{{ row.project }}</el-tag>
            <span v-else style="color: #ccc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.category" size="small" type="info">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="window_title" label="窗口标题" show-overflow-tooltip />
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTimeline } from '../api/activity'
import dayjs from 'dayjs'

const date = ref(dayjs().format('YYYY-MM-DD'))
const projectFilter = ref('')
const events = ref<any[]>([])
const projectList = ref<string[]>([])

function formatDuration(s: number): string {
  if (!s) return '-'
  const m = Math.floor(s / 60)
  const sec = s % 60
  if (m > 0) return `${m}m ${sec}s`
  return `${sec}s`
}

async function loadData() {
  try {
    const res = await getTimeline(date.value, projectFilter.value || undefined)
    events.value = res.data
    const projects = new Set<string>()
    res.data.forEach((e: any) => { if (e.project) projects.add(e.project) })
    projectList.value = Array.from(projects)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>
