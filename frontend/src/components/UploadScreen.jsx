import React from 'react';

function UploadScreen({ file, setFile, onUpload, loading }) {
  return (
    <div className="upload-section">
      <div className="upload-box">
        <h2>Upload a Contract</h2>
        <p>Supports PDF and DOCX files</p>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={onUpload} disabled={!file || loading}>
          {loading ? 'Processing...' : 'Upload & Analyze'}
        </button>
        {loading && (
          <p className="loading-text">
            Extracting, chunking, embedding, and scanning for risks... This may take a few minutes.
          </p>
        )}
      </div>
    </div>
  );
}

export default UploadScreen;