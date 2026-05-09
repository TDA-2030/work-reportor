<template>
  <div>
    <h2 style="margin-bottom: 20px">设置</h2>

    <el-tabs>
      <!-- Watch Dirs -->
      <el-tab-pane label="监听目录">
        <el-card shadow="hover">
          <div style="display: flex; gap: 8px; margin-bottom: 16px">
            <el-input v-model="newWatchDir" placeholder="输入目录路径，如 D:/Projects" />
            <el-button type="primary" @click="handleAddWatchDir">添加</el-button>
          </div>
          <el-table :data="watchDirs" stripe>
            <el-table-column prop="path" label="路径" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" text @click="handleRemoveWatchDir(row.path)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="watchDirs.length === 0" style="color: #909399; text-align: center; padding: 20px">
            未添加监听目录
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Projects -->
      <el-tab-pane label="项目规则">
        <el-card shadow="hover">
          <div style="margin-bottom: 16px">
            <el-button type="primary" @click="showProjectDialog = true">添加项目</el-button>
          </div>
          <el-table :data="projects" stripe>
            <el-table-column prop="name" label="名称" width="160" />
            <el-table-column prop="path" label="路径" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column label="Git" width="80">
              <template #default="{ row }">
                <el-tag :type="row.enable_git ? 'success' : 'info'" size="small">
                  {{ row.enable_git ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" text @click="handleDeleteProject(row.name)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Ignore Rules -->
      <el-tab-pane label="忽略规则">
        <el-card shadow="hover">
          <div style="display: flex; gap: 8px; margin-bottom: 16px">
            <el-select v-model="newRule.rule_type" style="width: 130px">
              <el-option label="目录" value="dir" />
              <el-option label="扩展名" value="extension" />
              <el-option label="关键词" value="keyword" />
            </el-select>
            <el-input v-model="newRule.pattern" placeholder="匹配模式" />
            <el-button type="primary" @click="handleAddRule">添加</el-button>
          </div>
          <el-table :data="ignoreRules" stripe>
            <el-table-column prop="rule_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ { dir: '目录', extension: '扩展名', keyword: '关键词' }[row.rule_type] || row.rule_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pattern" label="模式" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" text @click="handleDeleteRule(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- AI Settings -->
      <el-tab-pane label="AI 设置">
        <el-card shadow="hover">
          <el-form :model="aiForm" label-width="100px" style="max-width: 500px">
            <el-form-item label="API Key">
              <el-input v-model="aiForm.api_key" type="password" show-password placeholder="sk-..." />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="aiForm.base_url" placeholder="留空使用默认，或填入自定义地址" />
            </el-form-item>
            <el-form-item label="模型">
              <el-input v-model="aiForm.model" placeholder="gpt-4o-mini" />
            </el-form-item>
            <el-form-item label="语言">
              <el-select v-model="aiForm.language">
                <el-option label="中文" value="zh" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>
            <el-form-item label="风格">
              <el-select v-model="aiForm.style">
                <el-option label="正式" value="formal" />
                <el-option label="简洁" value="brief" />
                <el-option label="技术" value="technical" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAISettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- Add Project Dialog -->
    <el-dialog v-model="showProjectDialog" title="添加项目" width="500px">
      <el-form :model="projectForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="projectForm.name" />
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="projectForm.path" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="projectForm.type">
            <el-option label="Python" value="python" />
            <el-option label="Node.js" value="node" />
            <el-option label="Go" value="go" />
            <el-option label="Rust" value="rust" />
            <el-option label="Java" value="java" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Git 扫描">
          <el-switch v-model="projectForm.enable_git" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProjectDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getSettings, addWatchDir, removeWatchDir,
  addIgnoreRule, deleteIgnoreRule, updateAISettings,
  getProjects, createProject, deleteProject,
} from '../api/settings'
import { ElMessage, ElMessageBox } from 'element-plus'

const watchDirs = ref<{ path: string }[]>([])
const newWatchDir = ref('')
const ignoreRules = ref<any[]>([])
const newRule = ref({ rule_type: 'dir', pattern: '' })
const projects = ref<any[]>([])
const showProjectDialog = ref(false)
const projectForm = ref({ name: '', path: '', type: 'python', enable_git: true })
const aiForm = ref({ api_key: '', base_url: '', model: 'gpt-4o-mini', language: 'zh', style: 'formal' })

async function loadSettings() {
  try {
    const res = await getSettings()
    const config = res.data.config || {}
    watchDirs.value = (config.watch_dirs || []).map((p: string) => ({ path: p }))
    ignoreRules.value = res.data.ignore_rules || []
    const ai = config.ai || {}
    aiForm.value = {
      api_key: ai.api_key || '',
      base_url: ai.base_url || '',
      model: ai.model || 'gpt-4o-mini',
      language: ai.language || 'zh',
      style: ai.style || 'formal',
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadProjects() {
  try {
    const res = await getProjects()
    projects.value = res.data
  } catch {}
}

async function handleAddWatchDir() {
  if (!newWatchDir.value) return
  try {
    await addWatchDir(newWatchDir.value)
    ElMessage.success('添加成功')
    newWatchDir.value = ''
    loadSettings()
  } catch {
    ElMessage.error('添加失败')
  }
}

async function handleRemoveWatchDir(path: string) {
  try {
    await removeWatchDir(path)
    ElMessage.success('已删除')
    loadSettings()
  } catch {}
}

async function handleAddRule() {
  if (!newRule.value.pattern) return
  try {
    await addIgnoreRule(newRule.value)
    ElMessage.success('添加成功')
    newRule.value = { rule_type: 'dir', pattern: '' }
    loadSettings()
  } catch {
    ElMessage.error('添加失败')
  }
}

async function handleDeleteRule(id: number) {
  try {
    await deleteIgnoreRule(id)
    ElMessage.success('已删除')
    loadSettings()
  } catch {}
}

async function handleAddProject() {
  if (!projectForm.value.name || !projectForm.value.path) {
    ElMessage.warning('请填写名称和路径')
    return
  }
  try {
    await createProject(projectForm.value)
    ElMessage.success('添加成功')
    showProjectDialog.value = false
    projectForm.value = { name: '', path: '', type: 'python', enable_git: true }
    loadProjects()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  }
}

async function handleDeleteProject(name: string) {
  try {
    await ElMessageBox.confirm(`确定删除项目 "${name}"？`, '提示', { type: 'warning' })
    await deleteProject(name)
    ElMessage.success('已删除')
    loadProjects()
  } catch {}
}

async function saveAISettings() {
  try {
    await updateAISettings(aiForm.value)
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadSettings()
  loadProjects()
})
</script>
