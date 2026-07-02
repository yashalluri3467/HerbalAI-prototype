import React from 'react';
import { History, Trash2, Clock, CheckSquare } from 'lucide-react';

export default function HistoryTrack({ history, onClearHistory }) {
  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.5rem' }}>
            <History size={24} style={{ color: 'var(--primary)' }} />
            Diagnostic Session History
          </h2>
          <p className="upload-subtext" style={{ marginTop: '0.25rem' }}>
            Track logs, classifications, and efficacy results generated during your current session.
          </p>
        </div>
        
        {history.length > 0 && (
          <button 
            className="tab-button" 
            onClick={onClearHistory}
            style={{ 
              background: 'rgba(239, 68, 68, 0.1)', 
              color: '#ef4444', 
              border: '1px solid rgba(239, 68, 68, 0.2)',
              fontSize: '0.8rem',
              padding: '0.4rem 1rem'
            }}
          >
            <Trash2 size={14} />
            Clear Log History
          </button>
        )}
      </div>

      <div className="divider" style={{ margin: '0' }}></div>

      {history.length === 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
          <History size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
          <h3>No diagnostic logs recorded yet</h3>
          <p className="upload-subtext" style={{ marginTop: '0.5rem', textAlign: 'center' }}>
            Upload skin or leaf images in the tabs above to run classification pipelines. Logs will register here.
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-light)', color: 'var(--text-primary)' }}>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Evaluation Type</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Input Image(s)</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Classified Prediction</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Calibrated Score</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '700' }}>Action Summary</th>
              </tr>
            </thead>
            <tbody>
              {history.map((log, index) => (
                <tr key={index} style={{ borderBottom: '1px solid var(--border-light)', transition: 'background 0.2s' }} className="history-row-tr">
                  <td style={{ padding: '1rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <Clock size={13} />
                      {log.timestamp}
                    </div>
                  </td>
                  <td style={{ padding: '1rem', fontWeight: '600' }}>
                    <span 
                      className="badge" 
                      style={{ 
                        fontSize: '0.7rem',
                        background: log.type === 'Skin Diagnosis' ? 'rgba(16, 185, 129, 0.1)' : log.type === 'Joint Evaluation' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(13, 148, 136, 0.1)',
                        color: log.type === 'Skin Diagnosis' ? 'var(--primary)' : log.type === 'Joint Evaluation' ? 'var(--accent)' : 'var(--secondary)',
                        border: '1px solid currentColor'
                      }}
                    >
                      {log.type}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {log.inputName}
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-primary)', fontWeight: '600' }}>
                    {log.prediction}
                  </td>
                  <td style={{ padding: '1rem', fontWeight: '700', color: 'var(--primary)' }}>
                    {log.score}
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <CheckSquare size={13} style={{ color: 'var(--primary)' }} />
                      {log.details}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
