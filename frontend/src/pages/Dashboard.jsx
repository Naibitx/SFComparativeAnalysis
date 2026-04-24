import { useState, useEffect } from 'react';
import Card, { StatCard, Badge } from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { evaluationsApi, adminApi } from '../api/client.js';
import './Page.css';
import './Dashboard.css';

const TASK_LABELS = {
  a: 'Read Text File',
  b: 'Read JSON (threads)',
  c: 'Write Text File',
  d: 'Write JSON (threads)',
  e: 'Produce ZIP Archive',
  f: 'MySQL DB Query',
  g: 'MongoDB DB Query',
  h: 'Auth (JS/PHP)',
};

const STATUS_COLOR = {
  completed: 'green',
  failed: 'red',
  running: 'blue',
  queued: 'yellow',
};

function safeText(value, fallback = '—') {
  if (value == null) return fallback;

  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return String(value);
  }

  if (typeof value === 'object') {
    return value.name || value.label || value.id || fallback;
  }

  return fallback;
}

function normalizeRun(run, index) {
  const assistants = Array.isArray(run?.assistants)
    ? run.assistants.map((a, i) => ({
        id: safeText(a?.id ?? a, `assistant-${i}`),
        name: safeText(a?.name ?? a, `Assistant ${i + 1}`),
      }))
    : [];

  return {
    id: safeText(run?.id ?? run?.run_id, `run-${index}`),
    run_id: safeText(run?.run_id ?? run?.id, `run-${index}`),
    task_id: safeText(run?.task_id, ''),
    task: safeText(run?.task, ''),
    assistants,
    date: safeText(run?.date, ''),
    status: safeText(run?.status, 'completed'),
    winner: safeText(run?.winner, ''),
  };
}

export default function Dashboard({ navigateTo }) {
  const [runs, setRuns] = useState([]);
  const [stats, setStats] = useState({
    completed: 0,
    reports: 0,
    failed: 0,
  });
  const [backendOk, setBackendOk] = useState(null);

  useEffect(() => {
    adminApi.healthCheck()
      .then(() => {
        setBackendOk(true);
        return evaluationsApi.list();
      })
      .then(data => {
        const normalizedRuns = Array.isArray(data?.runs)
          ? data.runs.map(normalizeRun)
          : [];

        setRuns(normalizedRuns);

        setStats({
          completed: normalizedRuns.filter(r => r.status === 'completed').length,
          failed: normalizedRuns.filter(r => r.status === 'failed').length,
          reports: normalizedRuns.filter(r => r.status === 'completed').length,
        });
      })
      .catch(err => {
        console.error(err);
        setBackendOk(false);
        setRuns([]);
        setStats({
          completed: 0,
          reports: 0,
          failed: 0,
        });
      });
  }, []);

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-sub">
            Comparative Analysis Framework for AI-Based Coding Assistants
          </p>
        </div>

        <div className="header-actions">
          <div className={`backend-pill ${backendOk === null ? 'unknown' : backendOk ? 'ok' : 'err'}`}>
            <span className="status-dot" />
            {backendOk === null
              ? 'Checking backend…'
              : backendOk
                ? 'Backend online'
                : 'Backend offline'}
          </div>

          <Button onClick={() => navigateTo('tasks')}>
            ▷ &nbsp;Start New Evaluation
          </Button>
        </div>
      </div>

      <div className="dashboard-hero">
        <div className="hero-content">
          <h2>Welcome to the Analysis Framework</h2>
          <p>
            Compare multiple AI coding assistants across benchmark tasks.
            Evaluate correctness, security, quality, and performance metrics
            across eight programming tasks.
          </p>
        </div>

        <div className="hero-grid">
          {['ChatGPT', 'Copilot', 'Gemini', 'Claude', 'Grok'].map((a, i) => (
            <span
              key={a}
              className="hero-pill"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              {a}
            </span>
          ))}
        </div>
      </div>

      <div className="stats-row">
        <StatCard
          label="Completed Runs"
          value={stats.completed}
          accent="green"
          sub="Evaluation sessions finished"
        />

        <StatCard
          label="Generated Reports"
          value={stats.reports}
          accent="blue"
          sub="Downloadable comparison reports"
        />

        <StatCard
          label="Failed Runs"
          value={stats.failed}
          accent="red"
          sub="Runs with errors or timeouts"
        />

        <StatCard
          label="AI Assistants"
          value={5}
          sub="ChatGPT · Copilot · Gemini · Claude · Grok"
        />
      </div>

      <Card className="table-card">
        <div className="table-header">
          <h2 className="section-title">Recent Evaluation Runs</h2>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Assistants</th>
                <th>Date</th>
                <th>Status</th>
                <th>Winner</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {runs.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-muted text-sm">
                    No saved evaluation runs yet. Start a new evaluation to populate this table.
                  </td>
                </tr>
              )}

              {runs.map((run, index) => (
                <tr key={`${run.id}-${index}`}>
                  <td>
                    <span className="task-tag">
                      {run.task_id ? `Task ${run.task_id.toUpperCase()}` : 'Task'}
                    </span>

                    <span className="task-name">
                      {run.task || TASK_LABELS[run.task_id] || run.task_id || 'Unknown Task'}
                    </span>
                  </td>

                  <td>
                    <div className="assistant-chips">
                      {run.assistants.map((a, i) => (
                        <span key={`${a.id}-${i}`} className="chip">
                          {a.name}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td className="text-muted text-sm">
                    {run.date ? run.date.slice(0, 10) : '—'}
                  </td>

                  <td>
                    <Badge color={STATUS_COLOR[run.status] || 'default'}>
                      {run.status}
                    </Badge>
                  </td>

                  <td>
                    {run.winner ? (
                      <span className="winner-badge">🏆 {run.winner}</span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>

                  <td>
                    <button
                      className="view-btn"
                      onClick={() => navigateTo('results', run.run_id)}
                      type="button"
                    >
                      View Results →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="quick-section">
        <h2 className="section-title" style={{ marginBottom: '1rem' }}>
          Benchmark Tasks
        </h2>

        <div className="task-quick-grid">
          {Object.entries(TASK_LABELS).map(([id, label]) => (
            <button
              key={id}
              className="task-quick-card"
              onClick={() => navigateTo('tasks')}
              type="button"
            >
              <span className="task-quick-id">Task {id.toUpperCase()}</span>
              <span className="task-quick-label">{label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}