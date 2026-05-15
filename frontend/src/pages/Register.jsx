import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function Register() {
  const [form, setForm]   = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await api.post('/api/auth/register/', form);
      localStorage.setItem('access_token',  res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      navigate('/');
    } catch {
      setError('Registration failed. Try a different username.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ backgroundColor: '#080d1a' }}>
      <div className="w-full max-w-sm">

        <div className="text-center mb-8">
          <div className="text-4xl mb-3">∑</div>
          <h1 className="text-white font-bold text-2xl">Math Solver</h1>
          <p className="text-slate-500 text-sm mt-1">Create your account</p>
        </div>

        <form onSubmit={handleSubmit}
              className="rounded-2xl border border-slate-800 p-8 space-y-4"
              style={{ backgroundColor: '#0d1526' }}>

          <div>
            <label className="text-slate-400 text-xs font-semibold uppercase tracking-widest block mb-2">Username</label>
            <input type="text" value={form.username}
                   onChange={e => setForm({ ...form, username: e.target.value })}
                   className="w-full bg-transparent border border-slate-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors"
                   placeholder="choose a username" required />
          </div>

          <div>
            <label className="text-slate-400 text-xs font-semibold uppercase tracking-widest block mb-2">Password</label>
            <input type="password" value={form.password}
                   onChange={e => setForm({ ...form, password: e.target.value })}
                   className="w-full bg-transparent border border-slate-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors"
                   placeholder="min. 6 characters" required minLength={6} />
          </div>

          {error && <p className="text-red-400 text-sm text-center">{error}</p>}

          <button type="submit" disabled={loading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl font-semibold text-sm transition-colors mt-2">
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="text-slate-500 text-sm text-center mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300 transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
