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

// Fallback mock data so the UI looks good even without a running backend
const MOCK_STATS = { completed: 12, reports: 8, failed: 3 };
const MOCK_RUNS = [
  { id: 1, task_id: 'a', assistants: ['Copilot', 'ChatGPT', 'Claude'], date: '2026-03-09', status: 'completed', winner: 'ChatGPT' },
  { id: 2, task_id: 'c', assistants: ['Gemini', 'Claude', 'Grok'],     date: '2026-03-08', status: 'completed', winner: 'Claude' },
  { id: 3, task_id: 'e', assistants: ['Copilot', 'ChatGPT'],           date: '2026-03-07', status: 'failed',    winner: null },
  { id: 4, task_id: 'h', assistants: ['ChatGPT', 'Gemini', 'Grok'],   date: '2026-03-06', status: 'completed', winner: 'Gemini' },
  { id: 5, task_id: 'f', assistants: ['Claude', 'Copilot', 'Grok'],   date: '2026-03-05', status: 'completed', winner: 'Copilot' },
];

export default function Dashboard({ navigateTo }) {
  const [runs, setRuns] = useState(MOCK_RUNS);
  const [stats, setStats] = useState(MOCK_STATS);
  const [backendOk, setBackendOk] = useState(null);

  useEffect(() => {
    adminApi.healthCheck()
      .then(() => {
        setBackendOk(true);
        return evaluationsApi.list();
      })
      .then(data => {
        if (data?.runs) {
          setRuns(data.runs);
          setStats({
            completed: data.runs.filter(r => r.status === 'completed').length,
            failed: data.runs.filter(r => r.status === 'failed').length,
            reports: data.runs.filter(r => r.status === 'completed').length,
          });
        }
      })
      .catch(() => setBackendOk(false));
  }, []);

  return (
    <div className="page animate-in">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-sub">Comparative Analysis Framework for AI-Based Coding Assistants</p>
        </div>
        <div className="header-actions">
          <div className={`backend-pill ${backendOk === null ? 'unknown' : backendOk ? 'ok' : 'err'}`}>
            <span className="status-dot" />
            {backendOk === null ? 'Checking backend…' : backendOk ? 'Backend online' : 'Backend offline (mock data)'}
          </div>
          <Button onClick={() => navigateTo('tasks')}>
            ▷ &nbsp;Start New Evaluation
          </Button>
        </div>
      </div>

      {/* Hero banner */}
      <div className="dashboard-hero">
        <div className="hero-content">
          <h2>Welcome to the Analysis Framework</h2>
          <p>Compare multiple AI coding assistants across benchmark tasks. Evaluate correctness, security, quality, and performance metrics across eight programming tasks (a–h).</p>
        </div>
        <div className="hero-grid">
          {['ChatGPT', 'Copilot', 'Gemini', 'Claude', 'Grok'].map((a, i) => (
            <span key={a} className="hero-pill" style={{ animationDelay: `${i * 60}ms` }}>{a}</span>
          ))}
        </div>
      </div>

      {/* Stat cards */}
      <div className="stats-row">
        <StatCard label="Completed Runs"   value={stats.completed} accent="green"  sub="Evaluation sessions finished" />
        <StatCard label="Generated Reports" value={stats.reports}   accent="blue"   sub="Downloadable comparison reports" />
        <StatCard label="Failed Runs"       value={stats.failed}    accent="red"    sub="Runs with errors or timeouts" />
        <StatCard label="AI Assistants"     value={5}               sub="ChatGPT · Copilot · Gemini · Claude · Grok" />
      </div>

      {/* Recent runs table */}
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
              {runs.map(run => (
                <tr key={run.id}>
                  <td>
                    <span className="task-tag">Task {run.task_id?.toUpperCase()}</span>
                    <span className="task-name">{TASK_LABELS[run.task_id] || run.task_id}</span>
                  </td>
                  <td>
                    <div className="assistant-chips">
                      {(run.assistants || []).map(a => (
                        <span key={a} className="chip">{a}</span>
                      ))}
                    </div>
                  </td>
                  <td className="text-muted text-sm">{run.date?.slice(0, 10)}</td>
                  <td>
                    <Badge color={STATUS_COLOR[run.status] || 'default'}>
                      {run.status}
                    </Badge>
                  </td>
                  <td>
                    {run.winner
                      ? <span className="winner-badge">🏆 {run.winner}</span>
                      : <span className="text-muted">—</span>}
                  </td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={() => navigateTo('results', run.id)}
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

      {/* Quick task grid */}
      <div className="quick-section">
        <h2 className="section-title" style={{ marginBottom: '1rem' }}>Benchmark Tasks</h2>
        <div className="task-quick-grid">
          {Object.entries(TASK_LABELS).map(([id, label]) => (
            <button
              key={id}
              className="task-quick-card"
              onClick={() => navigateTo('tasks')}
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
