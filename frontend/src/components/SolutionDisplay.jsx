import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

const DOMAIN_STYLE = {
  calculus:    { color: 'text-blue-400',   bg: 'bg-blue-500/10   border-blue-500/30',   label: 'Calculus' },
  probability: { color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/30', label: 'Probability' },
  discrete:    { color: 'text-green-400',  bg: 'bg-green-500/10  border-green-500/30',  label: 'Discrete Math' },
  unknown:     { color: 'text-slate-400',  bg: 'bg-slate-500/10  border-slate-500/30',  label: 'Math' },
};

// Split raw solution text into typed segments: plain | inline \(...\) | block \[...\]
function parseSegments(text) {
  const segments = [];
  const re = /\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      segments.push({ type: 'text', content: text.slice(last, m.index) });
    }
    const raw = m[0];
    if (raw.startsWith('\\[')) {
      segments.push({ type: 'block',  content: raw.slice(2, -2).trim() });
    } else {
      segments.push({ type: 'inline', content: raw.slice(2, -2).trim() });
    }
    last = m.index + raw.length;
  }
  if (last < text.length) {
    segments.push({ type: 'text', content: text.slice(last) });
  }
  return segments;
}

function renderSegment(seg, i) {
  if (seg.type === 'block') {
    return (
      <div key={i} className="my-3 overflow-x-auto">
        <BlockMath math={seg.content} />
      </div>
    );
  }
  if (seg.type === 'inline') {
    return <InlineMath key={i} math={seg.content} />;
  }
  // Plain text — render markdown headings and line breaks
  const lines = seg.content.split('\n');
  return lines.map((line, j) => {
    if (line.startsWith('### ')) {
      return (
        <p key={`${i}-${j}`} className="font-semibold text-white mt-4 mb-1">
          {line.slice(4)}
        </p>
      );
    }
    if (line.startsWith('## ')) {
      return (
        <p key={`${i}-${j}`} className="font-bold text-white text-base mt-5 mb-1">
          {line.slice(3)}
        </p>
      );
    }
    return (
      <span key={`${i}-${j}`}>
        {line}
        {j < lines.length - 1 && <br />}
      </span>
    );
  });
}

export default function SolutionDisplay({ solution, domain }) {
  const d = DOMAIN_STYLE[domain] || DOMAIN_STYLE.unknown;
  const segments = parseSegments(solution);

  const copyToClipboard = () => navigator.clipboard.writeText(solution);

  return (
    <div className="rounded-2xl border border-slate-800" style={{ backgroundColor: '#0d1526' }}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <span className="text-white font-semibold">Solution</span>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${d.bg} ${d.color}`}>
            {d.label}
          </span>
        </div>
        <button onClick={copyToClipboard}
                className="text-slate-500 hover:text-white text-xs transition-colors px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600">
          Copy
        </button>
      </div>

      <div className="px-6 py-5 text-slate-300 text-sm leading-relaxed">
        {segments.map((seg, i) => renderSegment(seg, i))}
      </div>
    </div>
  );
}
