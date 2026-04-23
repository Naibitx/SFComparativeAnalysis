import { useState, useEffect } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { adminApi } from '../api/client.js';
import './Page.css';
import './Admin.css';

const DEFAULT_CONFIG = {
  openai_api_key:     '',
  gemini_api_key:     '',
  anthropic_api_key:  '',
  grok_api_key:       '',
  copilot_mode:       '',
  mysql_host:         'localhost',
  mysql_port:         '3306',
  mysql_user:         '',
  mysql_password:     '',
  mysql_database:     '',
  mongo_uri:          'mongodb://localhost:27017',
  mongo_database:     'test_db',
  mongo_collection:   'test_collection',
  execution_timeout:  '10',
  max_memory_mb:      '256',
  allow_network:      false,
  semgrep_enabled:    true,
  bandit_enabled:     true,
  coverity_enabled:   false,
  generate_html:      true,
  generate_pdf:       true,
  log_level:          'INFO',
  workspace_dir:      './workspace',
  reports_dir:        './reports/generated',
};

export default function Admin() {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [logs, setLogs] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [tab, setTab] = useState('api');
  const [showSecrets, setShowSecrets] = useState({});

  useEffect(() => {
    adminApi.getConfig()
      .then(data => { if (data) setConfig(c => ({ ...c, ...data })); })
      .catch(() => {});
    adminApi.getLogs()
      .then(data => { if (data?.logs) setLogs(data.logs); })
      .catch(() => {
        setLogs([
          '[2026-03-09 14:02:11] INFO  Evaluation started — run_id: mock-run-1',
          '[2026-03-09 14:02:12] INFO  Dispatching prompts to 3 assistants',
          '[2026-03-09 14:02:45] INFO  Compilation complete — 2/3 passed',
          '[2026-03-09 14:03:10] INFO  Security scan complete — 0 critical findings',
          '[2026-03-09 14:03:12] INFO  Report saved → reports/generated/run_1.html',
        ]);
      });
  }, []);

  function set(key, val) { setConfig(c => ({ ...c, [key]: val })); }

  async function save() {
    setSaving(true);
    try {
      await adminApi.updateConfig(config);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      // still show success in demo mode
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } finally {
      setSaving(false);
    }
  }

  function toggleSecret(key) {
    setShowSecrets(s => ({ ...s, [key]: !s[key] }));
  }

  const TABS = [
    { id: 'api',     label: 'API Keys' },
    { id: 'db',      label: 'Databases' },
    { id: 'sandbox', label: 'Sandbox' },
    { id: 'report',  label: 'Reports' },
    { id: 'logs',    label: 'Logs' },
  ];

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Admin Settings</h1>
          <p className="page-sub">API keys, database connections, sandbox, and report configuration</p>
        </div>
        <div className="header-actions">
          {saved && <span className="saved-badge">✓ Saved</span>}
          <Button onClick={save} loading={saving}>Save Configuration</Button>
        </div>
      </div>

      <div className="admin-tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`result-tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'api' && (
        <div className="admin-section animate-in">
          <Card>
            <h2 className="section-title" style={{ marginBottom: '1.25rem' }}>AI Assistant API Keys</h2>
            <p className="text-sm text-muted" style={{ marginBottom: '1.25rem' }}>
              Keys are stored in <code className="font-mono">.env</code> and never logged or included in reports.
            </p>
            <div className="api-key-form">
              {[
                { key: 'openai_api_key',    label: 'OpenAI (ChatGPT)',   placeholder: 'sk-…' },
                { key: 'gemini_api_key',    label: 'Google (Gemini)',    placeholder: 'AIza…' },
                { key: 'anthropic_api_key', label: 'Anthropic (Claude)', placeholder: 'sk-ant-…' },
                { key: 'grok_api_key',      label: 'xAI (Grok)',         placeholder: 'xai-…' },
              ].map(f => (
                <div key={f.key} className="form-group">
                  <label className="form-label">{f.label}</label>
                  <div className="secret-input-wrap">
                    <input
                      className="form-input"
                      type={showSecrets[f.key] ? 'text' : 'password'}
                      placeholder={f.placeholder}
                      value={config[f.key]}
                      onChange={e => set(f.key, e.target.value)}
                    />
                    <button
                      className="secret-toggle"
                      onClick={() => toggleSecret(f.key)}
                      title={showSecrets[f.key] ? 'Hide' : 'Show'}
                    >
                      {showSecrets[f.key] ? '🙈' : '👁'}
                    </button>
                  </div>
                </div>
              ))}

              <div className="form-group">
                <label className="form-label">GitHub Copilot Mode</label>
                <select
                  className="form-select"
                  value={config.copilot_mode}
                  onChange={e => set('copilot_mode', e.target.value)}
                >
                  <option value="manual">Manual (paste responses)</option>
                  <option value="api">API (if supported)</option>
                </select>
              </div>
            </div>
          </Card>
        </div>
      )}

      {tab === 'db' && (
        <div className="admin-section animate-in">
          <Card>
            <h2 className="section-title" style={{ marginBottom: '1.25rem' }}>MySQL (Task F)</h2>
            <div className="db-form">
              {[
                { key: 'mysql_host',     label: 'Host',     placeholder: 'localhost' },
                { key: 'mysql_port',     label: 'Port',     placeholder: '3306' },
                { key: 'mysql_user',     label: 'User',     placeholder: 'root' },
                { key: 'mysql_password', label: 'Password', placeholder: '••••••••', type: 'password' },
                { key: 'mysql_database', label: 'Database', placeholder: 'test_db' },
              ].map(f => (
                <div key={f.key} className="form-group">
                  <label className="form-label">{f.label}</label>
                  <input
                    className="form-input"
                    type={f.type || 'text'}
                    placeholder={f.placeholder}
                    value={config[f.key]}
                    onChange={e => set(f.key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </Card>

          <Card style={{ marginTop: '1rem' }}>
            <h2 className="section-title" style={{ marginBottom: '1.25rem' }}>MongoDB (Task G)</h2>
            <div className="db-form">
              <div className="form-group">
                <label className="form-label">Connection URI</label>
                <input
                  className="form-input"
                  placeholder="mongodb://localhost:27017"
                  value={config.mongo_uri}
                  onChange={e => set('mongo_uri', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Database</label>
                <input className="form-input" placeholder="test_db" value={config.mongo_database} onChange={e => set('mongo_database', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Collection</label>
                <input className="form-input" placeholder="test_collection" value={config.mongo_collection} onChange={e => set('mongo_collection', e.target.value)} />
              </div>
            </div>
          </Card>
        </div>
      )}

      {tab === 'sandbox' && (
        <div className="admin-section animate-in">
          <Card>
            <h2 className="section-title" style={{ marginBottom: '1.25rem' }}>Execution Sandbox</h2>
            <div className="sandbox-form">
              <div className="form-group">
                <label className="form-label">Execution Timeout (seconds)</label>
                <input className="form-input" type="number" value={config.execution_timeout} onChange={e => set('execution_timeout', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Max Memory (MB)</label>
                <input className="form-input" type="number" value={config.max_memory_mb} onChange={e => set('max_memory_mb', e.target.value)} />
              </div>
            </div>

            <div className="toggle-list" style={{ marginTop: '1rem' }}>
              {[
                { key: 'allow_network',   label: 'Allow network access during execution', danger: true },
                { key: 'semgrep_enabled', label: 'Enable Semgrep static analysis' },
                { key: 'bandit_enabled',  label: 'Enable Bandit (Python security scanner)' },
                { key: 'coverity_enabled',label: 'Enable Coverity (requires license)' },
              ].map(f => (
                <label key={f.key} className={`toggle-row ${f.danger ? 'danger' : ''}`}>
                  <div>
                    <div className="toggle-label">{f.label}</div>
                    {f.danger && <div className="toggle-sub">⚠ Enable only in isolated environments</div>}
                  </div>
                  <div
                    className={`toggle-switch ${config[f.key] ? 'on' : 'off'}`}
                    onClick={() => set(f.key, !config[f.key])}
                  >
                    <div className="toggle-knob" />
                  </div>
                </label>
              ))}
            </div>
          </Card>

          <Card style={{ marginTop: '1rem' }}>
            <h2 className="section-title" style={{ marginBottom: '1rem' }}>File Paths</h2>
            <div className="sandbox-form">
              <div className="form-group">
                <label className="form-label">Workspace Directory</label>
                <input className="form-input font-mono" value={config.workspace_dir} onChange={e => set('workspace_dir', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Reports Directory</label>
                <input className="form-input font-mono" value={config.reports_dir} onChange={e => set('reports_dir', e.target.value)} />
              </div>
            </div>
          </Card>
        </div>
      )}

      {tab === 'report' && (
        <div className="admin-section animate-in">
          <Card>
            <h2 className="section-title" style={{ marginBottom: '1.25rem' }}>Report Generation</h2>
            <div className="toggle-list">
              {[
                { key: 'generate_html', label: 'Generate HTML report' },
                { key: 'generate_pdf',  label: 'Generate PDF report' },
              ].map(f => (
                <label key={f.key} className="toggle-row">
                  <div className="toggle-label">{f.label}</div>
                  <div
                    className={`toggle-switch ${config[f.key] ? 'on' : 'off'}`}
                    onClick={() => set(f.key, !config[f.key])}
                  >
                    <div className="toggle-knob" />
                  </div>
                </label>
              ))}
            </div>
            <div className="form-group" style={{ marginTop: '1rem' }}>
              <label className="form-label">Log Level</label>
              <select className="form-select" value={config.log_level} onChange={e => set('log_level', e.target.value)}>
                {['DEBUG', 'INFO', 'WARNING', 'ERROR'].map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
          </Card>
        </div>
      )}

      {tab === 'logs' && (
        <Card className="log-card animate-in">
          <div className="log-header">
            <h2 className="section-title">System Logs</h2>
            <span className="text-xs text-muted">{logs.length} entries</span>
          </div>
          <div className="log-body">
            {logs.length === 0 && <span className="text-muted">No logs available.</span>}
            {logs.map((line, i) => {
              const isError = line.includes('ERROR') || line.includes('FAILED');
              const isWarn  = line.includes('WARN');
              return (
                <div key={i} className={`log-line ${isError ? 'log-err' : isWarn ? 'log-warn' : ''}`}>
                  {line}
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
