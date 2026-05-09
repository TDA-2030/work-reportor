<template>
  <div>
    <h2 style="margin-bottom: 20px">今日概览</h2>

    <!-- Stat Cards -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <StatCard label="活跃时间" :value="formatDuration(data.active_time)" icon="Timer" color="#409EFF" />
      </el-col>
      <el-col :span="8">
        <StatCard label="活跃项目" :value="data.top_projects.length" icon="Folder" color="#67C23A" />
      </el-col>
      <el-col :span="8">
        <StatCard label="文件变更" :value="data.recent_files.length" icon="Document" color="#E6A23C" />
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Project Rankings -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>项目活跃度排行</template>
          <div v-if="data.top_projects.length === 0" class="empty-text">暂无数据</div>
          <div v-for="p in data.top_projects" :key="p.name" class="project-item">
            <span class="project-name">{{ p.name }}</span>
            <el-progress
              :percentage="getPercentage(p.duration)"
              :stroke-width="16"
              :format="() => formatDuration(p.duration)"
            />
          </div>
        </el-card>
      </el-col>

      <!-- Category Distribution -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>工作类型分布</template>
          <div v-if="data.categories.length === 0" class="empty-text">暂无数据</div>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- Recent Files -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>最近文件变化</template>
          <div v-if="data.recent_files.length === 0" class="empty-text">暂无数据</div>
          <div v-for="f in data.recent_files" :key="f.timestamp + f.file_path" class="event-item">
            <el-tag :type="getFileTagType(f.event_type)" size="small">{{ f.event_type }}</el-tag>
            <span class="file-name">{{ f.file_name || f.file_path.split('/').pop() }}</span>
            <span class="event-time">{{ f.timestamp.split(' ')[1] }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- Recent Git -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>最近 Git 提交</template>
          <div v-if="data.recent_git.length === 0" class="empty-text">暂无数据</div>
          <div v-for="g in data.recent_git" :key="g.timestamp + g.message" class="event-item">
            <el-tag size="small" type="success">{{ g.project }}</el-tag>
            <span class="git-message">{{ g.message }}</span>
            <span class="event-time">{{ g.timestamp.split(' ')[1] }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { getDashboardToday } from '../api/dashboard'
import StatCard from '../components/StatCard.vue'
import * as echarts from 'echarts'

const data = ref<any>({
  active_time: 0,
  top_projects: [],
  categories: [],
  recent_files: [],
  recent_git: [],
})

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function formatDuration(seconds: number): string {
  if (!seconds) return '0m'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

function getPercentage(duration: number): number {
  const max = data.value.top_projects[0]?.duration || 1
  return Math.round((duration / max) * 100)
}

function getFileTagType(type: string) {
  const map: Record<string, string> = { created: 'success', modified: '', deleted: 'danger', moved: 'warning' }
  return map[type] || ''
}

function renderChart() {
  if (!chartRef.value || data.value.categories.length === 0) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.value.categories.map((c: any) => ({
        name: c.name,
        value: c.duration,
      })),
      label: {
        formatter: '{b}: {d}%',
      },
    }],
  })
}

onMounted(async () => {
  try {
    const res = await getDashboardToday()
    data.value = res.data
    await nextTick()
    renderChart()
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.project-item {
  margin-bottom: 12px;
}
.project-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
  display: block;
}
.event-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.event-item:last-child {
  border-bottom: none;
}
.file-name, .git-message {
  flex: 1;
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.event-time {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}
.empty-text {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
</style>
