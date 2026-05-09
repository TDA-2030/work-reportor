<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>项目统计</h2>
      <el-button type="primary" @click="showAddDialog = true">添加项目</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="p in projects" :key="p.name" style="margin-bottom: 20px">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="font-weight: 600">{{ p.name }}</span>
              <div>
                <el-tag size="small" type="info">{{ p.type || 'unknown' }}</el-tag>
                <el-button type="danger" size="small" text @click="handleDelete(p.name)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          <div class="stat-row"><span>活跃时间</span><strong>{{ formatDuration(p.stats?.active_time || 0) }}</strong></div>
          <div class="stat-row"><span>文件修改</span><strong>{{ p.stats?.file_changes || 0 }} 次</strong></div>
          <div class="stat-row"><span>Git 提交</span><strong>{{ p.stats?.git_commits || 0 }} 次</strong></div>
          <div class="stat-row" style="color: #909399; font-size: 12px">
            <span>路径</span><span>{{ p.path }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="projects.length === 0" style="text-align: center; padding: 60px; color: #909399">
      暂无项目，请先在设置中添加监听目录或手动添加项目
    </div>

    <!-- Add Project Dialog -->
    <el-dialog v-model="showAddDialog" title="添加项目" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="form.path" placeholder="项目路径" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="选择类型">
            <el-option label="Python" value="python" />
            <el-option label="Node.js" value="node" />
            <el-option label="Go" value="go" />
            <el-option label="Rust" value="rust" />
            <el-option label="Java" value="java" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Git 扫描">
          <el-switch v-model="form.enable_git" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getProjects, createProject, deleteProject, getProjectStats } from '../api/settings'
import { ElMessage, ElMessageBox } from 'element-plus'

const projects = ref<any[]>([])
const showAddDialog = ref(false)
const form = ref({ name: '', path: '', type: 'python', enable_git: true })

function formatDuration(seconds: number): string {
  if (!seconds) return '0m'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

async function loadData() {
  try {
    const res = await getProjects()
    const list = res.data
    // Load stats for each project
    for (const p of list) {
      try {
        const statsRes = await getProjectStats(p.name)
        p.stats = statsRes.data
      } catch {
        p.stats = {}
      }
    }
    projects.value = list
  } catch (e) {
    console.error(e)
  }
}

async function handleAdd() {
  if (!form.value.name || !form.value.path) {
    ElMessage.warning('请填写名称和路径')
    return
  }
  try {
    await createProject(form.value)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    form.value = { name: '', path: '', type: 'python', enable_git: true }
    loadData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  }
}

async function handleDelete(name: string) {
  try {
    await ElMessageBox.confirm(`确定删除项目 "${name}"？`, '提示', { type: 'warning' })
    await deleteProject(name)
    ElMessage.success('已删除')
    loadData()
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
  color: #606266;
}
</style>
