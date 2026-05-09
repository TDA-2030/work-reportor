import api from './request'

export function previewReport(data: { report_type: string; start_date: string; end_date: string }) {
  return api.post('/reports/preview', data)
}

export function generateReport(data: { report_type: string; start_date: string; end_date: string; style?: string }) {
  return api.post('/reports/generate', data)
}

export function generateAIReport(data: { report_type: string; start_date: string; end_date: string; style?: string; summary_data?: any }) {
  return api.post('/reports/generate-ai', data)
}

export function listReports() {
  return api.get('/reports/list')
}

export function getReport(type: string, filename: string) {
  return api.get(`/reports/${type}/${filename}`)
}
