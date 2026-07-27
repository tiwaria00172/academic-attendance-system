import React, { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { authAPI } from './services/api';

import Login     from './pages/Login';
import Dashboard from './pages/Dashboard';
import AttendanceMarking from './pages/AttendanceMarking';
import Reports   from './pages/Reports';
import StudentManagement from './pages/StudentManagement';
import Header    from './components/Header';
import Sidebar   from './components/Sidebar';

/* ── Auth context ──────────────────────────── */
const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { setLoading(false); return; }
    authAPI.me()
      .then((r) => setUser(r.data.user))
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setLoading(false));
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('access_token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <AuthCtx.Provider value={{ user, login, logout }}>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />

        <Route path="/" element={
          <ProtectedRoute><AppLayout><Dashboard /></AppLayout></ProtectedRoute>
        } />
        <Route path="/students" element={
          <ProtectedRoute><AppLayout><StudentManagement /></AppLayout></ProtectedRoute>
        } />
        <Route path="/attendance/:classroomId" element={
          <ProtectedRoute><AppLayout><AttendanceMarking /></AppLayout></ProtectedRoute>
        } />
        <Route path="/reports" element={
          <ProtectedRoute><AppLayout><Reports /></AppLayout></ProtectedRoute>
        } />
        <Route path="/reports/:classroomId" element={
          <ProtectedRoute><AppLayout><Reports /></AppLayout></ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthCtx.Provider>
  );
}
