import { useState, useEffect } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { Badge } from '../components/Card.jsx';
import { evaluationsApi } from '../api/client.js';
import './Page.css';
import './Results.css';

const MOCK_RESULT = {
  run_id: 'mock-run-1',
  task: 'Task A – Read Text File',
  language: 'Python',
  winner: 'ChatGPT',
  winner_score: 0.91,
  winner_justification:
    'ChatGPT produced the most concise correct solution with zero warnings, the fastest execution time (98ms), and no security findings. GitHub Copilot was a close second but had a slightly higher readability score offset by a minor warning.',
  assistants: [
    {
      id: 'copilot', name: 'GitHub Copilot', compile: true, correct: true,
      warnings: 0, time_ms: 142, memory_mb: 18.2, readability: 82, security: 0, score: 0.88,
      code: `# GitHub Copilot — Task A
with open("input.txt", "r") as f:
    data = f.read()
print(data)`,
    },
    {
      id: 'chatgpt', name: 'ChatGPT', compile: true, correct: true,
      warnings: 1, time_ms: 98, memory_mb: 15.1, readability: 89, security: 0, score: 0.91,
      code: `# ChatGPT — Task A
import sys

def read_file(path: str) -> str:
    """Read and return file contents."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

if __name__ == "__main__":
    print(read_file(sys.argv[1]))`,
    },
    {
      id: 'gemini', name: 'Google Gemini', compile: false, correct: false,
      warnings: 2, time_ms: null, memory_mb: null, readability: 54, security: 1, score: 0.22,
      code: `# Google Gemini — Task A (compile failed)
def readFile(path)
    f = open(path
    return f.read()`,
    },
    {
      id: 'claude', name: 'Anthropic Claude', compile: true, correct: true,
      warnings: 0, time_ms: 115, memory_mb: 16.4, readability: 91, security: 0, score: 0.89,
      code: `# Anthropic Claude — Task A
from pathlib import Path

def read_text_file(file_path: str) -> str:
    """
    Read data from a text file and return its contents.
    Args:
        file_path: Path to the text file
    Returns:
        File contents as a string
    """
    return Path(file_path).read_text(encoding="utf-8")

if __name__ == "__main__":
    import sys
    print(read_text_file(sys.argv[1]))`,
    },
    {
      id: 'grok', name: 'Grok', compile: false, correct: false,
      warnings: 0, time_ms: null, memory_mb: null, readability: 60, security: 0, score: 0.20,
      code: `# Grok — Task A (compile failed)
import nonexistent_module
with open("input.txt") as f:
    print(f.read())`,
    },
  ],
};

const METRIC_COLS = [
  { key: 'compile',     label: 'Compiles',     render: v => v ? <Badge color="green">✓ Yes</Badge> : <Badge color="red">✗ No</Badge> },
  { key: 'correct',     label: 'Correct',      render: v => v ? <Badge color="green">✓ Yes</Badge> : <Badge color="red">✗ No</Badge> },
  { key: 'warnings',    label: 'Warnings',     render: v => <Badge color={v === 0 ? 'green' : 'yellow'}>{v}</Badge> },
  { key: 'time_ms',     label: 'Time (ms)',    render: v => v != null ? <span className="mono">{v}</span> : '—' },
  { key: 'memory_mb',   label: 'Memory (MB)',  render: v => v != null ? <span className="mono">{v}</span> : '—' },
  { key: 'readability', label: 'Readability',  render: v => <ReadBar value={v} /> },
  { key: 'security',    label: 'Vulns',        render: v => <Badge color={v === 0 ? 'green' : 'red'}>{v}</Badge> },
  { key: 'score',       label: 'Score',        render: v => <ScoreBar value={v} /> },
];

function ReadBar({ value }) {
  if (value == null) return <span className="mono">—</span>;

  const color = value >= 80 ? 'var(--green)' : value >= 60 ? 'var(--yellow)' : 'var(--red)';

  return (
    <div className="bar-wrap">
      <div className="bar-fill" style={{ width: `${value}%`, background: color }} />
      <span className="bar-label">{value}</span>
    </div>
  );
}

function ScoreBar({ value }) {
  if (value == null) return <span className="mono">—</span>;

  const pct = Math.round(value * 100);
  const color = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--yellow)' : 'var(--red)';

  return (
    <div className="bar-wrap">
      <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      <span className="bar-label">{Number(value).toFixed(2)}</span>
    </div>
  );
}

export default function Results({ navigateTo, activeRunId }) {
  const [result, setResult] = useState(null);
  const [activeCode, setActiveCode] = useState(null);
  const [tab, setTab] = useState('comparison');

  useEffect(() => {
    if (!activeRunId) return;
    evaluationsApi.get(activeRunId)
      .then(data => setResult(data))
      .catch(err => {
        console.error(err);
        setResult(null);
      });
  }, [activeRunId]);

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
          <Button variant="ghost" onClick={() => navigateTo('reports')}>View Reports</Button>
          <Button onClick={() => window.open(evaluationsApi.reportUrl(activeRunId || 'mock', 'html'), '_blank')}>
            Export HTML →
          </Button>
        </div>
      </div>

      {/* Winner banner */}
      <div className="winner-banner animate-in">
        <div className="winner-left">
          <span className="winner-trophy">🏆</span>
          <div>
            <div className="winner-label">Best Assistant for this Task</div>
            <div className="winner-name">{r.winner}</div>
          </div>
          <div className="winner-score">
            <span className="score-num">
              {r.winner_score != null ? (r.winner_score * 100).toFixed(0) : '—'}
            </span>
            <span className="score-unit">/100</span>
          </div>
        </div>
        <p className="winner-justification">{r.winner_justification}</p>
      </div>

      {/* Tabs */}
      <div className="result-tabs">
        {['comparison', 'code'].map(t => (
          <button key={t} className={`result-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
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
                  {METRIC_COLS.map(c => <th key={c.key}>{c.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {r.assistants?.map(a => (
                  <tr key={a.id} className={a.name === r.winner ? 'winner-row' : ''}>
                    <td>
                      <div className="flex items-center gap-1">
                        {a.name === r.winner && <span className="row-trophy">🏆</span>}
                        <span className="font-weight-600">{a.name}</span>
                      </div>
                    </td>
                    {METRIC_COLS.map(c => (
                      <td key={c.key}>{c.render(a[c.key])}</td>
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
            {r.assistants?.map(a => (
              <button
                key={a.id}
                className={`code-tab ${activeCode === a.id || (!activeCode && a.id === r.assistants[0]?.id) ? 'active' : ''} ${!a.compile ? 'failed' : ''}`}
                onClick={() => setActiveCode(a.id)}
              >
                {a.name}
                {!a.compile && <span className="tab-fail-mark">✗</span>}
                {a.name === r.winner && <span className="tab-win-mark">🏆</span>}
              </button>
            ))}
          </div>
          {r.assistants?.map(a => {
            const active = activeCode === a.id || (!activeCode && a.id === r.assistants[0]?.id);
            if (!active) return null;
            return (
              <Card key={a.id} className="code-card">
                <div className="code-card-header">
                  <span className="section-title">{a.name}</span>
                  <div className="flex gap-1">
                    {a.compile ? <Badge color="green">Compiles</Badge> : <Badge color="red">Compile Failed</Badge>}
                    {a.correct ? <Badge color="green">Correct</Badge> : <Badge color="red">Incorrect</Badge>}
                    <Badge color={a.security === 0 ? 'green' : 'red'}>{a.security} vulns</Badge>
                  </div>
                </div>
                <pre className="code-block">{a.code}</pre>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
