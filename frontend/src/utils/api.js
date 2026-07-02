const envUrl = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE_URL = envUrl.endsWith('/') ? envUrl.slice(0, -1) : envUrl;

export async function fetchHerbs() {
  const response = await fetch(`${API_BASE_URL}/api/herbs`);
  if (!response.ok) {
    throw new Error('Failed to fetch herbs database');
  }
  return response.json();
}

export async function predictSkin(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/predict/skin`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to analyze skin image');
  }
  return response.json();
}

export async function predictLeaf(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/predict/leaf`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to analyze leaf image');
  }
  return response.json();
}

export async function predictJoint(skinFile, leafFile) {
  const formData = new FormData();
  formData.append('skin_file', skinFile);
  formData.append('leaf_file', leafFile);
  
  const response = await fetch(`${API_BASE_URL}/api/predict/joint`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to perform joint evaluation');
  }
  return response.json();
}

// ---------------------------------------------------------------------------
// TensorFlow / Keras model endpoints
// ---------------------------------------------------------------------------

export async function fetchTfDatasets() {
  const response = await fetch(`${API_BASE_URL}/api/tf/datasets`);
  if (!response.ok) throw new Error('Failed to fetch TF datasets list');
  return response.json();
}

export async function predictTf(datasetName, file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/tf/predict/${datasetName}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `TF prediction failed for dataset: ${datasetName}`);
  }
  return response.json();
}
