import React from 'react';
import { useAuth } from '../App';
import { Menu, LogOut, ScanFace } from 'lucide-react';

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 flex items-center justify-between px-4 md:px-8
                        bg-white/70 backdrop-blur-xl border-b border-slate-200/60
                        sticky top-0 z-30">
      {/* Left */}
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick}
                className="p-2 rounded-xl hover:bg-slate-100 transition-colors md:hidden">
          <Menu size={20} className="text-slate-600" />
        </button>
        <div className="hidden md:flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-violet-500
                          flex items-center justify-center shadow-lg shadow-brand-500/20">
            <ScanFace size={18} className="text-white" />
          </div>
          <span className="font-bold text-lg bg-gradient-to-r from-brand-600 to-violet-600
                           bg-clip-text text-transparent">
            FaceAttend
          </span>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <p className="text-sm font-semibold text-slate-700">{user?.username}</p>
          <p className="text-xs text-slate-400">{user?.role}</p>
        </div>
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-violet-500
                        flex items-center justify-center text-white font-bold text-sm shadow">
          {user?.username?.charAt(0).toUpperCase()}
        </div>
        <button onClick={logout}
                className="p-2 rounded-xl text-slate-400 hover:text-rose-500 hover:bg-rose-50
                           transition-colors" title="Sign out">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
