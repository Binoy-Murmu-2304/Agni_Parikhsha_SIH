import React, { useState, useRef } from 'react';
import { Upload, File, Loader } from 'lucide-react';

const UploadView = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    
    // In a full implementation, we'd add a mapping step here if needed.
    // For MVP, we rely on the backend auto-detect heuristics.

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      onSuccess(data.lot_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: '600px', margin: '0 auto', marginTop: '2rem' }}>
      <h2 style={{ marginTop: 0 }}>Upload ESS Data</h2>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>
        Upload your burn-in CSV file. The system will auto-detect lot IDs, part IDs, parameters, and timepoints.
      </p>

      <div 
        className="file-upload-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input 
          type="file" 
          accept=".csv" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
        />
        {file ? (
          <div>
            <File size={48} color="var(--primary)" style={{ margin: '0 auto' }} />
            <p style={{ fontWeight: '500', marginTop: '1rem' }}>{file.name}</p>
            <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div>
            <Upload size={48} color="var(--muted)" style={{ margin: '0 auto' }} />
            <p style={{ fontWeight: '500', marginTop: '1rem' }}>Drag & Drop CSV here</p>
            <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>or click to browse</p>
          </div>
        )}
      </div>

      {error && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '0.375rem', border: '1px solid var(--danger)' }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button 
          className="btn" 
          disabled={!file || uploading} 
          onClick={handleUpload}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: (!file || uploading) ? 0.5 : 1 }}
        >
          {uploading ? <Loader className="spin" size={18} /> : null}
          {uploading ? 'Processing...' : 'Upload & Analyze'}
        </button>
      </div>
    </div>
  );
};

export default UploadView;
