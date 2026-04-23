import { useState, useEffect } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { Badge } from '../components/Card.jsx';
import { reportsApi, evaluationsApi } from '../api/client.js';
import './Page.css';
import './Reports.css';

const MOCK_REPORTS = [
  { id: 1, run_id: 1, task: 'Task A – Read Text File',          language: 'Python',     date: '2026-03-09', winner: 'ChatGPT',  assistants: 3, status: 'completed' },
  { id: 2, run_id: 2, task: 'Task C – Write Text File',         language: 'Python',     date: '2026-03-08', winner: 'Claude',   assistants: 3, status: 'completed' },
  { id: 3, run_id: 4, task: 'Task H – Password Auth (JS/PHP)',  language: 'JavaScript', date: '2026-03-06', winner: 'Gemini',   assistants: 3, status: 'completed' },
  { id: 4, run_id: 5, task: 'Task F – MySQL DB Query',          language: 'Python',     date: '2026-03-05', winner: 'Copilot', assistants: 3, status: 'completed' },
];

export default function Reports({ navigateTo }) {
  const [reports, setReports] = useState(MOCK_REPORTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.list()
      .then(data => { if (data?.reports) setReports(data.reports); })
      .catch(() => {}) // keep mock data
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Reports</h1>
          <p className="page-sub">Download and review all completed evaluation reports</p>
        </div>
      </div>

      {loading && <div className="text-muted text-sm">Loading reports…</div>}

      <div className="reports-grid">
        {reports.map(r => (
          <Card key={r.id} className="report-card">
            <div className="report-card-header">
              <div>
                <div className="report-task">{r.task}</div>
                <div className="report-meta">
                  <span className="chip">{r.language}</span>
                  <span className="text-xs text-muted">{r.date?.slice(0, 10)}</span>
                  <span className="text-xs text-muted">{r.assistants} assistants</span>
                </div>
              </div>
              <Badge color="green">{r.status}</Badge>
            </div>

            {r.winner && (
              <div className="report-winner">
                <span className="report-winner-label">Best Assistant</span>
                <span className="report-winner-name">🏆 {r.winner}</span>
              </div>
            )}

            <div className="report-actions">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateTo('results', r.run_id)}
              >
                View Results
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.open(evaluationsApi.reportUrl(r.run_id, 'html'), '_blank')}
              >
                ↓ HTML
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.open(evaluationsApi.reportUrl(r.run_id, 'pdf'), '_blank')}
              >
                ↓ PDF
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {reports.length === 0 && !loading && (
        <div className="empty-state">
          <h3>No reports yet</h3>
          <p>Run an evaluation to generate your first report.</p>
          <div style={{ marginTop: '1rem' }}>
            <Button onClick={() => navigateTo('tasks')}>Start Evaluation</Button>
          </div>
        </div>
      )}
    </div>
  );
}
