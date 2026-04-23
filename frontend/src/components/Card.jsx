import './Card.css';

export default function Card({ children, className = '', style }) {
  return (
    <div className={`card ${className}`} style={style}>
      {children}
    </div>
  );
}

export function StatCard({ label, value, sub, accent }) {
  return (
    <div className={`stat-card ${accent ? `accent-${accent}` : ''}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

export function Badge({ children, color = 'default' }) {
  return <span className={`badge badge-${color}`}>{children}</span>;
}
