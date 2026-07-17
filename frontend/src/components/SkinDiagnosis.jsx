import React, { useState } from 'react';
import { Upload, Sparkles, AlertCircle, FileText, CheckCircle2, BrainCircuit } from 'lucide-react';
import { predictSkin } from '../utils/api';

export default function SkinDiagnosis({ onAddHistory }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDiagnose = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await predictSkin(selectedFile);
      setResult(data);
      
      // Log to history
      onAddHistory({
        type: 'Skin Diagnosis',
        inputName: selectedFile.name,
        timestamp: new Date().toLocaleTimeString(),
        prediction: data.disease,
        score: Math.round(data.confidence_score * 100) + '%',
        details: data.recommendations[0]?.name
          ? `Recommendation: ${data.recommendations[0].name}`
          : 'No knowledge-base recommendation'
      });
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  // Helper for drawing circular progress indicators
  const renderCircleScore = (score, label, color) => {
    const radius = 32;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    
    return (
      <div className="circular-score">
        <div className="circular-svg">
          <svg width="80" height="80">
            <circle className="circle-bg" cx="40" cy="40" r={radius} />
            <circle 
              className="circle-val" 
              cx="40" 
              cy="40" 
              r={radius} 
              stroke={color}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="circle-text" style={{ color }}>{score}%</div>
        </div>
        <span className="upload-subtext">{label}</span>
      </div>
    );
  };

  return (
    <div className="grid-2">
      {/* Upload Column */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Upload size={22} style={{ color: 'var(--primary)' }} />
            Skin Condition Analysis
          </h2>
          <p className="upload-subtext" style={{ marginTop: '0.25rem' }}>
            Upload an image of the affected skin area. The CNN will run preprocessing, detect the condition, and recommend matching herbs.
          </p>
        </div>

        <div className="upload-container">
          <input 
            type="file" 
            accept="image/*" 
            className="file-input" 
            onChange={handleFileChange} 
            disabled={loading}
          />
          {previewUrl ? (
            <img 
              src={previewUrl} 
              alt="Preview" 
              style={{ width: '100%', maxHeight: '250px', objectFit: 'contain', borderRadius: '8px' }} 
            />
          ) : (
            <>
              <Upload className="upload-icon" size={40} />
              <div className="upload-text">Select or Drag Skin Image</div>
              <div className="upload-subtext">Supports PNG, JPG, WEBP (Max 5MB)</div>
            </>
          )}
        </div>

        {selectedFile && !loading && (
          <button className="btn-primary" onClick={handleDiagnose} style={{ width: '100%', justifyContent: 'center' }}>
            <Sparkles size={18} />
            Analyze & Diagnose Skin
          </button>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <div className="loading-text">Pre-processing image (Denoising & Contrast Enhancement)...</div>
            <div className="upload-subtext" style={{ marginTop: '0.25rem' }}>Running skin-condition classifier...</div>
          </div>
        )}

        {error && (
          <div className="alert-box alert-info" style={{ borderColor: 'rgba(239, 68, 68, 0.25)', background: 'rgba(239, 68, 68, 0.05)' }}>
            <AlertCircle size={20} style={{ color: '#ef4444' }} />
            <div className="alert-text">
              <div className="alert-title" style={{ color: '#ef4444' }}>Diagnosis Error</div>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Result Column */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {!result && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '350px', color: 'var(--text-muted)' }}>
            <FileText size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>Upload and run analysis to view diagnostic output and herbal recommendations.</p>
          </div>
        )}

        {result && (
          <>
            <div className="card-header" style={{ marginBottom: '0.5rem' }}>
              <div>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span className="badge badge-success">
                    {result.is_healthy ? "Healthy Skin Detected" : "Assessment Calibrated"}
                  </span>
                </div>
                <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {result.is_healthy ? "No Skin Condition Detected" : "Condition Identified:"}{" "}
                  <span style={{ color: 'var(--primary)' }}>{result.disease}</span>
                </h2>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                {renderCircleScore(Math.round(result.confidence_score * 100), 'Confidence Rating', 'var(--primary)')}
              </div>
            </div>

            <div className="divider" style={{ margin: '0.5rem 0' }}></div>

            {/* Herbal Recommendations */}
            <div>
              {result.is_healthy ? (
                <div className="rec-item" style={{ borderLeft: '3px solid #10b981', background: 'rgba(16, 185, 129, 0.04)', padding: '1rem 1.25rem', borderRadius: '8px' }}>
                  <div className="rec-name" style={{ fontSize: '1.25rem' }}>No Treatment Needed</div>
                  <p className="detail-value" style={{ margin: '0.75rem 0 0', fontStyle: 'italic', lineHeight: '1.5' }}>
                    Your skin appears healthy. No herbal treatment is recommended at this time.
                  </p>
                </div>
              ) : (
                <>
              <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '1rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                Recommended Ayurvedic Herbs
              </h3>

              <div className="rec-list">
                {result.recommendations.map((rec, index) => (
                  <div key={rec.name} className="rec-item">
                    <div className="rec-header" style={{ flexWrap: 'wrap', gap: '1rem', marginBottom: '0.75rem' }}>
                      <div>
                        <span className="rec-name" style={{ fontSize: '1.25rem' }}>{rec.name}</span>
                        <span className="rec-botanical" style={{ fontSize: '0.85rem' }}>({rec.botanical_name})</span>
                        {index === 0 && (
                          <span className="badge badge-accent" style={{ marginLeft: '0.75rem', fontSize: '0.65rem' }}>
                            Primary Therapy
                          </span>
                        )}
                      </div>
                      
                      {/* Efficacy & Confidence Progress Bars instead of plain text */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '220px', flex: 1 }}>
                        <div className="progress-container">
                          <div className="progress-label-row">
                            <span>Clinical Efficacy</span>
                            <span style={{ color: 'var(--primary)' }}>{rec.efficacy_score}%</span>
                          </div>
                          <div className="progress-bar-bg">
                            <div className="progress-bar-fill primary" style={{ width: `${rec.efficacy_score}%` }}></div>
                          </div>
                        </div>
                        <div className="progress-container">
                          <div className="progress-label-row">
                            <span>Recommendation Confidence</span>
                            <span style={{ color: 'var(--accent)' }}>{rec.recommendation_confidence}%</span>
                          </div>
                          <div className="progress-bar-bg">
                            <div className="progress-bar-fill accent" style={{ width: `${rec.recommendation_confidence}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <p className="detail-value" style={{ margin: '0.75rem 0', fontStyle: 'italic', background: 'rgba(16, 185, 129, 0.02)', padding: '0.75rem', borderRadius: '6px', borderLeft: '3px solid var(--primary)', lineHeight: '1.5' }}>
                      <strong>Ayurvedic Actions:</strong> {rec.explanation.reasoning}
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginTop: '0.75rem', fontSize: '0.8rem' }}>
                      <div>
                        <div className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <CheckCircle2 size={13} style={{ color: 'var(--primary)' }} />
                          Preparation & Mode
                        </div>
                        <div className="detail-value" style={{ marginTop: '0.15rem' }}>{rec.explanation.preparation_method}</div>
                      </div>
                      <div>
                        <div className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <AlertCircle size={13} style={{ color: '#eab308' }} />
                          Safety Precautions
                        </div>
                        <div className="detail-value" style={{ marginTop: '0.15rem', color: rec.explanation.contraindications.includes('None') ? 'var(--text-secondary)' : '#f59e0b' }}>
                          {rec.explanation.contraindications.join(', ')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {result.recommendations.length === 0 && (
                  <p className="upload-subtext">No matching knowledge-base records are available.</p>
                )}
              </div>
              </>
              )}
            </div>

            {/* LLM AI Supplement */}
            {!result.is_healthy && !result.llm_summary && result.llm_error && (
              <div className="alert-box alert-info" style={{ borderColor: 'rgba(239, 68, 68, 0.25)', background: 'rgba(239, 68, 68, 0.05)' }}>
                <AlertCircle size={20} style={{ color: '#ef4444' }} />
                <div className="alert-text">
                  <div className="alert-title" style={{ color: '#ef4444' }}>LLM Summary Unavailable</div>
                  {result.llm_error}
                </div>
              </div>
            )}
            {result.llm_summary && (
              <>
                <div className="divider" style={{ margin: '0.5rem 0' }}></div>
                <div style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.02) 0%, rgba(16, 185, 129, 0.02) 100%)', border: '1px solid rgba(16, 185, 129, 0.15)', borderRadius: '12px', padding: '1.25rem' }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'uppercase', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '0.5rem', letterSpacing: '0.05em' }}>
                    <BrainCircuit size={16} />
                    Clinical Reference Summary
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '0.85rem', margin: 0 }}>
                    {result.llm_summary}
                  </p>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    Note: Information generated dynamically by clinical LLM for medical decision support references.
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>

    </div>
  );
}
