import { useState } from 'react';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Tasks from './pages/Tasks.jsx';
import Execution from './pages/Execution.jsx';
import Results from './pages/Results.jsx';
import Reports from './pages/Reports.jsx';
import Admin from './pages/Admin.jsx';
import './App.css';

const PAGES = {
  dashboard: Dashboard,
  tasks:     Tasks,
  execution: Execution,
  results:   Results,
  reports:   Reports,
  admin:     Admin,
};

export default function App() {
  const [page, setPage] = useState('dashboard');
  // activeRunId is set after kicking off an evaluation so Execution page can poll it
  const [activeRunId, setActiveRunId] = useState(null);

  const PageComponent = PAGES[page] || Dashboard;

  function navigateTo(p, runId) {
    if (runId !== undefined) setActiveRunId(runId);
    setPage(p);
  }

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={navigateTo} />
      <main className="app-main">
        <PageComponent navigateTo={navigateTo} activeRunId={activeRunId} />
      </main>
    </div>
  );
}
