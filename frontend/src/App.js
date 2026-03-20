import React, { useState } from 'react';
import './App.css';

const API = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [risks, setRisks] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');

  const uploadContract = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API}/contracts/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setContract(data);

      // Fetch risks
      const riskRes = await fetch(`${API}/contracts/${data.contract_name}/risks`);
      const riskData = await riskRes.json();
      setRisks(riskData.risks || []);
    } catch (err) {
      alert('Error uploading: ' + err.message);
    }
    setLoading(false);
  };

  const askQuestion = async () => {
    if (!question.trim() || !contract) return;

    const userMsg = { role: 'user', text: question };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch(`${API}/contracts/${contract.contract_name}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question }),
      });
      const data = await res.json();

      const botMsg = {
        role: 'assistant',
        text: data.answer,
        sources: data.sources,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error: ' + err.message }]);
    }
    setLoading(false);
  };

  const severityColor = (severity) => {
    if (severity === 'High') return '#e74c3c';
    if (severity === 'Medium') return '#f39c12';
    return '#27ae60';
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Legal Contract Analyzer</h1>
        <p>RAG-powered contract analysis with risk highlighting</p>
      </header>

      {!contract ? (
        <div className="upload-section">
          <div className="upload-box">
            <h2>Upload a Contract</h2>
            <p>Supports PDF and DOCX files</p>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={uploadContract} disabled={!file || loading}>
              {loading ? 'Processing...' : 'Upload & Analyze'}
            </button>
            {loading && <p className="loading-text">Extracting, chunking, embedding, and scanning for risks... This may take a few minutes.</p>}
          </div>
        </div>
      ) : (
        <div className="main-content">
          <div className="contract-info">
            <span>📄 {contract.filename}</span>
            <span>{contract.pages} pages</span>
            <span>{contract.chunks} chunks</span>
            <span style={{color: contract.risks_found > 0 ? '#e74c3c' : '#27ae60'}}>
              {contract.risks_found} risks found
            </span>
          </div>

          <div className="tabs">
            <button
              className={activeTab === 'chat' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('chat')}
            >
              Chat Q&A
            </button>
            <button
              className={activeTab === 'risks' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('risks')}
            >
              Risk Report ({risks.length})
            </button>
          </div>

          {activeTab === 'chat' && (
            <div className="chat-section">
              <div className="messages">
                {messages.length === 0 && (
                  <div className="empty-state">
                    <p>Ask a question about your contract</p>
                    <div className="suggestions">
                      {['What is confidential information?',
                        'Can the company assign its rights?',
                        'What happens if there is a breach?',
                        'How long do obligations last?'
                      ].map((q, i) => (
                        <button key={i} className="suggestion" onClick={() => setQuestion(q)}>
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {messages.map((msg, i) => (
                  <div key={i} className={`message ${msg.role}`}>
                    <div className="message-text">{msg.text}</div>
                    {msg.sources && (
                      <div className="sources">
                        <p className="sources-title">Sources:</p>
                        {msg.sources.map((s, j) => (
                          <div key={j} className="source-card">
                            <div className="source-heading">{s.heading}</div>
                            <div className="source-text">{s.text.substring(0, 200)}...</div>
                            <div className="source-score">Relevance: {Math.abs(s.score).toFixed(2)}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {loading && <div className="message assistant"><div className="message-text">Thinking...</div></div>}
              </div>

              <div className="input-row">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
                  placeholder="Ask about the contract..."
                />
                <button onClick={askQuestion} disabled={loading || !question.trim()}>
                  Send
                </button>
              </div>
            </div>
          )}

          {activeTab === 'risks' && (
            <div className="risks-section">
              {risks.length === 0 ? (
                <p className="no-risks">No risky clauses detected.</p>
              ) : (
                risks.map((r, i) => (
                  <div key={i} className="risk-card">
                    <div className="risk-header">
                      <span className="risk-severity" style={{background: severityColor(r.severity)}}>
                        {r.severity}
                      </span>
                      <span className="risk-category">{r.category}</span>
                    </div>
                    <p className="risk-explanation">{r.explanation}</p>
                    <p className="risk-clause">{r.text.substring(0, 200)}...</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;