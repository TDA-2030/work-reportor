<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>Git 活动</h2>
      <div style="display: flex; gap: 12px">
        <el-date-picker v-model="dateRange" type="daterange" format="YYYY-MM-DD" value-format="YYYY-MM-DD"
          start-placeholder="开始日期" end-placeholder="结束日期" @change="loadData" />
        <el-select v-model="projectFilter" placeholder="全部项目" clearable @change="loadData" style="width: 150px">
          <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="commits" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="project" label="项目" width="160">
          <template #default="{ row }">
            <el-tag size="small">{{ row.project }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="提交信息" show-overflow-tooltip />
        <el-table-column prop="files_changed" label="文件数" width="90" align="center" />
        <el-table-column label="增/删" width="120" align="center">
          <template #default="{ row }">
            <span style="color: #67C23A">+{{ row.insertions }}</span>
            <span style="color: #F56C6C; margin-left: 8px">-{{ row.deletions }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="commits.length === 0" style="text-align: center; padding: 40px; color: #909399">
        暂无 Git 提交记录
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/request'
import dayjs from 'dayjs'

const dateRange = ref<string[]>([
  dayjs().subtract(7, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD'),
])
const projectFilter = ref('')
const commits = ref<any[]>([])
const projectList = ref<string[]>([])

async function loadData() {
  if (!dateRange.value || dateRange.value.length < 2) return
  try {
    const res = await api.get('/activity/git', {
      params: {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        project: projectFilter.value || undefined,
      }
    })
    commits.value = res.data
    const projects = new Set<string>()
    res.data.forEach((e: any) => { if (e.project) projects.add(e.project) })
    projectList.value = Array.from(projects)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>
