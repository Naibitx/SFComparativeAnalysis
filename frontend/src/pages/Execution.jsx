import { useState, useEffect, useRef } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { Badge } from '../components/Card.jsx';
import { evaluationsApi } from '../api/client.js';
import './Page.css';
import './Execution.css';

const MOCK_STATUS = {
  run_id: 'mock-run-1',
  task: 'Task A – Read Text File',
  language: 'Python',
  overall_status: 'completed',
  assistants: [
    { id: 'copilot',  name: 'GitHub Copilot',   status: 'completed', progress: 100, compile: true,  correct: true,  warnings: 0, time_ms: 142 },
    { id: 'chatgpt',  name: 'ChatGPT',           status: 'completed', progress: 100, compile: true,  correct: true,  warnings: 1, time_ms: 98  },
    { id: 'gemini',   name: 'Google Gemini',     status: 'completed', progress: 100, compile: false, correct: false, warnings: 2, time_ms: null },
    { id: 'claude',   name: 'Anthropic Claude',  status: 'completed', progress: 100, compile: true,  correct: true,  warnings: 0, time_ms: 115 },
    { id: 'grok',     name: 'Grok',              status: 'failed',    progress: 100, compile: false, correct: false, warnings: 0, time_ms: null },
  ],
};

const MOCK_LOGS = [
  '[00:00.00] Evaluation started — Task A · Python',
  '[00:00.12] Prompt dispatched to: GitHub Copilot',
  '[00:00.14] Prompt dispatched to: ChatGPT',
  '[00:00.15] Prompt dispatched to: Google Gemini',
  '[00:00.16] Prompt dispatched to: Anthropic Claude',
  '[00:00.17] Prompt dispatched to: Grok',
  '[00:01.03] GitHub Copilot → code received (84 lines)',
  '[00:01.22] ChatGPT → code received (61 lines)',
  '[00:01.45] Google Gemini → code received (102 lines)',
  '[00:01.51] Anthropic Claude → code received (73 lines)',
  '[00:01.88] Grok → code received (55 lines)',
  '[00:02.10] Compiling GitHub Copilot code… ✓ success (0 errors, 0 warnings)',
  '[00:02.14] Compiling ChatGPT code… ✓ success (0 errors, 1 warning)',
  '[00:02.18] Compiling Google Gemini code… ✗ FAILED — SyntaxError on line 34',
  '[00:02.23] Compiling Anthropic Claude code… ✓ success (0 errors, 0 warnings)',
  '[00:02.27] Compiling Grok code… ✗ FAILED — ImportError: module not found',
  '[00:02.50] Executing GitHub Copilot code in sandbox… ✓ correct (142ms)',
  '[00:02.54] Executing ChatGPT code in sandbox… ✓ correct (98ms)',
  '[00:02.60] Executing Anthropic Claude code in sandbox… ✓ correct (115ms)',
  '[00:02.80] Running Semgrep security scan on 3 passing files…',
  '[00:03.10] Security scan complete — 0 critical, 1 medium, 0 low',
  '[00:03.15] Readability scoring complete',
  '[00:03.20] Metrics saved to database',
  '[00:03.22] ✓ Evaluation complete — winner: ChatGPT (score 0.91)',
];

const STATUS_COLOR = { completed: 'green', running: 'blue', queued: 'yellow', failed: 'red' };

export default function Execution({ navigateTo, activeRunId }) {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [done, setDone] = useState(false);
  const logRef = useRef(null);

  // Poll backend; fall back to mock data
  useEffect(() => {
    if (!activeRunId) return;

    let cancelled = false;
    let logIdx = 0;

    async function poll() {
      try {
        const data = await evaluationsApi.status(activeRunId);
        if (!cancelled) {
          setStatus(data);
          if (data.logs) setLogs(data.logs);
          if (['completed', 'failed'].includes(data.overall_status)) {
            setDone(true);
            return; // stop polling
          }
          setTimeout(poll, 2000);
        }
      } catch (e) {
        if (!cancelled) {
          setLogs(prev => [...prev, `Backend error: ${e.message}`]);
          setDone(true);
        }
      }
    }

    poll();
    return () => { cancelled = true; };
  }, [activeRunId]);

  // Auto-scroll log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  if (!status) {
  return (
    <div className="page animate-in">
      <h1 className="page-title">Execution Monitor</h1>
      <p className="page-sub">Loading run from backend...</p>
    </div>
  );
}
const s = status;

  const overallDone = done || ['completed', 'failed'].includes(s.overall_status);

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Execution Monitor</h1>
          <p className="page-sub">{s.task} · {s.language}</p>
        </div>
        <div className="header-actions">
          {overallDone && (
            <Button onClick={() => navigateTo('results', activeRunId)}>
              View Results →
            </Button>
          )}
        </div>
      </div>

      {/* Per-assistant progress */}
      <div className="exec-grid">
        {s.assistants?.map(a => (
          <Card key={a.id} className="assistant-card">
            <div className="assistant-card-header">
              <span className="assistant-card-name">{a.name}</span>
              <Badge color={STATUS_COLOR[a.status] || 'default'}>{a.status}</Badge>
            </div>

            <div className="progress-bar-wrap">
              <div
                className={`progress-bar ${a.status === 'failed' ? 'fail' : ''}`}
                style={{ width: `${a.progress}%` }}
              />
            </div>

            <div className="assistant-metrics">
              <div className={`metric-pill ${a.compile ? 'ok' : 'fail'}`}>
                {a.compile ? '✓' : '✗'} Compile
              </div>
              <div className={`metric-pill ${a.correct ? 'ok' : 'fail'}`}>
                {a.correct ? '✓' : '✗'} Correct
              </div>
              <div className={`metric-pill ${a.warnings === 0 ? 'ok' : 'warn'}`}>
                {a.warnings} warn
              </div>
              {a.time_ms && (
                <div className="metric-pill neutral">{a.time_ms}ms</div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Log stream */}
      <Card className="log-card">
        <div className="log-header">
          <h2 className="section-title">Live Log Stream</h2>
          <div className="flex items-center gap-1">
            {!overallDone && <span className="pulse-dot" />}
            <span className="text-xs text-muted">{logs.length} lines</span>
          </div>
        </div>
        <div className="log-body" ref={logRef}>
          {logs.length === 0 && (
            <span className="text-muted text-sm">Waiting for log output…</span>
          )}
          {logs.map((line, i) => {
            const isError   = line.includes('✗') || line.includes('FAILED') || line.includes('Error');
            const isSuccess = line.includes('✓') || line.includes('complete');
            const isWarn    = line.includes('warning') || line.includes('warn');
            return (
              <div
                key={i}
                className={`log-line ${isError ? 'log-err' : isSuccess ? 'log-ok' : isWarn ? 'log-warn' : ''}`}
              >
                {line}
              </div>
            );
          })}
          {!overallDone && <span className="log-cursor">▌</span>}
        </div>
      </Card>

      {overallDone && (
        <div className="exec-done animate-in">
          <span className="done-icon">✓</span>
          <div>
            <strong>Evaluation complete</strong>
            <p className="text-sm text-muted">All assistants have been evaluated. View the full results and report below.</p>
          </div>
          <Button onClick={() => navigateTo('results', activeRunId)} size="lg">
            View Full Results →
          </Button>
        </div>
      )}
    </div>
  );
}
