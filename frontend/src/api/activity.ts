import api from './request'

export function getTimeline(date?: string, project?: string, category?: string) {
  return api.get('/activity/timeline', { params: { date, project, category } })
}

export function getFiles(params: { date?: string; project?: string; file_ext?: string; page?: number; page_size?: number }) {
  return api.get('/activity/files', { params })
}

export function getWindows(date?: string) {
  return api.get('/activity/windows', { params: { date } })
}
