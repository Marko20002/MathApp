import { useState, useRef } from 'react';

const TABS = [
  { id: 'text',  label: '✏️ Text',  desc: 'Type or paste a math problem' },
  { id: 'image', label: '🖼️ Image', desc: 'Upload a photo of a problem' },
  { id: 'pdf',   label: '📄 PDF',   desc: 'Upload a PDF with problems' },
];

export default function SolverInput({ onSolve, solving }) {
  const [tab, setTab]             = useState('text');
  const [text, setText]           = useState('');
  const [ocrEngine, setOcrEngine] = useState('1');
  const [preview, setPreview]     = useState(null);   // base64 preview for image
  const [fileName, setFileName]   = useState('');
  const [fileB64, setFileB64]     = useState('');     // base64 content to send
  const fileRef = useRef();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (ev) => {
      // ev.target.result is "data:image/png;base64,AAAA..."
      // We only want the base64 part after the comma
      const b64 = ev.target.result.split(',')[1];
      setFileB64(b64);
      if (tab === 'image') setPreview(ev.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = () => {
    if (tab === 'text') {
      if (!text.trim()) return;
      onSolve({ input_type: 'text', content: text });
    } else {
      if (!fileB64) return;
      onSolve({ input_type: tab, content: fileB64, ocr_engine: ocrEngine });
    }
  };

  const clearFile = () => {
    setFileB64(''); setFileName(''); setPreview(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  return (
    <div className="rounded-2xl border border-slate-800" style={{ backgroundColor: '#0d1526' }}>

      {/* Tab bar */}
      <div className="flex border-b border-slate-800">
        {TABS.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); clearFile(); setText(''); }}
                  className={`flex-1 py-3.5 text-sm font-semibold transition-colors
                    ${tab === t.id
                      ? 'text-blue-400 border-b-2 border-blue-500'
                      : 'text-slate-500 hover:text-slate-300'}`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="p-6">
        <p className="text-slate-500 text-xs mb-4">
          {TABS.find(t => t.id === tab)?.desc}
        </p>

        {/* Text tab */}
        {tab === 'text' && (
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            rows={5}
            placeholder="e.g. Solve the integral of x² from 0 to 3"
            className="w-full bg-transparent border border-slate-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors resize-none"
          />
        )}

        {/* Image tab */}
        {tab === 'image' && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <label className="cursor-pointer px-4 py-2.5 rounded-xl border border-slate-700 hover:border-blue-500 text-slate-400 hover:text-white text-sm transition-colors">
                Choose Image
                <input ref={fileRef} type="file" accept="image/*"
                       className="hidden" onChange={handleFileChange} />
              </label>
              {fileName && <span className="text-slate-400 text-sm truncate max-w-xs">{fileName}</span>}
            </div>

            <p className="text-slate-500 text-xs">
              EasyOCR will extract the text, then DeepSeek will solve it.
            </p>

            {preview && (
              <img src={preview} alt="preview"
                   className="max-h-48 rounded-xl border border-slate-700 object-contain" />
            )}
          </div>
        )}

        {/* PDF tab */}
        {tab === 'pdf' && (
          <div className="flex items-center gap-3">
            <label className="cursor-pointer px-4 py-2.5 rounded-xl border border-slate-700 hover:border-blue-500 text-slate-400 hover:text-white text-sm transition-colors">
              Choose PDF
              <input ref={fileRef} type="file" accept="application/pdf"
                     className="hidden" onChange={handleFileChange} />
            </label>
            {fileName && (
              <span className="text-slate-400 text-sm truncate max-w-xs">📄 {fileName}</span>
            )}
          </div>
        )}

        {/* Solve button */}
        <button
          onClick={handleSubmit}
          disabled={solving || (tab === 'text' ? !text.trim() : !fileB64)}
          className="mt-5 w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl font-semibold text-sm transition-colors">
          {solving ? '⏳ Solving…' : '▶ Solve'}
        </button>
      </div>
    </div>
  );
}
