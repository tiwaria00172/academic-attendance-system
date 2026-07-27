import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { authAPI } from '../services/api';
import { ScanFace, Eye, EyeOff, ArrowRight } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole]         = useState('teacher');
  const [showPw, setShowPw]     = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const handleDemoLogin = async (demoUser, demoPw) => {
    setError('');
    setLoading(true);
    try {
      const res = await authAPI.login(demoUser, demoPw);
      login(res.data.access_token, res.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Demo login failed. Is backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = isSignup
        ? await authAPI.signup(username, email, password, role)
        : await authAPI.login(username, password);
      login(res.data.access_token, res.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center
                    bg-gradient-to-br from-slate-950 via-brand-950 to-violet-950
                    relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px]
                      bg-brand-500/10 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px]
                      bg-violet-500/10 rounded-full blur-3xl animate-pulse-slow" />

      <div className="relative z-10 w-full max-w-md mx-4 animate-slide-up">
        {/* Card */}
        <div className="glass-dark p-8 md:p-10">
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-violet-500
                            flex items-center justify-center shadow-2xl shadow-brand-500/30 mb-4">
              <ScanFace size={32} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">FaceAttend</h1>
            <p className="text-slate-400 text-sm mt-1">AI-Powered Attendance System</p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20
                            text-rose-400 text-sm text-center animate-fade-in">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <input value={username} onChange={(e) => setUsername(e.target.value)}
                     className="input-field !bg-slate-800/60 !border-slate-700 !text-white
                                !placeholder-slate-500 !focus:ring-brand-500/30"
                     placeholder="Enter username" required />
            </div>

            {isSignup && (
              <div className="space-y-4 animate-fade-in">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                    Email
                  </label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                         className="input-field !bg-slate-800/60 !border-slate-700 !text-white
                                    !placeholder-slate-500"
                         placeholder="you@school.edu" required />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                    Select Role
                  </label>
                  <select value={role} onChange={(e) => setRole(e.target.value)}
                          className="input-field !bg-slate-800/60 !border-slate-700 !text-white">
                    <option value="teacher">👨‍🏫 Teacher (Can scan classroom attendance)</option>
                    <option value="admin">🛡️ Admin (Can add students & upload photos)</option>
                    <option value="student">🎓 Student (Read-only attendance view)</option>
                  </select>
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <input type={showPw ? 'text' : 'password'}
                       value={password} onChange={(e) => setPassword(e.target.value)}
                       className="input-field !bg-slate-800/60 !border-slate-700 !text-white
                                  !placeholder-slate-500 pr-11"
                       placeholder="••••••••" required />
                <button type="button" onClick={() => setShowPw(!showPw)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500
                                   hover:text-slate-300 transition-colors">
                  {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2">
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isSignup ? 'Create Account' : 'Sign In'}
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button onClick={() => { setIsSignup(!isSignup); setError(''); }}
                    className="text-sm text-slate-400 hover:text-brand-400 transition-colors">
              {isSignup ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
            </button>
          </div>

          {/* Quick Demo Login Accounts */}
          {!isSignup && (
            <div className="mt-6 pt-4 border-t border-slate-800/60">
              <p className="text-xs font-semibold text-slate-400 text-center mb-3 uppercase tracking-wider">
                ⚡ Instant 1-Click Role Demo Login
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button type="button" onClick={() => handleDemoLogin('admin', 'admin123')}
                        className="py-2 px-2 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 
                                   border border-purple-500/20 text-purple-300 text-xs font-medium 
                                   transition-all flex flex-col items-center gap-1">
                  <span>🛡️</span>
                  <span>Admin</span>
                </button>
                <button type="button" onClick={() => handleDemoLogin('teacher', 'teacher123')}
                        className="py-2 px-2 rounded-xl bg-brand-500/10 hover:bg-brand-500/20 
                                   border border-brand-500/20 text-brand-300 text-xs font-medium 
                                   transition-all flex flex-col items-center gap-1">
                  <span>👨‍🏫</span>
                  <span>Teacher</span>
                </button>
                <button type="button" onClick={() => handleDemoLogin('student', 'student123')}
                        className="py-2 px-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 
                                   border border-emerald-500/20 text-emerald-300 text-xs font-medium 
                                   transition-all flex flex-col items-center gap-1">
                  <span>🎓</span>
                  <span>Student</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
