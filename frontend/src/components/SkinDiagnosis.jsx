import React, { useState } from 'react';
import { Upload, Sparkles, AlertCircle, FileText, CheckCircle2, ShieldAlert, ArrowRight, BrainCircuit } from 'lucide-react';
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
        details: `Recommends: ${data.recommendations[0]?.name || 'N/A'}`
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
            <div className="upload-subtext" style={{ marginTop: '0.25rem' }}>Running MobileNetV3 classifier...</div>
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
            <div className="card-header">
              <div>
                <span className="badge badge-success">AI Predictions Calibrated</span>
                {result.llm_fallback_used && (
                  <span className="badge" style={{ marginLeft: '0.5rem', backgroundColor: 'var(--accent)', color: '#fff' }}>LLM Fallback Triggered</span>
                )}
                <h2 style={{ fontSize: '1.8rem', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  Diagnosis: <span style={{ color: 'var(--primary)' }}>{result.disease}</span>
                </h2>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                {renderCircleScore(Math.round(result.confidence_score * 100), 'Diagnosis Confidence', 'var(--primary)')}
              </div>
            </div>

            <div className="divider"></div>

            {/* Explainable AI Visualizer Row */}
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                Explainable AI (XAI) Visualizer
              </h3>
              <div className="visualizer-row">
                <div className="image-box">
                  <img src={result.original_image} alt="Original" />
                  <div className="image-label">1. Original Image</div>
                </div>
                <div className="image-box">
                  <img src={result.enhanced_image} alt="Enhanced" />
                  <div className="image-label">2. Preprocessed (CLAHE)</div>
                </div>
                <div className="image-box" style={{ border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                  <img src={result.gradcam_heatmap} alt="Gradcam" />
                  <div className="image-label" style={{ color: 'var(--accent)' }}>3. Grad-CAM Attention Map</div>
                </div>
              </div>
              <div className="alert-box alert-info" style={{ marginTop: '0.75rem', padding: '0.75rem' }}>
                <Sparkles size={16} className="alert-info-icon" style={{ marginTop: '2px' }} />
                <div className="alert-text" style={{ fontSize: '0.8rem' }}>
                  <strong>Grad-CAM Explanation:</strong> The red and orange glowing areas indicate where the classifier model focused its parameters to detect the characteristic markers of {result.disease}.
                </div>
              </div>
            </div>

            <div className="divider"></div>

            {/* Herbal Recommendations */}
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                Top Recommended Ayurvedic Herbs
              </h3>
              
              <div className="rec-list">
                {result.recommendations.map((rec, index) => (
                  <div key={rec.name} className="rec-item">
                    <div className="rec-header">
                      <div>
                        <span className="rec-name">{rec.name}</span>
                        <span className="rec-botanical">({rec.botanical_name})</span>
                        {index === 0 && (
                          <span className="badge badge-accent" style={{ marginLeft: '0.75rem', fontSize: '0.65rem' }}>
                            Best Match
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '1rem' }}>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--primary)' }}>
                            {rec.efficacy_score}%
                          </div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Expected Efficacy</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--accent)' }}>
                            {rec.recommendation_confidence}%
                          </div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Rec Confidence</div>
                        </div>
                      </div>
                    </div>

                    <p className="detail-value" style={{ margin: '0.5rem 0', fontStyle: 'italic', background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '4px', borderLeft: '2px solid var(--primary)' }}>
                      <strong>Clinical Reasoning:</strong> {rec.explanation.reasoning}
                    </p>



                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.75rem', fontSize: '0.8rem' }}>
                      <div>
                        <div className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <CheckCircle2 size={13} style={{ color: 'var(--primary)' }} />
                          Preparation & Method
                        </div>
                        <div className="detail-value">{rec.explanation.preparation_method}</div>
                      </div>
                      <div>
                        <div className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <ShieldAlert size={13} style={{ color: '#eab308' }} />
                          Contraindications
                        </div>
                        <div className="detail-value" style={{ color: rec.explanation.contraindications.includes('None') ? 'var(--text-secondary)' : '#f59e0b' }}>
                          {rec.explanation.contraindications.join(', ')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* LLM AI Supplement — shown at the very bottom */}
            {result.llm_summary && (
              <>
                <div className="divider"></div>
                <div style={{ background: 'rgba(99, 102, 241, 0.04)', border: '1px solid rgba(99, 102, 241, 0.15)', borderRadius: '8px', padding: '1.25rem' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '0.75rem', textTransform: 'uppercase', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <BrainCircuit size={18} />
                    AI-Powered Supplement
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7', fontSize: '0.9rem', margin: 0 }}>
                    {result.llm_summary}
                  </p>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    Generated by LLM (supplementary to local model analysis)
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
