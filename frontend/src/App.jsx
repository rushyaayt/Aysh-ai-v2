import React, { useState, useEffect } from 'react'

export default function App() {
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: "Hey there! 👋 I'm Aysh AI v2. I can edit photos & videos (including my signature Aura Edit style), generate visuals, or run code in our sandbox. What are we creating today?" }
  ])
  const [chatInput, setChatInput] = useState('')
  const [aiMode, setAiMode] = useState('Normal')
  const [selectedFile, setSelectedFile] = useState(null)
  const [activeMediaUrl, setActiveMediaUrl] = useState(null)
  const [activeMediaType, setActiveMediaType] = useState(null)
  const [fileList, setFileList] = useState([])
  const [code, setCode] = useState("print('Hello from Aysh AI v2 Sandbox!')")
  const [consoleOutput, setConsoleOutput] = useState('')
  const [uploadProgress, setUploadProgress] = useState(null)

  useEffect(() => {
    fetchFiles()
  }, [])

  const fetchFiles = async () => {
    try {
      const res = await fetch('/api/files')
      const data = await res.json()
      if (data.files) {
        setFileList(data.files)
      }
    } catch (err) {
      console.error('Error fetching file list:', err)
    }
  }

  const handleSendMessage = async (e) => {
    e?.preventDefault()
    if (!chatInput.trim()) return

    const userText = chatInput
    setMessages(prev => [...prev, { sender: 'user', text: userText }])
    setChatInput('')

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          file_context: selectedFile,
          ai_mode: aiMode
        })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { sender: 'assistant', text: data.reply }])

      if (data.output_file) {
        setActiveMediaUrl(data.output_file)
        if (data.output_file.endsWith('.mp4') || data.output_file.endsWith('.webm')) {
          setActiveMediaType('video')
        } else {
          setActiveMediaType('image')
        }
        fetchFiles()
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'assistant', text: "Oops, something went wrong communicating with backend!" }])
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const chunkSize = 8 * 1024 * 1024 // 8MB
    const totalChunks = Math.ceil(file.size / chunkSize)
    const uploadId = Math.random().toString(36).substring(2)

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize
      const end = Math.min(file.size, start + chunkSize)
      const chunk = file.slice(start, end)

      const formData = new FormData()
      formData.append('file', chunk)
      formData.append('upload_id', uploadId)
      formData.append('chunk_index', i)
      formData.append('total_chunks', totalChunks)
      formData.append('filename', file.name)

      setUploadProgress(Math.round(((i + 1) / totalChunks) * 100))

      await fetch('/api/upload_chunk', {
        method: 'POST',
        body: formData
      })
    }

    setUploadProgress(null)
    setSelectedFile(file.name)
    fetchFiles()
  }

  const handleRunCode = async () => {
    setConsoleOutput('Executing code in sandbox...')
    try {
      const res = await fetch('/api/sandbox/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })
      const data = await res.json()
      if (data.success) {
        setConsoleOutput(data.stdout || '(Code executed with no output)')
      } else {
        setConsoleOutput(data.stderr || 'Execution failed')
      }
    } catch (err) {
      setConsoleOutput('Execution error: ' + err.message)
    }
  }

  return (
    <div>
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-badge">v2.0</span>
          <h1 className="app-title">Aysh AI Studio & Sandbox</h1>
        </div>
        <div className="ai-mode-container">
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>🧠 Mode:</span>
          <select
            value={aiMode}
            onChange={(e) => setAiMode(e.target.value)}
            className="ai-mode-select"
          >
            <option value="Normal">⚡ Normal</option>
            <option value="Pro">🌟 Pro</option>
            <option value="Advance">🚀 Advance</option>
            <option value="Powerful Intelligent">🔥 Powerful Intelligent</option>
          </select>
        </div>
      </header>

      <main className="studio-grid">
        {/* Left Panel: Sandbox Workspace */}
        <section className="panel">
          <div className="panel-header">
            <span>⚙️ Sandbox Workspace</span>
          </div>
          <div className="panel-content">
            <div style={{ marginBottom: '16px' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                Upload Large Media File (&gt;2GB supported):
              </label>
              <input type="file" onChange={handleFileUpload} style={{ fontSize: '12px' }} />
              {uploadProgress !== null && (
                <p style={{ fontSize: '12px', color: 'var(--accent-cyan)', marginTop: '4px' }}>
                  Uploading: {uploadProgress}%
                </p>
              )}
              {selectedFile && (
                <p style={{ fontSize: '12px', color: '#00ff66', marginTop: '4px' }}>
                  Active File Context: {selectedFile}
                </p>
              )}
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Python Sandbox Code:</span>
                <button className="btn" style={{ padding: '4px 8px', fontSize: '12px' }} onClick={handleRunCode}>
                  Run Code
                </button>
              </div>
              <textarea
                className="code-area"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </div>

            <div>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                Console Output:
              </span>
              <pre style={{ background: '#000', padding: '10px', borderRadius: '6px', fontSize: '12px', color: '#00f0ff', minHeight: '80px', overflowX: 'auto' }}>
                {consoleOutput || 'Ready for script execution...'}
              </pre>
            </div>

            <div style={{ marginTop: '16px' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                Sandbox Files:
              </span>
              <div className="file-list">
                {fileList.map((f) => (
                  <div key={f.name} className="file-item">
                    <span>{f.name}</span>
                    <a href={`/api/download/${f.name}`} download style={{ color: 'var(--accent-cyan)', fontSize: '12px' }}>
                      Download
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Center Panel: Live Visual Preview */}
        <section className="panel">
          <div className="panel-header">
            <span>🎨 Visual Preview Studio</span>
            {activeMediaUrl && (
              <a
                href={`/api/download/${activeMediaUrl.split('/').pop()}`}
                download
                className="btn btn-secondary"
                style={{ fontSize: '12px', padding: '4px 10px', textDecoration: 'none' }}
              >
                📥 Download Output
              </a>
            )}
          </div>
          <div className="panel-content">
            <div className="preview-container">
              {activeMediaUrl ? (
                activeMediaType === 'video' ? (
                  <video src={activeMediaUrl} controls autoPlay className="media-preview" />
                ) : (
                  <img src={activeMediaUrl} alt="Preview" className="media-preview" />
                )
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  No media generated or edited yet. Ask Aysh AI in chat to create or edit photos/videos!
                </p>
              )}
            </div>
          </div>
        </section>

        {/* Right Panel: Friendly AI Chat */}
        <section className="panel">
          <div className="panel-header">
            <span>💬 Friendly AI Assistant</span>
          </div>
          <div className="chat-messages">
            {messages.map((m, idx) => (
              <div key={idx} className={`message-bubble ${m.sender}`}>
                {m.text}
              </div>
            ))}
          </div>
          <form className="chat-input-area" onSubmit={handleSendMessage}>
            <input
              type="text"
              className="chat-input"
              placeholder="e.g. edit photo in aura style, generate video..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="submit" className="btn">Send</button>
          </form>
        </section>
      </main>
    </div>
  )
}
