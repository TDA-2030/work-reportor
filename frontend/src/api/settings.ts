import api from './request'

export function getSettings() {
  return api.get('/settings')
}

export function updateSettings(data: any) {
  return api.put('/settings', data)
}

export function addWatchDir(path: string) {
  return api.post('/settings/watch-dirs', { path })
}

export function removeWatchDir(path: string) {
  return api.delete('/settings/watch-dirs', { params: { path } })
}

export function addIgnoreRule(data: { rule_type: string; pattern: string }) {
  return api.post('/settings/ignore-rules', data)
}

export function deleteIgnoreRule(id: number) {
  return api.delete(`/settings/ignore-rules/${id}`)
}

export function updateAISettings(data: any) {
  return api.put('/settings/ai', data)
}

export function getProjects() {
  return api.get('/projects')
}

export function createProject(data: { name: string; path: string; type?: string; enable_git?: boolean }) {
  return api.post('/projects', data)
}

export function deleteProject(name: string) {
  return api.delete(`/projects/${name}`)
}

export function getProjectStats(name: string) {
  return api.get(`/projects/${name}/stats`)
}
