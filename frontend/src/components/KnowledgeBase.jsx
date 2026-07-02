import React, { useState, useEffect } from 'react';
import { Search, Filter, BookOpen, Layers, FileText, Activity, AlertCircle } from 'lucide-react';
import { fetchHerbs } from '../utils/api';

export default function KnowledgeBase() {
  const [herbs, setHerbs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtering states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDisease, setSelectedDisease] = useState('All');

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchHerbs();
        setHerbs(data);
      } catch (err) {
        setError(err.message || 'Failed to load Ayurvedic knowledge base.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const uniqueDiseases = [
    'All',
    'Acne',
    'Dry Skin',
    'Pigmentation',
    'Eczema',
    'Wrinkles',
    'Psoriasis',
    'Dermatitis',
    'Fungal Infection',
    'Healthy Skin'
  ];

  // Filtering logic
  const filteredHerbs = herbs.filter(herb => {
    const matchesSearch = 
      herb.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      herb.botanical_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      herb.active_compounds.some(c => c.toLowerCase().includes(searchTerm.toLowerCase()));
      
    const matchesDisease = 
      selectedDisease === 'All' || 
      herb.disease_mapping.hasOwnProperty(selectedDisease);
      
    return matchesSearch && matchesDisease;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header and Controls */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.5rem' }}>
              <BookOpen size={24} style={{ color: 'var(--primary)' }} />
              Ayurvedic Herbal Knowledge Base
            </h2>
            <p className="upload-subtext" style={{ marginTop: '0.25rem' }}>
              Explore phytochemical constituents, therapeutic benefits, and clinical evidence indices for the 18 core Ayurvedic herbs.
            </p>
          </div>
          <span className="badge badge-info">
            {filteredHerbs.length} Herbs Loaded
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
          {/* Search bar */}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              placeholder="Search by herb name, botanical name, or active compounds..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-light)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                outline: 'none',
                fontFamily: 'var(--font-body)',
              }}
            />
          </div>

          {/* Disease filter */}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Filter size={16} style={{ position: 'absolute', left: '12px', color: 'var(--text-muted)' }} />
            <select
              value={selectedDisease}
              onChange={(e) => setSelectedDisease(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 0.75rem 0.75rem 2.25rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-light)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                outline: 'none',
                fontFamily: 'var(--font-body)',
                cursor: 'pointer',
              }}
            >
              {uniqueDiseases.map(disease => (
                <option key={disease} value={disease} style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>
                  Condition: {disease}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <div className="loading-text">Loading Ayurvedic database...</div>
        </div>
      )}

      {error && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', border: '1px solid rgba(239,68,68,0.2)' }}>
          <AlertCircle size={40} style={{ color: '#ef4444', marginBottom: '1rem' }} />
          <h3 style={{ color: 'var(--text-primary)' }}>Error Loading Database</h3>
          <p className="upload-subtext" style={{ marginTop: '0.5rem' }}>{error}</p>
        </div>
      )}

      {/* Grid of Cards */}
      {!loading && !error && (
        <div className="grid-3">
          {filteredHerbs.map(herb => (
            <div key={herb.name} className="glass-card herb-card">
              <div className="herb-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <span className="herb-title">{herb.name}</span>
                  <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>
                    {herb.evidence_level.split(' ')[0]} Evidence
                  </span>
                </div>
                <div className="herb-scientific">{herb.botanical_name}</div>
                <div className="herb-meta">Family: {herb.family}</div>
              </div>

              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {/* Active Compounds */}
                <div className="herb-detail-item">
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Layers size={13} style={{ color: 'var(--primary)' }} />
                    Active Compounds
                  </span>
                  <div className="tag-container">
                    {herb.active_compounds.map(c => (
                      <span key={c} className="tag">{c}</span>
                    ))}
                  </div>
                </div>

                {/* Phytochemicals */}
                <div className="herb-detail-item">
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Activity size={13} style={{ color: 'var(--secondary)' }} />
                    Phytochemical Group
                  </span>
                  <div className="tag-container">
                    {herb.phytochemicals.map(p => (
                      <span key={p} className="tag" style={{ border: '1px solid rgba(13, 148, 136, 0.2)' }}>{p}</span>
                    ))}
                  </div>
                </div>

                {/* Skincare Benefits */}
                <div className="herb-detail-item">
                  <span className="detail-label">Skincare Benefits</span>
                  <div className="tag-container">
                    {herb.benefits.map(b => (
                      <span key={b} className="tag" style={{ background: 'rgba(16, 185, 129, 0.05)', borderColor: 'rgba(16, 185, 129, 0.2)', color: 'var(--text-primary)' }}>
                        {b}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Contraindications */}
                <div className="herb-detail-item">
                  <span className="detail-label">Contraindications</span>
                  <span className="detail-value" style={{ fontSize: '0.8rem', color: herb.contraindications.includes('None') ? 'var(--text-secondary)' : '#f59e0b' }}>
                    {herb.contraindications.join(', ')}
                  </span>
                </div>

                {/* Preparation */}
                <div className="herb-detail-item" style={{ borderTop: '1px solid var(--border-light)', paddingTop: '0.5rem', marginTop: 'auto' }}>
                  <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <FileText size={13} style={{ color: 'var(--text-muted)' }} />
                    Suggested Preparation
                  </span>
                  <span className="detail-value" style={{ fontSize: '0.8rem' }}>{herb.preparation_method}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && filteredHerbs.length === 0 && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
          <BookOpen size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
          <h3>No matching herbs found</h3>
          <p className="upload-subtext" style={{ marginTop: '0.5rem' }}>Try adjusting your search query or selecting a different skin condition filter.</p>
        </div>
      )}
    </div>
  );
}
