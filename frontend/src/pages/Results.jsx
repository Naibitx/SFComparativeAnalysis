import { useState, useEffect } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { Badge } from '../components/Card.jsx';
import { evaluationsApi } from '../api/client.js';
import './Page.css';
import './Results.css';

const METRIC_COLS = [
  {
    key: 'compile',
    label: 'Compiles',
    render: v => v ? <Badge color="green">✓ Yes</Badge> : <Badge color="red">✗ No</Badge>,
  },
  {
    key: 'correct',
    label: 'Correct',
    render: v => v ? <Badge color="green">✓ Yes</Badge> : <Badge color="red">✗ No</Badge>,
  },
  {
    key: 'warnings',
    label: 'Warnings',
    render: v => <Badge color={Number(v || 0) === 0 ? 'green' : 'yellow'}>{Number(v || 0)}</Badge>,
  },
  {
    key: 'time_ms',
    label: 'Time (ms)',
    render: v => v != null ? <span className="mono">{String(v)}</span> : '—',
  },
  {
    key: 'memory_mb',
    label: 'Memory (MB)',
    render: v => v != null ? <span className="mono">{String(v)}</span> : '—',
  },
  {
    key: 'readability',
    label: 'Readability',
    render: v => <ReadBar value={v} />,
  },
  {
    key: 'security',
    label: 'Vulns',
    render: v => <Badge color={Number(v || 0) === 0 ? 'green' : 'red'}>{Number(v || 0)}</Badge>,
  },
  {
    key: 'score',
    label: 'Score',
    render: v => <ScoreBar value={v} />,
  },
];

function safeText(value, fallback = '—') {
  if (value == null) return fallback;
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  if (typeof value === 'object') {
    return value.name || value.label || value.id || fallback;
  }
  return fallback;
}

function normalizeAssistant(a, index) {
  return {
    id: safeText(a?.id, `assistant-${index}`),
    name: safeText(a?.name, `Assistant ${index + 1}`),
    status: safeText(a?.status, 'completed'),
    compile: Boolean(a?.compile),
    correct: Boolean(a?.correct),
    warnings: Number(a?.warnings || 0),
    time_ms: a?.time_ms ?? null,
    memory_mb: a?.memory_mb ?? null,
    readability: a?.readability ?? null,
    security: Number(a?.security || 0),
    score: a?.score ?? null,
    code: typeof a?.code === 'string' ? a.code : '',
    output: typeof a?.output === 'string' ? a.output : '',
    error: typeof a?.error === 'string' ? a.error : '',
  };
}

function normalizeResult(data) {
  const assistants = Array.isArray(data?.assistants)
    ? data.assistants.map(normalizeAssistant)
    : [];

  return {
    ...data,
    task: safeText(data?.task, 'Unknown Task'),
    language: safeText(data?.language, 'Python'),
    winner: safeText(data?.winner, 'Unknown'),
    winner_score: data?.winner_score ?? null,
    winner_justification: safeText(
      data?.winner_justification,
      'Evaluation completed. Detailed explanation is not available yet.'
    ),
    assistants,
  };
}

function ReadBar({ value }) {
  if (value == null || Number.isNaN(Number(value))) return <span className="mono">—</span>;

  const numeric = Number(value);
  const color = numeric >= 80 ? 'var(--green)' : numeric >= 60 ? 'var(--yellow)' : 'var(--red)';

  return (
    <div className="bar-wrap">
      <div className="bar-fill" style={{ width: `${numeric}%`, background: color }} />
      <span className="bar-label">{numeric}</span>
    </div>
  );
}

function ScoreBar({ value }) {
  if (value == null || Number.isNaN(Number(value))) return <span className="mono">—</span>;

  const numeric = Number(value);
  const pct = Math.round(numeric * 100);
  const color = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--yellow)' : 'var(--red)';

  return (
    <div className="bar-wrap">
      <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      <span className="bar-label">{numeric.toFixed(2)}</span>
    </div>
  );
}

export default function Results({ navigateTo, activeRunId }) {
  const [result, setResult] = useState(null);
  const [activeCode, setActiveCode] = useState(null);
  const [tab, setTab] = useState('comparison');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!activeRunId) return;

    setError('');

    evaluationsApi.get(activeRunId)
      .then(data => {
        const normalized = normalizeResult(data);
        setResult(normalized);

        if (normalized.assistants.length > 0) {
          setActiveCode(normalized.assistants[0].id);
        }
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setResult(null);
      });
  }, [activeRunId]);

  if (error) {
    return (
      <div className="page animate-in">
        <h1 className="page-title">Results</h1>
        <p className="page-sub">Could not load results from backend.</p>
        <div className="error-box">{error}</div>
        <Button onClick={() => navigateTo('tasks')}>Back to Tasks</Button>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="page animate-in">
        <h1 className="page-title">Results</h1>
        <p className="page-sub">Loading results from backend...</p>
      </div>
    );
  }

  const r = result;

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Results</h1>
          <p className="page-sub">{r.task} · {r.language}</p>
        </div>

        <div className="header-actions">
          <Button variant="ghost" onClick={() => navigateTo('reports')}>
            View Reports
          </Button>

          <Button onClick={() => window.open(evaluationsApi.reportUrl(activeRunId, 'html'), '_blank')}>
            Export HTML →
          </Button>
        </div>
      </div>

      <div className="winner-banner animate-in">
        <div className="winner-left">
          <span className="winner-trophy">🏆</span>

          <div>
            <div className="winner-label">Best Assistant for this Task</div>
            <div className="winner-name">{r.winner}</div>
          </div>

          <div className="winner-score">
            <span className="score-num">
              {r.winner_score != null ? (Number(r.winner_score) * 100).toFixed(0) : '—'}
            </span>
            <span className="score-unit">/100</span>
          </div>
        </div>

        <p className="winner-justification">{r.winner_justification}</p>
      </div>

      <div className="result-tabs">
        {['comparison', 'code'].map(t => (
          <button
            key={t}
            className={`result-tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
            type="button"
          >
            {t === 'comparison' ? '◫ Comparison Table' : '⌨ Generated Code'}
          </button>
        ))}
      </div>

      {tab === 'comparison' && (
        <Card className="table-card animate-in">
          <div className="table-wrapper">
            <table className="data-table results-table">
              <thead>
                <tr>
                  <th>Assistant</th>
                  {METRIC_COLS.map(c => (
                    <th key={c.key}>{c.label}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {r.assistants.map((a, index) => (
                  <tr key={`${a.id}-${index}`} className={a.name === r.winner ? 'winner-row' : ''}>
                    <td>
                      <div className="flex items-center gap-1">
                        {a.name === r.winner && <span className="row-trophy">🏆</span>}
                        <span className="font-weight-600">{a.name}</span>
                      </div>
                    </td>

                    {METRIC_COLS.map(c => (
                      <td key={`${a.id}-${c.key}`}>{c.render(a[c.key])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {tab === 'code' && (
        <div className="code-section animate-in">
          <div className="code-tabs">
            {r.assistants.map((a, index) => (
              <button
                key={`${a.id}-tab-${index}`}
                className={`code-tab ${activeCode === a.id ? 'active' : ''} ${!a.compile ? 'failed' : ''}`}
                onClick={() => setActiveCode(a.id)}
                type="button"
              >
                {a.name}
                {!a.compile && <span className="tab-fail-mark">✗</span>}
                {a.name === r.winner && <span className="tab-win-mark">🏆</span>}
              </button>
            ))}
          </div>

          {r.assistants.map((a, index) => {
            if (activeCode !== a.id) return null;

            return (
              <Card key={`${a.id}-code-${index}`} className="code-card">
                <div className="code-card-header">
                  <span className="section-title">{a.name}</span>

                  <div className="flex gap-1">
                    {a.compile ? <Badge color="green">Compiles</Badge> : <Badge color="red">Compile Failed</Badge>}
                    {a.correct ? <Badge color="green">Correct</Badge> : <Badge color="red">Incorrect</Badge>}
                    <Badge color={a.security === 0 ? 'green' : 'red'}>{a.security} vulns</Badge>
                  </div>
                </div>

                <pre className="code-block">{a.code || 'No generated code saved for this assistant.'}</pre>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
