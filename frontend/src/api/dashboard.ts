import api from './request'

export function getDashboardToday() {
  return api.get('/dashboard/today')
}

export function getDashboardWeek() {
  return api.get('/dashboard/week')
}
