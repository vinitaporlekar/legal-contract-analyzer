import React from 'react';

const severityColor = (severity) => {
  if (severity === 'High') return '#e74c3c';
  if (severity === 'Medium') return '#f39c12';
  return '#27ae60';
};

function RiskDashboard({ risks = [] }) {
  if (!risks || risks.length === 0) {
    return <p className="no-risks">No risky clauses detected.</p>;
  }

  return (
    <div className="risks-section">
      {risks.map((r, i) => (
        <div key={i} className="risk-card">
          <div className="risk-header">
            <span
              className="risk-severity"
              style={{ background: severityColor(r.severity) }}
            >
              {r.severity}
            </span>
            <span className="risk-category">{r.category}</span>
          </div>
          <p className="risk-explanation">{r.explanation}</p>
          <p className="risk-clause">{r.text ? r.text.substring(0, 200) + '...' : ''}</p>
        </div>
      ))}
    </div>
  );
}

export default RiskDashboard;