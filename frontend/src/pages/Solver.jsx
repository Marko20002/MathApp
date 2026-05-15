import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import SolverInput     from '../components/SolverInput';
import SolutionDisplay from '../components/SolutionDisplay';
import SolveHistory    from '../components/SolveHistory';

export default function Solver() {
  const [user, setUser]           = useState(null);
  const [solution, setSolution]   = useState(null);
  const [domain, setDomain]       = useState('');
  const [solving, setSolving]     = useState(false);
  const [error, setError]         = useState('');
  const [historyKey, setHistoryKey] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/auth/me/').then(r => setUser(r.data)).catch(() => navigate('/login'));
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const handleSolve = async (payload) => {
    setSolving(true); setError(''); setSolution(null);
    try {
      const res = await api.post('/api/solver/solve/', payload);
      setSolution(res.data.solution);
      setDomain(res.data.domain);
      setHistoryKey(k => k + 1);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Is the backend running?');
    } finally { setSolving(false); }
  };

  return (
    <div className="flex flex-col h-screen" style={{ backgroundColor: '#080d1a' }}>

      {/* Header */}
      <header className="flex items-center justify-between px-6 border-b border-slate-800 flex-shrink-0"
              style={{ height: '60px', backgroundColor: '#0d1526' }}>
        <span className="text-white font-bold text-lg">∑ Math Solver</span>
        {user && (
          <div className="flex items-center gap-4">
            <Link to="/profile" className="text-slate-400 hover:text-white text-sm transition-colors">
              👤 {user.username}
            </Link>
            <button onClick={handleLogout}
                    className="px-3 py-1.5 rounded-lg border border-slate-700 hover:border-red-500/50 text-slate-400 hover:text-red-400 text-xs transition-colors">
              Logout
            </button>
          </div>
        )}
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">

        {/* Left: input + solution */}
        <div className="flex-1 flex flex-col gap-6 p-6 overflow-y-auto">
          <SolverInput onSolve={handleSolve} solving={solving} />

          {error && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-400 text-sm">
              ⚠️ {error}
            </div>
          )}

          {solving && (
            <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-4 py-4 text-blue-400 text-sm text-center">
              ⏳ Solving… DeepSeek is thinking through the problem
            </div>
          )}

          {solution && !solving && (
            <SolutionDisplay solution={solution} domain={domain} />
          )}
        </div>

        {/* Right: history panel */}
        <SolveHistory key={historyKey} />
      </div>
    </div>
  );
}
