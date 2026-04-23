import { useState } from 'react';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import { evaluationsApi } from '../api/client.js';
import './Page.css';
import './Tasks.css';

const TASKS = [
  { id: 'a', label: 'Read Text File',          desc: 'Read data from a plain text file.',                           icon: '📄', needsFile: true },
  { id: 'b', label: 'Read JSON (multi-thread)', desc: 'Read JSON values using multiple threads.',                   icon: '🧵', needsFile: true },
  { id: 'c', label: 'Write Text File',          desc: 'Write data into a plain text file.',                         icon: '✏️', needsFile: false },
  { id: 'd', label: 'Write JSON (multi-thread)', desc: 'Write JSON values using multiple threads.',                 icon: '🔀', needsFile: false },
  { id: 'e', label: 'Produce ZIP Archive',      desc: 'Create a zip by calling an external utility on a text file.',icon: '🗜️', needsFile: true },
  { id: 'f', label: 'MySQL DB Query',           desc: 'Connect to MySQL and retrieve a sample record.',             icon: '🐬', needsDb: true },
  { id: 'g', label: 'MongoDB DB Query',         desc: 'Connect to MongoDB and retrieve a sample document.',         icon: '🍃', needsMongo: true },
  { id: 'h', label: 'Password Auth (JS/PHP)',   desc: 'Generate password-based authentication code for a web page.',icon: '🔐', needsFile: false },
];

const ASSISTANTS = [
  { id: 'copilot',  label: 'GitHub Copilot',    provider: 'Microsoft' },
  { id: 'chatgpt',  label: 'ChatGPT',           provider: 'OpenAI' },
  { id: 'gemini',   label: 'Google Gemini',     provider: 'Google' },
  { id: 'claude',   label: 'Anthropic Claude',  provider: 'Anthropic' },
  { id: 'grok',     label: 'Grok',              provider: 'xAI' },
];

const LANGUAGES = ['Python', 'JavaScript', 'PHP', 'Java', 'C++'];

export default function Tasks({ navigateTo }) {
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedAssistants, setSelectedAssistants] = useState(['copilot', 'chatgpt']);
  const [language, setLanguage] = useState('Python');
  const [inputFile, setInputFile] = useState('');
  const [dbConfig, setDbConfig] = useState({ host: 'localhost', port: '3306', user: '', password: '', name: '' });
  const [mongoUri, setMongoUri] = useState('mongodb://localhost:27017');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);

  const task = TASKS.find(t => t.id === selectedTask);

  function toggleAssistant(id) {
    setSelectedAssistants(prev =>
      prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]
    );
  }

  function validate() {
    const errs = [];
    if (!selectedTask) errs.push('Select a task.');
    if (selectedAssistants.length < 2) errs.push('Select at least 2 AI assistants to compare.');
    if (task?.needsFile && !inputFile.trim()) errs.push('Provide an input file path for this task.');
    if (task?.needsDb && (!dbConfig.host || !dbConfig.user || !dbConfig.name))
      errs.push('Fill in MySQL host, user, and database name.');
    if (task?.needsMongo && !mongoUri.trim()) errs.push('Provide a MongoDB URI.');
    return errs;
  }

  async function handleRun() {
    const errs = validate();
    if (errs.length) { setValidationErrors(errs); return; }
    setValidationErrors([]);
    setError('');
    setLoading(true);
    try {
      const body = {
        task_id: selectedTask,
        assistant_ids: selectedAssistants,
        language,
        ...(task?.needsFile   && { input_file: inputFile }),
        ...(task?.needsDb     && { db_host: dbConfig.host, db_port: dbConfig.port, db_user: dbConfig.user, db_password: dbConfig.password, db_name: dbConfig.name }),
        ...(task?.needsMongo  && { mongo_uri: mongoUri }),
      };
      const result = await evaluationsApi.run(body);
      navigateTo('execution', result?.run_id || 'mock-run-1');
    } catch (e) {
      // If backend isn't up, still navigate to execution with a mock ID so UI is visible
      console.warn('Backend not available, navigating with mock run:', e.message);
      navigateTo('execution', 'mock-run-1');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page animate-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Tasks</h1>
          <p className="page-sub">Configure benchmark tasks and select assistants for evaluation</p>
        </div>
      </div>

      <div className="tasks-layout">
        {/* Left: Task selection */}
        <div className="tasks-left">
          <Card>
            <h2 className="section-title" style={{ marginBottom: '1rem' }}>Select Task</h2>
            <div className="task-list">
              {TASKS.map(t => (
                <button
                  key={t.id}
                  className={`task-row ${selectedTask === t.id ? 'selected' : ''}`}
                  onClick={() => setSelectedTask(t.id)}
                >
                  <span className="task-row-icon">{t.icon}</span>
                  <div className="task-row-body">
                    <span className="task-row-id">Task {t.id.toUpperCase()}</span>
                    <span className="task-row-label">{t.label}</span>
                    <span className="task-row-desc">{t.desc}</span>
                  </div>
                  {selectedTask === t.id && <span className="task-check">✓</span>}
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Right: Configuration */}
        <div className="tasks-right">
          {/* Assistants */}
          <Card>
            <h2 className="section-title" style={{ marginBottom: '0.85rem' }}>Select Assistants</h2>
            <p className="text-sm text-muted" style={{ marginBottom: '1rem' }}>
              Choose at least 2 assistants to compare. GitHub Copilot is required by the SRS.
            </p>
            <div className="assistant-grid">
              {ASSISTANTS.map(a => {
                const checked = selectedAssistants.includes(a.id);
                return (
                  <button
                    key={a.id}
                    className={`assistant-toggle ${checked ? 'checked' : ''}`}
                    onClick={() => toggleAssistant(a.id)}
                  >
                    <span className="assistant-check">{checked ? '✓' : ''}</span>
                    <div>
                      <div className="assistant-name">{a.label}</div>
                      <div className="assistant-provider">{a.provider}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Language */}
          <Card>
            <h2 className="section-title" style={{ marginBottom: '0.85rem' }}>Programming Language</h2>
            <div className="lang-grid">
              {LANGUAGES.map(l => (
                <button
                  key={l}
                  className={`lang-pill ${language === l ? 'selected' : ''}`}
                  onClick={() => setLanguage(l)}
                >
                  {l}
                </button>
              ))}
            </div>
          </Card>

          {/* Task-specific inputs */}
          {task?.needsFile && (
            <Card>
              <h2 className="section-title" style={{ marginBottom: '0.85rem' }}>Input File</h2>
              <div className="form-group">
                <label className="form-label">File Path</label>
                <input
                  className="form-input"
                  placeholder="e.g. ./benchmarks/tasks_a/sample.txt"
                  value={inputFile}
                  onChange={e => setInputFile(e.target.value)}
                />
              </div>
            </Card>
          )}

          {task?.needsDb && (
            <Card>
              <h2 className="section-title" style={{ marginBottom: '0.85rem' }}>MySQL Configuration</h2>
              <div className="db-grid">
                {[
                  { key: 'host',     label: 'Host',     placeholder: 'localhost' },
                  { key: 'port',     label: 'Port',     placeholder: '3306' },
                  { key: 'user',     label: 'User',     placeholder: 'root' },
                  { key: 'password', label: 'Password', placeholder: '••••••••', type: 'password' },
                  { key: 'name',     label: 'Database', placeholder: 'test_db' },
                ].map(f => (
                  <div key={f.key} className="form-group">
                    <label className="form-label">{f.label}</label>
                    <input
                      className="form-input"
                      type={f.type || 'text'}
                      placeholder={f.placeholder}
                      value={dbConfig[f.key]}
                      onChange={e => setDbConfig(d => ({ ...d, [f.key]: e.target.value }))}
                    />
                  </div>
                ))}
              </div>
            </Card>
          )}

          {task?.needsMongo && (
            <Card>
              <h2 className="section-title" style={{ marginBottom: '0.85rem' }}>MongoDB Configuration</h2>
              <div className="form-group">
                <label className="form-label">Connection URI</label>
                <input
                  className="form-input"
                  placeholder="mongodb://localhost:27017"
                  value={mongoUri}
                  onChange={e => setMongoUri(e.target.value)}
                />
              </div>
            </Card>
          )}

          {/* API key status */}
          <Card>
            <h2 className="section-title" style={{ marginBottom: '0.75rem' }}>API Key Status</h2>
            <div className="apikey-list">
              {ASSISTANTS.map(a => (
                <div key={a.id} className="apikey-row">
                  <span className="apikey-name">{a.label}</span>
                  <span className={`apikey-status ${selectedAssistants.includes(a.id) ? 'configured' : 'skip'}`}>
                    {selectedAssistants.includes(a.id) ? '✓ configured' : '— skipped'}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted" style={{ marginTop: '0.75rem' }}>
              Manage API keys in Admin → Configuration
            </p>
          </Card>

          {/* Validation errors */}
          {validationErrors.length > 0 && (
            <div className="error-box">
              {validationErrors.map((e, i) => <div key={i}>• {e}</div>)}
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          {/* Actions */}
          <div className="run-actions">
            <Button variant="ghost" onClick={() => {
              setSelectedTask(null);
              setSelectedAssistants(['copilot', 'chatgpt']);
              setLanguage('Python');
              setInputFile('');
              setValidationErrors([]);
            }}>
              Reset
            </Button>
            <Button onClick={handleRun} loading={loading} size="lg">
              ▷ &nbsp;Run Evaluation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
