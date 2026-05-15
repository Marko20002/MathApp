import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function Profile() {
  const [user, setUser]   = useState(null);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([api.get('/api/auth/me/'), api.get('/api/solver/stats/')])
      .then(([uRes, sRes]) => { setUser(uRes.data); setStats(sRes.data); })
      .catch(() => navigate('/login'));
  }, [navigate]);

  if (!user) return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#080d1a' }}>
      <p className="text-slate-600">Loading…</p>
    </div>
  );

  return (
    <div className="min-h-screen px-6 py-12" style={{ backgroundColor: '#080d1a' }}>
      <div className="max-w-lg mx-auto">

        <Link to="/" className="text-slate-500 hover:text-white text-sm transition-colors inline-flex items-center gap-2 mb-8">
          ← Back to Solver
        </Link>

        {/* Avatar + name */}
        <div className="flex items-center gap-5 mb-10">
          <div className="w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-2xl">
            ∑
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">{user.username}</h1>
            <p className="text-slate-500 text-sm mt-0.5">Math Solver User</p>
          </div>
        </div>

        {/* Stats grid */}
        {stats && (
          <div className="grid grid-cols-2 gap-4 mb-8">
            {[
              { label: 'Total Solved', value: stats.total,        color: 'text-white' },
              { label: 'Text',         value: stats.text_solves,  color: 'text-blue-400' },
              { label: 'Image',        value: stats.image_solves, color: 'text-purple-400' },
              { label: 'PDF',          value: stats.pdf_solves,   color: 'text-green-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="rounded-xl border border-slate-800 p-4 text-center"
                   style={{ backgroundColor: '#0d1526' }}>
                <p className={`text-3xl font-bold ${color}`}>{value}</p>
                <p className="text-slate-500 text-xs mt-1">{label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Domain breakdown */}
        {stats && (
          <div className="rounded-xl border border-slate-800 p-6" style={{ backgroundColor: '#0d1526' }}>
            <p className="text-slate-500 text-xs uppercase tracking-widest font-semibold mb-4">By Domain</p>
            {[
              { label: 'Calculus',     value: stats.calculus,    color: 'bg-blue-500' },
              { label: 'Probability',  value: stats.probability, color: 'bg-purple-500' },
              { label: 'Discrete',     value: stats.discrete,    color: 'bg-green-500' },
            ].map(({ label, value, color }) => (
              <div key={label} className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">{label}</span>
                  <span className="text-white font-semibold">{value}</span>
                </div>
                <div className="h-1.5 rounded-full" style={{ backgroundColor: '#1e293b' }}>
                  <div className={`h-1.5 rounded-full ${color} transition-all duration-700`}
                       style={{ width: stats.total ? `${(value / stats.total) * 100}%` : '0%' }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
