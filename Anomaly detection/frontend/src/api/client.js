import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export async function fetchDashboard() {
  const { data } = await api.get('/dashboard');
  return data;
}

export async function detectEvent(params) {
  const { data } = await api.post('/detect', params);
  return data;
}

export async function fetchModelComparison() {
  const { data } = await api.get('/models/comparison');
  return data;
}

export async function fetchPerformance() {
  const { data } = await api.get('/performance');
  return data;
}

export async function fetchAlerts({ severity, attackType, department } = {}) {
  const params = new URLSearchParams();
  if (severity?.length) params.set('severity', severity.join(','));
  if (attackType?.length) params.set('attack_type', attackType.join(','));
  if (department?.length) params.set('department', department.join(','));
  const { data } = await api.get(`/alerts?${params.toString()}`);
  return data;
}

export default api;
