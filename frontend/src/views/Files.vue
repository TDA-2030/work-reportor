<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>文件活动</h2>
      <div style="display: flex; gap: 12px">
        <el-date-picker v-model="date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" @change="loadData" />
        <el-select v-model="projectFilter" placeholder="全部项目" clearable @change="loadData" style="width: 150px">
          <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
        </el-select>
        <el-select v-model="extFilter" placeholder="全部类型" clearable @change="loadData" style="width: 120px">
          <el-option v-for="e in extList" :key="e" :label="e" :value="e" />
        </el-select>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="fileData.items" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">{{ row.timestamp?.split(' ')[1] || '' }}</template>
        </el-table-column>
        <el-table-column prop="event_type" label="事件" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.event_type)" size="small">{{ row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_name" label="文件名" width="200" show-overflow-tooltip />
        <el-table-column prop="file_ext" label="扩展名" width="100" />
        <el-table-column prop="project" label="项目" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.project" size="small">{{ row.project }}</el-tag>
            <span v-else style="color: #ccc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_path" label="路径" show-overflow-tooltip />
      </el-table>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="page"
          :page-size="50"
          :total="fileData.total"
          layout="prev, pager, next, total"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFiles } from '../api/activity'
import dayjs from 'dayjs'

const date = ref(dayjs().format('YYYY-MM-DD'))
const projectFilter = ref('')
const extFilter = ref('')
const page = ref(1)
const fileData = ref<any>({ items: [], total: 0 })
const projectList = ref<string[]>([])
const extList = ref<string[]>([])

function tagType(type: string) {
  const map: Record<string, string> = { created: 'success', modified: '', deleted: 'danger', moved: 'warning' }
  return map[type] || ''
}

async function loadData() {
  try {
    const res = await getFiles({
      date: date.value,
      project: projectFilter.value || undefined,
      file_ext: extFilter.value || undefined,
      page: page.value,
      page_size: 50,
    })
    fileData.value = res.data
    // Extract filter options
    const projects = new Set<string>()
    const exts = new Set<string>()
    res.data.items.forEach((e: any) => {
      if (e.project) projects.add(e.project)
      if (e.file_ext) exts.add(e.file_ext)
    })
    if (projectList.value.length === 0) projectList.value = Array.from(projects)
    if (extList.value.length === 0) extList.value = Array.from(exts)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>
