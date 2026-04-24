import { useState, useEffect, useRef } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { Badge } from '../components/Card.jsx';
import { evaluationsApi } from '../api/client.js';
import './Page.css';
import './Execution.css';

const STATUS_COLOR = {
  completed: 'green',
  running: 'blue',
  queued: 'yellow',
  failed: 'red',
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

function normalizeAssistant(a, index) {
  return {
    id: safeText(a?.id, `assistant-${index}`),
    name: safeText(a?.name, `Assistant ${index + 1}`),
    status: safeText(a?.status, 'completed'),
    progress: Number(a?.progress ?? 100),
    compile: Boolean(a?.compile),
    correct: Boolean(a?.correct),
    warnings: Number(a?.warnings ?? 0),
    time_ms: a?.time_ms ?? null,
  };
}

function normalizeStatus(data) {
  return {
    ...data,
    task: safeText(data?.task, 'Unknown Task'),
    language: safeText(data?.language, 'Python'),
    overall_status: safeText(data?.overall_status || data?.status, 'completed'),
    assistants: Array.isArray(data?.assistants)
      ? data.assistants.map(normalizeAssistant)
      : [],
    logs: Array.isArray(data?.logs)
      ? data.logs.map(line => safeText(line))
      : [],
  };
}

export default function Execution({ navigateTo, activeRunId }) {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [done, setDone] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    if (!activeRunId) return;

    let cancelled = false;

    async function poll() {
      try {
        const data = await evaluationsApi.status(activeRunId);
        const normalized = normalizeStatus(data);

        if (!cancelled) {
          setStatus(normalized);
          setLogs(normalized.logs);

          if (['completed', 'failed'].includes(normalized.overall_status)) {
            setDone(true);
            return;
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

    return () => {
      cancelled = true;
    };
  }, [activeRunId]);

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

      <div className="exec-grid">
        {s.assistants.map((a, index) => (
          <Card key={`${a.id}-${index}`} className="assistant-card">
            <div className="assistant-card-header">
              <span className="assistant-card-name">{a.name}</span>
              <Badge color={STATUS_COLOR[a.status] || 'default'}>
                {a.status}
              </Badge>
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

              {a.time_ms != null && (
                <div className="metric-pill neutral">{a.time_ms}ms</div>
              )}
            </div>
          </Card>
        ))}
      </div>

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
            const text = safeText(line);
            const isError = text.includes('✗') || text.includes('FAILED') || text.includes('Error');
            const isSuccess = text.includes('✓') || text.includes('complete');
            const isWarn = text.includes('warning') || text.includes('warn');

            return (
              <div
                key={`${i}-${text.slice(0, 20)}`}
                className={`log-line ${isError ? 'log-err' : isSuccess ? 'log-ok' : isWarn ? 'log-warn' : ''}`}
              >
                {text}
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
            <p className="text-sm text-muted">
              All assistants have been evaluated. View the full results and report below.
            </p>
          </div>

          <Button onClick={() => navigateTo('results', activeRunId)} size="lg">
            View Full Results →
          </Button>
        </div>
      )}
    </div>
  );
}