import React, { useEffect, useState } from 'react';
import { History, RefreshCw, Clock, CheckSquare, ImageOff } from 'lucide-react';
import { fetchSessions } from '../utils/api';

const TYPE_META = {
  skin: { label: 'Skin Diagnosis', color: 'var(--primary)' },
  leaf: { label: 'Herb Classifier', color: 'var(--secondary)' },
  joint: { label: 'Joint Evaluation', color: 'var(--accent)' },
  tf: { label: 'TF Prediction', color: '#f59e0b' },
};

function fmtScore(confidence) {
  if (confidence == null) return '—';
  return `${(confidence * 100).toFixed(1)}%`;
}

function sessionSummary(s) {
  const parts = [];
  if (s.status) parts.push(s.status);
  if (Array.isArray(s.recommendations) && s.recommendations.length) {
    parts.push(`${s.recommendations.length} herb${s.recommendations.length > 1 ? 's' : ''}`);
  }
  return parts.join(' · ') || '—';
}

export default function HistoryTrack({ history, onClearHistory }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingDb, setUsingDb] = useState(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSessions(50, 0);
      setSessions(data.sessions || []);
      setUsingDb(Boolean(data.db_enabled));
    } catch (e) {
      setError(e.message || 'Failed to load session history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rows = usingDb ? sessions : history;
  const isEmpty = !loading && !error && rows.length === 0;

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.5rem' }}>
            <History size={24} style={{ color: 'var(--primary)' }} />
            Diagnostic Session History
          </h2>
          <p className="upload-subtext" style={{ marginTop: '0.25rem' }}>
            {usingDb
              ? 'Persisted in the database — survives refreshes and is shared across sessions.'
              : 'Showing this browser\'s local log (database not connected).'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="tab-button"
            onClick={load}
            disabled={loading}
            style={{ fontSize: '0.8rem', padding: '0.4rem 1rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            {loading ? 'Loading…' : 'Refresh'}
          </button>
          {!usingDb && history.length > 0 && (
            <button
              className="tab-button"
              onClick={onClearHistory}
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                color: '#ef4444',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                fontSize: '0.8rem',
                padding: '0.4rem 1rem',
              }}
            >
              Clear Local Log
            </button>
          )}
        </div>
      </div>

      <div className="divider" style={{ margin: '0' }} />

      {loading ? (
        <div style={{ padding: '4rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading session history…
        </div>
      ) : error ? (
        <div style={{ padding: '4rem 1rem', textAlign: 'center', color: '#ef4444' }}>
          <h3>Could not load history</h3>
          <p className="upload-subtext" style={{ marginTop: '0.5rem' }}>{error}</p>
        </div>
      ) : isEmpty ? (
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
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Evaluation Type</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Input Image(s)</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Classified Prediction</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Calibrated Score</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Action Summary</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((log, index) => {
                const meta = usingDb ? TYPE_META[log.session_type] || TYPE_META.tf : null;
                const typeLabel = usingDb
                  ? meta.label
                  : log.type;
                const typeColor = usingDb
                  ? meta.color
                  : log.type === 'Skin Diagnosis'
                  ? 'var(--primary)'
                  : log.type === 'Joint Evaluation'
                  ? 'var(--accent)'
                  : 'var(--secondary)';
                const image = usingDb ? log.image : null;
                const prediction = usingDb ? log.predicted_class : log.prediction;
                const score = usingDb ? fmtScore(log.confidence) : log.score;
                const summary = usingDb ? sessionSummary(log) : log.details;
                const timestamp = usingDb ? log.created_at : log.timestamp;
                return (
                  <tr key={log.id ?? index} style={{ borderBottom: '1px solid var(--border-light)', transition: 'background 0.2s' }} className="history-row-tr">
                    <td style={{ padding: '1rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <Clock size={13} />
                        {timestamp}
                      </div>
                    </td>
                    <td style={{ padding: '1rem', fontWeight: 600 }}>
                      <span
                        className="badge"
                        style={{
                          fontSize: '0.7rem',
                          background: 'color-mix(in srgb, ' + typeColor + ' 12%, transparent)',
                          color: typeColor,
                          border: '1px solid currentColor',
                        }}
                      >
                        {typeLabel}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      {image ? (
                        <img
                          src={image}
                          alt="input"
                          style={{ width: 72, height: 72, objectFit: 'cover', borderRadius: 8, border: '1px solid var(--border-light)' }}
                        />
                      ) : (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          <ImageOff size={14} /> none
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                      {prediction || '—'}
                    </td>
                    <td style={{ padding: '1rem', fontWeight: 700, color: 'var(--primary)' }}>
                      {score}
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <CheckSquare size={13} style={{ color: 'var(--primary)' }} />
                        {summary}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
