const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => 'Unknown error');
    throw new Error(`API ${res.status}: ${text}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const tasksApi = {
  list: () => request('/api/tasks'),
  get: (id) => request(`/api/tasks/${id}`),
};

export const evaluationsApi = {
  run: (body) =>
    request('/api/evaluations/run', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  list: (taskId) =>
    request(taskId ? `/api/evaluations?task_id=${taskId}` : '/api/evaluations'),

  get: (runId) => request(`/api/evaluations/${runId}`),

  status: (runId) => request(`/api/evaluations/${runId}/status`),

  reportUrl: (runId, format = 'html') =>
    `${BASE_URL}/api/evaluations/${runId}/report?format=${format}`,
};

export const reportsApi = {
  list: () => request('/api/reports'),
  get: (id) => request(`/api/reports/${id}`),
};

export const adminApi = {
  getConfig: () => request('/api/admin/config'),
  updateConfig: (body) =>
    request('/api/admin/config', {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  getLogs: () => request('/api/admin/logs'),
  healthCheck: () => request('/api/health'),
};