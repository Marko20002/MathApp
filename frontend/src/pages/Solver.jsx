import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';
import MathText from '../components/MathText';
import '../chat.css';

const subjects = { CALCULUS: 'Calculus', PROBABILITY: 'Probability', DISCRETE: 'Discrete mathematics', OTHER: 'Other mathematics', UNKNOWN: 'Uncertain' };
const samples = ['Evaluate the limit of 1/x as x tends to infinity.', 'What is the probability of two heads in three fair coin flips?', 'Explain why a tree with n vertices has n − 1 edges.'];
const failure = (error) => error.response?.data?.error || error.response?.data?.detail ||
  (error.response?.data ? Object.values(error.response.data).flat().join(' ') : 'Could not connect. Check the backend and try again.');

function Icon({ name, size = 20 }) {
  const paths = {
    plus: <path d="M12 5v14M5 12h14" />,
    send: <path d="M12 19V5m-6 6 6-6 6 6" />,
    chat: <path d="M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-6 3V6a2 2 0 0 1 2-2Z" />,
    menu: <path d="M4 6h16M4 12h16M4 18h16" />,
    close: <path d="m6 6 12 12M6 18 18 6" />,
    attach: <path d="m9 13 6-6a3 3 0 0 1 4 4l-9 9a5 5 0 0 1-7-7L13 3" />,
    chart: <path d="M4 19h16M7 15v-4m5 4V5m5 10V8" />,
    download: <path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5" />,
    logout: <path d="M9 5H4v14h5m4-14 7 7-7 7m-5-7h12" />,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function Insights({ analysis, staff, onReference }) {
  const [answer, setAnswer] = useState('');
  const [label, setLabel] = useState('CALCULUS');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    setAnswer(analysis?.reference?.answer || '');
    setLabel(analysis?.reference?.label || 'CALCULUS');
    setError('');
  }, [analysis?.problem_id, analysis?.reference?.answer]);
  if (!analysis) return <div className="insight-empty"><div className="insight-symbol"><Icon name="chart" size={28} /></div><h3>A closer look at your question</h3><p>Send a problem to compare your local classifier with OpenAI’s assessment.</p><div className="insight-note">The local model identifies subjects. It does not solve or verify answers.</div></div>;
  const c = analysis.classification || {};
  const scores = c.scores || {};
  const confidence = c.confidence ?? (Object.keys(scores).length ? Math.max(...Object.values(scores)) : null);
  const reference = analysis.reference;
  async function save(event) {
    event.preventDefault(); setSaving(true); setError('');
    try {
      const response = await api.patch('/api/solver/problems/' + analysis.problem_id + '/reference/', { answer, label });
      onReference(response.data);
    } catch (err) { setError(failure(err)); }
    finally { setSaving(false); }
  }
  return <>
    <section className="insight-section">
      <div className="eyebrow">YOUR LOCAL CLASSIFIER</div>
      <div className="prediction-heading"><h3>{subjects[c.label] || 'Uncertain'}</h3><span className="small-tag">ML</span></div>
      <p className="confidence-number">{confidence === null ? '—' : (confidence * 100).toFixed(1) + '%'}<span>top-class confidence</span></p>
      {['CALCULUS', 'PROBABILITY', 'DISCRETE'].map(key => <div className="score" key={key}>
        <div><span>{subjects[key]}</span><span>{scores[key] == null ? '—' : (scores[key] * 100).toFixed(1) + '%'}</span></div>
        <div className="score-track"><div style={{ width: ((scores[key] || 0) * 100) + '%' }} /></div>
      </div>)}
      <p className="subtle">Confidence is an uncalibrated model score, not measured accuracy. The classifier reads only this message; follow-ups may be uncertain.</p>
      <span className="version">{c.model_version}{c.experimental ? ' · experimental' : ''}</span>
    </section>
    <section className="insight-section">
      <div className="eyebrow">OPENAI ASSESSMENT</div>
      <h3>{subjects[analysis.openai_subject] || 'Not recorded'}</h3>
      {c.label !== 'UNKNOWN' && analysis.openai_subject && <p className="comparison">{c.label === analysis.openai_subject ? 'Same subject as the local model' : 'Different subject from the local model'}</p>}
      <div className="answer-preview"><MathText text={analysis.final_answer || 'No separate final answer was recorded for this older response.'} /></div>
      <p className="subtle">Generated answer · not independently verified</p>
    </section>
    <section className="insight-section">
      <div className="eyebrow">REVIEWED REFERENCE ANSWER</div>
      {reference?.reviewed_at ? <><h3>{subjects[reference.label]}</h3><MathText text={reference.answer} /><p className="subtle">Saved by a human reviewer. Compare with the generated answer above; no automatic correctness score.</p></> :
        <p className="subtle">No reviewed answer yet. OpenAI’s output is not ground truth.</p>}
      {staff && <details className="reference-editor"><summary>{reference?.reviewed_at ? 'Edit reference' : 'Add a reference answer'}</summary><form onSubmit={save}>
        <label>Reviewed subject<select value={label} onChange={e => setLabel(e.target.value)}>{Object.entries(subjects).map(([key, value]) => <option key={key} value={key}>{value}</option>)}</select></label>
        <label>Reference answer<textarea value={answer} onChange={e => setAnswer(e.target.value)} maxLength={20000} required rows={4} /></label>
        <button className="secondary-button" disabled={saving}>{saving ? 'Saving…' : 'Save reference'}</button>
        {error && <p role="alert">{error}</p>}
      </form></details>}
    </section>
    <section className="insight-section">
      <div className="eyebrow">CONVERSATION MEMORY</div>
      <div className="memory-status"><span className="status-dot" />{analysis.context?.mode === 'compact' ? 'Compact memory + recent turns' : 'Full recent conversation'}</div>
      <p className="subtle">{analysis.context?.mode === 'compact' ? 'Older details are summarized and may be omitted. Restate exact equations if needed. Your full transcript remains saved.' : 'Follow-ups use earlier messages in this chat. Long chats switch to a compact memory.'}</p>
      <dl className="usage-list">
        <div><dt>Input tokens</dt><dd>{analysis.usage?.input_tokens ?? '—'}</dd></div>
        <div><dt>Cached input</dt><dd>{analysis.usage?.cached_input_tokens ?? '—'}</dd></div>
        <div><dt>Output tokens</dt><dd>{analysis.usage?.output_tokens ?? '—'}</dd></div>
      </dl>
      <p className="subtle">{analysis.provider_model} · one API request per answer</p>
    </section>
  </>;
}

export default function Solver() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [nextChats, setNextChats] = useState(null);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [nextMessages, setNextMessages] = useState(null);
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [drawer, setDrawer] = useState(false);
  const [panel, setPanel] = useState(false);
  const end = useRef(null);
  const input = useRef(null);
  const textarea = useRef(null);
  const generation = useRef(0);
  const submitLock = useRef(false);

  useEffect(() => {
    if (!file?.type.startsWith('image/')) { setImagePreview(null); return; }
    const url = URL.createObjectURL(file);
    setImagePreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  async function refreshChats() {
    const response = await api.get('/api/solver/conversations/');
    setConversations(response.data.results); setNextChats(response.data.next);
  }
  useEffect(() => {
    let alive = true;
    api.get('/api/auth/me/').then(async response => {
      if (!alive) return;
      setUser(response.data);
      await refreshChats();
    }).catch(err => { if (alive) setError(failure(err)); });
    return () => { alive = false; };
  }, []);
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages.at(-1)?.id, sending]);
  useEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = 'auto';
      textarea.current.style.height = Math.min(textarea.current.scrollHeight, 180) + 'px';
    }
  }, [text]);

  function newChat() {
    if (sending) return;
    generation.current += 1; setActive(null); setMessages([]); setNextMessages(null);
    setSelected(null); setError(''); setFile(null); setText(''); setLoading(false); setDrawer(false);
    textarea.current?.focus();
  }
  async function openChat(id) {
    if (sending) return;
    const request = ++generation.current;
    setActive(id); setLoading(true); setMessages([]); setNextMessages(null); setSelected(null);
    setText(''); setFile(null); setError(''); setDrawer(false);
    try {
      const response = await api.get('/api/solver/conversations/' + id + '/messages/');
      if (generation.current !== request) return;
      setMessages([...response.data.results].reverse()); setNextMessages(response.data.next);
    } catch (err) { if (generation.current === request) setError(failure(err)); }
    finally { if (generation.current === request) setLoading(false); }
  }
  async function earlier() {
    setLoading(true);
    const request = generation.current;
    try {
      const response = await api.get(nextMessages);
      if (generation.current !== request) return;
      setMessages(previous => [...response.data.results.reverse(), ...previous]);
      setNextMessages(response.data.next);
    } catch (err) { if (generation.current === request) setError(failure(err)); }
    finally { if (generation.current === request) setLoading(false); }
  }
  function acceptAttachment(chosen) {
    if (!chosen || sending || loading) return;
    if (file) { setError('Remove the current attachment before adding another.'); return; }
    if (!['image/png', 'image/jpeg', 'image/webp', 'application/pdf'].includes(chosen.type)) {
      setError('Choose a PNG, JPEG, WebP image, or PDF.'); return;
    }
    if (chosen.size > 10000000) { setError('Please choose a file below 10 MB.'); return; }
    setFile(chosen); setError('');
  }
  function attach(event) {
    const chosen = event.target.files?.[0]; event.target.value = '';
    acceptAttachment(chosen);
  }
  function pasteImage(event) {
    const items = Array.from(event.clipboardData?.items || []);
    const imageItems = items.filter(item => item.kind === 'file' && item.type.startsWith('image/'));
    const images = imageItems.length
      ? imageItems.map(item => item.getAsFile()).filter(Boolean)
      : Array.from(event.clipboardData?.files || []).filter(item => item.type.startsWith('image/'));
    // Let the browser insert ordinary text/LaTeX normally. Never fetch URLs or
    // HTML images from the clipboard, and upload only when the user presses Send.
    if (!images.length) return;
    event.preventDefault();
    if (images.length > 1) { setError('Paste one image at a time.'); return; }
    acceptAttachment(images[0]);
  }
  async function send(event) {
    event.preventDefault();
    if (submitLock.current || loading || (!text.trim() && !file)) return;
    submitLock.current = true; setSending(true); setError(''); setSelected(null);
    const question = text;
    const attachment = file;
    try {
      let payload;
      if (attachment) {
        payload = new FormData();
        payload.append('file', attachment);
        payload.append('input_type', attachment.type === 'application/pdf' ? 'pdf' : 'image');
        payload.append('content', question);
        if (active) payload.append('conversation_id', active);
      } else {
        payload = { content: question, ...(active ? { conversation_id: active } : {}) };
      }
      const response = await api.post('/api/solver/solve/', payload);
      setMessages(previous => [...previous, ...response.data.messages]);
      setActive(response.data.conversation_id); setText(''); setFile(null);
      try { await refreshChats(); } catch { setError('Answer saved. The chat list could not refresh; reload when convenient.'); }
    } catch (err) { setError(failure(err)); }
    finally { submitLock.current = false; setSending(false); textarea.current?.focus(); }
  }
  async function exportChat() {
    try {
      const response = await api.get('/api/solver/conversations/' + active + '/export/', { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a'); link.href = url; link.download = 'mathapp-chat-' + active + '.json.gz';
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch { setError('Could not download this conversation.'); }
  }
  async function moreChats() {
    try {
      const response = await api.get(nextChats);
      setConversations(previous => [...previous, ...response.data.results]); setNextChats(response.data.next);
    } catch (err) { setError(failure(err)); }
  }
  const inspected = messages.find(m => m.id === selected) || [...messages].reverse().find(m => m.role === 'assistant');
  const analysis = inspected?.analysis;
  function referenceSaved(reference) {
    setMessages(previous => previous.map(m => m.id === inspected.id ? { ...m, analysis: { ...m.analysis, reference } } : m));
  }
  function logout() {
    localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); navigate('/login');
  }
  return <div className="chat-app">
    {drawer && <button className="mobile-scrim" onClick={() => setDrawer(false)} aria-label="Close conversations" />}
    <aside className={'chat-sidebar ' + (drawer ? 'is-open' : '')}>
      <div className="brand"><span className="brand-mark">∑</span><span>MathApp<span className="brand-caption">A little more understanding.</span></span></div>
      <button className="new-chat" onClick={newChat} disabled={sending}><Icon name="plus" />New chat<span>↗</span></button>
      <div className="sidebar-label">YOUR CONVERSATIONS</div>
      <nav aria-label="Saved conversations">
        {!conversations.length && <p className="sidebar-empty">Your conversations will appear here.</p>}
        {conversations.map(chat => <button key={chat.id} disabled={sending} className={'conversation-link ' + (chat.id === active ? 'active' : '')} onClick={() => openChat(chat.id)} title={chat.title}><Icon name="chat" size={17} /><span>{chat.title}</span></button>)}
        {nextChats && <button className="text-button" onClick={moreChats}>More conversations</button>}
      </nav>
      <div className="sidebar-bottom"><div className="private-note"><span className="status-dot" />Saved in your workspace</div>
        <div className="account"><Link to="/profile"><span className="avatar">{user?.username?.slice(0, 1).toUpperCase() || 'M'}</span><span>{user?.username || 'Your account'}<small>{user?.is_staff ? 'Owner' : 'Member'}</small></span></Link><button className="icon-button" onClick={logout} aria-label="Log out"><Icon name="logout" size={18} /></button></div>
      </div>
    </aside>
    <main className="chat-main">
      <header className="chat-header"><div><button className="icon-button mobile-menu" onClick={() => setDrawer(true)} aria-label="Open conversations"><Icon name="menu" /></button><span className="header-title">MathApp <span className="header-model">/ Math companion</span></span></div><div className="header-actions">{active && <button className="icon-button" title="Download compressed conversation (.json.gz)" aria-label="Download compressed conversation" onClick={exportChat}><Icon name="download" /></button>}<button className={'icon-button ' + (panel ? 'selected' : '')} title="Question insights" aria-label="Toggle question insights" onClick={() => setPanel(!panel)}><Icon name="chart" /></button></div></header>
      <div className="message-scroll" aria-label="Conversation">
        {!messages.length && !loading && !sending && <div className="welcome"><div className="welcome-mark">∑</div><div className="eyebrow">SPACE TO THINK</div><h1>Let’s make it<br /><span>make sense.</span></h1><p>Bring a problem. Ask why. Work through it together.</p><div className="suggestions">{['Explore a limit', 'Think in probabilities', 'Untangle a proof'].map((title, i) => <button key={title} onClick={() => { setText(samples[i]); textarea.current?.focus(); }}><span className="suggestion-number">0{i + 1}</span><strong>{title}</strong><span>↗</span></button>)}</div></div>}
        {nextMessages && <button className="load-earlier" onClick={earlier} disabled={loading}>{loading ? 'Loading…' : 'Load earlier messages'}</button>}
        {loading && !messages.length && <p className="loading-note">Opening conversation…</p>}
        <div className="messages">{messages.map(message => <article key={message.id} className={'message ' + message.role + (inspected?.id === message.id ? ' inspected' : '')}>
          {message.role === 'assistant' && <div className="assistant-label"><span className="mini-mark">∑</span>MathApp</div>}
          <div className="message-content">{message.role === 'assistant' ? <MathText text={message.content} /> : <div className="user-text">{message.content}</div>}</div>
          {message.role === 'assistant' && <div className="message-actions"><button onClick={() => { setSelected(message.id); setPanel(true); }}>View insights</button><button onClick={() => navigator.clipboard.writeText(message.content).catch(() => setError('Clipboard is unavailable in this browser.'))}>Copy</button></div>}
        </article>)}
        {sending && <><article className="message user"><div className="message-content user-text">{file && <div className="pending-file">{file.name}</div>}{text}</div></article><div className="thinking" role="status"><span className="mini-mark">∑</span><span className="thinking-dots">Working through it<span>•••</span></span></div></>}
        <div ref={end} /></div>
      </div>
      <div className="composer-area">
        {error && <div className="chat-error" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}
        <form className="composer" onSubmit={send}>
          {file && <div className="file-chip" role="status">{imagePreview ? <img className="attachment-thumbnail" src={imagePreview} alt="Attached image preview" /> : <Icon name="attach" size={16} />}<span>{file.name || 'Pasted image'}</span><button type="button" disabled={sending} onClick={() => { setFile(null); setError(''); }} aria-label="Remove attachment">×</button></div>}
          <textarea ref={textarea} aria-label="Message MathApp" placeholder={messages.length ? 'Ask a follow-up…' : 'Ask anything about mathematics…'} value={text} maxLength={20000} disabled={sending || loading} rows={1} onPaste={pasteImage} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(e); } }} />
          <div className="composer-controls"><div><button type="button" className="icon-button" disabled={sending || loading} onClick={() => input.current?.click()} aria-label="Attach image or PDF"><Icon name="plus" /></button><span className="composer-hint">Paste an image with Ctrl+V · up to 10 MB</span></div><button className="send-button" type="submit" aria-label="Send message" disabled={sending || loading || (!text.trim() && !file)}><Icon name="send" /></button></div>
          <input ref={input} type="file" accept="image/png,image/jpeg,image/webp,application/pdf" hidden onChange={attach} />
        </form><p className="composer-footer">MathApp can make mistakes. Check important steps. <span>Shift + Enter for a new line</span></p>
      </div>
    </main>
    <aside className={'insights-panel ' + (panel ? 'is-open' : '')}><header><div><span className="status-dot" /><strong>Question insights</strong></div><button className="icon-button insights-close" onClick={() => setPanel(false)} aria-label="Close insights"><Icon name="close" size={17} /></button></header><div className="insights-body"><Insights analysis={analysis && Object.keys(analysis).length ? analysis : null} staff={user?.is_staff} onReference={referenceSaved} /></div></aside>
  </div>;
}
