import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../App';
import {
  LayoutDashboard, Camera, BarChart3, ScanFace, ChevronLeft, Users, ShieldAlert,
} from 'lucide-react';

export default function Sidebar({ open, onToggle }) {
  const { user } = useAuth();
  const role = user?.role || 'teacher';

  const links = [
    { to: '/',        icon: LayoutDashboard, label: 'Dashboard', roles: ['admin', 'teacher', 'student'] },
    { to: '/students',icon: Users,           label: 'Student Photos',roles: ['admin'] },
    { to: '/reports', icon: BarChart3,       label: 'Reports',   roles: ['admin', 'teacher', 'student'] },
  ];

  const roleBadges = {
    admin:   { label: '🛡️ ADMIN',   bg: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
    teacher: { label: '👨‍🏫 TEACHER', bg: 'bg-brand-500/20 text-brand-300 border-brand-500/30' },
    student: { label: '🎓 STUDENT', bg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
  };
  const badge = roleBadges[role] || roleBadges.teacher;

  return (
    <>
      {/* Overlay on mobile */}
      {open && (
        <div className="fixed inset-0 bg-black/40 z-40 md:hidden" onClick={onToggle} />
      )}

      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          flex flex-col
          bg-gradient-to-b from-slate-900 to-slate-950
          border-r border-slate-800/60
          transition-all duration-300 ease-in-out
          ${open ? 'w-64 translate-x-0' : 'w-0 md:w-20 -translate-x-full md:translate-x-0'}
        `}
      >
        {/* Brand */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800/60
                        overflow-hidden whitespace-nowrap">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-violet-500
                            flex items-center justify-center shadow-lg shadow-brand-500/30 flex-shrink-0">
              <ScanFace size={20} className="text-white" />
            </div>
            {open && (
              <div className="flex flex-col">
                <span className="text-white font-bold text-base tracking-tight animate-fade-in">
                  FaceAttend
                </span>
                <span className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border uppercase w-max mt-0.5 ${badge.bg}`}>
                  {badge.label}
                </span>
              </div>
            )}
          </div>
          <button onClick={onToggle}
                  className="hidden md:flex p-1.5 rounded-lg text-slate-400
                             hover:text-white hover:bg-slate-800 transition-colors">
            <ChevronLeft size={18} className={`transition-transform duration-300
              ${open ? '' : 'rotate-180'}`} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-hidden">
          {links
            .filter((l) => l.roles.includes(role))
            .map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
                 ${isActive
                   ? 'bg-brand-600/20 text-brand-400 shadow-sm'
                   : 'text-slate-400 hover:text-white hover:bg-slate-800/60'}`
              }
            >
              <Icon size={20} className="flex-shrink-0" />
              {open && <span className="text-sm font-medium truncate">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/60 overflow-hidden">
          {open && (
            <p className="text-[11px] text-slate-600 text-center animate-fade-in">
              FaceAttend v1.0 · AI Attendance
            </p>
          )}
        </div>
      </aside>
    </>
  );
}
