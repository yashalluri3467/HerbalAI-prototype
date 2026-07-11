import React, { useState } from 'react';
import { Upload, Sparkles, AlertCircle, FileText, CheckCircle2, HelpCircle, HeartHandshake, BrainCircuit } from 'lucide-react';
import { predictLeaf, predictJoint } from '../utils/api';

export default function HerbEvaluator({ onAddHistory }) {
  // Mode selection: 'leaf' or 'joint'
  const [evalMode, setEvalMode] = useState('leaf'); 
  
  // Single leaf state
  const [leafFile, setLeafFile] = useState(null);
  const [leafPreview, setLeafPreview] = useState(null);
  
  // Joint state
  const [skinFile, setSkinFile] = useState(null);
  const [skinPreview, setSkinPreview] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Result holders
  const [leafResult, setLeafResult] = useState(null);
  const [jointResult, setJointResult] = useState(null);

  const handleLeafFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setLeafFile(file);
      setLeafPreview(URL.createObjectURL(file));
      setLeafResult(null);
      setJointResult(null);
      setError(null);
    }
  };

  const handleSkinFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSkinFile(file);
      setSkinPreview(URL.createObjectURL(file));
      setJointResult(null);
      setError(null);
    }
  };

  const handleAnalyzeLeaf = async () => {
    if (!leafFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await predictLeaf(leafFile);
      setLeafResult(data);
      
      onAddHistory({
        type: 'Herb Classifier',
        inputName: leafFile.name,
        timestamp: new Date().toLocaleTimeString(),
        prediction: data.herb,
        score: Math.round(data.confidence_score * 100) + '%',
        details: data.details?.active_compounds?.[0]
          ? `Active compound: ${data.details.active_compounds[0]}`
          : 'No knowledge-base record'
      });
    } catch (err) {
      setError(err.message || 'An error occurred during leaf analysis.');
    } finally {
      setLoading(false);
    }
  };

  const handleJointEvaluate = async () => {
    if (!skinFile || !leafFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await predictJoint(skinFile, leafFile);
      setJointResult(data);
      
      onAddHistory({
        type: 'Joint Evaluation',
        inputName: `${skinFile.name} + ${leafFile.name}`,
        timestamp: new Date().toLocaleTimeString(),
        prediction: `${data.herb_display || data.herb || 'Uncertain leaf'} for ${data.disease}`,
        score: data.evaluation ? `${data.evaluation.efficacy_score}% Efficacy` : 'Not evaluated',
        details: data.evaluation
          ? (data.evaluation.is_compatible ? 'Compatible' : 'Not compatible')
          : (data.leaf_classification_status === 'uncertain' ? 'Leaf model uncertain' : 'Knowledge base unavailable')
      });
    } catch (err) {
      setError(err.message || 'An error occurred during joint analysis.');
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
      {/* Upload and Selection Column */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={22} style={{ color: 'var(--primary)' }} />
            Ayurvedic Herb & Leaf Evaluator
          </h2>
          <p className="upload-subtext" style={{ marginTop: '0.25rem' }}>
            Identify herbal leaves directly using computer vision, or upload both a skin image and a leaf image to test their therapeutic compatibility.
          </p>
        </div>

        {/* Tab Selection */}
        <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(3, 6, 5, 0.7)', padding: '0.25rem', borderRadius: '9999px', border: '1px solid var(--border-light)' }}>
          <button 
            className={`tab-button ${evalMode === 'leaf' ? 'active' : ''}`}
            onClick={() => { setEvalMode('leaf'); setError(null); }}
            style={{ flex: 1, borderRadius: '9999px', justifyContent: 'center' }}
          >
            Identify Herbal Leaf
          </button>
          <button 
            className={`tab-button ${evalMode === 'joint' ? 'active' : ''}`}
            onClick={() => { setEvalMode('joint'); setError(null); }}
            style={{ flex: 1, borderRadius: '9999px', justifyContent: 'center' }}
          >
            Skin + Herb Compatibility
          </button>
        </div>

        {evalMode === 'leaf' ? (
          /* SINGLE LEAF UPLOAD */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="upload-container">
              <input 
                type="file" 
                accept="image/*" 
                className="file-input" 
                onChange={handleLeafFileChange} 
                disabled={loading}
              />
              {leafPreview ? (
                <img 
                  src={leafPreview} 
                  alt="Leaf Preview" 
                  style={{ width: '100%', maxHeight: '250px', objectFit: 'contain', borderRadius: '8px' }} 
                />
              ) : (
                <>
                  <Upload className="upload-icon" size={40} style={{ color: 'var(--secondary)' }} />
                  <div className="upload-text">Select or Drag Leaf Image</div>
                  <div className="upload-subtext">Supports PNG, JPG, WEBP (Max 5MB)</div>
                </>
              )}
            </div>

            {leafFile && !loading && (
              <button className="btn-primary" onClick={handleAnalyzeLeaf} style={{ width: '100%', justifyContent: 'center' }}>
                <Sparkles size={18} />
                Classify & Analyze Leaf
              </button>
            )}
          </div>
        ) : (
          /* JOINT SKIN AND LEAF UPLOAD */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span className="detail-label" style={{ marginBottom: '0.5rem', textAlign: 'center' }}>1. Skin Condition Image</span>
                <div className="upload-container" style={{ padding: '1.5rem 0.5rem' }}>
                  <input 
                    type="file" 
                    accept="image/*" 
                    className="file-input" 
                    onChange={handleSkinFileChange} 
                    disabled={loading}
                  />
                  {skinPreview ? (
                    <img 
                      src={skinPreview} 
                      alt="Skin Preview" 
                      style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px' }} 
                    />
                  ) : (
                    <>
                      <Upload className="upload-icon" size={24} />
                      <div className="upload-text" style={{ fontSize: '0.8rem' }}>Upload Skin Image</div>
                    </>
                  )}
                </div>
              </div>

              <div>
                <span className="detail-label" style={{ marginBottom: '0.5rem', textAlign: 'center' }}>2. Ayurvedic Leaf Image</span>
                <div className="upload-container" style={{ padding: '1.5rem 0.5rem' }}>
                  <input 
                    type="file" 
                    accept="image/*" 
                    className="file-input" 
                    onChange={handleLeafFileChange} 
                    disabled={loading}
                  />
                  {leafPreview ? (
                    <img 
                      src={leafPreview} 
                      alt="Leaf Preview" 
                      style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px' }} 
                    />
                  ) : (
                    <>
                      <Upload className="upload-icon" size={24} style={{ color: 'var(--secondary)' }} />
                      <div className="upload-text" style={{ fontSize: '0.8rem' }}>Upload Leaf Image</div>
                    </>
                  )}
                </div>
              </div>
            </div>

            {skinFile && leafFile && !loading && (
              <button className="btn-primary" onClick={handleJointEvaluate} style={{ width: '100%', justifyContent: 'center' }}>
                <HeartHandshake size={18} />
                Evaluate Joint Compatibility
              </button>
            )}
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <div className="loading-text">Extracting morphological and chemical features...</div>
            <div className="upload-subtext" style={{ marginTop: '0.25rem' }}>Running DNN Efficacy Engine...</div>
          </div>
        )}

        {error && (
          <div className="alert-box alert-info" style={{ borderColor: 'rgba(239, 68, 68, 0.25)', background: 'rgba(239, 68, 68, 0.05)' }}>
            <AlertCircle size={20} style={{ color: '#ef4444' }} />
            <div className="alert-text">
              <div className="alert-title" style={{ color: '#ef4444' }}>Analysis Error</div>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Result Display Column */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {!leafResult && !jointResult && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '350px', color: 'var(--text-muted)' }}>
            <FileText size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>Upload files and run classification or evaluation mode to view metrics.</p>
          </div>
        )}

        {/* 1. SINGLE LEAF CLASSIFICATION OUTPUT */}
        {leafResult && evalMode === 'leaf' && (
          <>
            <div className="card-header" style={{ marginBottom: '0.5rem' }}>
              <div>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span className={`badge ${leafResult.classification_status === 'uncertain' ? 'badge-info' : 'badge-success'}`}>
                    {leafResult.classification_status === 'uncertain' ? 'Model Uncertain' : 'Herb Classified'}
                  </span>
                </div>
                <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>
                  Botanical Match: <span style={{ color: 'var(--primary)' }}>{leafResult.herb}</span>
                </h2>
                <div className="herb-scientific" style={{ fontSize: '1rem', marginTop: '0.15rem' }}>
                  {leafResult.details
                    ? `${leafResult.details.botanical_name} (Family: ${leafResult.details.family})`
                    : 'No matching knowledge-base record'}
                </div>
              </div>
              <div>
                {renderCircleScore(Math.round(leafResult.confidence_score * 100), 'Classification Confidence', 'var(--primary)')}
              </div>
            </div>

            {leafResult.classification_status === 'uncertain' && (
              <div className="alert-box alert-info" style={{ borderColor: 'rgba(239, 68, 68, 0.25)', background: 'rgba(239, 68, 68, 0.05)' }}>
                <AlertCircle size={20} style={{ color: '#ef4444' }} />
                <div className="alert-text">
                  <div className="alert-title" style={{ color: '#ef4444' }}>Leaf Model Needs Retraining</div>
                  The saved model is not separating classes strongly enough to report a plant name. Raw top class: {leafResult.raw_model_prediction}. Confidence margin: {Math.round((leafResult.model_quality?.margin || 0) * 100)}%.
                </div>
              </div>
            )}

            {leafResult.top_predictions?.length > 0 && (
              <div>
                <h3 style={{ fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                  Dataset Probability Ranking
                </h3>
                <div className="rec-list" style={{ gap: '0.5rem' }}>
                  {leafResult.top_predictions.map((prediction) => (
                    <div key={prediction.label} className="progress-container">
                      <div className="progress-label-row">
                        <span>{prediction.label}</span>
                        <span style={{ color: 'var(--primary)' }}>{Math.round(prediction.confidence * 100)}%</span>
                      </div>
                      <div className="progress-bar-bg">
                        <div className="progress-bar-fill primary" style={{ width: `${Math.round(prediction.confidence * 100)}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {/* Phytochemical & Morphological extraction */}
            {leafResult.details && <div>
              <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                Extracted Phytochemical & Herb Profile
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', fontSize: '0.85rem' }}>
                <div>
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-primary)' }}>
                    Active Compounds
                  </span>
                  <div className="tag-container" style={{ marginBottom: '0.75rem', marginTop: '0.25rem' }}>
                    {leafResult.details.active_compounds.map(c => (
                      <span key={c} className="tag">{c}</span>
                    ))}
                  </div>
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-primary)' }}>
                    Phytochemical Constituents
                  </span>
                  <div className="tag-container" style={{ marginTop: '0.25rem' }}>
                    {leafResult.details.phytochemicals.map(p => (
                      <span key={p} className="tag" style={{ border: '1px solid rgba(13, 148, 136, 0.2)' }}>{p}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="detail-label" style={{ color: 'var(--text-primary)' }}>Therapeutic Skincare Benefits</span>
                  <ul className="list-unstyled" style={{ color: 'var(--text-secondary)', lineHeight: '1.6', marginTop: '0.35rem' }}>
                    {leafResult.details.benefits.map(b => (
                      <li key={b} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                        <CheckCircle2 size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>}

            {/* LLM AI Supplement */}
            {!leafResult.llm_summary && leafResult.llm_error && (
              <div className="alert-box alert-info" style={{ borderColor: 'rgba(239, 68, 68, 0.25)', background: 'rgba(239, 68, 68, 0.05)' }}>
                <AlertCircle size={20} style={{ color: '#ef4444' }} />
                <div className="alert-text">
                  <div className="alert-title" style={{ color: '#ef4444' }}>LLM Summary Unavailable</div>
                  {leafResult.llm_error}
                </div>
              </div>
            )}
            {leafResult.llm_summary && (
              <>
                <div className="divider" style={{ margin: '0.5rem 0' }}></div>
                <div style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.02) 0%, rgba(16, 185, 129, 0.02) 100%)', border: '1px solid rgba(16, 185, 129, 0.15)', borderRadius: '12px', padding: '1.25rem' }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'uppercase', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '0.5rem', letterSpacing: '0.05em' }}>
                    <BrainCircuit size={16} />
                    Clinical Reference Summary
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '0.85rem', margin: 0 }}>
                    {leafResult.llm_summary}
                  </p>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    Note: Information generated dynamically by clinical LLM for botanical verification reference.
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {/* 2. JOINT COMPATIBILITY EVALUATION OUTPUT */}
        {jointResult && evalMode === 'joint' && jointResult.evaluation && (
          <>
            <div className="card-header" style={{ marginBottom: '0.5rem' }}>
              <div>
                <span className="badge badge-accent">Compatibility Assessment</span>
                <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>
                  {jointResult.evaluation.is_compatible ? (
                    <span style={{ color: 'var(--primary)' }}>Therapeutically Compatible Match</span>
                  ) : (
                    <span style={{ color: '#ef4444' }}>Low Compatibility Recommendation</span>
                  )}
                </h2>
                <div className="herb-scientific" style={{ fontSize: '1rem', marginTop: '0.15rem' }}>
                  Evaluating {jointResult.herb_display || jointResult.herb} leaf for {jointResult.disease} condition
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                {renderCircleScore(jointResult.evaluation.efficacy_score, 'Efficacy Index', 'var(--primary)')}
                {renderCircleScore(jointResult.evaluation.joint_confidence, 'Joint Confidence', 'var(--accent)')}
              </div>
            </div>


            {/* Details Assessment Card */}
            <div className={`compat-card ${jointResult.evaluation.is_compatible ? '' : 'incompatible'}`}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                AI Recommendation Report
              </h3>
              <p className="detail-value" style={{ lineHeight: '1.6', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                {jointResult.explanation.reasoning}
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', fontSize: '0.8rem', borderTop: '1px solid var(--border-light)', paddingTop: '1rem' }}>
                <div>
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-primary)' }}>
                    <CheckCircle2 size={13} style={{ color: 'var(--primary)' }} />
                    Suggested Preparation
                  </span>
                  <span className="detail-value" style={{ display: 'block', marginTop: '0.15rem' }}>{jointResult.explanation.preparation_method}</span>
                </div>
                <div>
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-primary)' }}>
                    <HelpCircle size={13} style={{ color: 'var(--accent)' }} />
                    Evidence Level
                  </span>
                  <span className="detail-value" style={{ display: 'block', marginTop: '0.15rem' }}>{jointResult.explanation.evidence_level}</span>
                </div>
              </div>
            </div>
          </>
        )}
        {jointResult && evalMode === 'joint' && !jointResult.evaluation && (
          <div className="alert-box alert-info">
            <AlertCircle size={20} />
            <div className="alert-text">
              <div className="alert-title">Compatibility unavailable</div>
              Enable the knowledge base in settings to evaluate dataset-backed compatibility.
              {jointResult.leaf_classification_status === 'uncertain' && ' The leaf classifier also needs retraining before compatibility can be trusted.'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
