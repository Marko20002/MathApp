import { useState, useEffect } from 'react';
import api from '../api';

const INPUT_ICON   = { text: '✏️', image: '🖼️', pdf: '📄' };
const DOMAIN_COLOR = { calculus: 'text-blue-400', probability: 'text-purple-400',
                       discrete: 'text-green-400', unknown: 'text-slate-400' };

export default function SolveHistory() {
  const [stats, setStats]     = useState(null);
  const [history, setHistory] = useState([]);
  const [expanded, setExpanded] = useState(null);   // id of expanded item
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/api/solver/stats/'), api.get('/api/solver/history/')])
      .then(([sRes, hRes]) => { setStats(sRes.data); setHistory(hRes.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <aside className="w-72 flex-shrink-0 border-l border-slate-800 p-5"
           style={{ backgroundColor: '#0a0f1e', height: 'calc(100vh - 60px)' }}>
      <p className="text-slate-600 text-sm text-center mt-8">Loading…</p>
    </aside>
  );

  return (
    <aside className="w-72 flex-shrink-0 border-l border-slate-800 p-5 overflow-y-auto"
           style={{ backgroundColor: '#0a0f1e', height: 'calc(100vh - 60px)' }}>

      {/* Stats */}
      {stats && (
        <div className="rounded-xl border border-slate-800 p-4 mb-5"
             style={{ backgroundColor: '#0d1526' }}>
          <p className="text-slate-500 text-xs uppercase tracking-widest font-semibold mb-3">Your Stats</p>
          <div className="text-center mb-3">
            <span className="text-4xl font-bold text-white">{stats.total}</span>
            <p className="text-slate-500 text-xs mt-1">Problems Solved</p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[['✏️', stats.text_solves,  'Text'],
              ['🖼️', stats.image_solves, 'Image'],
              ['📄', stats.pdf_solves,   'PDF']].map(([icon, val, label]) => (
              <div key={label} className="text-center rounded-lg p-2" style={{ backgroundColor: '#080d1a' }}>
                <p className="text-sm">{icon}</p>
                <p className="text-lg font-bold text-white">{val}</p>
                <p className="text-slate-600 text-xs">{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History list */}
      <p className="text-slate-500 text-xs uppercase tracking-widest font-semibold mb-3">History</p>

      {history.length === 0 ? (
        <p className="text-slate-600 text-sm text-center mt-4">No solves yet. Try a problem!</p>
      ) : (
        <div className="space-y-2">
          {history.map(h => (
            <div key={h.id} className="rounded-xl border border-slate-800 p-3"
                 style={{ backgroundColor: '#0d1526' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm">{INPUT_ICON[h.input_type] || '❓'}</span>
                <span className={`text-xs font-semibold capitalize ${DOMAIN_COLOR[h.domain]}`}>
                  {h.domain}
                </span>
              </div>

              {h.problem_text && (
                <p className="text-slate-400 text-xs mb-1 line-clamp-2">{h.problem_text}</p>
              )}

              <p className="text-slate-600 text-xs mb-2">
                {new Date(h.created_at).toLocaleDateString(undefined, {
                  day: '2-digit', month: 'short', year: 'numeric',
                })}
              </p>

              <button onClick={() => setExpanded(expanded === h.id ? null : h.id)}
                      className="w-full py-1.5 rounded-lg border border-slate-700 hover:border-blue-500 text-slate-400 hover:text-white text-xs transition-colors">
                {expanded === h.id ? '▲ Hide' : '▼ Show solution'}
              </button>

              {expanded === h.id && (
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <p className="text-slate-400 text-xs solution-text max-h-48 overflow-y-auto">
                    {h.solution}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}
