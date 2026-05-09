<template>
  <div>
    <h2 style="margin-bottom: 20px">报告生成</h2>

    <el-row :gutter="20">
      <!-- Config Panel -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>报告设置</template>

          <el-form label-width="80px">
            <el-form-item label="类型">
              <el-radio-group v-model="form.report_type">
                <el-radio value="daily">日报</el-radio>
                <el-radio value="weekly">周报</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                start-placeholder="开始"
                end-placeholder="结束"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="风格">
              <el-select v-model="form.style" style="width: 100%">
                <el-option label="正式周报" value="formal" />
                <el-option label="技术总结" value="technical" />
                <el-option label="日报简版" value="brief" />
                <el-option label="项目复盘" value="review" />
              </el-select>
            </el-form-item>

            <div style="display: flex; gap: 8px">
              <el-button type="primary" @click="handlePreview" :loading="loading">预览数据</el-button>
              <el-button type="success" @click="handleGenerate" :loading="loading">生成报告</el-button>
              <el-button type="warning" @click="handleAIGenerate" :loading="aiLoading">AI 生成</el-button>
            </div>
          </el-form>
        </el-card>

        <!-- History -->
        <el-card shadow="hover" style="margin-top: 20px">
          <template #header>历史报告</template>
          <div v-if="historyList.length === 0" style="color: #909399; text-align: center; padding: 20px">暂无报告</div>
          <div v-for="r in historyList" :key="r.filename" class="history-item" @click="loadHistory(r)">
            <el-tag :type="r.type === 'daily' ? '' : 'success'" size="small">{{ r.type === 'daily' ? '日报' : '周报' }}</el-tag>
            <span>{{ r.filename }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- Preview / Result -->
      <el-col :span="16">
        <!-- Preview Data -->
        <el-card v-if="previewData && !markdown" shadow="hover">
          <template #header>数据预览</template>
          <div v-if="previewData.projects && previewData.projects.length > 0">
            <div v-for="p in previewData.projects" :key="p.name" style="margin-bottom: 16px">
              <h4>{{ p.name }}</h4>
              <p>活跃时间: {{ p.active_time }} | 文件修改: {{ p.file_changes }} 次</p>
              <p v-if="p.commits && p.commits.length">提交: {{ p.commits.join('; ') }}</p>
            </div>
          </div>
          <div v-else style="color: #909399; text-align: center; padding: 20px">该时间段无数据</div>
        </el-card>

        <!-- Markdown Result -->
        <el-card v-if="markdown" shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>报告内容</span>
              <div>
                <el-button size="small" @click="copyMarkdown">复制</el-button>
                <el-button size="small" type="primary" @click="downloadMarkdown">下载</el-button>
              </div>
            </div>
          </template>
          <div class="markdown-body" v-html="renderedMarkdown"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { previewReport, generateReport, generateAIReport, listReports, getReport } from '../api/report'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const form = ref({
  report_type: 'weekly',
  style: 'formal',
})
const dateRange = ref<string[]>([
  dayjs().startOf('week').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD'),
])
const loading = ref(false)
const aiLoading = ref(false)
const previewData = ref<any>(null)
const markdown = ref('')
const historyList = ref<any[]>([])

const renderedMarkdown = computed(() => {
  if (!markdown.value) return ''
  return marked(markdown.value)
})

function getParams() {
  return {
    report_type: form.value.report_type,
    start_date: dateRange.value?.[0] || '',
    end_date: dateRange.value?.[1] || '',
    style: form.value.style,
  }
}

async function handlePreview() {
  loading.value = true
  markdown.value = ''
  try {
    const res = await previewReport(getParams())
    previewData.value = res.data
  } catch (e: any) {
    ElMessage.error('预览失败')
  }
  loading.value = false
}

async function handleGenerate() {
  loading.value = true
  try {
    const res = await generateReport(getParams())
    markdown.value = res.data.markdown
    previewData.value = res.data.data
    loadHistory()
  } catch (e: any) {
    ElMessage.error('生成失败')
  }
  loading.value = false
}

async function handleAIGenerate() {
  aiLoading.value = true
  try {
    const res = await generateAIReport({
      ...getParams(),
      summary_data: previewData.value || undefined,
    })
    markdown.value = res.data.markdown
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'AI 生成失败')
  }
  aiLoading.value = false
}

function copyMarkdown() {
  navigator.clipboard.writeText(markdown.value)
  ElMessage.success('已复制')
}

function downloadMarkdown() {
  const blob = new Blob([markdown.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${dateRange.value?.[0]}_${dateRange.value?.[1]}.md`
  a.click()
  URL.revokeObjectURL(url)
}

async function loadHistory(item?: any) {
  if (item) {
    try {
      const res = await getReport(item.type, item.filename)
      markdown.value = res.data.content
    } catch {}
    return
  }
  try {
    const res = await listReports()
    historyList.value = res.data
  } catch {}
}

onMounted(() => loadHistory())
</script>

<style scoped>
.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}
.history-item:hover {
  color: #409EFF;
}
.markdown-body {
  line-height: 1.8;
  font-size: 14px;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin-top: 16px;
  margin-bottom: 8px;
}
.markdown-body ul, .markdown-body ol {
  padding-left: 20px;
}
.markdown-body li {
  margin-bottom: 4px;
}
</style>
