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
  //204 No Content
  if (res.status === 204) return null;
  return res.json();
}

//Assistants
export const assistantsApi = {
  list: () => request('/api/assistants'),
};

//Tasks
export const tasksApi = {
  list: () => request('/api/tasks'),
  get: (id) => request(`/api/tasks/${id}`),
};

//Evaluations
export const evaluationsApi = {
  /**
   * New evaluation run.
   * body: { task_id, assistant_ids: [], language, input_file?, db_host?, db_port?, db_user?, db_pass?, db_name? }
   */
  run: (body) =>
    request('/api/evaluations/run', { method: 'POST', body: JSON.stringify(body) }),

  /**this list all past evaluation runs */
  list: (taskId) =>
    request(taskId ? `/api/evaluations?task_id=${taskId}` : '/api/evaluations'),

  /**single evaluation run with full metrics */
  get: (runId) => request(`/api/evaluations/${runId}`),

  /** Get status of a running evaluation (poll this) */
  status: (runId) => request(`/api/evaluations/${runId}/status`),

  /** Download the report for a run */
  reportUrl: (runId, format = 'html') =>
    `${BASE_URL}/api/evaluations/${runId}/report?format=${format}`,
};

//Reports
export const reportsApi = {
  list: () => request('/api/reports'),
  get: (id) => request(`/api/reports/${id}`),
};

//Admin
export const adminApi = {
  getConfig: () => request('/api/admin/config'),
  updateConfig: (body) =>
    request('/api/admin/config', { method: 'PUT', body: JSON.stringify(body) }),
  getLogs: () => request('/api/admin/logs'),
  healthCheck: () => request('/api/health'),
};

//Auth
export const authApi = {
  login: (body) =>
    request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  me: () => request('/api/auth/me'),
};
