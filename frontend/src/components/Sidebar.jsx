import { useState } from 'react';
import './Sidebar.css';

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: '⬡' },
  { id: 'tasks',     label: 'Tasks',     icon: '◈' },
  { id: 'execution', label: 'Execution', icon: '▷' },
  { id: 'results',   label: 'Results',   icon: '◫' },
  { id: 'reports',   label: 'Reports',   icon: '◻' },
  { id: 'admin',     label: 'Admin',     icon: '⚙' },
];

export default function Sidebar({ page, setPage }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">⬡</span>
          {!collapsed && (
            <div className="logo-text">
              <span className="logo-title">AI Compare</span>
              <span className="logo-sub">Coding Assistants</span>
            </div>
          )}
        </div>
        <button className="collapse-btn" onClick={() => setCollapsed(c => !c)}>
          {collapsed ? '›' : '‹'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(item => (
          <button
            key={item.id}
            className={`nav-item ${page === item.id ? 'active' : ''}`}
            onClick={() => setPage(item.id)}
            title={collapsed ? item.label : ''}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && <span className="nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="status-dot green" />
          <span className="text-xs text-muted">Backend connected</span>
        </div>
      )}
    </aside>
  );
}
